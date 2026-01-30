import os
import google.generativeai as genai
from typing import List

class ModelChecker:
    """Check which Gemini models are available in parallel"""
    
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if self.api_key:
            genai.configure(api_key=self.api_key)
    
    def check_models_parallel(self, models: List[str]) -> List[str]:
        """Test all models with simple prompt, return working ones"""
        working_models = []
        
        test_prompt = "Say 'OK' in one word."
        
        for model_name in models:
            try:
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(test_prompt)
                if response.text:
                    working_models.append(model_name)
                    print(f"✓ {model_name} available")
            except Exception as e:
                print(f"✗ {model_name} quota exceeded or unavailable")
                continue
        
        return working_models if working_models else ["gemini-2.5-flash"]  # Fallback
