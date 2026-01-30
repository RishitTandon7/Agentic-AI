import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc

class PriceExtractor:
    """Extracts real prices from product pages using Selenium"""
    
    def __init__(self):
        self.driver = None
    
    def _init_driver(self):
        """Initialize undetected Chrome driver with crash prevention"""
        if self.driver:
            try:
                # Test if driver is still alive
                self.driver.title
                return  # Driver is working
            except:
                # Driver is dead, recreate it
                try:
                    self.driver.quit()
                except:
                    pass
                self.driver = None
        
        try:
            options = uc.ChromeOptions()
            options.add_argument('--headless=new')  # Use new headless mode
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--window-size=1920,1080')
            options.add_argument('--disable-blink-features=AutomationControlled')
            
            self.driver = uc.Chrome(options=options, version_main=143)  # Match your Chrome version
        except Exception as e:
            print(f"Failed to init Chrome: {e}")
            self.driver = None
    
    def extract_price(self, url: str, source: str) -> float:
        """Extract real price from product URL"""
        try:
            self._init_driver()
            self.driver.get(url)
            time.sleep(2)  # Wait for dynamic content
            
            if 'amazon' in source:
                return self._extract_amazon_price()
            elif 'flipkart' in source:
                return self._extract_flipkart_price()
            elif 'croma' in source:
                return self._extract_croma_price()
            else:
                return 0.0
                
        except Exception as e:
            print(f"Price extraction error for {url}: {e}")
            return 0.0
    
    def _extract_amazon_price(self) -> float:
        """Extract price from Amazon page"""
        selectors = [
            "span.a-price-whole",
            "span.a-offscreen",
            "#priceblock_ourprice",
            "#priceblock_dealprice"
        ]
        
        for selector in selectors:
            try:
                element = self.driver.find_element(By.CSS_SELECTOR, selector)
                price_text = element.text.replace(',', '').replace('₹', '').strip()
                price = float(price_text)
                if price > 0:
                    return price
            except:
                continue
        return 0.0
    
    def _extract_flipkart_price(self) -> float:
        """Extract price from Flipkart page"""
        selectors = [
            "div._30jeq3",
            "div._1vC4OE",
            "div._16Jk6d"
        ]
        
        for selector in selectors:
            try:
                element = self.driver.find_element(By.CSS_SELECTOR, selector)
                price_text = element.text.replace(',', '').replace('₹', '').strip()
                price = float(price_text)
                if price > 0:
                    return price
            except:
                continue
        return 0.0
    
    def _extract_croma_price(self) -> float:
        """Extract price from Croma page"""
        selectors = [
            "span.amount",
            "span.new-price",
            "span.sale-price"
        ]
        
        for selector in selectors:
            try:
                element = self.driver.find_element(By.CSS_SELECTOR, selector)
                price_text = element.text.replace(',', '').replace('₹', '').strip()
                price = float(price_text)
                if price > 0:
                    return price
            except:
                continue
        return 0.0
    
    def close(self):
        """Close the browser"""
        if self.driver:
            self.driver.quit()
            self.driver = None
