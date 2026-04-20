from storage.engine import CollectionStore, NOW

CollectionName = 'tickets'

_store = CollectionStore(
    name=CollectionName,
    defaults={'extra_users': [], 'closed': False, 'deleted': False, 'created_at': NOW},
    unique_sets=[['ticket_id', 'ticket_module_id', 'guild_id']],
    json_fields=set(['extra_users']),
    datetime_fields=set(['closed_at', 'created_at']),
    sequence_fields={'ticket_id': ['guild_id', 'ticket_module_id']},
    update_cache=None,
    delete_cache=None,
)

async def create_table():
    return await _store.prepare()

async def insert(

    id:int=None,
    ticket_id:int=None,
    ticket_module_id:int=None,
    guild_id:int=None,
    creator_id:int=None,
    extra_users:list=None,
    channel_id:int=None,
    closed:bool=None,
    deleted:bool=None,
    close_ticket_message_id:int=None,
    closed_at:str=None,
    created_at:str=None
):
    return await _store.insert(locals())

async def update(

    id:int,
    ticket_id:int=None,
    ticket_module_id:int=None,
    guild_id:int=None,
    creator_id:int=None,
    extra_users:list=None,
    channel_id:int=None,
    closed:bool=None,
    deleted:bool=None,
    close_ticket_message_id:int=None,
    closed_at:str=None,
    created_at:str=None
):
    return await _store.update(locals())

async def get(

    id:int=None,
    ticket_id:int=None,
    ticket_module_id:int=None,
    guild_id:int=None,
    creator_id:int=None,
    extra_users:list=None,
    channel_id:int=None,
    closed:bool=None,
    deleted:bool=None,
    close_ticket_message_id:int=None,
    closed_at:str=None,
    created_at:str=None
):
    return await _store.get(locals())

async def gets(

    id:int=None,
    ticket_id:int=None,
    ticket_module_id:int=None,
    guild_id:int=None,
    creator_id:int=None,
    extra_users:list=None,
    channel_id:int=None,
    closed:bool=None,
    deleted:bool=None,
    close_ticket_message_id:int=None,
    closed_at:str=None,
    created_at:str=None
):
    return await _store.gets(locals())

async def delete(

    id:int=None,
    ticket_id:int=None,
    ticket_module_id:int=None,
    guild_id:int=None,
    creator_id:int=None,
    extra_users:list=None,
    channel_id:int=None,
    closed:bool=None,
    deleted:bool=None,
    close_ticket_message_id:int=None,
    closed_at:str=None,
    created_at:str=None
):
    return await _store.delete(locals())

async def get_all():
    return await _store.get_all()

async def count(

    id:int=None,
    ticket_id:int=None,
    ticket_module_id:int=None,
    guild_id:int=None,
    creator_id:int=None,
    extra_users:list=None,
    channel_id:int=None,
    closed:bool=None,
    deleted:bool=None,
    close_ticket_message_id:int=None,
    closed_at:str=None,
    created_at:str=None
):
    return await _store.count(locals())

