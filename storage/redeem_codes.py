from storage.engine import CollectionStore, NOW

CollectionName = 'redeem_codes'

_store = CollectionStore(
    name=CollectionName,
    defaults={'claimed': False, 'created_at': NOW},
    unique_sets=[['code']],
    json_fields=set([]),
    datetime_fields=set(['claimed_at', 'created_at', 'expires_at']),
    sequence_fields={},
    update_cache=('redeem_codes_cache', ['code']),
    delete_cache=('redeem_codes_cache', ['code']),
)

async def create_table():
    return await _store.prepare()

async def insert(

    id:int=None,
    code:str=None,
    code_type:str=None,
    code_value:str=None,
    valid_for_days:int=None,
    expires_at:str=None,
    claimed:bool=None,
    claimed_by:int=None,
    claimed_at:str=None,
    created_at:str=None
):
    return await _store.insert(locals())

async def update(

    id:int,
    code:str=None,
    code_type:str=None,
    code_value:str=None,
    valid_for_days:int=None,
    expires_at:str=None,
    claimed:bool=None,
    claimed_by:int=None,
    claimed_at:str=None,
    created_at:str=None
):
    return await _store.update(locals())

async def get(

    id:int=None,
    code:str=None,
    code_type:str=None,
    code_value:str=None,
    valid_for_days:int=None,
    expires_at:str=None,
    claimed:bool=None,
    claimed_by:int=None,
    claimed_at:str=None,
    created_at:str=None
):
    return await _store.get(locals())

async def gets(

    id:int=None,
    code:str=None,
    code_type:str=None,
    code_value:str=None,
    valid_for_days:int=None,
    expires_at:str=None,
    claimed:bool=None,
    claimed_by:int=None,
    claimed_at:str=None,
    created_at:str=None
):
    return await _store.gets(locals())

async def delete(

    id:int=None,
    code:str=None,
    code_type:str=None,
    code_value:str=None,
    valid_for_days:int=None,
    expires_at:str=None,
    claimed:bool=None,
    claimed_by:int=None,
    claimed_at:str=None,
    created_at:str=None
):
    return await _store.delete(locals())

async def get_all():
    return await _store.get_all()

