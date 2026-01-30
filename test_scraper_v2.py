from scraper.direct_scraper import DirectSearchScraper
import sys

# Force utf-8 for windows console
sys.stdout.reconfigure(encoding='utf-8')

def test_scraper():
    print("🚀 Starting Test Scraper...")
    scraper = DirectSearchScraper()
    
    query = "Samsung S24 Ultra Cover"
    print(f"🔎 Searching for: {query}")
    
    results = scraper.search_amazon(query)
    print(f"Amazon Results: {len(results)}")
    for p in results:
        print(f" - {p['name'][:50]}... : {p['price']}")

    results_fk = scraper.search_flipkart(query)
    print(f"Flipkart Results: {len(results_fk)}")
    for p in results_fk:
        print(f" - {p['name'][:50]}... : {p['price']}")
        
    print("✅ Done.")

if __name__ == "__main__":
    test_scraper()
