from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import re
import threading

class DirectSearchScraper:
    """Scrape directly from Amazon/Flipkart search pages (NO Google CSE!)"""
    
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.context = None
    
    def search(self, query: str, budget: float, sources: list):
        """Main search method matching ScraperProvider interface"""
        all_results = []
        
        # Electronics sources
        if not sources or 'amazon' in sources:
            amazon_results = self.search_amazon(query, count=5)
            all_results.extend(amazon_results)
        
        if not sources or 'flipkart' in sources:
            flipkart_results = self.search_flipkart(query, count=5)
            all_results.extend(flipkart_results)
        
        # Clothing/Fashion sources
        if not sources or 'myntra' in sources:
            myntra_results = self.search_myntra(query, count=5)
            all_results.extend(myntra_results)
        
        if not sources or 'ajio' in sources:
            ajio_results = self.search_ajio(query, count=5)
            all_results.extend(ajio_results)
        
        if not sources or 'shein' in sources:
            shein_results = self.search_shein(query, count=5)
            all_results.extend(shein_results)
        
        if not sources or 'savana' in sources:
            savana_results = self.search_savana(query, count=5)
            all_results.extend(savana_results)
        
        # Sort by price and limit to 12
        all_results.sort(key=lambda x: x['price'])
        return all_results[:12]
    
    # Thread-local persistence
    _thread_local = threading.local()

    def _ensure_browser(self):
        """Initialize browser for the current thread if needed"""
        if not hasattr(DirectSearchScraper._thread_local, 'playwright'):
            print(f"🚀 Launching Headless Browser (Thread {threading.get_ident()})...")
            p = sync_playwright().start()
            # Run in headless mode for production (set to False for debugging)
            b = p.chromium.launch(
                headless=True,  # Changed to True - no browser window
                args=['--no-sandbox', '--disable-setuid-sandbox']
            )
            DirectSearchScraper._thread_local.playwright = p
            DirectSearchScraper._thread_local.browser = b
        
        self.playwright = DirectSearchScraper._thread_local.playwright
        self.browser = DirectSearchScraper._thread_local.browser
        self.context = self.browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            viewport={'width': 1920, 'height': 1080}
        )
    
    def search_amazon(self, query: str, count: int = 5):
        """Search Amazon directly and get products with prices"""
        self._ensure_browser()
        
        search_url = f"https://www.amazon.in/s?k={query.replace(' ', '+')}"
        page = self.context.new_page()
        
        try:
            page.goto(search_url, timeout=30000)
            
            # AMAZON CAPTCHA DETECTION
            if "Enter the characters you see below" in page.content():
                print("⚠️ AMAZON CAPTCHA DETECTED! Please solve it in the browser window...")
                try:
                    # Wait for results grid to appear
                    page.wait_for_selector("div.s-main-slot", timeout=45000)
                    print("✅ Amazon CAPTCHA Solved!")
                except:
                    print("❌ Amazon CAPTCHA Timed out.")
                    page.close()
                    return []

            page.wait_for_timeout(2000) # Fast wait
            
            soup = BeautifulSoup(page.content(), 'html.parser')
            cards = soup.select("div.s-main-slot div[data-component-type='s-search-result']")
            
            results = []
            seen = set()
            
            for card in cards:
                if len(results) >= count:
                    break
                
                # Get link
                a = card.select_one("a.a-link-normal.s-no-outline")
                if not a: continue
                
                raw_href = a.get("href")
                link = "https://www.amazon.in" + raw_href if raw_href.startswith("/") else raw_href
                    
                if link in seen: continue
                seen.add(link)
                
                # Get title/rating
                title_elem = card.select_one("h2 span")
                title = title_elem.get_text(strip=True) if title_elem else "Unknown Product"
                
                rating = 4.0
                try:
                    rating_elem = card.select_one("span[aria-label*='out of 5 stars']")
                    if rating_elem: rating = float(rating_elem.get("aria-label").split()[0])
                except: pass

                # Get Price
                whole = card.select_one("span.a-price-whole")
                if whole:
                    price = self._parse_price(whole.get_text(strip=True))
                    if price > 0:
                        results.append({
                            'name': title[:100],
                            'price': price,
                            'url': link,
                            'source': 'amazon',
                            'rating': rating,
                            'reviews': 100
                        })
            
            page.close()
            return self._filter_results(results, query)
        except Exception as e:
            print(f"Amazon Error: {e}")
            page.close()
            return []

    def search_flipkart(self, query: str, count: int = 5):
        """Search Flipkart directly"""
        self._ensure_browser()
        search_url = f"https://www.flipkart.com/search?q={query.replace(' ', '%20')}"
        page = self.context.new_page()
        try:
            print(f"DEBUG: Visiting {search_url}")
            page.goto(search_url, timeout=30000)
            page.wait_for_timeout(3000)
            
            # Dismiss generic popups
            try: page.keyboard.press("Escape")
            except: pass

            # JAVA SCRIPT INJECTION (The Nuclear Option)
            # Run extraction logic INSIDE the browser
            results = page.evaluate("""() => {
                const items = [];
                const cards = document.querySelectorAll('div[data-id], div.cPHDOP, div._1AtVbE, div.slAVV4, div._75nlfW');
                
                cards.forEach(card => {
                    if (items.length >= 8) return;

                    // LINK
                    const linkEl = card.querySelector('a[href*="/p/"], a.VJA3rP, a.CGtC98, a._1fQZEK, a.s1Q9rs');
                    if (!linkEl) return;
                    
                    // TITLE
                    let title = "Unknown";
                    const titleEl = card.querySelector('div.KzDlHZ, a.wjcEIp, div._4rR01T, .s1Q9rs');
                    if (titleEl) title = titleEl.innerText;
                    else if (linkEl.title) title = linkEl.title;
                    else title = linkEl.innerText;

                    // PRICE
                    let price = 0;
                    const priceEl = card.querySelector('div.Nx9bqj, div._30jeq3, div.hl05eU, div._1_WHN1');
                    if (priceEl) {
                        const txt = priceEl.innerText;
                        const clean = txt.replace(/[^\d]/g, '');
                        if (clean) price = parseFloat(clean);
                    } else {
                        // Regex fallback
                        const txt = card.innerText;
                        const m = txt.match(/([₹]|Rs\.?|INR)\s?([\d,]+)/i);
                        if (m) {
                            price = parseFloat(m[2].replace(/,/g, ''));
                        }
                    }

                    if (price > 100) { // Filter out garbage low prices
                        items.push({
                            name: title.trim(),
                            price: price,
                            url: linkEl.href,
                            source: 'flipkart',
                            rating: 4.2, // Mock rating if missing
                            reviews: 50
                        });
                    }
                });
                return items;
            }""")
            
            print(f"DEBUG: JS Extracted {len(results)} products")
            page.close()
            return self._filter_results(results, query)
        except Exception as e:
            print(f"Flipkart JS Error: {e}")
            page.close()
            return []
    
    def search_google_shopping(self, query: str, max_results: int = 12):
        """Scrape Google Shopping for global results"""
        self._ensure_browser()
        search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}&tbm=shop"
        
        page = self.context.new_page()
        try:
            print(f"🌍 Searching Google Shopping (Global): {query}")
            print(f"   URL: {search_url}")
            page.goto(search_url, timeout=30000)
            page.wait_for_timeout(3000)
            
            # Dismiss consent popup if present
            try:
                page.click('button:has-text("Accept all")', timeout=2000)
            except:
                pass
            
            # Debug: Check if page loaded
            title = page.title()
            print(f"   Page title: {title}")
            
            # Debug: Get page HTML sample
            html_sample = page.content()[:500]
            print(f"   HTML sample: {html_sample[:200]}...")
            
            # Extract product cards using JavaScript
            results = page.evaluate("""() => {
                const items = [];
                
                // Try multiple selectors
                let cards = document.querySelectorAll('.sh-dgr__gr-auto');
                console.log('Selector .sh-dgr__gr-auto found:', cards.length);
                
                if (cards.length === 0) {
                    cards = document.querySelectorAll('div[data-docid]');
                    console.log('Selector div[data-docid] found:', cards.length);
                }
                
                if (cards.length === 0) {
                    cards = document.querySelectorAll('.sh-dgr__content');
                    console.log('Selector .sh-dgr__content found:', cards.length);
                }
                
                console.log('Total cards to process:', cards.length);
                
                cards.forEach((card, index) => {
                    if (items.length >= 12) return;
                    
                    // Find link
                    const linkEl = card.querySelector('a');
                    if (!linkEl) {
                        console.log('Card', index, '- No link found');
                        return;
                    }
                    
                    // Extract title
                    const titleEl = card.querySelector('.tAxDx, .sh-np__product-title, h3, h4');
                    const title = titleEl ? titleEl.innerText : (linkEl.innerText || 'Unknown Product');
                    
                    // Extract price
                    const priceEl = card.querySelector('.a8Pemb, .T14wmb, [aria-label*="$"], [aria-label*="₹"]');
                    let price = 0;
                    if (priceEl) {
                        const priceText = priceEl.innerText || priceEl.getAttribute('aria-label') || '';
                        const match = priceText.match(/[₹$]?([\d,]+)/);
                        price = match ? parseInt(match[1].replace(/,/g, '')) : 0;
                    }
                    
                    console.log('Card', index, '- Title:', title, 'Price:', price);
                    
                    // Extract rating
                    let rating = 4.0;
                    const ratingEl = card.querySelector('[aria-label*="star"], .Rsc7Yb');
                    if (ratingEl) {
                        const ratingText = ratingEl.getAttribute('aria-label') || ratingEl.innerText;
                        const ratingMatch = ratingText.match(/([0-9.]+)/);
                        rating = ratingMatch ? parseFloat(ratingMatch[1]) : 4.0;
                    }
                    
                    // Detect source from URL
                    const url = linkEl.href;
                    let source = 'unknown';
                    if (url.includes('amazon.in') || url.includes('amazon.com')) source = 'amazon';
                    else if (url.includes('flipkart.com')) source = 'flipkart';
                    else if (url.includes('myntra.com')) source = 'myntra';
                    else if (url.includes('ajio.com')) source = 'ajio';
                    else if (url.includes('shein.com')) source = 'shein';
                    else if (url.includes('croma.com')) source = 'croma';
                    else if (url.includes('reliancedigital.in')) source = 'reliance';
                    
                    if (price > 0 && title !== 'Unknown Product') {
                        items.push({
                            name: title,
                            price: price,
                            url: url,
                            source: source,
                            rating: rating,
                            reviews: 100
                        });
                        console.log('Added product:', title);
                    } else {
                        console.log('Skipped - invalid data');
                    }
                });
                
                console.log('Total products extracted:', items.length);
                return items;
            }""")
            
            print(f"   ✅ Google Shopping extracted {len(results)} products (before filter)")
            
            # Debug: Show what we got
            for idx, r in enumerate(results[:3]):
                print(f"   Sample {idx+1}: {r.get('name', 'N/A')[:40]} - ₹{r.get('price', 0)} ({r.get('source', 'unknown')})")
            
            page.close()
            
            filtered = self._filter_results(results, query)
            print(f"   📊 After filtering: {len(filtered)} products")
            
            return filtered
            
        except Exception as e:
            print(f"   ❌ Google Shopping Error: {e}")
            import traceback
            traceback.print_exc()
            page.close()
            return []

    def search_myntra(self, query: str, count: int = 5):
        """Scrape Myntra search results"""
        self._ensure_browser()
        search_url = f"https://www.myntra.com/{query.replace(' ', '-')}"
        
        page = self.context.new_page()
        try:
            print(f"🛍️ Searching Myntra: {query}")
            page.goto(search_url, timeout=45000)  # Increased timeout
            page.wait_for_timeout(4000)  # Wait longer for JS
            
            results = page.evaluate("""() => {
                const items = [];
                const cards = document.querySelectorAll('li.product-base, ul.results-base li');
                
                cards.forEach(card => {
                    if (items.length >= 8) return;
                    
                    const linkEl = card.querySelector('a');
                    if (!linkEl) return;
                    
                    const title = card.querySelector('h3, h4, .product-product')?.innerText || 'Unknown';
                    const priceText = card.querySelector('.product-price, .product-discountedPrice')?.innerText || '0';
                    const price = parseInt(priceText.replace(/[^0-9]/g, '')) || 0;
                    const ratingText = card.querySelector('.product-rating')?.innerText || '4.0';
                    const rating = parseFloat(ratingText) || 4.0;
                    
                    items.push({
                        name: title,
                        price: price,
                        url: 'https://www.myntra.com' + linkEl.getAttribute('href'),
                        source: 'myntra',
                        rating: rating,
                        reviews: 100
                    });
                });
                return items;
            }""")
            
            page.close()
            print(f"   ✅ Myntra: {len(results)} products")
            return self._filter_results(results, query)
        except Exception as e:
            print(f"   ⚠️ Myntra Error: {str(e)[:100]}")
            page.close()
            return []
    
    def search_ajio(self, query: str, count: int = 5):
        """Scrape Ajio search results"""
        self._ensure_browser()
        search_url = f"https://www.ajio.com/search/?text={query.replace(' ', '%20')}"
        
        page = self.context.new_page()
        try:
            print(f"🛍️ Searching Ajio: {query}")
            page.goto(search_url, timeout=45000)  # Increased timeout
            page.wait_for_timeout(4000)  # Wait for dynamic content
            
            results = page.evaluate("""() => {
                const items = [];
                const cards = document.querySelectorAll('.item, .rilrtl-products-list__item');
                
                cards.forEach(card => {
                    if (items.length >= 8) return;
                    
                    const linkEl = card.querySelector('a');
                    if (!linkEl) return;
                    
                    const title = card.querySelector('.nameCls, .name')?.innerText || 'Unknown';
                    const priceText = card.querySelector('.price, .price-value')?.innerText || '0';
                    const price = parseInt(priceText.replace(/[^0-9]/g, '')) || 0;
                    
                    items.push({
                        name: title,
                        price: price,
                        url: 'https://www.ajio.com' + linkEl.getAttribute('href'),
                        source: 'ajio',
                        rating: 4.1,
                        reviews: 80
                    });
                });
                return items;
            }""")
            
            page.close()
            print(f"   ✅ Ajio: {len(results)} products")
            return self._filter_results(results, query)
        except Exception as e:
            print(f"   ⚠️ Ajio Error: {str(e)[:100]}")
            page.close()
            return []
    
    def search_shein(self, query: str, count: int = 5):
        """Scrape Shein India search results"""
        self._ensure_browser()
        search_url = f"https://www.sheinindia.in/search/{query.replace(' ', '-')}"
        
        page = self.context.new_page()
        try:
            print(f"🛍️ Searching Shein: {query}")
            page.goto(search_url, timeout=60000)  # Shein needs more time
            page.wait_for_timeout(5000)  # Wait for React to render
            
            results = page.evaluate("""() => {
                const items = [];
                const cards = document.querySelectorAll('.product-card, .S-product-item, [class*="product"]');
                
                cards.forEach(card => {
                    if (items.length >= 8) return;
                    
                    const linkEl = card.querySelector('a');
                    if (!linkEl) return;
                    
                    const title = card.querySelector('.product-card__title, .goods-title, h3')?.innerText || 'Unknown';
                    const priceText = card.querySelector('.product-card__price, .price-section')?.innerText || '0';
                    const price = parseInt(priceText.replace(/[^0-9]/g, '')) || 0;
                    const ratingText = card.querySelector('.she-rate-star, .product-card__rating')?.innerText || '4.2';
                    const rating = parseFloat(ratingText) || 4.2;
                    
                    items.push({
                        name: title,
                        price: price,
                        url: linkEl.href.startsWith('http') ? linkEl.href : 'https://in.shein.com' + linkEl.href,
                        source: 'shein',
                        rating: rating,
                        reviews: 150
                    });
                });
                return items;
            }""")
            
            page.close()
            print(f"   ✅ Shein: {len(results)} products")
            return self._filter_results(results, query)
        except Exception as e:
            print(f"   ⚠️ Shein Error: {str(e)[:100]}")
            page.close()
            return []
    
    def search_savana(self, query: str, count: int = 5):
        """Scrape Savana search results"""
        self._ensure_browser()
        search_url = f"https://www.savana.in/search?q={query.replace(' ', '+')}"
        
        page = self.context.new_page()
        try:
            print(f"🛍️ Searching Savana: {query}")
            page.goto(search_url, timeout=30000)
            page.wait_for_timeout(3000)
            
            results = page.evaluate("""() => {
                const items = [];
                const cards = document.querySelectorAll('.product-item, .product-card, [class*=\"product\"]');
                
                cards.forEach(card => {
                    if (items.length >= 8) return;
                    
                    const linkEl = card.querySelector('a');
                    if (!linkEl) return;
                    
                    const title = card.querySelector('.product-title, h3, h4')?.innerText || 'Unknown';
                    const priceText = card.querySelector('.price, .product-price')?.innerText || '0';
                    const price = parseInt(priceText.replace(/[^0-9]/g, '')) || 0;
                    
                    items.push({
                        name: title,
                        price: price,
                        url: linkEl.href.startsWith('http') ? linkEl.href : 'https://www.savana.in' + linkEl.href,
                        source: 'savana',
                        rating: 4.0,
                        reviews: 60
                    });
                });
                return items;
            }""")
            
            page.close()
            return self._filter_results(results, query)
        except Exception as e:
            print(f"Savana Error: {e}")
            page.close()
            return []

    def _filter_results(self, results, query):
        """Clean up results by removing obvious accessories unless requested"""
        filtered = []
        query_lower = query.lower()
        # Common junk keywords for tech products
        negatives = ['case', 'cover', 'screen protector', 'guard', 'tempered glass', 'skin', 'sticker', 'stand', 'fan', 'mount']
        
        print(f"DEBUG: Filtering {len(results)} raw items for relevance...")
        
        for p in results:
            title = p['name'].lower()
            is_relevant = True
            
            # 1. Negative Keyword Filter
            for neg in negatives:
                if neg in title and neg not in query_lower:
                    pattern = r'\b' + re.escape(neg) + r'\b'
                    if re.search(pattern, title):
                        print(f"DEBUG: Excluded '{p['name'][:30]}...' (Hit negative: {neg})")
                        is_relevant = False
                        break
            
            # 2. Mandatory Category Check
            # If query asks for "Laptop", result MUST say "Laptop"
            # Synonyms: phone <-> mobile
            categories = {
                'laptop': ['laptop', 'notebook', 'macbook', 'chromebook', 
                           'victus', 'pavilion', 'omen', 'envy',  # HP models
                           'loq', 'ideapad', 'legion', 'thinkpad',  # Lenovo models
                           'tuf', 'rog', 'vivobook', 'zenbook',  # Asus models
                           'inspiron', 'xps', 'alienware', 'latitude',  # Dell models
                           'predator', 'aspire', 'swift',  # Acer models
                           'cyborg', 'katana', 'stealth', 'raider'],  # MSI models
                'mobile': ['mobile', 'phone', 'smartphone', 'android', 'iphone'],
                'phone': ['mobile', 'phone', 'smartphone', 'android', 'iphone'],
                'monitor': ['monitor', 'display', 'screen'],
                'watch': ['watch'],
                'tv': ['tv', 'television'],
                'shoe': ['shoe', 'sneaker', 'boot', 'sandal'],
            }
            
            if is_relevant:
                for cat, synonyms in categories.items():
                    if cat in query_lower: # User asked for this category
                        # Check if title has AT LEAST ONE of the synonyms
                        has_cat = any(syn in title for syn in synonyms)
                        if not has_cat:
                            print(f"DEBUG: Excluded '{p['name'][:30]}...' (Missing mandatory category: {cat})")
                            is_relevant = False
                            break

            if is_relevant:
                filtered.append(p)
                
        return filtered

    def _parse_price(self, text: str) -> float:
        import re
        text = text.replace('₹', '').replace(',', '').replace('Rs', '').strip()
        match = re.search(r'(\d+(?:\.\d+)?)', text)
        return float(match.group(1)) if match else 0.0

    def search_google_shopping(self, query: str, count: int = 5):
        """Scrape Google Shopping directly (No API Key needed)"""
        self._ensure_browser()
        # Search specifically in Shopping tab
        search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}&tbm=shop&hl=en"
        
        page = self.context.new_page()
        try:
            print(f"DEBUG: Visiting {search_url}")
            page.goto(search_url, timeout=30000)
            
            # CAPTCHA DETECTION
            # Google often redirects to 'Sorry...' page on automated traffic
            if "Sorry" in page.title() or "CAPTCHA" in page.content() or "Unusual traffic" in page.content():
                 print("⚠️ GOOGLE CAPTCHA DETECTED! ⚠️")
                 print("👉 Please solve the CAPTCHA in the browser window manually!")
                 print("⏳ Waiting 45 seconds for you to solve it...")
                 try:
                     # Wait for product grid to appear after solution
                     page.wait_for_selector('.sh-dgr__content, .i0X6df, .sh-np__click-target', timeout=45000)
                     print("✅ CAPTCHA Solved! Resuming scrape...")
                 except:
                     print("❌ CAPTCHA Timed out. Skipping Google Shopping.")
                     page.close()
                     return []

            page.wait_for_timeout(3000) # Wait for skeleton to fill
            
            # JS Injection for Google Shopping
            # Google classes are obfuscated (e.g. 'i0X6df'), but structure is fairly consistent
            results = page.evaluate("""() => {
                const items = [];
                // Select generic product containers in grid/list
                // .sh-dgr__content is common for grid items
                // .i0X6df is common for list
                const cards = document.querySelectorAll('.sh-dgr__content, .i0X6df, .sh-np__click-target');
                
                cards.forEach(card => {
                    if (items.length >= 8) return;
                    
                    // TITLE (h3 usually)
                    let title = "Unknown";
                    const tEl = card.querySelector('h3, .tAxDx');
                    if (tEl) title = tEl.innerText;
                    
                    // PRICE
                    let price = 0;
                    // Find any text looking like a price
                    const priceEl = card.querySelector('span.a8Pemb, .a8Pemb, .HRLxBb');
                    if (priceEl) {
                         const txt = priceEl.innerText;
                         const clean = txt.replace(/[^\d.]/g, '');
                         if (clean) price = parseFloat(clean);
                    }
                    
                    // VENDOR (Simulated source detection)
                    let source = 'web';
                    const vendorEl = card.querySelector('.aULzUe, .IuHnof');
                    if (vendorEl) source = vendorEl.innerText.toLowerCase().replace(' ', '');
                    
                    // LINK
                    // Often inside a parent 'a' tag with href='/url?q=...'
                    let link = '';
                    const aEl = card.querySelector('a[href^="/url"], a[href^="http"]');
                    if (aEl) {
                        link = aEl.href;
                        // Clean Google Redirects if possible, or just use as is
                        if (link.includes('url?url=')) {
                             link = decodeURIComponent(link.split('url=')[1].split('&')[0]);
                        }
                    }

                    if (price > 100 && link) {
                        items.push({
                            name: title.trim(),
                            price: price,
                            url: link,
                            source: source || 'google_shopping',
                            rating: 4.0,
                            reviews: 10
                        });
                    }
                });
                return items;
            }""")
            
            print(f"DEBUG: Google Shopping Extracted {len(results)} items")
            page.close()
            return self._filter_results(results, query)
            
        except Exception as e:
            print(f"Google Shopping Error: {e}")
            page.close()
            return []

    # Remove close() logic that kills the browser
    def close(self):
        """Only close context, keep browser alive"""
        if self.context:
            self.context.close()
        # Do NOT close self.browser or self.playwright here
