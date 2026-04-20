from storage.engine import CollectionStore, NOW

CollectionName = 'shop'

_store = CollectionStore(
    name=CollectionName,
    defaults={'price': 0, 'created_at': NOW},
    unique_sets=[['name']],
    json_fields=set([]),
    datetime_fields=set(['created_at']),
    sequence_fields={},
    update_cache=('shop_cache', ['id']),
    delete_cache=('shop_cache', ['id']),
)

async def create_table():
    return await _store.prepare()

async def insert(

    id:int=None,
    name:str=None,
    description:str=None,
    price:float=None,
    image_url:str=None,
    created_at:str=None
):
    return await _store.insert(locals())

async def update(

    id:int,
    name:str=None,
    description:str=None,
    price:float=None,
    image_url:str=None,
    created_at:str=None
):
    return await _store.update(locals())

async def get(

    id:int=None,
    name:str=None,
    description:str=None,
    price:float=None,
    image_url:str=None,
    created_at:str=None
):
    return await _store.get(locals())

async def gets(

    id:int=None,
    name:str=None,
    description:str=None,
    price:float=None,
    image_url:str=None,
    created_at:str=None
):
    return await _store.gets(locals())

async def delete(

    id:int=None,
    name:str=None,
    description:str=None,
    price:float=None,
    image_url:str=None,
    created_at:str=None
):
    return await _store.delete(locals())

async def get_all():
    return await _store.get_all()

async def count(

    id:int=None,
    name:str=None,
    description:str=None,
    price:float=None,
    image_url:str=None,
    created_at:str=None
):
    return await _store.count(locals())

