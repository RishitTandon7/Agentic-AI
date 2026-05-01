"""
ModelWarmer — pre-validates the best available model in the background
so the first negotiation round starts instantly (no cold-start delay).
Now delegates to ModelRotator for actual model selection.
"""
import threading
from model_rotator import ModelRotator


class ModelWarmer:
    _instance = None
    _ready = False
    _lock = threading.Lock()
    _is_checking = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def start_check_async(self):
        """Start verifying the best model in background."""
        if self._is_checking or self._ready:
            return
        t = threading.Thread(target=self._ping_best_model, daemon=True)
        t.start()

    def _ping_best_model(self):
        with self._lock:
            self._is_checking = True
        try:
            rotator = ModelRotator()
            model_id, model = rotator.get_best_model(task="negotiation")
            model.generate_content("Say OK.")
            self._ready = True
            print(f"✅ Warmer: Best model ready → {model_id}")
        except Exception as e:
            print(f"⚠️  Warmer: ping failed ({e}) — rotator will handle on demand")
        finally:
            self._is_checking = False

    def get_verified_model(self):
        """
        Legacy compatibility: return (None, None) — 
        ModelRotator handles selection internally now.
        """
        return None, None

    def clear(self):
        self._ready = False
