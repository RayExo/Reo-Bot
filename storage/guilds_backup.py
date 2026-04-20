from storage.engine import CollectionStore, NOW

CollectionName = 'guilds_backup'

_store = CollectionStore(
    name=CollectionName,
    defaults={'backup': [], 'created_at': NOW},
    unique_sets=[],
    json_fields=set(['backup']),
    datetime_fields=set(['created_at']),
    sequence_fields={},
    update_cache=('guilds_backup_cache', ['guild_id']),
    delete_cache=('guilds_backup_cache', ['guild_id', 'id']),
)

async def create_table():
    return await _store.prepare()

async def insert(

    id:int=None,
    guild_id:int=None,
    backup:str=None,
    created_at:str=None
):
    return await _store.insert(locals())

async def update(

    id:int,
    guild_id:int=None,
    backup:str=None,
    created_at:str=None
):
    return await _store.update(locals())

async def get(

    id:int=None,
    guild_id:int=None,
    backup:str=None,
    created_at:str=None
):
    return await _store.get(locals())

async def gets(

    id:int=None,
    guild_id:int=None,
    backup:str=None,
    created_at:str=None
):
    return await _store.gets(locals())

async def delete(

    id:int=None,
    guild_id:int=None,
    backup:str=None,
    created_at:str=None
):
    return await _store.delete(locals())

async def get_all():
    return await _store.get_all()

