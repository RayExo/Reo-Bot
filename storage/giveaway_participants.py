from storage.engine import CollectionStore, NOW

CollectionName = 'giveaway_participants'

_store = CollectionStore(
    name=CollectionName,
    defaults={'winning_rate': 50, 'created_at': NOW},
    unique_sets=[],
    json_fields=set([]),
    datetime_fields=set(['created_at']),
    sequence_fields={},
    update_cache=None,
    delete_cache=None,
)

async def create_table():
    return await _store.prepare()

async def insert(

    id:int=None,
    guild_id:int=None,
    giveaway_id:int=None,
    user_id:int=None,
    winning_rate:float=None,
    created_at:str=None
):
    return await _store.insert(locals())

async def update(

    id:int,
    guild_id:int=None,
    giveaway_id:int=None,
    user_id:int=None,
    winning_rate:float=None,
    created_at:str=None
):
    return await _store.update(locals())

async def get(

    id:int=None,
    guild_id:int=None,
    giveaway_id:int=None,
    user_id:int=None,
    winning_rate:float=None,
    created_at:str=None
):
    return await _store.get(locals())

async def gets(

    id:int=None,
    guild_id:int=None,
    giveaway_id:int=None,
    user_id:int=None,
    winning_rate:float=None,
    created_at:str=None
):
    return await _store.gets(locals())

async def delete(

    id:int=None,
    guild_id:int=None,
    giveaway_id:int=None,
    user_id:int=None,
    winning_rate:float=None,
    created_at:str=None
):
    return await _store.delete(locals())

async def get_all():
    return await _store.get_all()

async def count(

    id:int=None,
    guild_id:int=None,
    giveaway_id:int=None,
    user_id:int=None,
    winning_rate:float=None,
    created_at:str=None
):
    return await _store.count(locals())

