"""
ModelRotator - 16-key x model round-robin rotation
Strategy: cycle keys first (spread RPM load), fallback models on quota hit.
Built for 1-hour burst capacity: ~1,300 calls/min sustained.
"""
import os
import itertools
import threading
import time
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

# ─────────────────────────────────────────────
# MODEL PRIORITY (quality-first for negotiation)
# ─────────────────────────────────────────────
# tier 1 = best quality (Gemini Flash)
# tier 2 = good quality (Gemma 4)
# tier 3 = decent fallback (Gemma 3 27B)
# tier 4 = last resort (Gemma 3 12B)

NEGOTIATION_MODELS = [
    "gemini-2.5-flash",       # tier 1 - best quality
    "gemini-2.5-flash-lite",  # tier 1 - fast + good
    "gemini-2.0-flash-lite",  # tier 1 - reliable
    "gemma-3-27b-it",         # tier 3 - solid fallback
]

FAST_MODELS = [
    "gemini-2.5-flash-lite",
    "gemini-2.0-flash-lite",
    "gemma-3-27b-it",
    "gemma-3-12b-it",
]

ALL_MODELS = list(dict.fromkeys(NEGOTIATION_MODELS + FAST_MODELS))


def _load_keys() -> list:
    """Load all GOOGLE_API_KEY_1 .. GOOGLE_API_KEY_20 from env."""
    keys = []
    for i in range(1, 21):
        k = os.getenv(f"GOOGLE_API_KEY_{i}")
        if k and k.strip():
            keys.append(k.strip())
    # Fallback to legacy GOOGLE_API_KEY if nothing numbered found
    if not keys:
        legacy = os.getenv("GOOGLE_API_KEY")
        if legacy:
            keys.append(legacy.strip())
    return keys


class ModelRotator:
    """
    Singleton rotator: cycles through 16 keys round-robin.
    On quota/rate error for a (key, model) pair → marks it exhausted,
    tries next key for same model, then falls back to next model tier.
    """
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                inst = super().__new__(cls)
                inst._init()
                cls._instance = inst
        return cls._instance

    def _init(self):
        self.keys = _load_keys()
        if not self.keys:
            raise ValueError("No GOOGLE_API_KEY_* found in environment!")

        self._key_cycle = itertools.cycle(self.keys)
        self._current_key = next(self._key_cycle)

        # Track exhausted (key, model) pairs
        self._exhausted: set = set()
        self._last_reset = time.time()

        print(f"[ModelRotator] Loaded {len(self.keys)} API keys. Ready.")

    # ─────────────────────────────
    # Primary generate method
    # ─────────────────────────────

    def generate(self, prompt: str, task: str = "negotiation",
                 generation_config: dict = None) -> str:
        """
        Generate text. Rotates keys first, then falls back to next model.
        task: 'negotiation' | 'fast' | 'any'
        """
        self._maybe_reset()

        models = NEGOTIATION_MODELS if task != "fast" else FAST_MODELS

        for model_id in models:
            # Try every key for this model before giving up on it
            for attempt in range(len(self.keys)):
                key = self._get_next_key()
                pair = (key[-8:], model_id)  # track by key suffix + model

                if pair in self._exhausted:
                    continue

                try:
                    genai.configure(api_key=key)
                    m = genai.GenerativeModel(model_id)
                    cfg = genai.types.GenerationConfig(**(generation_config or {})) if generation_config else None
                    response = m.generate_content(prompt, generation_config=cfg)

                    if response and response.text:
                        return response.text.strip()

                except Exception as e:
                    err = str(e).lower()
                    if any(x in err for x in ["quota", "429", "resource_exhausted", "rate_limit"]):
                        print(f"[Rotator] {model_id} | key ..{key[-6:]} | quota hit -> next key")
                        self._exhausted.add(pair)
                    elif any(x in err for x in ["not found", "invalid", "disabled", "permission", "not supported"]):
                        print(f"[Rotator] {model_id} | unavailable on key ..{key[-6:]} -> skipping")
                        self._exhausted.add(pair)
                    else:
                        print(f"[Rotator] {model_id} | error: {type(e).__name__}")
                    continue

        raise RuntimeError("[ModelRotator] All models and keys exhausted! Check quotas.")

    # ─────────────────────────────
    # Helper: get best available model object
    # ─────────────────────────────

    def get_best_model(self, task: str = "negotiation"):
        """Returns (model_id, key, genai.GenerativeModel) for best available pair."""
        self._maybe_reset()
        models = NEGOTIATION_MODELS if task != "fast" else FAST_MODELS

        for model_id in models:
            for _ in range(len(self.keys)):
                key = self._get_next_key()
                pair = (key[-8:], model_id)
                if pair in self._exhausted:
                    continue
                genai.configure(api_key=key)
                return model_id, key, genai.GenerativeModel(model_id)

        raise RuntimeError("[ModelRotator] No models available.")

    def mark_exhausted(self, model_id: str, key: str = None):
        if key:
            self._exhausted.add((key[-8:], model_id))
        else:
            # Mark for all keys
            for k in self.keys:
                self._exhausted.add((k[-8:], model_id))

    def get_status(self) -> dict:
        return {
            "total_keys": len(self.keys),
            "exhausted_pairs": len(self._exhausted),
            "exhausted_detail": list(self._exhausted),
            "models_in_rotation": NEGOTIATION_MODELS,
        }

    # ─────────────────────────────
    # Internals
    # ─────────────────────────────

    def _get_next_key(self) -> str:
        with self._lock:
            self._current_key = next(self._key_cycle)
            return self._current_key

    def _maybe_reset(self):
        """Clear exhausted set every 24h (daily quota resets)."""
        if time.time() - self._last_reset > 86400:
            print("[ModelRotator] 24h reset - clearing exhausted pairs")
            self._exhausted.clear()
            self._last_reset = time.time()
