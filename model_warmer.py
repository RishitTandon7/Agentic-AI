import threading
import google.generativeai as genai
import random
from key_manager import KeyManager

class ModelWarmer:
    _instance = None
    _verified_model = None
    _verified_key = None
    _lock = threading.Lock()
    _is_checking = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ModelWarmer, cls).__new__(cls)
            cls._instance.models_pool = [
                "gemini-2.0-flash", "gemini-2.5-flash", 
                "gemini-1.5-flash", "gemini-1.5-pro",
                "gemma-2-9b-it" 
            ]
        return cls._instance

    def start_check_async(self):
        """Start finding a working model in background"""
        if self._is_checking: return
        t = threading.Thread(target=self._find_working_model)
        t.daemon = True
        t.start()

    def _find_working_model(self):
        with self._lock:
            self._is_checking = True
            
        km = KeyManager()
        print("🔥 Warmer: Checking for valid model/key...")
        
        # Try finding a working combination
        # Limit total attempts to avoid infinite resource usage
        attempts = 0
        while attempts < 4:
            attempts += 1
            model = random.choice(self.models_pool)
            key = km.get_current_key()
            
            try:
                genai.configure(api_key=key)
                m = genai.GenerativeModel(model)
                # Quick ping
                m.generate_content("Hi")
                
                # Success!
                self._verified_model = model
                self._verified_key = key
                print(f"✅ Warmer: Found working model: {model} with key ...{key[-4:]}")
                self._is_checking = False
                return
            except Exception as e:
                # Rotate and try again
                km.rotate_key()
        
        print("⚠️ Warmer: Could not verified model in background.")
        self._is_checking = False

    def get_verified_model(self):
        """Return the pre-verified model if available, else None"""
        return self._verified_model, self._verified_key

    def clear(self):
        self._verified_model = None
        self._verified_key = None
