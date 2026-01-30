import httpx
from bs4 import BeautifulSoup
import re

class FastPriceExtractor:
    """Lightning-fast price extractor using httpx (no browser needed)"""
    
    def __init__(self):
        self.client = httpx.Client(
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            },
            timeout=5.0,
            follow_redirects=True
        )
    
    def extract_price(self, url: str, source: str) -> float:
        """Extract price via fast HTTP request"""
        try:
            response = self.client.get(url)
            if response.status_code != 200:
                return 0.0
            
            soup = BeautifulSoup(response.text, 'lxml')
            
            if 'amazon' in source:
                return self._extract_amazon_price(soup)
            elif 'flipkart' in source:
                return self._extract_flipkart_price(soup)
            else:
                return self._extract_generic_price(soup)
                
        except Exception as e:
            return 0.0
    
    def _extract_amazon_price(self, soup) -> float:
        """Extract price from Amazon HTML"""
        selectors = [
            ('span', {'class': 'a-price-whole'}),
            ('span', {'class': 'a-offscreen'}),
            ('span', {'id': 'priceblock_ourprice'}),
            ('span', {'id': 'priceblock_dealprice'})
        ]
        
        for tag, attrs in selectors:
            element = soup.find(tag, attrs)
            if element:
                price_text = element.get_text().replace(',', '').replace('₹', '').strip()
                try:
                    return float(re.search(r'\d+', price_text).group())
                except:
                    continue
        return 0.0
    
    def _extract_flipkart_price(self, soup) -> float:
        """Extract price from Flipkart HTML"""
        selectors = [
            ('div', {'class': '_30jeq3'}),
            ('div', {'class': '_1vC4OE'}),
            ('div', {'class': '_16Jk6d'})
        ]
        
        for tag, attrs in selectors:
            element = soup.find(tag, attrs)
            if element:
                price_text = element.get_text().replace(',', '').replace('₹', '').strip()
                try:
                    return float(re.search(r'\d+', price_text).group())
                except:
                    continue
        return 0.0
    
    def _extract_generic_price(self, soup) -> float:
        """Extract price using generic patterns"""
        # Look for common price patterns in the entire page
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
                    if 50 < p < 100000:
                        prices.append(p)
                except:
                    continue
        
        return min(prices) if prices else 0.0
    
    def close(self):
        """Close HTTP client"""
        self.client.close()
