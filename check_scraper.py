import sys
sys.path.insert(0, r'd:\DUAL PERSONA AGENTIC AI')

from scraper.providers import get_scraper

scraper = get_scraper()
print(f"Scraper type: {type(scraper).__name__}")
print(f"Has selenium? {hasattr(scraper, 'use_selenium_prices') if hasattr(scraper, '__dict__') else 'N/A'}")
print(f"Has price_extractor? {hasattr(scraper, 'price_extractor') if hasattr(scraper, '__dict__') else 'N/A'}")
