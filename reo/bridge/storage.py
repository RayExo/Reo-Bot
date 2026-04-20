from __future__ import annotations

from motor.motor_asyncio import AsyncIOMotorClient

from reo.console.logging import logger
from reo.config.config import storage as StorageConfig

_client: AsyncIOMotorClient | None = None
_database = None
_storage_settings = StorageConfig()


async def get_client() -> AsyncIOMotorClient:
    global _client
    if _client is None:
        _client = AsyncIOMotorClient(_storage_settings.uri, serverSelectionTimeoutMS=10000)
        await _client.admin.command('ping')
        logger.info('Connected to Mongo storage')
    return _client


async def get_database():
    global _database
    if _database is None:
        client = await get_client()
        _database = client[_storage_settings.name]
    return _database


async def get_collection(name: str):
    database = await get_database()
    return database[name]


async def get_connection():
    return await get_database()


async def release_connection(_connection=None):
    return None


async def ping() -> float:
    client = await get_client()
    await client.admin.command('ping')
    return 1.0
