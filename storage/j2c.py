from storage.engine import CollectionStore, NOW

CollectionName = 'j2c'

_store = CollectionStore(
    name=CollectionName,
    defaults={'created_at': NOW},
    unique_sets=[['channel_id', 'guild_id', 'owner_id']],
    json_fields=set([]),
    datetime_fields=set(['created_at']),
    sequence_fields={},
    update_cache=('j2c_cache', ['channel_id']),
    delete_cache=('j2c_cache', ['channel_id']),
)

async def create_table():
    return await _store.prepare()

async def insert(

    id:int=None,
    channel_id:int=None,
    guild_id:int=None,
    owner_id:int=None,
    controller_message_id:int=None,
    created_at:str=None
):
    return await _store.insert(locals())

async def update(

    id:int,
    channel_id:int=None,
    guild_id:int=None,
    owner_id:int=None,
    controller_message_id:int=None,
    created_at:str=None
):
    return await _store.update(locals())

async def get(

    id:int=None,
    channel_id:int=None,
    guild_id:int=None,
    owner_id:int=None,
    controller_message_id:int=None,
    created_at:str=None
):
    return await _store.get(locals())

async def gets(

    id:int=None,
    channel_id:int=None,
    guild_id:int=None,
    owner_id:int=None,
    controller_message_id:int=None,
    created_at:str=None
):
    return await _store.gets(locals())

async def delete(

    id:int=None,
    channel_id:int=None,
    guild_id:int=None,
    owner_id:int=None,
    controller_message_id:int=None,
    created_at:str=None
):
    return await _store.delete(locals())

async def get_all():
    return await _store.get_all()

