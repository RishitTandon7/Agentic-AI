from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import re

class PlaywrightPriceExtractor:
    """Fast and reliable price extractor using Playwright"""
    
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.context = None
    
    def _ensure_browser(self):
        """Initialize browser only when needed"""
        if not self.browser:
            self.playwright = sync_playwright().start()
            self.browser = self.playwright.chromium.launch(
                headless=False, # Visible browser to bypass bot detection
                args=['--disable-blink-features=AutomationControlled']
            )
            self.context = self.browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                viewport={'width': 1920, 'height': 1080}
            )
    
    def extract_price(self, url: str, source: str) -> float:
        """Extract real price from product URL"""
        try:
            self._ensure_browser()
            page = self.context.new_page()
            page.goto(url, timeout=45000, wait_until='domcontentloaded') # Increased timeout
            page.wait_for_timeout(2000)  # Initial wait for page skeleton
            
            # DISMISS POPUPS/MODALS
            # 1. Press Escape (Closes most modals)
            try:
                page.keyboard.press('Escape')
                page.wait_for_timeout(500)
            except: pass
            
            # 2. Click common close/accept buttons
            dismiss_selectors = [
                'button:has-text("Accept")',
                'button:has-text("Close")',
                'button:has-text("×")',
                'button:has-text("Got it")',
                'button[aria-label="Close"]',
                'div.modal-close',
                'a.close-modal'
            ]
            for selector in dismiss_selectors:
                try:
                    if page.locator(selector).count() > 0:
                        page.locator(selector).first.click(timeout=1000)
                        page.wait_for_timeout(300)
                except: pass
            
            # 3. Remove overlay divs via JavaScript (Nuclear option)
            try:
                page.evaluate("""() => {
                    const overlays = document.querySelectorAll('[class*="modal"], [class*="popup"], [class*="overlay"], [id*="modal"]');
                    overlays.forEach(el => {
                        if (el.style.zIndex > 100 || getComputedStyle(el).position === 'fixed') {
                            el.remove();
                        }
                    });
                }""")
            except: pass
            
            page.wait_for_timeout(3000)  # Wait after dismissal for dynamic content
            
            html = page.content()
            page_title = page.title()
            page.close()
            
            # Debug output
            print(f"  → Visited: {url[:80]}")
            print(f"  → Title: {page_title[:60]}")
            
            soup = BeautifulSoup(html, 'lxml')
            
            # Try JSON-LD first (most reliable for OEM sites)
            price = self._extract_from_jsonld(soup)
            if price > 0:
                print(f"  ✓ Extracted from JSON-LD: ₹{price}")
                return price
            
            if 'amazon' in source:
                return self._extract_amazon_price(soup)
            elif 'flipkart' in source:
                return self._extract_flipkart_price(soup)
            elif 'croma' in source:
                return self._extract_croma_price(soup)
            elif 'reliance' in source:
                return self._extract_reliance_price(soup)
            else:
                return self._extract_generic_price(soup)
                
        except Exception as e:
            print(f"Playwright error for {url[:50]}: {str(e)[:100]}")
            return 0.0
    
    def _extract_amazon_price(self, soup) -> float:
        """Extract price from Amazon HTML"""
        selectors = [
            ('span', {'class': 'a-price-whole'}),
            # ... (keep existing) ...
            ('span', {'class': 'a-offscreen'}),
            ('span', {'id': 'priceblock_ourprice'}),
            ('span', {'id': 'priceblock_dealprice'}),
            ('span', {'class': 'a-price'}),
        ]
        return self._run_selectors(soup, selectors)

    def _extract_flipkart_price(self, soup) -> float:
        selectors = [
            ('div', {'class': '_30jeq3'}),
            ('div', {'class': '_1vC4OE'}),
            ('div', {'class': '_16Jk6d'}),
            ('div', {'class': '_25b18c'}),
        ]
        return self._run_selectors(soup, selectors)

    def _extract_croma_price(self, soup) -> float:
        selectors = [
            ('span', {'id': 'pdp-product-price'}),
            ('div', {'class': 'cp-price'}),
            ('span', {'class': 'amount'}),
            ('h2', {'class': 'cp-price'}),
        ]
        return self._run_selectors(soup, selectors)

    def _extract_reliance_price(self, soup) -> float:
        selectors = [
            ('span', {'class': 'pdp__offerPrice'}),
            ('span', {'class': 'pdp__dealPrice'}),
            ('span', {'class': 'pdp__mrpPrice'}),
        ]
        return self._run_selectors(soup, selectors)

    def _run_selectors(self, soup, selectors):
        for tag, attrs in selectors:
            elements = soup.find_all(tag, attrs)
            for element in elements:
                text = element.get_text().replace(',', '').replace('₹', '').strip()
                match = re.search(r'(\d+)', text)
                if match:
                    price = float(match.group(1))
                    if 100 < price < 1000000: # Raised limit to 10 Lakh
                        return price
        return 0.0
    
    def _extract_from_jsonld(self, soup) -> float:
        """Extract price from JSON-LD structured data (Schema.org Product)"""
        import json
        scripts = soup.find_all('script', {'type': 'application/ld+json'})
        for script in scripts:
            try:
                data = json.loads(script.string)
                # Handle both single object and array
                if isinstance(data, list):
                    data = data[0] if data else {}
                
                # Standard Product schema
                if data.get('@type') == 'Product' or 'Product' in str(data.get('@type', '')):
                    offers = data.get('offers', {})
                    if isinstance(offers, list):
                        offers = offers[0] if offers else {}
                    
                    # Try different price fields
                    price_fields = ['price', 'lowPrice', 'highPrice']
                    for field in price_fields:
                        price_val = offers.get(field)
                        if price_val:
                            try:
                                p = float(str(price_val).replace(',', '').replace('₹', '').replace('INR', '').strip())
                                if 100 < p < 1000000:
                                    return p
                            except: pass
            except: pass
        return 0.0
    
    def _extract_generic_price(self, soup) -> float:
        """Extract price using generic patterns and meta tags"""
        # 1. Meta Tags (High confidence)
        meta_selectors = [
            ('meta', {'property': 'og:price:amount'}),
            ('meta', {'property': 'product:price:amount'}),
            ('meta', {'itemprop': 'price'}),
            ('meta', {'name': 'twitter:data1'}),
        ]
        for tag, attrs in meta_selectors:
            el = soup.find(tag, attrs)
            if el and el.get('content'):
                try:
                    c = el['content'].replace(',', '').replace('₹', '')
                    p = float(c)
                    if 100 < p < 1000000: return p
                except: pass

        # 2. Text Patterns (Fallback)
        text = soup.get_text()
        patterns = [
            r'₹\s*(\d+(?:,\d+)*)',
            r'Rs\.?\s*(\d+(?:,\d+)*)',
            r'INR\s*(\d+(?:,\d+)*)'
        ]
        
        prices = []
        for pattern in patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                try:
                    p = float(match.replace(',', ''))
                    # Filter junk
                    if 2020 <= p <= 2030: continue
                    if 100 < p < 1000000: # Raised limit
                        prices.append(p)
                except: continue
        
        if not prices: return 0.0
        
        # Heuristic: If we have prices > 10000, ignore anything < 5000 (EMI)
        max_p = max(prices)
        if max_p > 10000:
            prices = [x for x in prices if x > 5000]
            if not prices: return max_p # Should not happen
        
        # Return likely deal price (min of valid big prices)
        return min(prices)
    
    def close(self):
        """Close browser and cleanup"""
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
