from storage.engine import CollectionStore, NOW

CollectionName = 'j2c_settings'

_store = CollectionStore(
    name=CollectionName,
    defaults={'enabled': False, 'created_at': NOW},
    unique_sets=[['guild_id']],
    json_fields=set([]),
    datetime_fields=set(['created_at']),
    sequence_fields={},
    update_cache=('j2c_settings_cache', ['guild_id']),
    delete_cache=('j2c_settings_cache', ['guild_id']),
)

async def create_table():
    return await _store.prepare()

async def insert(

    id:int=None,
    guild_id:int=None,
    enabled:bool=None,
    create_vc_channel_id:int=None,
    create_vc_category_id:int=None,
    created_at:str=None
):
    return await _store.insert(locals())

async def update(

    id:int,
    guild_id:int=None,
    enabled:bool=None,
    create_vc_channel_id:int=None,
    create_vc_category_id:int=None,
    created_at:str=None
):
    return await _store.update(locals())

async def get(

    id:int=None,
    guild_id:int=None,
    enabled:bool=None,
    create_vc_channel_id:int=None,
    create_vc_category_id:int=None,
    created_at:str=None
):
    return await _store.get(locals())

async def gets(

    id:int=None,
    guild_id:int=None,
    enabled:bool=None,
    create_vc_channel_id:int=None,
    create_vc_category_id:int=None,
    created_at:str=None
):
    return await _store.gets(locals())

async def delete(

    id:int=None,
    guild_id:int=None,
    enabled:bool=None,
    create_vc_channel_id:int=None,
    create_vc_category_id:int=None,
    created_at:str=None
):
    return await _store.delete(locals())

async def get_all():
    return await _store.get_all()

