from __future__ import annotations

import ast
import json
from copy import deepcopy
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from pymongo import ReturnDocument

from reo.bridge.storage import get_collection
from reo.console.logging import logger

NOW = object()


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _clean_document(document: dict[str, Any] | None) -> dict[str, Any] | None:
    if not document:
        return None
    cleaned = dict(document)
    cleaned.pop('_id', None)
    return cleaned


def _clone_default(value: Any) -> Any:
    if value is NOW:
        return _utc_now()
    return deepcopy(value)


@dataclass(slots=True)
class CollectionStore:
    name: str
    defaults: dict[str, Any] = field(default_factory=dict)
    unique_sets: list[list[str]] = field(default_factory=list)
    json_fields: set[str] = field(default_factory=set)
    datetime_fields: set[str] = field(default_factory=set)
    sequence_fields: dict[str, list[str]] = field(default_factory=dict)
    update_cache: tuple[str, list[str]] | None = None
    delete_cache: tuple[str, list[str]] | None = None

    async def prepare(self) -> None:
        collection = await self._collection()
        await self._create_index(collection, [('id', 1)], unique=True, name=f'{self.name}_id_unique')
        for unique_fields in self.unique_sets:
            if not unique_fields:
                continue
            index_name = f"{self.name}_{'_'.join(unique_fields)}_unique"
            await self._create_index(
                collection,
                [(field, 1) for field in unique_fields],
                unique=True,
                sparse=True,
                name=index_name,
            )
        logger.info(f'Database collection {self.name} ready')

    async def insert(self, payload: dict[str, Any]) -> dict[str, Any] | None:
        incoming = self._filter_payload(payload)
        existing = await self._find_existing_unique(incoming)
        if existing:
            await self._trigger_update_hook(existing)
            return existing

        document = {key: _clone_default(value) for key, value in self.defaults.items()}
        for key, value in incoming.items():
            document[key] = self._coerce_value(key, value)

        for field, scope_fields in self.sequence_fields.items():
            if document.get(field) is None:
                scope = {scope_field: document.get(scope_field) for scope_field in scope_fields}
                document[field] = await self._next_sequence(f'{self.name}:{field}', scope)

        if document.get('id') is None:
            document['id'] = await self._next_sequence(f'{self.name}:id', {})

        collection = await self._collection()
        await collection.insert_one(document)
        result = await self.get({'id': document['id']})
        await self._trigger_update_hook(result)
        return result

    async def update(self, payload: dict[str, Any]) -> dict[str, Any] | None:
        incoming = self._filter_payload(payload)
        identifier = incoming.pop('id', None)
        if identifier is None:
            raise ValueError(f'{self.name}.update requires an id')

        update_data: dict[str, Any] = {}
        for key, value in incoming.items():
            update_data[key] = self._coerce_value(key, value)

        collection = await self._collection()
        result = await collection.find_one_and_update(
            {'id': identifier},
            {'$set': update_data},
            return_document=ReturnDocument.AFTER,
        )
        cleaned = _clean_document(result)
        await self._trigger_update_hook(cleaned)
        return cleaned

    async def get(self, filters: dict[str, Any]) -> dict[str, Any] | None:
        prepared = self._build_filters(filters)
        collection = await self._collection()
        result = await collection.find_one(prepared or {}, sort=[('id', 1)])
        return _clean_document(result)

    async def gets(self, filters: dict[str, Any]) -> list[dict[str, Any]]:
        prepared = self._build_filters(filters)
        collection = await self._collection()
        cursor = collection.find(prepared or {}).sort('id', 1)
        return [_clean_document(document) for document in await cursor.to_list(length=None)]

    async def delete(self, filters: dict[str, Any]) -> list[dict[str, Any]]:
        prepared = self._build_filters(filters)
        collection = await self._collection()
        cursor = collection.find(prepared or {}).sort('id', 1)
        documents = [_clean_document(document) for document in await cursor.to_list(length=None)]
        if not documents:
            return []
        await collection.delete_many({'id': {'$in': [document['id'] for document in documents]}})
        for document in documents:
            await self._trigger_delete_hook(document)
        return documents

    async def get_all(self) -> list[dict[str, Any]]:
        collection = await self._collection()
        cursor = collection.find({}).sort('id', 1)
        return [_clean_document(document) for document in await cursor.to_list(length=None)]

    async def count(self, filters: dict[str, Any]) -> int:
        prepared = self._build_filters(filters)
        collection = await self._collection()
        return await collection.count_documents(prepared or {})

    async def delete_limited(self, limit: int, filters: dict[str, Any]) -> list[dict[str, Any]]:
        prepared = self._build_filters(filters)
        collection = await self._collection()
        documents = [_clean_document(document) for document in await collection.find(prepared).sort('id', -1).to_list(length=None)]
        if len(documents) <= limit:
            return []
        overflow = documents[limit:]
        await collection.delete_many({'id': {'$in': [document['id'] for document in overflow]}})
        for document in overflow:
            await self._trigger_delete_hook(document)
        return overflow

    async def adjust_field(self, *, filters: dict[str, Any], field: str, delta: int | float) -> dict[str, Any] | None:
        prepared = self._build_filters(filters)
        current = await self.get(prepared)
        if not current:
            return None
        existing_value = current.get(field, 0) or 0
        if isinstance(existing_value, bool):
            existing_value = int(existing_value)
        target_value = existing_value + delta
        return await self.update({'id': current['id'], field: target_value})

    async def _collection(self):
        return await get_collection(self.name)

    async def _create_index(self, collection, keys, **kwargs) -> None:
        try:
            await collection.create_index(keys, **kwargs)
        except Exception as error:
            logger.warning(f'Failed to create index on {self.name}: {error}')

    async def _find_existing_unique(self, payload: dict[str, Any]) -> dict[str, Any] | None:
        for unique_fields in self.unique_sets:
            if not unique_fields or any(payload.get(field) is None for field in unique_fields):
                continue
            existing = await self.get({field: payload.get(field) for field in unique_fields})
            if existing:
                return existing
        return None

    async def _next_sequence(self, key: str, scope: dict[str, Any]) -> int:
        counters = await get_collection('__counters__')
        scope_key = '|'.join(f'{field}={scope.get(field)}' for field in sorted(scope)) if scope else 'global'
        result = await counters.find_one_and_update(
            {'name': key, 'scope': scope_key},
            {'$inc': {'value': 1}},
            upsert=True,
            return_document=ReturnDocument.AFTER,
        )
        return int(result['value'])

    async def _trigger_update_hook(self, document: dict[str, Any] | None) -> None:
        if not document or not self.update_cache:
            return
        cache_name, arg_names = self.update_cache
        kwargs = {arg_name: document.get(arg_name) for arg_name in arg_names}
        kwargs['data'] = document
        await self._call_cache(cache_name, 'update', kwargs)

    async def _trigger_delete_hook(self, document: dict[str, Any] | None) -> None:
        if not document or not self.delete_cache:
            return
        cache_name, arg_names = self.delete_cache
        kwargs = {arg_name: document.get(arg_name) for arg_name in arg_names}
        await self._call_cache(cache_name, 'delete', kwargs)

    async def _call_cache(self, cache_name: str, method_name: str, kwargs: dict[str, Any]) -> None:
        try:
            from reo.workflows import cache as cache_module

            cache_handler = getattr(cache_module, cache_name, None)
            if cache_handler is None:
                return
            method = getattr(cache_handler, method_name, None)
            if method is None:
                return
            await method(**kwargs)
        except Exception as error:
            logger.warning(f'Cache sync skipped for {self.name}: {error}')

    def _filter_payload(self, payload: dict[str, Any]) -> dict[str, Any]:
        return {key: value for key, value in payload.items() if value is not None}

    def _build_filters(self, payload: dict[str, Any]) -> dict[str, Any]:
        return {key: self._coerce_value(key, value) for key, value in self._filter_payload(payload).items()}

    def _coerce_value(self, key: str, value: Any) -> Any:
        if value == '':
            return None
        if value is None:
            return None
        if key in self.json_fields:
            return self._coerce_json(value)
        if key in self.datetime_fields:
            return self._coerce_datetime(value)
        default_value = self.defaults.get(key)
        if isinstance(default_value, bool) and isinstance(value, str):
            lowered = value.lower()
            if lowered in {'true', 'false'}:
                return lowered == 'true'
        if isinstance(default_value, int) and isinstance(value, str) and value.isdigit():
            return int(value)
        if isinstance(default_value, float) and isinstance(value, str):
            try:
                return float(value)
            except ValueError:
                return value
        return value

    def _coerce_json(self, value: Any) -> Any:
        if isinstance(value, (list, dict)):
            return deepcopy(value)
        if isinstance(value, str):
            text = value.strip()
            if not text:
                return []
            for parser in (json.loads, ast.literal_eval):
                try:
                    return parser(text)
                except Exception:
                    continue
        return value

    def _coerce_datetime(self, value: Any) -> Any:
        if isinstance(value, datetime):
            return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
        if isinstance(value, str):
            text = value.strip()
            if not text:
                return None
            normalized = text.replace('Z', '+00:00')
            for candidate in (normalized, normalized.replace(' ', 'T')):
                try:
                    parsed = datetime.fromisoformat(candidate)
                    return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)
                except ValueError:
                    continue
        return value
