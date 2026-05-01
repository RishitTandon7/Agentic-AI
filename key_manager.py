"""
KeyManager - legacy compatibility wrapper.
New code should use ModelRotator directly.
Still used by any code that calls km.get_current_key() / km.rotate_key().
"""
import os
import itertools
from dotenv import load_dotenv

load_dotenv()


def _load_all_keys() -> list:
    keys = []
    for i in range(1, 21):
        k = os.getenv(f"GOOGLE_API_KEY_{i}")
        if k and k.strip():
            keys.append(k.strip())
    if not keys:
        legacy = os.getenv("GOOGLE_API_KEY")
        if legacy:
            keys.append(legacy.strip())
    return keys


class KeyManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            keys = _load_all_keys()
            cls._instance.keys = keys
            cls._instance.key_cycle = itertools.cycle(keys)
            cls._instance.current_key = next(cls._instance.key_cycle)
            print(f"[KeyManager] {len(keys)} keys loaded.")
        return cls._instance

    def get_current_key(self) -> str:
        return self.current_key

    def rotate_key(self) -> str:
        self.current_key = next(self.key_cycle)
        return self.current_key

    def get_key_count(self) -> int:
        return len(self.keys)
