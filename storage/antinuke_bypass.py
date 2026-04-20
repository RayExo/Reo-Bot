from storage.engine import CollectionStore, NOW

CollectionName = 'antinuke_bypass'

_store = CollectionStore(
    name=CollectionName,
    defaults={'anti_channel_create': False, 'anti_channel_delete': False, 'anti_channel_update': False, 'anti_role_create': False, 'anti_role_delete': False, 'anti_role_update': False, 'anti_member_ban': False, 'anti_member_unban': False, 'anti_member_kick': False, 'anti_member_update': False, 'anti_bot_add': False, 'anti_invite_delete': False, 'anti_webhook_create': False, 'anti_webhook_delete': False, 'anti_webhook_update': False, 'anti_server_update': False, 'anti_emote_create': False, 'anti_emote_delete': False, 'anti_emote_update': False, 'anti_prune_member': False, 'anti_everyone_mention': False, 'created_at': NOW},
    unique_sets=[['guild_id', 'user_id']],
    json_fields=set([]),
    datetime_fields=set(['created_at']),
    sequence_fields={},
    update_cache=('antinuke_bypass_cache', ['guild_id', 'user_id']),
    delete_cache=('antinuke_bypass_cache', ['guild_id', 'user_id']),
)

async def create_table():
    return await _store.prepare()

async def insert(

    id:int=None,
    guild_id:int=None,
    user_id:int=None, 
    anti_channel_create:bool=None,
    anti_channel_delete:bool=None,
    anti_channel_update:bool=None,
    anti_role_create:bool=None,
    anti_role_delete:bool=None,
    anti_role_update:bool=None,
    anti_member_ban:bool=None,
    anti_member_unban:bool=None,
    anti_member_kick:bool=None,
    anti_member_update:bool=None,
    anti_bot_add:bool=None,
    anti_invite_delete:bool=None,
    anti_webhook_create:bool=None,
    anti_webhook_delete:bool=None,
    anti_webhook_update:bool=None,
    anti_server_update:bool=None,
    anti_emote_create:bool=None,
    anti_emote_delete:bool=None,
    anti_emote_update:bool=None,
    anti_prune_member:bool=None,
    anti_everyone_mention:bool=None,
    created_at:str=None
):
    return await _store.insert(locals())

async def update(

    id:int,
    guild_id:int=None,
    user_id:int=None,
    anti_channel_create:bool=None,
    anti_channel_delete:bool=None,
    anti_channel_update:bool=None,
    anti_role_create:bool=None,
    anti_role_delete:bool=None,
    anti_role_update:bool=None,
    anti_member_ban:bool=None,
    anti_member_unban:bool=None,
    anti_member_kick:bool=None,
    anti_member_update:bool=None,
    anti_bot_add:bool=None,
    anti_invite_delete:bool=None,
    anti_webhook_create:bool=None,
    anti_webhook_delete:bool=None,
    anti_webhook_update:bool=None,
    anti_server_update:bool=None,
    anti_emote_create:bool=None,
    anti_emote_delete:bool=None,
    anti_emote_update:bool=None,
    anti_prune_member:bool=None,
    anti_everyone_mention:bool=None,
    created_at:str=None
):
    return await _store.update(locals())

async def get(

    id:int=None,
    guild_id:int=None,
    user_id:int=None,
    anti_channel_create:bool=None,
    anti_channel_delete:bool=None,
    anti_channel_update:bool=None,
    anti_role_create:bool=None,
    anti_role_delete:bool=None,
    anti_role_update:bool=None,
    anti_member_ban:bool=None,
    anti_member_unban:bool=None,
    anti_member_kick:bool=None,
    anti_member_update:bool=None,
    anti_bot_add:bool=None,
    anti_invite_delete:bool=None,
    anti_webhook_create:bool=None,
    anti_webhook_delete:bool=None,
    anti_webhook_update:bool=None,
    anti_server_update:bool=None,
    anti_emote_create:bool=None,
    anti_emote_delete:bool=None,
    anti_emote_update:bool=None,
    anti_prune_member:bool=None,
    anti_everyone_mention:bool=None,
    created_at:str=None
):
    return await _store.get(locals())

async def gets(

    id:int=None,
    guild_id:int=None,
    user_id:int=None,
    anti_channel_create:bool=None,
    anti_channel_delete:bool=None,
    anti_channel_update:bool=None,
    anti_role_create:bool=None,
    anti_role_delete:bool=None,
    anti_role_update:bool=None,
    anti_member_ban:bool=None,
    anti_member_unban:bool=None,
    anti_member_kick:bool=None,
    anti_member_update:bool=None,
    anti_bot_add:bool=None,
    anti_invite_delete:bool=None,
    anti_webhook_create:bool=None,
    anti_webhook_delete:bool=None,
    anti_webhook_update:bool=None,
    anti_server_update:bool=None,
    anti_emote_create:bool=None,
    anti_emote_delete:bool=None,
    anti_emote_update:bool=None,
    anti_prune_member:bool=None,
    anti_everyone_mention:bool=None,
    created_at:str=None
):
    return await _store.gets(locals())

async def delete(

    id:int=None,
    guild_id:int=None,
    user_id:int=None,
    anti_channel_create:bool=None,
    anti_channel_delete:bool=None,
    anti_channel_update:bool=None,
    anti_role_create:bool=None,
    anti_role_delete:bool=None,
    anti_role_update:bool=None,
    anti_member_ban:bool=None,
    anti_member_unban:bool=None,
    anti_member_kick:bool=None,
    anti_member_update:bool=None,
    anti_bot_add:bool=None,
    anti_invite_delete:bool=None,
    anti_webhook_create:bool=None,
    anti_webhook_delete:bool=None,
    anti_webhook_update:bool=None,
    anti_server_update:bool=None,
    anti_emote_create:bool=None,
    anti_emote_delete:bool=None,
    anti_emote_update:bool=None,
    anti_prune_member:bool=None,
    anti_everyone_mention:bool=None,
    created_at:str=None
):
    return await _store.delete(locals())

async def get_all():
    return await _store.get_all()

