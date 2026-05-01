import random
from typing import List, Dict
from model_rotator import ModelRotator


class SellerAgent:
    def __init__(self):
        self.rotator = ModelRotator()

    def select_product(self, products: List[Dict], round_num: int = 1):
        if not products:
            return None
        return products[0]

    def generate_pitch(self, product: Dict, round_num: int = 1,
                       model: str = None, use_template: bool = False) -> str:
        name = product.get('name', 'Product')
        price = product.get('price', 0)
        rating = product.get('rating', 'N/A')
        source = product.get('source', 'Unknown')

        # INSTANT MODE: Use template for Round 1 to start immediately
        if use_template:
            templates = [
                f"Take a look at this {name}. At ₹{price:,}, it's the premium choice with a {rating}★ rating.",
                f"I highly recommend this {name}. The quality is unmatched for ₹{price:,} — {rating} stars say it all.",
                f"For ₹{price:,}, you won't find a better option than this {name} (rated {rating}★).",
                f"Trust me, this {name} is exactly what you need. It's worth every rupee at ₹{price:,}.",
            ]
            return random.choice(templates)

        # Tone escalation by round
        tone_map = {
            1: "confident and enthusiastic",
            2: "persuasive and highlighting value",
            3: "empathetic but firm, addressing concerns",
            4: "compromising, willing to negotiate slightly",
            5: "final offer, urgent and convincing",
        }
        tone = tone_map.get(round_num, "professional and persuasive")

        prompt = (
            f"You are AURA, a sharp and persuasive AI sales agent.\n"
            f"Product: {name}\n"
            f"Price: ₹{price:,}\n"
            f"Platform: {source}\n"
            f"Rating: {rating}/5\n"
            f"Negotiation Round: {round_num}/5\n\n"
            f"Write ONE compelling sales pitch sentence in a {tone} tone.\n"
            f"Be specific about the product — mention the name, price, and rating naturally.\n"
            f"Sound human and conversational, not like a robot.\n"
            f"Do NOT use markdown, emojis, or bullet points.\n"
            f"Output only the pitch sentence, nothing else."
        )

        try:
            return self.rotator.generate(prompt, task="negotiation")
        except RuntimeError as e:
            print(f"⚠️  SellerAgent fallback to template: {e}")

        # Smart template fallback
        adjectives = ["exceptional", "fantastic", "premium", "top-rated", "highly-rated"]
        adj = random.choice(adjectives)
        if round_num == 1:
            return f"This {name} is a {adj} choice at ₹{price:,} with a {rating}★ rating — hard to beat."
        elif round_num <= 3:
            return f"Considering the {rating}★ reviews, this {name} at ₹{price:,} is genuinely excellent value."
        else:
            return f"Final pitch — this {name} at ₹{price:,} is the best I can offer. You won't regret it."
