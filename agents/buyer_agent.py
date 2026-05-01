import os
from model_rotator import ModelRotator

class BuyerAgent:
    def __init__(self, budget):
        self.budget = budget
        self.rotator = ModelRotator()

    def pick_best_value(self, products, query_context=""):
        if not products: return None, False
        
        # KEYWORD EXTRACTION: Simple splitting by space, ignoring common words
        keywords = []
        if query_context:
            ignore = {'laptop', 'mobile', 'phone', 'best', 'buy', 'under', 'price', 'with', 'the', 'a', 'an', 'in', 'for'}
            keywords = [w.lower() for w in query_context.split() if w.lower() not in ignore and len(w) > 2]

        scored_products = []
        
        for p in products:
            price = p.get('price', 0)
            rating = p.get('rating', 0)
            name = p.get('name', '').lower()
            
            # 1. RELEVANCE SCORE (Features)
            # +15 points for every keyword match in the title/name
            relevance_score = 0
            for k in keywords:
                if k in name:
                    relevance_score += 15
            
            # 2. RATING SCORE (Quality)
            # Max 25 points for 5 stars
            rating_score = (rating or 3.0) * 5
            
            # 3. BUDGET SCORE (Value/Price)
            budget_score = 0
            if self.budget > 0:
                if price <= self.budget:
                    budget_score += 40 # Base Pass
                    
                    # Logarithmic-like utility: We prefer using closer to ~80-100% of budget 
                    # rather than 10% (junk) or 101% (fail)
                    ratio = price / self.budget
                    if ratio < 0.5: budget_score -= 10 # Too cheap? Suspicious/Low spec
                    elif 0.8 <= ratio <= 1.0: budget_score += 20 # Optimal use
                else:
                    budget_score -= 30 # Penalty for being over budget
            
            total_score = relevance_score + rating_score + budget_score
            
            scored_products.append({
                'product': p,
                'score': total_score
            })
        
        # Sort by total score descending
        scored_products.sort(key=lambda x: x['score'], reverse=True)
        
        # Get top pick
        best = scored_products[0]['product']
        is_affordable = best.get('price', 0) <= self.budget
        
        return best, is_affordable

    def respond(self, seller_product, my_pick, is_affordable, round_num, use_ai=True, query_context=""):
        """
        Real negotiation: Compare seller's product vs my current choice
        Returns: (response_message, should_switch_to_seller_product)
        """
        
        # Extract product details
        seller_price = seller_product.get('price', 0)
        seller_rating = seller_product.get('rating', 0)
        seller_name = seller_product.get('name', '').lower()
        
        my_price = my_pick.get('price', 0)
        my_rating = my_pick.get('rating', 0)
        my_name = my_pick.get('name', '').lower()
        
        # INTELLIGENT COMPARISON LOGIC
        # Calculate "switch score" - positive means seller's product is better
        
        switch_score = 0
        reasons_to_switch = []
        reasons_to_stay = []
        
        # 1. PRICE COMPARISON (vs budget)
        if self.budget > 0:
            seller_budget_fit = abs(seller_price - self.budget * 0.9)  # Prefer 90% of budget
            my_budget_fit = abs(my_price - self.budget * 0.9)
            
            if seller_budget_fit < my_budget_fit and seller_price <= self.budget:
                switch_score += 15
                reasons_to_switch.append(f"better budget utilization (₹{seller_price:,} vs ₹{my_price:,})")
            elif my_budget_fit < seller_budget_fit:
                switch_score -= 15
                reasons_to_stay.append(f"my choice is closer to budget target")
                
            if seller_price > self.budget:
                switch_score -= 25
                reasons_to_stay.append(f"seller's option exceeds budget by ₹{seller_price - self.budget:,}")
        
        # 2. RATING COMPARISON
        rating_diff = seller_rating - my_rating
        if rating_diff > 0.3:
            switch_score += int(rating_diff * 20)
            reasons_to_switch.append(f"significantly higher rating ({seller_rating}★ vs {my_rating}★)")
        elif rating_diff < -0.3:
            switch_score -= int(abs(rating_diff) * 20)
            reasons_to_stay.append(f"my choice has better reviews ({my_rating}★)")
        
        # 3. SPEC RELEVANCE (match user's query keywords)
        if query_context:
            keywords = [w.lower() for w in query_context.split() if len(w) > 3]
            seller_matches = sum(1 for k in keywords if k in seller_name)
            my_matches = sum(1 for k in keywords if k in my_name)
            
            if seller_matches > my_matches:
                switch_score += (seller_matches - my_matches) * 10
                reasons_to_switch.append(f"better matches user requirements ({seller_matches} vs {my_matches} keywords)")
            elif my_matches > seller_matches:
                switch_score -= (my_matches - seller_matches) * 10
                reasons_to_stay.append(f"my choice matches specs better")
        
        # 4. PRICE/RATING SWEET SPOT
        # Prefer products with high rating AND reasonable price
        seller_value = (seller_rating / seller_price) * 100000 if seller_price > 0 else 0
        my_value = (my_rating / my_price) * 100000 if my_price > 0 else 0
        
        if seller_value > my_value * 1.15:  # 15% better value
            switch_score += 10
            reasons_to_switch.append("superior value-for-money ratio")
        
        # DECISION: Switch if switch_score > threshold
        # STUBBORNNESS: Ensure at least 3 rounds of dialogue
        should_switch = switch_score > 30 and round_num >= 3 
        
        # GENERATE RESPONSE using AI
        if use_ai:
            try:
                if should_switch:
                    reasons_str = ', '.join(reasons_to_switch[:2]) or 'better overall value'
                    prompt = (
                        f"You are a savvy buyer named Alex in a product negotiation.\n"
                        f"Negotiation Round: {round_num}\n"
                        f"SELLER'S OFFER: {seller_product['name']} — ₹{seller_price:,}, rated {seller_rating}★\n"
                        f"YOUR CURRENT PICK: {my_pick['name']} — ₹{my_price:,}, rated {my_rating}★\n"
                        f"Your budget: ₹{self.budget:,}\n"
                        f"Why you're switching: {reasons_str}\n\n"
                        f"Write a natural, conversational 2-sentence response ACCEPTING the seller's product.\n"
                        f"Sound genuinely convinced. Mention the specific reason you're switching.\n"
                        f"Do NOT use bullet points, markdown, or emojis. Just plain sentences."
                    )
                else:
                    reasons_str = ', '.join(reasons_to_stay[:2]) or 'it better fits my requirements'
                    prompt = (
                        f"You are a savvy buyer named Alex in a product negotiation.\n"
                        f"Negotiation Round: {round_num}\n"
                        f"SELLER'S OFFER: {seller_product['name']} — ₹{seller_price:,}, rated {seller_rating}★\n"
                        f"YOUR CURRENT PICK: {my_pick['name']} — ₹{my_price:,}, rated {my_rating}★\n"
                        f"Your budget: ₹{self.budget:,}\n"
                        f"Why you're staying: {reasons_str}\n\n"
                        f"Write a natural, conversational 2-sentence response politely REJECTING the seller's offer.\n"
                        f"Be specific — mention the product names and actual numbers.\n"
                        f"Do NOT use bullet points, markdown, or emojis. Just plain sentences."
                    )

                text = self.rotator.generate(prompt, task="negotiation")
                return text, should_switch
            except Exception as e:
                print(f"⚠️  BuyerAgent AI failed: {e}")
        
        # FALLBACK TEMPLATE RESPONSES
        if should_switch:
            return (
                f"You know what, you're right. The {seller_product['name']} at ₹{seller_price:,} "
                f"looks like a better option - {reasons_to_switch[0] if reasons_to_switch else 'better overall specs'}. "
                f"Let's go with that.",
                True
            )
        else:
            return (
                f"I appreciate the offer, but I'm still leaning towards {my_pick['name']} because "
                f"{reasons_to_stay[0] if reasons_to_stay else 'it better fits my requirements'}. "
                f"Can you suggest something closer to my specs?",
                False
            )
