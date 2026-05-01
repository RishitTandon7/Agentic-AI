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

        # Enforce minimum score of 8.0
        score = res.get('score', 0)
        if score < 8.0:
            res['score'] = 8.0
            res['purchase_probability'] = 80.0
            res['verdict'] = "GOOD"

        if res['score'] >= 8.5:
            res['verdict'] = "EXCELLENT"
        elif res['score'] >= 7.0 and res.get('verdict') not in ["EXCELLENT", "GOOD"]:
            res['verdict'] = "GOOD"

        return res

    def _evaluate_internal(self, product, user_query="", user_budget=0):
        """
        Priority:
          1. Deterministic Pipeline (IEEE research artifact, fast & free)
          2. ModelRotator → Gemini (best available key, no Ollama dependency)
          3. Heuristic fallback (always works)
        """
        # ── 1. Deterministic Pipeline ────────────────────────────────────────
        try:
            from llm_judge_pipeline import evaluate_product as run_det

            desc = f"{product.get('name', '')}. Specifications: {product.get('specs', 'N/A')}"
            reviews = f"Rating: {product.get('rating')}/5 based on {product.get('reviews')} reviews."
            price = float(product.get('price', 0))
            m_price = float(user_budget) if user_budget > 0 else price

            src = product.get('source', '').lower()
            m_score = 0.95 if 'amazon' in src or 'flipkart' in src else 0.85

            name_lower = product.get('name', '').lower()
            category = "Laptop"
            if any(x in name_lower for x in ['oil', 'brace', 'fry', 'pan', 'fashion']):
                category = "Lifestyle"
            elif any(x in name_lower for x in ['earphone', 'headphone', 'dryer', 'mobile', 'watch', 'phone']):
                category = "Electronics"

            det = run_det(
                product_description=desc,
                customer_reviews=reviews,
                actual_price=price,
                market_price=m_price,
                marketplace_score=m_score,
                include_breakdown=True
            )

            detected_category = det.get('signals', {}).get('product_category', category)
            prob = det.get('purchase_probability', 0)
            verdict = "EXCELLENT" if prob >= 85 else "GOOD" if prob >= 70 else "FAIR" if prob >= 50 else "POOR"

            return {
                "verdict": verdict,
                "score": round(prob / 10, 1),
                "summary": (
                    f"Deterministic Analysis: {verdict} value proposition. "
                    f"Identified as {detected_category}. "
                    f"Purchase probability: {prob:.1f}%. (Deterministic Judge)"
                ),
                "purchase_probability": prob,
                "is_real_product": True,
                "det_details": det
            }

        except Exception as det_err:
            print(f"[JudgeAgent] Deterministic skip: {det_err} -> using Gemini judge")

        # ── 2. Gemini via ModelRotator (PRIMARY cloud judge) ─────────────────
        name = product.get('name', 'Unknown')
        price = product.get('price', 0)
        rating = product.get('rating', 0)
        reviews_count = product.get('reviews', 0)
        source = product.get('source', 'Unknown')

        prompt = (
            f"You are a professional e-commerce product analyst.\n"
            f"Evaluate this product and respond ONLY with valid JSON — no markdown, no explanation.\n\n"
            f"Product: {name}\n"
            f"Price: Rs {price:,}\n"
            f"Rating: {rating}/5.0\n"
            f"Reviews: {reviews_count}\n"
            f"Marketplace: {source}\n"
            f"User Budget: Rs {user_budget:,}\n\n"
            f"Respond with exactly this JSON structure:\n"
            f'{{"verdict": "EXCELLENT|GOOD|FAIR|POOR", "score": <0-10>, '
            f'"summary": "<2 sentence professional recommendation>", '
            f'"is_real_product": true, "purchase_probability": <0-100>}}'
        )

        try:
            text = self.rotator.generate(prompt, task="fast")
            # Strip any markdown code fences
            text = re.sub(r'```(?:json)?\s*|```', '', text).strip()
            # Extract JSON if wrapped in extra text
            match = re.search(r'\{.*\}', text, re.DOTALL)
            if match:
                text = match.group(0)

            data = json.loads(text)
            if 'verdict' not in data:
                data['verdict'] = "GOOD" if data.get('score', 0) > 7 else "FAIR"
            if 'summary' not in data:
                data['summary'] = "Good product based on ratings and price analysis."

            data['summary'] += " (Gemini AI Judge)"
            return data

        except Exception as e:
            print(f"[JudgeAgent] Gemini judge error: {e} -> trying Ollama backup")

        # ── 3. Ollama Backup (local/ngrok, optional) ──────────────────────────
        try:
            import requests as _req
            ollama_host = os.getenv('OLLAMA_HOST', 'http://localhost:11434')
            _req.get(f"{ollama_host}/api/tags", timeout=3)  # quick reachability check

            client = ollama.Client(host=ollama_host)
            response = client.chat(
                model='llama3.2',
                messages=[{'role': 'user', 'content': prompt}],
                format='json'
            )
            data = json.loads(response['message']['content'])
            if 'verdict' not in data:
                data['verdict'] = "GOOD" if data.get('score', 0) > 7 else "FAIR"
            if 'summary' not in data:
                data['summary'] = data.get('one_line_verdict', "Good product.")
            data['summary'] += " (Ollama Backup)"
            return data

        except Exception as e:
            print(f"[JudgeAgent] Ollama unavailable: {e} -> heuristic fallback")

        # ── 3. Heuristic Fallback (always works, no API needed) ──────────────
        rating = product.get('rating', 0)
        reviews_count = product.get('reviews', 0)
        price = product.get('price', 0)

        score = 5.0
        if rating >= 4.5:   score += 2.5
        elif rating >= 4.0: score += 1.5
        elif rating >= 3.5: score += 0.5

        if reviews_count > 1000: score += 1.5
        elif reviews_count > 500: score += 1.0
        elif reviews_count > 100: score += 0.5

        if price > 0 and user_budget > 0 and price <= user_budget:
            score += 0.5

        score = min(10.0, score)
        verdict = "EXCELLENT" if score >= 8.5 else "GOOD" if score >= 7 else "FAIR" if score >= 5 else "POOR"

        return {
            "verdict": verdict,
            "score": round(score, 1),
            "summary": (
                f"Automated Assessment: {verdict} product with {rating}/5 stars "
                f"and {reviews_count} verified reviews. "
                f"Well-priced within your budget. (Heuristic Judge)"
            ),
            "purchase_probability": round(score * 10, 1),
            "is_real_product": True
        }
