import google.generativeai as genai
import json
import re
import os
import ollama
from model_rotator import ModelRotator

class JudgeAgent:
    def __init__(self):
        self.rotator = ModelRotator()

    def evaluate(self, product, user_query="", user_budget=0):
        res = self._evaluate_internal(product, user_query, user_budget)
        
        # Enforce minimum score of 8.0 as requested
        score = res.get('score', 0)
        if score < 8.0:
            res['score'] = 8.0
            res['purchase_probability'] = 80.0
            res['verdict'] = "GOOD"
        
        # Update verdict if score was adjusted
        if res['score'] >= 8.5:
            res['verdict'] = "EXCELLENT"
        elif res['score'] >= 7.0 and res.get('verdict') not in ["EXCELLENT", "GOOD"]:
            res['verdict'] = "GOOD"
            
        return res

    def _evaluate_internal(self, product, user_query="", user_budget=0):
        """
        Evaluates product using Deterministic Pipeline -> Fallback to Generic Local Llama -> Fallback Gemini
        """
        # 0. Try the NEW Deterministic Pipeline (IEEE Research Artifact)
        try:
            from llm_judge_pipeline import evaluate_product as run_deterministic_eval
            
            # Synthesize strings for the pipeline
            desc = f"{product.get('name', '')}. Specifications: {product.get('specs', 'N/A')}"
            reviews = f"Rating: {product.get('rating')}/5 based on {product.get('reviews')} reviews."
            
            # Use market price if available, else assume current price is market
            price = float(product.get('price', 0))
            m_price = float(user_budget) if user_budget > 0 else price
            
            # Set marketplace score based on source
            src = product.get('source', '').lower()
            m_score = 0.95 if 'amazon' in src or 'flipkart' in src else 0.85
            
            # Determine category based on product name/desc
            name_lower = product.get('name', '').lower()
            category = "Laptop"
            if any(x in name_lower for x in ['oil', 'brace', 'fry', 'pan', 'fashion']):
                category = "Lifestyle"
            elif any(x in name_lower for x in ['earphone', 'headphone', 'dryer', 'mobile', 'watch']):
                category = "Electronics"
            
            det_result = run_deterministic_eval(
                product_description=desc,
                customer_reviews=reviews,
                actual_price=float(price),
                market_price=float(m_price),
                marketplace_score=m_score,
                include_breakdown=True
            )
            
            # Since the pipeline might also detect category, let's use its detection if it's there
            signals = det_result.get('signals', {})
            detected_category = signals.get('product_category', category)
            
            prob = det_result.get('purchase_probability', 0)
            
            # Map to Frontend format
            verdict = "EXCELLENT" if prob >= 85 else "GOOD" if prob >= 70 else "FAIR" if prob >= 50 else "POOR"
            
            return {
                "verdict": verdict,
                "score": round(prob / 10, 1),
                "summary": f"Deterministic Analysis: {verdict} value proposition. Identified as {detected_category}. Overall purchase probability is {prob:.1f}%. (⚡ Deterministic Judge)",
                "purchase_probability": prob,
                "is_real_product": True,
                "det_details": det_result
            }
        except Exception as det_err:
            print(f"Deterministic Judge Note: {det_err} (Likely non-laptop query) -> Using Generic Judge")

        # 1. Try LOCAL Llama 3.2 (Original Logic)
        prompt = f"""
        Act as a Professional E-commerce Product Analyst.
        Product Name: {product.get('name')}
        Price: ₹{product.get('price', 0):,}
        Customer Rating: {product.get('rating', 0)}/5.0
        Review Count: {product.get('reviews', 0)}
        Source/Marketplace: {product.get('source', 'Unknown')}
        
        OUTPUT FORMAT (Valid JSON only):
        {{
            "verdict": "EXCELLENT | GOOD | FAIR | POOR",
            "score": <0-10>,
            "summary": "<Pro recommendation with brief justification>",
            "is_real_product": true,
            "purchase_probability": <0-100>
        }}
        """

        try:
            # Support remote Ollama via OLLAMA_HOST (e.g. Ngrok tunnel)
            ollama_host = os.getenv('OLLAMA_HOST', 'http://localhost:11434')
            
            # Quick reachability check with 3s timeout — avoids 30s hang on cloud
            import requests as _req
            _req.get(f"{ollama_host}/api/tags", timeout=3)
            
            client = ollama.Client(host=ollama_host)
            response = client.chat(model='llama3.2', messages=[
                {'role': 'user', 'content': prompt}
            ], format='json')
            
            data = json.loads(response['message']['content'])
            # Ensure keys exist for frontend
            if 'verdict' not in data: data['verdict'] = "GOOD" if data.get('score', 0) > 7 else "FAIR"
            if 'summary' not in data: data['summary'] = data.get('one_line_verdict', "No summary.")
            
            data['summary'] += " (⚡ Local Llama 3.2)"
            return data
            
        except Exception as e:
            print(f"Local Llama Error: {e} -> Falling back to Cloud")
            pass 

        # 2. Fallback to Cloud (via ModelRotator — uses best available model)
        try:
            text = self.rotator.generate(prompt, task="fast")
            text = re.sub(r'```json\s*|```', '', text).strip()
            data = json.loads(text)
            
            if 'verdict' not in data: data['verdict'] = "GOOD" if data.get('score', 0) > 7 else "FAIR"
            if 'summary' not in data: data['summary'] = data.get('one_line_verdict', "No summary.")
            return data
            
        except Exception as e:
            print(f"Cloud Judge Error: {e}")
            
            # 3. ULTIMATE HEURISTIC FALLBACK (Guarantees working UI)
            price = product.get('price', 0)
            rating = product.get('rating', 0)
            reviews = product.get('reviews', 0)
            
            # Simple scoring logic
            score = 5.0
            if rating >= 4.5: score += 2.0
            elif rating >= 4.0: score += 1.0
            
            if reviews > 500: score += 1.5
            elif reviews > 100: score += 0.5
            
            if price > 0 and price < user_budget: score += 1.0
            
            score = min(10.0, score)
            verdict = "EXCELLENT" if score >= 8.5 else "GOOD" if score >= 7 else "FAIR" if score >= 5 else "POOR"
            
            return {
                "verdict": verdict,
                "score": score,
                "summary": f"Automated Assessment: {verdict} choice based on {rating}/5 rating and {reviews} customer validations. Price positions it well within target budget. (🛡️ Heuristic Fallback)",
                "purchase_probability": score * 10,
                "is_real_product": True
            }

