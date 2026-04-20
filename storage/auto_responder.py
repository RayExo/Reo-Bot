from storage.engine import CollectionStore, NOW

CollectionName = 'auto_responder'

_store = CollectionStore(
    name=CollectionName,
    defaults={'created_at': NOW},
    unique_sets=[['guild_id', 'keyword']],
    json_fields=set([]),
    datetime_fields=set(['created_at']),
    sequence_fields={},
    update_cache=('auto_responder_cache', ['guild_id', 'keyword']),
    delete_cache=('auto_responder_cache', ['guild_id', 'keyword']),
)

async def create_table():
    return await _store.prepare()

async def insert(

    id:int=None,
    guild_id:int=None,
    keyword:str=None,
    response:str=None,
    created_at:str=None
):
    return await _store.insert(locals())

async def update(

    id:int,
    guild_id:int=None,
    keyword:str=None,
    response:str=None,
    created_at:str=None
):
    return await _store.update(locals())

async def get(

    id:int=None,
    guild_id:int=None,
    keyword:str=None,
    response:str=None,
    created_at:str=None
):
    return await _store.get(locals())

async def gets(

    id:int=None,
    guild_id:int=None,
    keyword:str=None,
    response:str=None,
    created_at:str=None
):
    return await _store.gets(locals())

async def delete(

    id:int=None,
    guild_id:int=None,
    keyword:str=None,
    response:str=None,
    created_at:str=None
):
    return await _store.delete(locals())

async def get_all():
    return await _store.get_all()

async def delete_limited(
    limit:int,
    guild_id:int
):
    return await _store.delete_limited(limit=limit, filters={'guild_id': guild_id})
