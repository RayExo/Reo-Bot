from storage.engine import CollectionStore, NOW

CollectionName = 'welcomer_settings'

_store = CollectionStore(
    name=CollectionName,
    defaults={'welcome': False, 'welcome_message': False, 'welcome_embed': False, 'autorole': False, 'autoroles_limit': 3, 'autoroles': [], 'autonick': False, 'greet': False, 'greet_message': 'Hello {user.mention} Welcome to {server}', 'greet_channels': [], 'greet_delete_after': 5, 'created_at': NOW},
    unique_sets=[['guild_id']],
    json_fields=set(['autoroles', 'greet_channels']),
    datetime_fields=set(['created_at']),
    sequence_fields={},
    update_cache=('guilds_welcomer_cache', ['guild_id']),
    delete_cache=('guilds_welcomer_cache', ['guild_id']),
)

async def create_table():
    return await _store.prepare()

async def insert(

    id:int=None,
    guild_id:int=None,
    welcome:bool=None,
    welcome_channel:int=None,
    welcome_message:bool=None,
    welcome_message_content:str=None,
    welcome_embed:bool=None,
    welcome_embed_title:str=None,
    welcome_embed_description:str=None,
    welcome_embed_thumbnail:str=None,
    welcome_embed_image:str=None,
    welcome_embed_footer:str=None,
    welcome_embed_footer_icon:str=None,
    welcome_embed_color:str=None,
    welcome_embed_author:str=None,
    welcome_embed_author_icon:str=None,
    welcome_embed_author_url:str=None,
    autorole:bool=None,
    autoroles_limit:int=None,
    autoroles:str=None,
    autonick:bool=None,
    autonick_format:str=None,
    greet:bool=None,
    greet_message:str=None,
    greet_channels:list=None,
    greet_delete_after:int=None,
    created_at:str=None
):
    return await _store.insert(locals())

async def update(

    id:int,
    guild_id:int=None,
    welcome:bool=None,
    welcome_channel:int=None,
    welcome_message:bool=None,
    welcome_message_content:str=None,
    welcome_embed:bool=None,
    welcome_embed_title:str=None,
    welcome_embed_description:str=None,
    welcome_embed_thumbnail:str=None,
    welcome_embed_image:str=None,
    welcome_embed_footer:str=None,
    welcome_embed_footer_icon:str=None,
    welcome_embed_color:str=None,
    welcome_embed_author:str=None,
    welcome_embed_author_icon:str=None,
    welcome_embed_author_url:str=None,
    autorole:bool=None,
    autoroles_limit:int=None,
    autoroles:str=None,
    autonick:bool=None,
    autonick_format:str=None,
    greet:bool=None,
    greet_message:str=None,
    greet_channels:list=None,
    greet_delete_after:int=None,
    created_at:str=None
):
    return await _store.update(locals())

async def get(

   id:int=None,
    guild_id:int=None,
    welcome:bool=None,
    welcome_channel:int=None,
    welcome_message:bool=None,
    welcome_message_content:str=None,
    welcome_embed:bool=None,
    welcome_embed_title:str=None,
    welcome_embed_description:str=None,
    welcome_embed_thumbnail:str=None,
    welcome_embed_image:str=None,
    welcome_embed_footer:str=None,
    welcome_embed_footer_icon:str=None,
    welcome_embed_color:str=None,
    welcome_embed_author:str=None,
    welcome_embed_author_icon:str=None,
    welcome_embed_author_url:str=None,
    autorole:bool=None,
    autoroles_limit:int=None,
    autoroles:str=None,
    autonick:bool=None,
    autonick_format:str=None,
    greet:bool=None,
    greet_message:str=None,
    greet_channels:list=None,
    greet_delete_after:int=None,
    created_at:str=None
):
    return await _store.get(locals())

async def gets(

   id:int=None,
    guild_id:int=None,
    welcome:bool=None,
    welcome_channel:int=None,
    welcome_message:bool=None,
    welcome_message_content:str=None,
    welcome_embed:bool=None,
    welcome_embed_title:str=None,
    welcome_embed_description:str=None,
    welcome_embed_thumbnail:str=None,
    welcome_embed_image:str=None,
    welcome_embed_footer:str=None,
    welcome_embed_footer_icon:str=None,
    welcome_embed_color:str=None,
    welcome_embed_author:str=None,
    welcome_embed_author_icon:str=None,
    welcome_embed_author_url:str=None,
    autorole:bool=None,
    autoroles_limit:int=None,
    autoroles:str=None,
    autonick:bool=None,
    autonick_format:str=None,
    greet:bool=None,
    greet_message:str=None,
    greet_channels:list=None,
    greet_delete_after:int=None,
    created_at:str=None
):
    return await _store.gets(locals())

async def delete(

   id:int=None,
    guild_id:int=None,
    welcome:bool=None,
    welcome_channel:int=None,
    welcome_message:bool=None,
    welcome_message_content:str=None,
    welcome_embed:bool=None,
    welcome_embed_title:str=None,
    welcome_embed_description:str=None,
    welcome_embed_thumbnail:str=None,
    welcome_embed_image:str=None,
    welcome_embed_footer:str=None,
    welcome_embed_footer_icon:str=None,
    welcome_embed_color:str=None,
    welcome_embed_author:str=None,
    welcome_embed_author_icon:str=None,
    welcome_embed_author_url:str=None,
    autorole:bool=None,
    autoroles_limit:int=None,
    autoroles:str=None,
    autonick:bool=None,
    autonick_format:str=None,
    greet:bool=None,
    greet_message:str=None,
    greet_channels:list=None,
    greet_delete_after:int=None,
    created_at:str=None
):
    return await _store.delete(locals())

async def get_all():
    return await _store.get_all()

