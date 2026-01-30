import os
import google.generativeai as genai
from typing import List, Dict

class SellerAgent:
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if self.api_key:
            genai.configure(api_key=self.api_key)
        
        # ALL available models for quota rotation
        self.models_pool = [
            "gemini-2.5-flash",
            "gemini-2.5-flash-lite",
            "gemini-2.5-flash-tts",
            "gemini-3-flash",
            "gemini-robotics-er-1.5-preview",
            "gemini-2.5-flash-native-audio-dialog",
            "gemma-3-27b",
            "gemma-3-12b",
            "gemma-3-4b",
            "gemma-3-2b",
            "gemma-3-1b"
        ]

    def select_product(self, products: List[Dict], round_num: int = 1):
        # Products are already sorted by relevance/price from scraper
        if not products: return None
        return products[0]

    def generate_pitch(self, product: Dict, round_num: int = 1, model: str = None, use_template: bool = False) -> str:
        name = product.get('name', 'Product')
        price = product.get('price', 0)
        rating = product.get('rating', 'N/A')
        source = product.get('source', 'Unknown')
        
        # INSTANT MODE: Use template for Round 1 to start immediately
        if use_template:
            templates = [
                f"Take a look at this {name}. At ₹{price}, it's the premium choice.",
                f"I highly recommend this {name}. The quality is unmatched for ₹{price}.",
                f"For ₹{price}, you won't find a better option than this {name}.",
                f"Trust me, this {name} is exactly what you need. It's worth every rupee of ₹{price}."
            ]
            import random
            return random.choice(templates)
        
        base_pitch = f"This {name} is a top pick at ₹{price} on {source} with a {rating} star rating."

        # Adjust tone based on round
        tone = 'aggressive' if round_num <= 2 else ('compromising' if round_num <= 4 else 'final offer')
        
        prompt = f"""
        Act as a persuasive sales AI named 'Aura'.
        Product: {name}
        Price: ₹{price}
        Source: {source}
        Rating: {rating}/5
        Round: {round_num}
        
        Write a {tone} 1-sentence pitch for this product.
        """
        
        # If specific model requested, try that first
        import random
        from key_manager import KeyManager
        
        km = KeyManager()
        pool = self.models_pool

        # 1. Check if Warmer has a ready model (FAST PATH)
        from model_warmer import ModelWarmer
        warmer = ModelWarmer()
        v_model, v_key = warmer.get_verified_model()
        
        if v_model and v_key:
            try:
                genai.configure(api_key=v_key)
                m = genai.GenerativeModel(v_model)
                response = m.generate_content(prompt)
                if response.text: return response.text.strip()
            except:
                # If verified failed, fall back to rotation
                warmer.clear() # Mark invalid
                pass

        # 2. Key Rotation Fallback (Standard Path)
        max_retries = 2
        
        for i in range(max_retries):
            try:
                # Pick a random model each time
                model_name = random.choice(pool) if pool else "gemini-2.0-flash"
                if i == 0 and model: model_name = model # First try preferred
                
                genai.configure(api_key=km.get_current_key())
                m = genai.GenerativeModel(model_name)
                response = m.generate_content(prompt)
                if response.text:
                    return response.text.strip()
            except Exception:
                km.rotate_key()
                continue
        
        # Fallback to smart template if AI fails
        adjectives = ["exceptional", "fantastic", "premium", "reliable", "top-rated"]
        adj = random.choice(adjectives)
        
        if round_num == 1:
            return f"I honestly believe this {name} is the {adj} choice for you at ₹{price}."
        elif round_num <= 3:
            return f"Considering the quality, this {name} at ₹{price} is a steal."
        else:
            return f"This is my final offer for the {name}. You won't find better value."
