import string, random

from reo.memory.cache import cache

def generate_redeem_code(length:int=20):
    code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=length//2)) + '-' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=length//2))
    if cache.redeem_codes.get(code):
        return generate_redeem_code(length)
    return code

