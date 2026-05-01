"""
Test script to demonstrate Google Shopping Amazon filter functionality.
This bypasses Amazon's CAPTCHA by scraping Google Shopping and filtering for Amazon products.
"""

from scraper.direct_scraper import DirectSearchScraper

def test_google_shopping_amazon_filter():
    """Test the new Google Shopping Amazon filter method"""
    
    print("=" * 80)
    print("Testing Google Shopping Amazon Filter")
    print("=" * 80)
    print()
    
    scraper = DirectSearchScraper()
    
    # Test query for laptops
    query = "gaming laptop RTX 4050"
    
    print(f"Query: '{query}'")
    print()
    
    # Method 1: Try direct Amazon search (will likely fail due to CAPTCHA)
    print("METHOD 1: Direct Amazon Search")
    print("-" * 80)
    try:
        amazon_direct = scraper.search_amazon(query, count=5)
        print(f"Direct Amazon: Found {len(amazon_direct)} products")
        for idx, product in enumerate(amazon_direct[:3], 1):
            print(f"   {idx}. {product['name'][:60]} - Rs.{product['price']}")
    except Exception as e:
        print(f"Direct Amazon failed: {e}")
        amazon_direct = []
    
    print()
    print()
    
    # Method 2: Use Google Shopping to find Amazon products (CAPTCHA bypass)
    print("METHOD 2: Google Shopping Amazon Filter (CAPTCHA Bypass)")
    print("-" * 80)
    try:
        amazon_via_google = scraper.search_google_shopping_amazon(query, count=5)
        print(f"Google Shopping Amazon Filter: Found {len(amazon_via_google)} products")
        for idx, product in enumerate(amazon_via_google[:5], 1):
            print(f"   {idx}. {product['name'][:60]}")
            print(f"      Price: Rs.{product['price']}")
            print(f"      Source: {product['source']}")
            print(f"      URL: {product['url'][:80]}...")
            print()
    except Exception as e:
        print(f"Google Shopping filter failed: {e}")
        import traceback
        traceback.print_exc()
    
    print()
    print("=" * 80)
    print("Test Complete!")
    print("=" * 80)
    
    # Cleanup
    try:
        scraper.close()
    except:
        pass

if __name__ == "__main__":
    test_google_shopping_amazon_filter()
