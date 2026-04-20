from storage.engine import CollectionStore, NOW

CollectionName = "command_access"

_store = CollectionStore(
    name=CollectionName,
    defaults={"disabled_commands": [], "created_at": NOW},
    unique_sets=[["guild_id"]],
    json_fields={"disabled_commands"},
    datetime_fields={"created_at"},
    sequence_fields={},
    update_cache=("command_access_cache", ["guild_id"]),
    delete_cache=("command_access_cache", ["guild_id"]),
)


async def create_table():
    return await _store.prepare()


async def insert(
    id: int = None,
    guild_id: int = None,
    disabled_commands: list = None,
    created_at: str = None,
):
    return await _store.insert(locals())


async def update(
    id: int,
    guild_id: int = None,
    disabled_commands: list = None,
    created_at: str = None,
):
    return await _store.update(locals())


async def get(
    id: int = None,
    guild_id: int = None,
    disabled_commands: list = None,
    created_at: str = None,
):
    return await _store.get(locals())


async def gets(
    id: int = None,
    guild_id: int = None,
    disabled_commands: list = None,
    created_at: str = None,
):
    return await _store.gets(locals())


async def delete(
    id: int = None,
    guild_id: int = None,
    disabled_commands: list = None,
    created_at: str = None,
):
    return await _store.delete(locals())


async def get_all():
    return await _store.get_all()
