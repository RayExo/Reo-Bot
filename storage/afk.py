from storage.engine import CollectionStore, NOW

CollectionName = 'afk'

_store = CollectionStore(
    name=CollectionName,
    defaults={'afk': False, 'reason': None, 'mentioned': 0, 'afk_end': None, 'created_at': NOW},
    unique_sets=[['user_id', 'guild_id']],
    json_fields=set([]),
    datetime_fields=set(['afk_end', 'created_at']),
    sequence_fields={},
    update_cache=('afk_cache', ['guild_id', 'user_id']),
    delete_cache=('afk_cache', ['guild_id', 'user_id']),
)

async def create_table():
    return await _store.prepare()

async def insert(

    id:int=None,
    user_id:int=None,
    guild_id:int=None,
    afk:bool=None,
    reason:str=None,
    mentioned:int=None,
    afk_end:str=None,
    created_at:str=None
):
    return await _store.insert(locals())

async def update(

    id:int,
    user_id:int=None,
    guild_id:int=None,
    afk:bool=None,
    reason:str=None,
    mentioned:int=None,
    afk_end:str=None,
    created_at:str=None
):
    return await _store.update(locals())

async def get(

    id:int=None,
    user_id:int=None,
    guild_id:int=None,
    afk:bool=None,
    reason:str=None,
    mentioned:int=None,
    afk_end:str=None,
    created_at:str=None
):
    return await _store.get(locals())

async def gets(

    id:int=None,
    user_id:int=None,
    guild_id:int=None,
    afk:bool=None,
    reason:str=None,
    mentioned:int=None,
    afk_end:str=None,
    created_at:str=None
):
    return await _store.gets(locals())

async def delete(

    id:int=None,
    user_id:int=None,
    guild_id:int=None,
    afk:bool=None,
    reason:str=None,
    mentioned:int=None,
    afk_end:str=None,
    created_at:str=None
):
    return await _store.delete(locals())

async def get_all():
    return await _store.get_all()

