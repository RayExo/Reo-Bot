from storage.engine import CollectionStore, NOW

CollectionName = 'users'

_store = CollectionStore(
    name=CollectionName,
    defaults={'balance': 0, 'level': 0, 'xp': 0, 'transfered_balance': 0, 'received_balance': 0, 'economy_rules_accepted': False, 'type': 'user', 'relationship': 'single', 'no_prefix': False, 'no_prefix_subscription': False, 'banned': False, 'updated_at': NOW, 'created_at': NOW},
    unique_sets=[['user_id']],
    json_fields=set([]),
    datetime_fields=set(['banned_at', 'created_at', 'daily_at', 'no_prefix_end', 'received_balance_at', 'transfered_balance_at', 'updated_at']),
    sequence_fields={},
    update_cache=('users_cache', ['user_id']),
    delete_cache=('users_cache', ['user_id']),
)

async def create_table():
    return await _store.prepare()

async def insert(

    id:int=None,
    user_id:int=None,
    balance:float=None,
    level:int=None,
    xp:int=None,
    transfered_balance:float=None,
    transfered_balance_at:str=None,
    received_balance:float=None,
    received_balance_at:str=None,
    economy_rules_accepted:bool=None,
    daily_at:str=None,
    type:str=None,
    relationship:str=None,
    no_prefix:bool=None,
    no_prefix_subscription:bool=None,
    no_prefix_end:str=None,
    banned:bool=None,
    banned_reason:str=None,
    banned_at:str=None,
    updated_at:str=None,
    created_at:str=None
):
    return await _store.insert(locals())

async def update(

    id:int,
    user_id:int=None,
    balance:float=None,
    level:int=None,
    xp:int=None,
    transfered_balance:float=None,
    transfered_balance_at:str=None,
    received_balance:float=None,
    received_balance_at:str=None,
    economy_rules_accepted:bool=None,
    daily_at:str=None,
    type:str=None,
    relationship:str=None,
    no_prefix:bool=None,
    no_prefix_subscription:bool=None,
    no_prefix_end:str=None,
    banned:bool=None,
    banned_reason:str=None,
    banned_at:str=None,
    updated_at:str=None,
    created_at:str=None
):
    return await _store.update(locals())

async def get(

    id:int=None,
    user_id:int=None,
    balance:float=None,
    level:int=None,
    xp:int=None,
    transfered_balance:float=None,
    transfered_balance_at:str=None,
    received_balance:float=None,
    received_balance_at:str=None,
    economy_rules_accepted:bool=None,
    daily_at:str=None,
    type:str=None,
    relationship:str=None,
    no_prefix:bool=None,
    no_prefix_subscription:bool=None,
    no_prefix_end:str=None,
    banned:bool=None,
    banned_reason:str=None,
    banned_at:str=None,
    updated_at:str=None,
    created_at:str=None
):
    return await _store.get(locals())

async def gets(

    id:int=None,
    user_id:int=None,
    balance:float=None,
    level:int=None,
    xp:int=None,
    transfered_balance:float=None,
    transfered_balance_at:str=None,
    received_balance:float=None,
    received_balance_at:str=None,
    economy_rules_accepted:bool=None,
    daily_at:str=None,
    type:str=None,
    relationship:str=None,
    no_prefix:bool=None,
    no_prefix_subscription:bool=None,
    no_prefix_end:str=None,
    banned:bool=None,
    banned_reason:str=None,
    banned_at:str=None,
    updated_at:str=None,
    created_at:str=None
):
    return await _store.gets(locals())

async def delete(

    id:int=None,
    user_id:int=None,
    balance:float=None,
    level:int=None,
    xp:int=None,
    transfered_balance:float=None,
    transfered_balance_at:str=None,
    received_balance:float=None,
    received_balance_at:str=None,
    economy_rules_accepted:bool=None,
    daily_at:str=None,
    type:str=None,
    relationship:str=None,
    no_prefix:bool=None,
    no_prefix_subscription:bool=None,
    no_prefix_end:str=None,
    banned:bool=None,
    banned_reason:str=None,
    banned_at:str=None,
    updated_at:str=None,
    created_at:str=None
):
    return await _store.delete(locals())

async def get_all():
    return await _store.get_all()

async def add_xp(
    user_id:int,
    xp:int
):
    return await _store.adjust_field(filters={'user_id': user_id}, field='xp', delta=xp)


async def remove_xp(
    user_id:int,
    xp:int
):
    return await _store.adjust_field(filters={'user_id': user_id}, field='xp', delta=-xp)


async def add_balance(
    user_id:int,
    balance:float
):
    return await _store.adjust_field(filters={'user_id': user_id}, field='balance', delta=balance)


async def remove_balance(
    user_id:int,
    balance:float
):
    return await _store.adjust_field(filters={'user_id': user_id}, field='balance', delta=-balance)
