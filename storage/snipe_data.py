from storage.engine import CollectionStore, NOW

CollectionName = 'snipe_data'

_store = CollectionStore(
    name=CollectionName,
    defaults={'type': 'delete', 'created_at': NOW},
    unique_sets=[['channel_id', 'message_id', 'type']],
    json_fields=set([]),
    datetime_fields=set(['created_at']),
    sequence_fields={},
    update_cache=('snipe_data_cache', ['channel_id']),
    delete_cache=('snipe_data_cache', ['channel_id', 'type']),
)

async def create_table():
    return await _store.prepare()

async def insert(

    id:int=None,
    channel_id:int=None,
    message_id:int=None,
    type:str=None,
    before_content:str=None,
    after_content:str=None,
    author_id:int=None,
    created_at:str=None
):
    return await _store.insert(locals())

async def update(

    id:int,
    channel_id:int=None,
    message_id:int=None,
    type:str=None,
    before_content:str=None,
    after_content:str=None,
    author_id:int=None,
    created_at:str=None
):
    return await _store.update(locals())

async def get(

    id:int=None,
    channel_id:int=None,
    message_id:int=None,
    type:str=None,
    before_content:str=None,
    after_content:str=None,
    author_id:int=None,
    created_at:str=None
):
    return await _store.get(locals())

async def gets(

    id:int=None,
    channel_id:int=None,
    message_id:int=None,
    type:str=None,
    before_content:str=None,
    after_content:str=None,
    author_id:int=None,
    created_at:str=None
):
    return await _store.gets(locals())

async def delete(

    id:int=None,
    channel_id:int=None,
    message_id:int=None,
    type:str=None,
    before_content:str=None,
    after_content:str=None,
    author_id:int=None,
    created_at:str=None
):
    return await _store.delete(locals())

async def get_all():
    return await _store.get_all()

