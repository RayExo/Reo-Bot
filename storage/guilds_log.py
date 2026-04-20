from storage.engine import CollectionStore, NOW

CollectionName = 'guilds_log'

_store = CollectionStore(
    name=CollectionName,
    defaults={'enabled': False, 'updated_at': NOW, 'created_at': NOW},
    unique_sets=[['guild_id']],
    json_fields=set([]),
    datetime_fields=set(['created_at', 'updated_at']),
    sequence_fields={},
    update_cache=('guilds_log_cache', ['guild_id']),
    delete_cache=('guilds_log_cache', ['guild_id']),
)

async def create_table():
    return await _store.prepare()

async def insert(

    id:int=None,
    guild_id:int=None,
    enabled:bool=None,
    member_join_channel_id:int=None,
    member_leave_channel_id:int=None,
    member_kick_channel_id:int=None,
    member_ban_channel_id:int=None,
    member_unban_channel_id:int=None,
    member_update_channel_id:int=None,
    message_delete_channel_id:int=None,
    message_edit_channel_id:int=None,
    message_bulk_delete_channel_id:int=None,
    channel_create_channel_id:int=None,
    channel_delete_channel_id:int=None,
    channel_update_channel_id:int=None,
    role_create_channel_id:int=None,
    role_delete_channel_id:int=None,
    role_update_channel_id:int=None,
    emoji_create_channel_id:int=None,
    emoji_delete_channel_id:int=None,
    emoji_update_channel_id:int=None,
    voice_state_update_channel_id:int=None,
    webhook_create_channel_id:int=None,
    webhook_delete_channel_id:int=None,
    webhook_update_channel_id:int=None,
    invite_create_channel_id:int=None,
    invite_delete_channel_id:int=None,
    guild_update_channel_id:int=None,
    antinuke_channel_id:int=None,
    updated_at:str=None,
    created_at:str=None
):
    return await _store.insert(locals())

async def update(

    id:int,
    guild_id:int=None,
    enabled:bool=None,
    member_join_channel_id:int=None,
    member_leave_channel_id:int=None,
    member_kick_channel_id:int=None,
    member_ban_channel_id:int=None,
    member_unban_channel_id:int=None,
    member_update_channel_id:int=None,
    message_delete_channel_id:int=None,
    message_edit_channel_id:int=None,
    message_bulk_delete_channel_id:int=None,
    channel_create_channel_id:int=None,
    channel_delete_channel_id:int=None,
    channel_update_channel_id:int=None,
    role_create_channel_id:int=None,
    role_delete_channel_id:int=None,
    role_update_channel_id:int=None,
    emoji_create_channel_id:int=None,
    emoji_delete_channel_id:int=None,
    emoji_update_channel_id:int=None,
    voice_state_update_channel_id:int=None,
    webhook_create_channel_id:int=None,
    webhook_delete_channel_id:int=None,
    webhook_update_channel_id:int=None,
    invite_create_channel_id:int=None,
    invite_delete_channel_id:int=None,
    guild_update_channel_id:int=None,
    antinuke_channel_id:int=None,
    updated_at:str=None,
    created_at:str=None
):
    return await _store.update(locals())

async def get(

    id:int=None,
    guild_id:int=None,
    enabled:bool=None,
    member_join_channel_id:int=None,
    member_leave_channel_id:int=None,
    member_kick_channel_id:int=None,
    member_ban_channel_id:int=None,
    member_unban_channel_id:int=None,
    member_update_channel_id:int=None,
    message_delete_channel_id:int=None,
    message_edit_channel_id:int=None,
    message_bulk_delete_channel_id:int=None,
    channel_create_channel_id:int=None,
    channel_delete_channel_id:int=None,
    channel_update_channel_id:int=None,
    role_create_channel_id:int=None,
    role_delete_channel_id:int=None,
    role_update_channel_id:int=None,
    emoji_create_channel_id:int=None,
    emoji_delete_channel_id:int=None,
    emoji_update_channel_id:int=None,
    voice_state_update_channel_id:int=None,
    webhook_create_channel_id:int=None,
    webhook_delete_channel_id:int=None,
    webhook_update_channel_id:int=None,
    invite_create_channel_id:int=None,
    invite_delete_channel_id:int=None,
    guild_update_channel_id:int=None,
    antinuke_channel_id:int=None,
    updated_at:str=None,
    created_at:str=None
):
    return await _store.get(locals())

async def gets(

    id:int=None,
    guild_id:int=None,
    enabled:bool=None,
    member_join_channel_id:int=None,
    member_leave_channel_id:int=None,
    member_kick_channel_id:int=None,
    member_ban_channel_id:int=None,
    member_unban_channel_id:int=None,
    member_update_channel_id:int=None,
    message_delete_channel_id:int=None,
    message_edit_channel_id:int=None,
    message_bulk_delete_channel_id:int=None,
    channel_create_channel_id:int=None,
    channel_delete_channel_id:int=None,
    channel_update_channel_id:int=None,
    role_create_channel_id:int=None,
    role_delete_channel_id:int=None,
    role_update_channel_id:int=None,
    emoji_create_channel_id:int=None,
    emoji_delete_channel_id:int=None,
    emoji_update_channel_id:int=None,
    voice_state_update_channel_id:int=None,
    webhook_create_channel_id:int=None,
    webhook_delete_channel_id:int=None,
    webhook_update_channel_id:int=None,
    invite_create_channel_id:int=None,
    invite_delete_channel_id:int=None,
    guild_update_channel_id:int=None,
    antinuke_channel_id:int=None,
    updated_at:str=None,
    created_at:str=None
):
    return await _store.gets(locals())

async def delete(

    id:int=None,
    guild_id:int=None,
    enabled:bool=None,
    member_join_channel_id:int=None,
    member_leave_channel_id:int=None,
    member_kick_channel_id:int=None,
    member_ban_channel_id:int=None,
    member_unban_channel_id:int=None,
    member_update_channel_id:int=None,
    message_delete_channel_id:int=None,
    message_edit_channel_id:int=None,
    message_bulk_delete_channel_id:int=None,
    channel_create_channel_id:int=None,
    channel_delete_channel_id:int=None,
    channel_update_channel_id:int=None,
    role_create_channel_id:int=None,
    role_delete_channel_id:int=None,
    role_update_channel_id:int=None,
    emoji_create_channel_id:int=None,
    emoji_delete_channel_id:int=None,
    emoji_update_channel_id:int=None,
    voice_state_update_channel_id:int=None,
    webhook_create_channel_id:int=None,
    webhook_delete_channel_id:int=None,
    webhook_update_channel_id:int=None,
    invite_create_channel_id:int=None,
    invite_delete_channel_id:int=None,
    guild_update_channel_id:int=None,
    antinuke_channel_id:int=None,
    updated_at:str=None,
    created_at:str=None
):
    return await _store.delete(locals())

async def get_all():
    return await _store.get_all()

