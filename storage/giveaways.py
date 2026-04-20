from storage.engine import CollectionStore, NOW

CollectionName = 'giveaways'

_store = CollectionStore(
    name=CollectionName,
    defaults={'winners': [], 'winner_limit': 1, 'ended': False, 'created_at': NOW},
    unique_sets=[['giveaway_id', 'guild_id']],
    json_fields=set(['winners']),
    datetime_fields=set(['created_at', 'ends_at']),
    sequence_fields={'giveaway_id': ['guild_id']},
    update_cache=('giveaways_cache', ['guild_id', 'giveaway_id']),
    delete_cache=('giveaways_cache', ['guild_id', 'giveaway_id']),
)

async def create_table():
    return await _store.prepare()

async def insert(

    id:int=None,
    giveaway_id:int=None,
    guild_id:int=None,
    channel_id:int=None,
    message_id:int=None,
    host_id:int=None,
    winners:list=None,
    winner_limit:int=None,
    prize:str=None,
    ends_at:str=None,
    ended:bool=None,
    created_at:str=None
):
    return await _store.insert(locals())

async def update(

    id:int,
    giveaway_id:int=None,
    guild_id:int=None,
    channel_id:int=None,
    message_id:int=None,
    host_id:int=None,
    winners:list=None,
    winner_limit:int=None,
    prize:str=None,
    ends_at:str=None,
    ended:bool=None,
    created_at:str=None
):
    return await _store.update(locals())

async def get(

    id:int=None,
    giveaway_id:int=None,
    guild_id:int=None,
    channel_id:int=None,
    message_id:int=None,
    host_id:int=None,
    winners:list=None,
    winner_limit:int=None,
    prize:str=None,
    ends_at:str=None,
    ended:bool=None,
    created_at:str=None
):
    return await _store.get(locals())

async def gets(

    id:int=None,
    giveaway_id:int=None,
    guild_id:int=None,
    channel_id:int=None,
    message_id:int=None,
    host_id:int=None,
    winners:list=None,
    winner_limit:int=None,
    prize:str=None,
    ends_at:str=None,
    ended:bool=None,
    created_at:str=None
):
    return await _store.gets(locals())

async def delete(

    id:int=None,
    giveaway_id:int=None,
    guild_id:int=None,
    channel_id:int=None,
    message_id:int=None,
    host_id:int=None,
    winners:list=None,
    winner_limit:int=None,
    prize:str=None,
    ends_at:str=None,
    ended:bool=None,
    created_at:str=None
):
    return await _store.delete(locals())

async def get_all():
    return await _store.get_all()

