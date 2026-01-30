import json
import os

CACHE_FILE = "model_cache.json"

def get_last_model_index():
    if not os.path.exists(CACHE_FILE):
        return 0
    try:
        with open(CACHE_FILE, 'r') as f:
            data = json.load(f)
            return data.get('last_index', 0)
    except:
        return 0

def save_last_model_index(index):
    try:
        with open(CACHE_FILE, 'w') as f:
            json.dump({'last_index': index}, f)
    except:
        pass
