from storage.engine import CollectionStore, NOW

CollectionName = 'ticket_settings'

_store = CollectionStore(
    name=CollectionName,
    defaults={
        'enabled': False,
        'support_roles': [],
        'ticket_limit': 1,
        'open_ticket_category_id': None,
        'closed_ticket_category_id': None,
        'ticket_panel_channel_id': None,
        'ticket_panel_message_id': None,
        'ticket_panel_message_content': None,
        'ticket_panel_message_embed': {},
        'close_ticket_message_content': None,
        'close_ticket_message_embed': {},
        'created_at': NOW,
    },
    unique_sets=[['ticket_module_id', 'guild_id']],
    json_fields=set(['close_ticket_message_embed', 'support_roles', 'ticket_panel_message_embed']),
    datetime_fields=set(['created_at']),
    sequence_fields={'ticket_module_id': ['guild_id']},
    update_cache=('ticket_settings_cache', ['guild_id', 'ticket_module_id']),
    delete_cache=('ticket_settings_cache', ['guild_id', 'ticket_module_id']),
)

async def create_table():
    return await _store.prepare()

async def insert(

    id:int=None,
    ticket_module_id:int=None,
    enabled:bool=None,
    guild_id:int=None,
    support_roles:list=None,
    ticket_limit:int=None,
    open_ticket_category_id:int=None,
    closed_ticket_category_id:int=None,
    ticket_panel_channel_id:int=None,
    ticket_panel_message_id:int=None,
    ticket_panel_message_content:str=None,
    ticket_panel_message_embed:dict=None,
    close_ticket_message_content:str=None,
    close_ticket_message_embed:dict=None,
    created_at:str=None
):
    return await _store.insert(locals())

async def update(

    id:int,
    ticket_module_id:int=None,
    enabled:bool=None,
    guild_id:int=None,
    support_roles:list=None,
    ticket_limit:int=None,
    open_ticket_category_id:int=None,
    closed_ticket_category_id:int=None,
    ticket_panel_channel_id:int=None,
    ticket_panel_message_id:int=None,
    ticket_panel_message_content:str=None,
    ticket_panel_message_embed:dict=None,
    close_ticket_message_content:str=None,
    close_ticket_message_embed:dict=None,
    created_at:str=None
):
    return await _store.update(locals())

async def get(

    id:int=None,
    ticket_module_id:int=None,
    enabled:bool=None,
    guild_id:int=None,
    support_roles:list=None,
    ticket_limit:int=None,
    open_ticket_category_id:int=None,
    closed_ticket_category_id:int=None,
    ticket_panel_channel_id:int=None,
    ticket_panel_message_id:int=None,
    ticket_panel_message_content:str=None,
    ticket_panel_message_embed:dict=None,
    close_ticket_message_content:str=None,
    close_ticket_message_embed:dict=None,
    created_at:str=None
):
    return await _store.get(locals())

async def gets(

    id:int=None,
    ticket_module_id:int=None,
    enabled:bool=None,
    guild_id:int=None,
    support_roles:list=None,
    ticket_limit:int=None,
    open_ticket_category_id:int=None,
    closed_ticket_category_id:int=None,
    ticket_panel_channel_id:int=None,
    ticket_panel_message_id:int=None,
    ticket_panel_message_content:str=None,
    ticket_panel_message_embed:dict=None,
    close_ticket_message_content:str=None,
    close_ticket_message_embed:dict=None,
    created_at:str=None
):
    return await _store.gets(locals())

async def delete(

    id:int=None,
    ticket_module_id:int=None,
    enabled:bool=None,
    guild_id:int=None,
    support_roles:list=None,
    ticket_limit:int=None,
    open_ticket_category_id:int=None,
    closed_ticket_category_id:int=None,
    ticket_panel_channel_id:int=None,
    ticket_panel_message_id:int=None,
    ticket_panel_message_content:str=None,
    ticket_panel_message_embed:dict=None,
    close_ticket_message_content:str=None,
    close_ticket_message_embed:dict=None,
    created_at:str=None
):
    return await _store.delete(locals())

async def get_all():
    return await _store.get_all()

