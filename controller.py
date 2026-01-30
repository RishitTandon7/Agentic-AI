from scraper.providers import get_scraper
from storage.csv_store import CSVStore
from agents.seller_agent import SellerAgent
from agents.buyer_agent import BuyerAgent
from model_persistence import get_last_model_index, save_last_model_index
import time

class NegotiationController:
    def __init__(self, query, budget, sources, max_results=5):
        self.query = query
        self.budget = budget
        self.sources = sources
        self.max_results = max_results  # User-configurable limit
        self.scraper = get_scraper() # Keeping original import, assuming DirectSearchScraper is not meant to be imported here
        self.buyer = BuyerAgent(budget)
        self.seller = SellerAgent()
        self.store = CSVStore() # Keeping original import, assuming ProductStore is not meant to be imported here
    
    def search_products(self):
        """Phase 1: Only scrape products and return them"""
        products = []
        try:
            # 1. Primary Search (Direct Amazon/Flipkart)
            print(f"✅ Using DirectSearchScraper (Amazon/Flipkart direct)")
            products = []
            
            # AUTO-DETECT CLOTHING QUERIES
            clothing_keywords = ['jacket', 'dress', 'shirt', 'pant', 'jeans', 'saree', 'kurta', 
                               'top', 'skirt', 'sweater', 'coat', 'hoodie', 'tshirt', 't-shirt',
                               'women', 'men', 'kids', 'clothing', 'fashion', 'wear']
            
            is_clothing = any(kw in self.query.lower() for kw in clothing_keywords)
            
            # Check if user selected "web/global" source
            if 'web' in self.sources:
                # User explicitly chose GLOBAL - use Google Custom Search API
                print(f"🌍 Global Search: Using Google Search API...")
                print(f"   (Query type: {'CLOTHING' if is_clothing else 'TECH'})")
                
                try:
                    # Load API keys
                    from scraper.providers import ProgrammableSearchEngineScraper
                    import os
                    from dotenv import load_dotenv
                    load_dotenv(override=True)
                    
                    api_key = os.getenv("GOOGLE_API_KEY")
                    cx = os.getenv("GOOGLE_CX") or os.getenv("SEARCH_ENGINE_ID")
                    
                    if api_key and cx:
                        print(f"   ✅ Using Google Search API (No CAPTCHA!)")
                        api_scraper = ProgrammableSearchEngineScraper(api_key, cx)
                        # Use 'web' mode for global search
                        global_results = api_scraper.search(self.query, self.budget, ['web'])
                        products.extend(global_results)
                        print(f"   ✅ Google Search API: {len(global_results)} products")
                    else:
                        print(f"   ❌ Google API keys not found. Falling back to Amazon/Flipkart...")
                        amazon_results = self.scraper.search_amazon(self.query, count=self.max_results)
                        products.extend(amazon_results)
                        flipkart_results = self.scraper.search_flipkart(self.query, count=self.max_results)
                        products.extend(flipkart_results)
                        
                except Exception as e:
                    print(f"   ❌ Google Search API failed: {e}")
                    import traceback
                    traceback.print_exc()
                    
                    # FALLBACK: Use Amazon/Flipkart
                    print(f"   ⚠️ Falling back to Amazon + Flipkart...")
                    try:
                        amazon_results = self.scraper.search_amazon(self.query, count=self.max_results)
                        products.extend(amazon_results)
                        flipkart_results = self.scraper.search_flipkart(self.query, count=self.max_results)
                        products.extend(flipkart_results)
                        print(f"   ✅ Fallback successful: {len(products)} products")
                    except Exception as fallback_error:
                        print(f"   ❌ Fallback also failed: {fallback_error}")
            
            elif is_clothing and not self.sources:
                # Clothing query with NO specific source selected → Use clothing platforms
                print(f"👗 Detected clothing query. Using clothing platforms...")
                clothing_sources = ['myntra', 'ajio', 'shein']
                for source in clothing_sources:
                    if source == 'myntra':
                        results = self.scraper.search_myntra(self.query, count=self.max_results)
                        products.extend(results)
                    elif source == 'ajio':
                        results = self.scraper.search_ajio(self.query, count=self.max_results)
                        products.extend(results)
                    elif source == 'shein':
                        results = self.scraper.search_shein(self.query, count=self.max_results)
                        products.extend(results)
                
                # FALLBACK: If clothing sites returned few/no products, also search Amazon/Flipkart
                if len(products) < 3:
                    print(f"   ⚠️ Only {len(products)} from clothing sites. Adding Amazon/Flipkart...")
                    results = self.scraper.search_amazon(self.query, count=self.max_results)
                    products.extend(results)
                    results = self.scraper.search_flipkart(self.query, count=self.max_results)
                    products.extend(results)
            else:
                # TECH/ELECTRONICS QUERY
                print(f"DEBUG: Sources requested: {self.sources}")
                
                # Check if 'web'/'global' is requested
                if 'web' in self.sources:
                    # ONLY use Google Shopping (don't use Amazon/Flipkart)
                    print(f"🌍 Global Search: Using Google Shopping scraper...")
                    try:
                        global_results = self.scraper.search_google_shopping(self.query, self.max_results)
                        products.extend(global_results)
                        print(f"   ✅ Google Shopping: {len(global_results)} products from mixed sources")
                    except Exception as e:
                        print(f"   ❌ Google Shopping failed: {e}")
                        import traceback
                        traceback.print_exc()
                        
                        # FALLBACK: If Google Shopping fails, use Amazon/Flipkart
                        print(f"   ⚠️ Falling back to Amazon + Flipkart...")
                        try:
                            amazon_results = self.scraper.search_amazon(self.query, count=self.max_results)
                            products.extend(amazon_results)
                            flipkart_results = self.scraper.search_flipkart(self.query, count=self.max_results)
                            products.extend(flipkart_results)
                            print(f"   ✅ Fallback successful: {len(products)} products from Amazon+Flipkart")
                        except Exception as fallback_error:
                            print(f"   ❌ Fallback also failed: {fallback_error}")
                else:
                    # Normal source selection (Amazon/Flipkart)
                    if not self.sources or 'amazon' in self.sources:
                        print(f"📦 Searching Amazon...")
                        amazon_results = self.scraper.search_amazon(self.query, count=self.max_results)
                        products.extend(amazon_results)
                        print(f"   ✅ Amazon: {len(amazon_results)} products")
                        
                    if not self.sources or 'flipkart' in self.sources:
                        print(f"📦 Searching Flipkart...")
                        flipkart_results = self.scraper.search_flipkart(self.query, count=self.max_results)
                        products.extend(flipkart_results)
                        print(f"   ✅ Flipkart: {len(flipkart_results)} products")
                    
                    print(f"DEBUG: Total before dedup: {len(products)} products")
                    
                    # Fallback to Google Shopping if no results
                    if not products:
                        print(f"⚠️ No results from selected sources. Trying Google Shopping...")
                        try:
                            global_results = self.scraper.search_google_shopping(self.query, self.max_results)
                            products.extend(global_results)
                        except Exception as e:
                            print(f"   ⚠️ Google Shopping fallback failed: {e}")
            
            # Deduplicate by URL
            seen = set()
            unique = []
            source_counts = {}
            
            for p in products:
                if p['url'] not in seen:
                    seen.add(p['url'])
                    unique.append(p)
                    # Track source distribution
                    source = p.get('source', 'unknown')
                    source_counts[source] = source_counts.get(source, 0) + 1
            
            # Limit to user's requested amount (default 5)
            products = unique[:self.max_results]
            
            # Show source breakdown
            if products:
                print(f"\n📊 Source Breakdown (after dedup):")
                for source, count in source_counts.items():
                    print(f"   {source.upper()}: {count} products")
                print(f"   TOTAL UNIQUE: {len(unique)} products")
                print(f"   RETURNING: {len(products)} products (max_results={self.max_results})\n")
            
            # JUDGE EVALUATION MOVED TO AFTER NEGOTIATION
            # (User wants to see search results first, then get judge verdict on final choice only)
            # The judge.evaluate() call happens at line ~196 after negotiation
            
            if products:
                self.store.save_products(products, self.query)
                print(f"✅ Found {len(products)} real products")
            else:
                print(f"❌ NO PRODUCTS FOUND - scraping returned 0 results")
                # DO NOT generate fake data - return empty list
                
        except Exception as e:
            print(f"❌ Scraping error: {e}")
            import traceback
            traceback.print_exc()
            
        return products
    
    def _generate_fallback_products(self, query, budget):
        """Generate realistic fallback products when scraping fails"""
        import random
        
        products = []
        base_price = budget * 0.6 if budget > 0 else 50000
        
        brands = ['Dell', 'HP', 'Lenovo', 'ASUS', 'Acer', 'MSI', 'Samsung', 'Apple']
        sources = ['amazon', 'flipkart', 'croma', 'reliance']
        
        for i in range(12):
            brand = random.choice(brands)
            source = random.choice(sources)
            price_variation = random.uniform(0.7, 1.4)
            price = int(base_price * price_variation)
            rating = round(random.uniform(3.8, 4.8), 1)
            reviews = random.randint(50, 1000)
            
            # Create realistic product name
            query_words = query.split()[:2]  # Take first 2 words
            product_name = f"{brand} {' '.join(query_words).title()} - Model {random.choice(['X1', 'Pro', 'Elite', 'Plus', 'Ultra'])}"
            
            products.append({
                'name': product_name,
                'price': price,
                'rating': rating,
                'reviews': reviews,
                'url': f'https://www.{source}.in/product-{i+1}',
                'source': source
            })
        
        products.sort(key=lambda x: x['price'])
        print(f"✅ Generated {len(products)} fallback products")
        return products

    def run_negotiation_streaming(self, products):
        """STREAMING VERSION: Yields each round as it completes"""
        if not products:
            yield {"type": "error", "message": "No products to negotiate"}
            return
        
        # Initialize
        buyer_pick, is_affordable = self.buyer.pick_best_value(products, self.query)
        
        yield {
            "type": "init",
            "buyer_choice": buyer_pick.get('name', 'Unknown'),
            "total_rounds": 5
        }
        
        conversation = []
        final_agreement_product = None
        
        models = [
            "gemini-2.5-flash", "gemini-2.5-flash-lite", "gemini-2.5-flash-tts",
            "gemini-3-flash", "gemini-2.0-flash", "gemini-1.5-flash"
        ]
        
        current_index = get_last_model_index()
        
        for round_num in range(1, 6):
            # Seller picks strategically
            if round_num == 1: 
                seller_pick = products[-1]
            elif round_num == 2:
                seller_pick = products[len(products)//2]
            elif round_num == 3:
                seller_pick = products[0]
            elif round_num == 4:
                seller_pick = products[len(products)//3] if len(products) > 3 else products[1]
            else:
                seller_pick = buyer_pick
            
            model_name = models[current_index % len(models)]
            current_index += 1
            
            # Seller pitch
            pitch = self.seller.generate_pitch(seller_pick, round_num, model=model_name)
            conversation.append({"role": "seller", "message": pitch, "round": round_num})
            
            # Send seller message immediately
            yield {
                "type": "message",
                "role": "seller",
                "message": pitch,
                "round": round_num,
                "product": seller_pick.get('name', 'Unknown')[:50]
            }
            
            # Buyer response
            response_text, should_switch = self.buyer.respond(
                seller_pick, buyer_pick, is_affordable, round_num,
                use_ai=True, query_context=self.query
            )
            conversation.append({"role": "buyer", "message": response_text, "round": round_num})
            
            # Send buyer message immediately
            yield {
                "type": "message",
                "role": "buyer",
                "message": response_text,
                "round": round_num,
                "switched": should_switch
            }
            
            # Check if switched
            if should_switch:
                print(f"  🔄 Round {round_num}: Buyer convinced! Switching to {seller_pick.get('name', 'Unknown')[:30]}")
                final_agreement_product = seller_pick
                
                yield {
                    "type": "switch",
                    "round": round_num,
                    "new_product": seller_pick.get('name', 'Unknown')
                }
                break
            else:
                print(f"  ⚔️ Round {round_num}: Buyer stands firm on {buyer_pick.get('name', 'Unknown')[:30]}")
        
        save_last_model_index(current_index)
        
        # Final decision
        if final_agreement_product is None:
            final_agreement_product = buyer_pick
        
        # Judge evaluation
        yield {"type": "status", "message": "Evaluating final choice..."}
        
        from agents.judge_agent import JudgeAgent
        judge = JudgeAgent()
        analysis = judge.evaluate(final_agreement_product, self.query, self.budget)
        final_agreement_product['judge_analysis'] = analysis
        
        # Send final result
        yield {
            "type": "complete",
            "final_choice": final_agreement_product,
            "conversation": conversation,
            "judge_analysis": analysis
        }

    def run_negotiation(self, products):
        """Phase 2: Negotiate based on already found products"""
        if not products: return None

        # Buyer Pick (Balanced AI Choice: Price + Specs + Keywords)
        # We pass the user's query to find matches for specific features (e.g. "RTX 3050")
        buyer_pick, is_affordable = self.buyer.pick_best_value(products, self.query)
        
        # Mark it in the list so frontend knows which one to highlight
        for p in products:
            if p['url'] == buyer_pick['url']:
                p['is_best_value'] = True
            else:
                p['is_best_value'] = False

        seller_pick_initial = products[-1] # Most expensive
        
        result = {
            "products": products,
            "premium_choice": seller_pick_initial,
            "negotiation": {"conversation": []},
            "final_choice": None
        }

        # Multi-Round Negotiation
        conversation = []
        final_agreement_product = buyer_pick
        
        models = [
            "gemini-2.5-flash-lite", "gemini-2.5-flash", 
            "gemini-1.5-flash", "gemini-2.0-flash"
        ]
        
        current_index = get_last_model_index()
        
        for round_num in range(1, 6): # 5 rounds for thorough negotiation
            # Seller picks strategically based on round
            if round_num == 1: 
                seller_pick = products[-1]  # Round 1: Most expensive/premium
            elif round_num == 2: 
                seller_pick = products[len(products)//2]  # Round 2: Mid-range
            elif round_num == 3:
                seller_pick = products[0]  # Round 3: Cheapest option
            elif round_num == 4:
                seller_pick = products[len(products)//3] if len(products) > 3 else products[1]  # Round 4: Upper-mid tier
            else: 
                seller_pick = buyer_pick  # Round 5: Finally align with buyer
            
            model_name = models[current_index % len(models)]
            current_index += 1
            
            # Seller Pitch: Real AI with product comparison
            pitch = self.seller.generate_pitch(seller_pick, round_num, model=model_name)
            conversation.append({"role": "seller", "message": pitch, "round": round_num})
            
            # CRITICAL: Buyer evaluates seller's product vs current choice
            # Returns: (response_text, should_switch_to_seller_product)
            response_text, should_switch = self.buyer.respond(
                seller_pick, 
                buyer_pick, 
                is_affordable, 
                round_num, 
                use_ai=True,
                query_context=self.query  # Pass user's search query for spec matching
            )
            conversation.append({"role": "buyer", "message": response_text, "round": round_num})
            
            # DYNAMIC OUTCOME: If seller convinces buyer, switch to seller's product
            if should_switch:
                print(f"  🔄 Round {round_num}: Buyer convinced! Switching from {buyer_pick.get('name', 'Unknown')[:30]} to {seller_pick.get('name', 'Unknown')[:30]}")
                final_agreement_product = seller_pick
                break
            else:
                print(f"  ⚔️ Round {round_num}: Buyer stands firm on {buyer_pick.get('name', 'Unknown')[:30]}")
        
        save_last_model_index(current_index)
        
        # Final decision: Use negotiation outcome (not forced buyer_pick)
        # If no agreement was reached, default to buyer's original choice
        if final_agreement_product is None:
            final_agreement_product = buyer_pick
            print(f"  ✅ No agreement - defaulting to buyer's original choice: {buyer_pick.get('name', 'Unknown')[:40]}")

        result["negotiation"]["conversation"] = conversation
        result["final_choice"] = final_agreement_product
        if final_agreement_product:
            result["final_choice"]["final_price"] = final_agreement_product.get("price", 0)
        
        # JUDGE PHASE
        if final_agreement_product:
            try:
                from agents.judge_agent import JudgeAgent
                judge = JudgeAgent()
                analysis = judge.evaluate(final_agreement_product, self.query, self.budget)
                result["final_choice"]["judge_analysis"] = analysis
            except Exception as e:
                print(f"Judging failed: {e}")
                # Don't crash if judge fails
                if "final_choice" in result and result["final_choice"]:
                    result["final_choice"]["judge_analysis"] = None
        
        # Prepare for NEXT session
        try:
            from model_warmer import ModelWarmer
            warmer = ModelWarmer()
            warmer.clear() # Clear old one
            warmer.start_check_async() # Find new one
        except: pass
        
        return result


    def run_api(self):
        """Legacy wrapper"""
        products = self.search_products()
        return self.run_negotiation(products)

    def run(self):
        # Keep CLI version working wrapper around run_api? 
        # Or just leave it for now. Let's update it to use run_api if we wanted DRY, 
        # but for safety let's just leave the CLI method alone or comment it out if not used.
        # Implmenting a simple CLI wrapper for backward compatibility
        res = self.run_api()
        print(f"Found {len(res['products'])} products.")
        if res['final_choice']:
             print("Negotiation Complete.")
             for msg in res['negotiation']['conversation']:
                 print(msg)
             print(f"Final Outcome: {res['final_choice']['name']}")

    def log(self, product, action, message, round_num):
        entry = {
            'timestamp': time.time(),
            'product_id': product.get('url'),
            'buyer_offer': 0, 
            'seller_response': message if action == "pitch" else "",
            'status': action,
            'round': round_num
        }
        self.store.log_negotiation(entry)
