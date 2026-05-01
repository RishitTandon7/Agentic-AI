# Amazon CAPTCHA Bypass Solution

## Problem
Amazon blocks automated scraping with CAPTCHA challenges, making it difficult to get product listings directly.

## Solution
We now use **Google Shopping as an intermediary** to get Amazon products without triggering CAPTCHA:

1. **Google Shopping scrapes** product listings from multiple sources (Amazon, Flipkart, etc.)
2. **Amazon filter** extracts only Amazon products from the results
3. **Automatic fallback** - If direct Amazon scraping fails, the system automatically uses Google Shopping

## How It Works

### Architecture
```
User Request → Try Direct Amazon
                     ↓ (CAPTCHA)
               Google Shopping → Filter Amazon Products → Return Results
```

### New Methods

#### 1. `search_google_shopping_amazon(query, count)`
Scrapes Google Shopping and filters **ONLY Amazon products**.

```python
from scraper.direct_scraper import DirectSearchScraper

scraper = DirectSearchScraper()
amazon_products = scraper.search_google_shopping_amazon("gaming laptop", count=10)

# Returns Amazon products found via Google Shopping
for product in amazon_products:
    print(f"{product['name']} - ₹{product['price']}")
    print(f"URL: {product['url']}")  # Links to Amazon.in
```

#### 2. Enhanced `search_google_shopping(query, max_results)`
Improved Google Shopping scraper with:
- Multiple selector strategies (Google changes CSS classes frequently)
- Better price extraction
- Source detection (Amazon, Flipkart, Myntra, etc.)
- CAPTCHA retry logic
- Indian locale support

### Automatic Fallback in Controller

The `NegotiationController` now automatically uses Google Shopping when Amazon CAPTCHA is detected:

```python
# In controller.py - lines 131-147
if not self.sources or 'amazon' in self.sources:
    print(f"📦 Searching Amazon...")
    amazon_results = self.scraper.search_amazon(self.query, count=self.max_results)
    
    # Automatic fallback if CAPTCHA blocks direct access
    if not amazon_results:
        print(f"   ⚠️ Amazon direct search failed (CAPTCHA detected)")
        print(f"   🔄 Using Google Shopping to find Amazon products...")
        amazon_results = self.scraper.search_google_shopping_amazon(
            self.query, 
            count=self.max_results
        )
        print(f"   ✅ Google Shopping Amazon filter: {len(amazon_results)} products")
    
    products.extend(amazon_results)
```

## Testing

Run the test script to see it in action:

```bash
python test_amazon_google_filter.py
```

This will:
1. Try direct Amazon scraping (likely CAPTCHA)
2. Fall back to Google Shopping Amazon filter
3. Display comparison of results

## Benefits

✅ **No CAPTCHA** - Google Shopping doesn't trigger CAPTCHA as aggressively  
✅ **Automatic fallback** - Seamless user experience  
✅ **Multiple sources** - Can filter for Amazon, Flipkart, or any other store  
✅ **Realistic data** - Actual product listings with prices and links  
✅ **Future-proof** - Multiple selector strategies handle Google's UI changes  

## Limitations

⚠️ **Rate limiting** - Google may still block if too many requests  
⚠️ **Selector changes** - Google Shopping CSS classes change frequently  
⚠️ **Indirect links** - Some products may have Google redirect URLs  

## Best Practices

1. **Use sparingly** - Implement delays between requests
2. **Cache results** - Store scraped data to reduce API calls
3. **User agent rotation** - Already implemented in the scraper
4. **Monitor failures** - Log when both direct and Google Shopping fail
5. **Respect robots.txt** - This is for educational/personal use

## Alternative: Google Custom Search API

For production use, consider the **Google Custom Search API** (already supported):

```python
# Set in .env file
GOOGLE_API_KEY=your_api_key
SEARCH_ENGINE_ID=your_cx_id

# Use 'web' source in your request
# This uses official API with no CAPTCHA, but has daily quota limits
```

## Files Modified

1. `scraper/direct_scraper.py` - Added `search_google_shopping_amazon()` method
2. `controller.py` - Added automatic fallback logic
3. `test_amazon_google_filter.py` - Test script for demonstration

## Summary

This solution provides a **robust, CAPTCHA-resistant** way to get Amazon product listings by leveraging Google Shopping as an intermediary. The system automatically falls back when direct scraping fails, ensuring a smooth user experience.
