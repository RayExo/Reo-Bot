import requests
import json
import random

from reo.config.config import urls

def get_gif(name:str,limit:int=10):
    base_url = urls.gif_api_base
    params = {
        "q":name,
        "key":urls.gif_api_key,
        "limit":limit
    }
    response = requests.get(base_url,params=params)
    if response.status_code != 200:
        return None
    data = response.json()    
    results = data.get('results',[])
    selected_gif = random.choice(results) if results else None
    if not selected_gif:
        return None
    return selected_gif.get('media',[])[0].get('gif',{}).get('url',None)
