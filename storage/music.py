from storage.engine import CollectionStore, NOW

CollectionName = 'music'

_store = CollectionStore(
    name=CollectionName,
    defaults={'default_volume': 80, 'default_repeat': False, 'default_autoplay': False, 'created_at': NOW},
    unique_sets=[['guild_id']],
    json_fields=set([]),
    datetime_fields=set(['created_at']),
    sequence_fields={},
    update_cache=('music_cache', ['guild_id']),
    delete_cache=('music_cache', ['guild_id']),
)

async def create_table():
    return await _store.prepare()

async def insert(

    id:int=None,
    guild_id:int=None,
    music_setup_channel_id:int=None,
    music_setup_message_id:int=None,
    default_volume:int=None,
    default_repeat:bool=None,
    default_autoplay:bool=None,
    created_at:str=None
):
    return await _store.insert(locals())

async def update(

    id:int,
    guild_id:int=None,
    music_setup_channel_id:int=None,
    music_setup_message_id:int=None,
    default_volume:int=None,
    default_repeat:bool=None,
    default_autoplay:bool=None,
    created_at:str=None
):
    return await _store.update(locals())

async def get(

    id:int=None,
    guild_id:int=None,
    music_setup_channel_id:int=None,
    music_setup_message_id:int=None,
    default_volume:int=None,
    default_repeat:bool=None,
    default_autoplay:bool=None,
    created_at:str=None
):
    return await _store.get(locals())

async def gets(

    id:int=None,
    guild_id:int=None,
    music_setup_channel_id:int=None,
    music_setup_message_id:int=None,
    default_volume:int=None,
    default_repeat:bool=None,
    default_autoplay:bool=None,
    created_at:str=None
):
    return await _store.gets(locals())

async def delete(

    id:int=None,
    guild_id:int=None,
    music_setup_channel_id:int=None,
    music_setup_message_id:int=None,
    default_volume:int=None,
    default_repeat:bool=None,
    default_autoplay:bool=None,
    created_at:str=None
):
    return await _store.delete(locals())

async def get_all():
    return await _store.get_all()

async def count(

    id:int=None,
    guild_id:int=None,
    music_setup_channel_id:int=None,
    music_setup_message_id:int=None,
    default_volume:int=None,
    default_repeat:bool=None,
    default_autoplay:bool=None,
    created_at:str=None
):
    return await _store.count(locals())

