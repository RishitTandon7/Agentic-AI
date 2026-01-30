import os
import itertools
from dotenv import load_dotenv

load_dotenv()

class KeyManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(KeyManager, cls).__new__(cls)
            # Load all keys
            keys = []
            if os.getenv("GOOGLE_API_KEY"): keys.append(os.getenv("GOOGLE_API_KEY"))
            if os.getenv("GOOGLE_API_KEY_2"): keys.append(os.getenv("GOOGLE_API_KEY_2"))
            
            # Add the one provided by user just in case it wasn't in env yet or if we want to hardcode fallback
            hardcoded_Key = "AIzaSyBbVaTnA00KD-qYGnTwlrv3NBnfO8myD1I" 
            if hardcoded_Key not in keys: keys.append(hardcoded_Key)
            
            cls._instance.keys = keys
            cls._instance.key_cycle = itertools.cycle(keys)
            cls._instance.current_key = next(cls._instance.key_cycle)
            
        return cls._instance

    def get_current_key(self):
        return self.current_key
    
    def rotate_key(self):
        """Switch to next API key"""
        self.current_key = next(self.key_cycle)
        # print(f"🔑 Rotated API Key to: ...{self.current_key[-6:]}") # Silence log to reduce noise
        return self.current_key
    
    def get_key_count(self):
        return len(self.keys)
