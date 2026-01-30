import os
import random
import re
import requests
import time
from typing import List, Dict, Any
from scraper.playwright_extractor import PlaywrightPriceExtractor

class ScraperProvider:
    def search(self, query: str, budget: float, sources: List[str]) -> List[Dict[str, Any]]:
        raise NotImplementedError

class SimulationScraper(ScraperProvider):
    def search(self, query: str, budget: float, sources: List[str]) -> List[Dict[str, Any]]:
        print(f"Simulating results for {query}...")
        results = []
        for i in range(5):
             price = budget * (1 - random.uniform(0.05, 0.2))
             results.append({
                 'name': f"Simulated {query} {i+1}",
                 'price': int(price),
                 'rating': round(random.uniform(3.5, 5.0), 1),
                 'reviews': random.randint(50, 5000),
                 'source': random.choice(sources) if sources else 'amazon',
                 'url': f"http://mock-url-{i}.com",
                 'timestamp': '2024-01-01'
             })
        return results

class ProgrammableSearchEngineScraper(ScraperProvider):
    def __init__(self, api_key: str, cx: str):
        # Load all available API keys for rotation
        self.api_keys = [api_key]  # First key from main env var
        
        # Load additional keys (GOOGLE_API_KEY_2, GOOGLE_API_KEY_3, etc.)
        i = 2
        while True:
            extra_key = os.getenv(f"GOOGLE_API_KEY_{i}")
            if extra_key:
                self.api_keys.append(extra_key)
                i += 1
            else:
                break
        
        print(f"DEBUG: Loaded {len(self.api_keys)} Google API key(s) for rotation")
        self.cx = cx
        self.url = "https://www.googleapis.com/customsearch/v1"
        self.current_key_index = 0
        
        # Playwright price extractor for EXACT prices
        self.price_extractor = PlaywrightPriceExtractor()
        self.use_selenium_prices = True  # Using Playwright for exact prices
        self.selenium_failures = 0
        self.max_selenium_failures = 5  # More tolerance for Playwright

    def search(self, query: str, budget: float, sources: List[str]) -> List[Dict[str, Any]]:
        start_time = time.time()
        
        # Write to log file since terminal prints don't show
        with open('scraper_log.txt', 'w', encoding='utf-8') as f:
            f.write(f"SEARCH STARTED: {query}\n")
            f.write(f"Budget: {budget}\n")
            f.write(f"Sources: {sources}\n")
            f.write(f"use_selenium_prices: {self.use_selenium_prices}\n")
        
        print(f"Scraping using Programmable Search Engine for '{query}'...")
        
        # Dynamic fetching based on source count
        query_batches = []
        base_query = query
        
        if not sources or 'web' in sources:
             # Trusted Official Sites Only (Requested by User)
             trusted_domains = [
                 "lenovo.com", "asus.com", "apple.com", "samsung.com", "mi.com", 
                 "reliancedigital.in", "croma.com", "dell.com", "hp.com"
             ]
             site_filter = " OR ".join([f"site:{d}" for d in trusted_domains])
             
             # Search specifically on these trusted domains
             query_batches.append({'q': f"{base_query} ({site_filter})", 'pages': 3})
             target_count = 5
        else:
             n = len(sources)
             pages = 2 if n == 1 else (3 if n == 2 else 4)
             target_count = 5 if n == 1 else (10 if n == 2 else 15)
             site_filters = " OR ".join([f"site:{s}.com" for s in sources] + [f"site:{s}.in" for s in sources])
             query_batches.append({'q': f"{base_query} ({site_filters})", 'pages': pages})

        # TIMING: API Calls
        api_start = time.time()
        items = []
        for batch in query_batches:
            search_query = batch['q']
            for page in range(batch['pages']):
                start_index = (page * 10) + 1
                
                # Try with key rotation on quota errors
                success = False
                for attempt in range(len(self.api_keys)):
                    current_key = self.api_keys[self.current_key_index]
                    params = {
                        'key': current_key,
                        'cx': self.cx,
                        'q': search_query,
                        'num': 10,
                        'start': start_index,
                        'gl': 'in',
                        'cr': 'countryIN'
                    }
                    
                    try:
                        response = requests.get(self.url, params=params)
                        response.raise_for_status()
                        data = response.json()
                        page_items = data.get('items', [])
                        if not page_items: break
                        items.extend(page_items)
                        success = True
                        break  # Success, exit retry loop
                    except requests.exceptions.HTTPError as e:
                        if e.response.status_code == 429:  # Quota exceeded
                            print(f"API Key #{self.current_key_index + 1} quota exceeded. Rotating...")
                            self.current_key_index = (self.current_key_index + 1) % len(self.api_keys)
                            if attempt == len(self.api_keys) - 1:
                                print("All API keys exhausted. Stopping search.")
                                break
                            continue  # Try next key
                        else:
                            print(f"CSE API Error: {e}")
                            break
                    except Exception as e:
                        print(f"CSE API Error: {e}")
                        break
                
                if not success:
                    break  # Stop pagination if all keys failed

        api_time = time.time() - api_start
        print(f"⏱️ API Calls took: {api_time:.2f}s ({len(items)} items)")
        
        # TIMING: Filtering
        filter_start = time.time()
        
        ignore_words = {'for', 'the', 'with', 'and', 'buy', 'price', 'online', 'in', 'at', 'under', 'graphics', 'card', 'edition', 'series'}
        query_keywords = [w for w in query.lower().split() if w not in ignore_words and len(w) > 1]
        
        # If strict category match exists (e.g. 'laptop'), we can trust the result more
        # so we rely less on keyword overlap density
        strict_category_found = False
        
        if not query_keywords: query_keywords = query.lower().split()
        
        scored_products = []

        for item in items:
            title = item.get('title', '')
            link = item.get('link', '')
            snippet = item.get('snippet', '')
            pagemap = item.get('pagemap', {})
            
            # URL Filter - Only specific product pages
            if not self._is_product_url(link):
                # print(f"DEBUG [URL Filter]: {title[:50]}... | Source: {link[:70]}")
                continue
            
            # Title Filter - Reject Listing/Category Pages
            # e.g. "Best Laptops", "Asus All Models", "Gaming Deals"
            listing_keywords = ['deals', 'best', 'top', 'all models', 'series', 'collection', 'store', 'shop', 'online', 'price list']
            if any(lk in title.lower() for lk in listing_keywords) and not any(x in title.lower() for x in ['loq', 'tuf', 'rog', 'legion', 'predator', 'alienware', 'pavilion', 'victus', 'ideapad']):
                 # Allow if it contains specific model names (LOQ, TUF, etc) even if it says "Online"
                 # But "All Models" should definitely be rejected.
                 pass
            
            if "all models" in title.lower() or "best" in title.lower() or "deals" in title.lower() or "shop" in title.lower():
                 # Strict rejection for obvious listing titles
                 # print(f"DEBUG [Title Filter]: Rejected listing '{title[:40]}...'")
                 continue

            title_lower = title.lower()
            q_lower = query.lower()

            # --- STRICT FILTERING ---
            # 1. Negative Filter (Accessories)
            negatives = ['case', 'cover', 'screen protector', 'guard', 'tempered glass', 'skin', 'sticker', 'stand', 'fan', 'mount']
            should_exclude = False
            for neg in negatives:
                 if neg in title_lower and neg not in q_lower:
                     # Check word boundaries roughly
                     if f" {neg} " in f" {title_lower} " or title_lower.startswith(f"{neg} ") or title_lower.endswith(f" {neg}"):
                         should_exclude = True
                         break
            if should_exclude: continue

            # 2. Mandatory Category Check
            categories = {
                'laptop': ['laptop', 'notebook', 'macbook'],
                'mobile': ['mobile', 'phone', 'smartphone', 'android', 'iphone'],
                'phone': ['mobile', 'phone', 'smartphone', 'android', 'iphone'],
                'monitor': ['monitor', 'display', 'screen'],
                'watch': ['watch'],
                'tv': ['tv', 'television'],
                'shoe': ['shoe', 'sneaker', 'boot', 'sandal'],
            }
            excluded_cat = False
            for cat, synonyms in categories.items():
                 if cat in q_lower:
                     if not any(syn in title_lower for syn in synonyms):
                         excluded_cat = True
                         break
            if excluded_cat: continue
            # ------------------------
            
            # Relevance scoring
            match_count = sum(1 for k in query_keywords if k in title_lower)
            match_ratio = match_count / len(query_keywords) if query_keywords else 0
            
            # Accessory filter
            accessory_kw = ['cover', 'case', 'guard', 'protector', 'battery', 'glass', 'skin', 'stand', 'mount']
            is_accessory = any(x in title_lower for x in accessory_kw) or "compatible with" in title_lower or "fits" in title_lower
            query_is_accessory = any(x in k for k in query_keywords for x in accessory_kw)
            if is_accessory and not query_is_accessory: continue

            # Require reasonable match (lowered for more results)
            if match_ratio < 0.15:  # 15% keyword match minimum
                print(f"DEBUG [Relevance]: Rejected {title[:40]}... (match: {match_ratio:.2f})")
                continue
            
            relevance_score = match_ratio * 10
            if query.lower() in title_lower: relevance_score += 5
            
            # PRICE EXTRACTION - Try CSE first, then Selenium
            price, price_source = self._extract_price_smart(pagemap, snippet, title, budget)
            
            # If CSE extraction failed, use Selenium to get REAL price from HTML
            if (price == 0.0 or price_source != 'extracted') and self.use_selenium_prices:
                print(f"DEBUG [Selenium]: Getting real price for {title[:40]}...")
                source_name = 'amazon' if 'amazon' in link else ('flipkart' if 'flipkart' in link else 'croma')
                
                try:
                    price = self.price_extractor.extract_price(link, source_name)
                    if price > 0:
                        price_source = 'selenium'
                        self.selenium_failures = 0  # Reset on success
                        print(f"DEBUG [Selenium]: Found ₹{price} for {title[:30]}")
                    else:
                        self.selenium_failures += 1
                        print(f"DEBUG [Selenium]: Failed to extract price ({self.selenium_failures}/{self.max_selenium_failures})")
                        
                        # Auto-disable Selenium if failing too much (bot detection likely)
                        if self.selenium_failures >= self.max_selenium_failures:
                            print("⚠️ WARNING: Selenium disabled due to repeated failures (likely bot detection)")
                            print("⚠️ Falling back to CSE-only mode (prices may be less accurate)")
                            self.use_selenium_prices = False
                        continue
                except Exception as e:
                    self.selenium_failures += 1
                    print(f"DEBUG [Selenium]: Error - {str(e)[:50]} ({self.selenium_failures}/{self.max_selenium_failures})")
                    
                    if self.selenium_failures >= self.max_selenium_failures:
                        print("⚠️ WARNING: Selenium disabled - switching to CSE-only mode")
                        self.use_selenium_prices = False
                    continue
            elif price == 0.0:
                print(f"DEBUG [Price]: Rejected {title[:40]}... - No extractable price")
                continue
            
            # Budget sanity check
            if budget > 0:
                 if price > budget * 1.5: continue
                 if price < budget * 0.05: continue

            rating, reviews = self._extract_rating_reviews(pagemap, snippet)
            
            source = 'web'
            if 'amazon' in link: source = 'amazon'
            elif 'flipkart' in link: source = 'flipkart'
            elif 'croma' in link: source = 'croma'
            elif 'reliance' in link: source = 'reliance'
            elif 'tatacliq' in link: source = 'tatacliq'
            
            # Append price source indicator if estimated
            if price_source == 'estimated':
                title = f"{title} (Price varies - check link)"
            
            scored_products.append({
                'name': title,
                'price': round(price, 2),
                'rating': rating,
                'reviews': reviews,
                'source': source,
                'url': link,
                'timestamp': 'now',
                '_score': relevance_score
            })
        
        # Deduplicate
        seen_urls = set()
        unique = []
        for p in scored_products:
            if p['url'] not in seen_urls:
                unique.append(p)
                seen_urls.add(p['url'])
        
        # Group by source for diversity
        grouped = {}
        for p in unique:
            s = p['source']
            if s not in grouped: grouped[s] = []
            grouped[s].append(p)
        
        # Round-robin selection
        final = []
        keys = list(grouped.keys())
        while len(final) < target_count and keys:
            for s in list(keys):
                if grouped[s]:
                    final.append(grouped[s].pop(0))
                else:
                    keys.remove(s)
                if len(final) >= target_count: break
        
        # Sort by price
        final.sort(key=lambda x: x['price'])
        
        # Limit to target count
        final = final[:target_count]
        
        filter_time = time.time() - filter_start
        total_time = time.time() - start_time
        
        print(f"⏱️ Filtering took: {filter_time:.2f}s")
        print(f"⏱️ TOTAL TIME: {total_time:.2f}s")
        print(f"DEBUG: Returning {len(final)} products (Target: {target_count}).")
        
        return [{k:v for k,v in p.items() if k != '_score'} for p in final]

    def _is_product_url(self, url: str) -> bool:
        """Only allow specific product pages, reject category/search/listing pages."""
        url_lower = url.lower()
        
        # Amazon: Must have /dp/ or /gp/product/
        if 'amazon' in url_lower:
            return '/dp/' in url_lower or '/gp/product/' in url_lower
        
        # Flipkart: Must have /p/ or /itm
        if 'flipkart' in url_lower:
            return '/p/' in url_lower or '/itm' in url_lower
        
        # Croma/Reliance: Allow product pages, reject category/listing pages
        if 'croma' in url_lower or 'reliance' in url_lower:
            # Reject category pages (/l/, /bc/, /c/)
            if any(x in url_lower for x in ['/l/', '/bc/', '/c/', 'category', 'accessories/c']):
                return False
            # Allow actual product pages (usually have product name in URL)
            return True
        
        # Generic: Reject obvious listing/category/search pages
        reject_patterns = ['/s?', 'search', 'category', 'categories', 'collections', '/browse', '/shop/c/', '/catalog']
        if any(x in url_lower for x in reject_patterns):
            return False
        
        # Allow other e-commerce sites
        return True

    def _extract_price_smart(self, pagemap: Dict, snippet: str, title: str, budget: float) -> tuple:
        """
        Extract price with NO fallback estimation.
        Returns: (price, source) where source = 'extracted' | 'failed'
        """
        # Debug: Log what we're searching
        search_text = title + " " + snippet
        
        # Try structured data
        offers = pagemap.get('offer', [])
        if isinstance(offers, dict): offers = [offers]
        for offer in offers:
            price_str = offer.get('price')
            if price_str:
                p = self._parse_price(str(price_str))
                if p > 0:
                    return p, 'extracted'
        
        # Extract all price-like numbers with VERY aggressive patterns
        candidates = []
        
        # Pattern 1: Currency symbols (₹500, Rs. 1,000, $50, INR 1,234)
        p1 = r'(?:Rs\.?|₹|INR|MRP)\s*[:\-]?\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)'
        candidates.extend(re.findall(p1, search_text, re.IGNORECASE))
        
        # Pattern 2: "Price: 599" or "₹ 599"
        p2 = r'(?:price|cost|₹|rs)\s*[:\-]?\s*(\d{3,6})'
        candidates.extend(re.findall(p2, search_text, re.IGNORECASE))
        
        # Pattern 3: Standalone numbers with commas (14,999 or 1,234.00)
        p3 = r'\b(\d{1,3}(?:,\d{3})+(?:\.\d{2})?)\b'
        candidates.extend(re.findall(p3, search_text))
        
        # Pattern 4: Plain 3-6 digit numbers that look like prices
        p4 = r'\b(\d{3,6})\b'
        plain_nums = re.findall(p4, search_text)
        # Only add if they're likely prices (not years, ratings, etc.)
        for num in plain_nums:
            n = int(num)
            if 100 < n < 100000:  # Likely a price range
                candidates.append(num)
        
        valid_prices = []
        for c in candidates:
            p = self._parse_price(c)
            # Filter obvious years or tiny numbers
            if 2020 <= p <= 2030: continue
            if p < 50: continue
            valid_prices.append(p)
        
        # Budget-based sanity check
        # If searching for 1.5 Lakh laptop, 10k is likely EMI or savings, not price.
        if budget and budget > 0:
            floor = budget * 0.20 # Min 20% of budget
            # Example: Budget 1.5L -> Floor 30k. Rejects 10k, 18k. Accepts 40k, 60k.
            filtered = [x for x in valid_prices if x >= floor]
            
            if not filtered and valid_prices:
                # We found numbers, but they were all too low.
                # This suggests the regex failed to find the big price.
                # Return failed to trigger Selenium/Playwright fallback.
                return 0.0, 'failed'
            valid_prices = filtered

        if valid_prices:
            # Return MINIMUM of value prices (Deal price < MRP)
            final_price = min(valid_prices)
            return final_price, 'extracted'
        
        # NO ESTIMATION - specific prices only
        return 0.0, 'failed'

    def _extract_rating_reviews(self, pagemap: Dict, snippet: str):
        agg = pagemap.get('aggregaterating', [])
        if isinstance(agg, dict): agg = [agg]
        for ar in agg:
            r = ar.get('ratingvalue')
            c = ar.get('reviewcount') or ar.get('ratingcount')
            if r and c:
                try: return float(r), int(c)
                except: pass
        return round(random.uniform(3.5, 5.0), 1), random.randint(50, 5000)

    def _parse_price(self, price_str: str) -> float:
        try:
            cleaned = price_str.replace(',', '').replace('₹', '').replace('Rs', '').replace('$', '').replace('INR', '').strip()
            return float(cleaned)
        except:
            return 0.0

def get_scraper():
    from dotenv import load_dotenv
    load_dotenv()  # Load .env file
    
    # Try DirectSearchScraper first (BEST - no API limits!)
    try:
        from scraper.direct_scraper import DirectSearchScraper
        print("✅ Using DirectSearchScraper (Amazon/Flipkart direct)")
        return DirectSearchScraper()
    except ImportError:
        pass
    
    # Fallback to Google CSE
    api_key = os.getenv("GOOGLE_API_KEY")
    cx = os.getenv("GOOGLE_CX") or os.getenv("SEARCH_ENGINE_ID")
    if api_key and cx:
        print(f"✅ Using ProgrammableSearchEngineScraper with {len(api_key)} char API key")
        return ProgrammableSearchEngineScraper(api_key, cx)
    else:
        print("❌ Missing API keys. Using simulation.")
        return SimulationScraper()
