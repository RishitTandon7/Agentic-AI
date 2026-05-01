# Quick Reference: Using Amazon CAPTCHA Bypass

## For End Users

### Nothing Changes!
Your existing code works exactly the same. The system automatically handles CAPTCHA.

```python
# Your existing code - NO CHANGES NEEDED
from controller import NegotiationController

controller = NegotiationController(
    query="gaming laptop",
    budget=60000,
    sources=['amazon']
)

products = controller.search_products()
# If Amazon CAPTCHA appears, automatically uses Google Shopping
# You get Amazon products either way!
```

## For Developers

### Direct Method Call

If you want to explicitly use Google Shopping for Amazon products:

```python
from scraper.direct_scraper import DirectSearchScraper

scraper = DirectSearchScraper()

# Get Amazon products via Google Shopping (bypasses CAPTCHA)
amazon_products = scraper.search_google_shopping_amazon(
    query="laptop",
    count=10
)

print(f"Found {len(amazon_products)} Amazon products")
for product in amazon_products:
    print(f"{product['name']} - Rs.{product['price']}")
    print(f"Link: {product['url']}")
```

### Get All Sources from Google Shopping

```python
# Get products from ALL stores (Amazon, Flipkart, Myntra, etc.)
all_products = scraper.search_google_shopping(
    query="laptop",
    max_results=20
)

# Filter manually
amazon = [p for p in all_products if 'amazon' in p['source']]
flipkart = [p for p in all_products if 'flipkart' in p['source']]
myntra = [p for p in all_products if 'myntra' in p['source']]
```

### Understanding the Flow

1. **Automatic Mode** (Recommended)
   ```
   Controller → Try Amazon Direct → [CAPTCHA] → Google Shopping → Filter Amazon → Return
   ```

2. **Manual Mode** (Advanced)
   ```
   DirectSearchScraper.search_google_shopping_amazon() → Always uses Google Shopping
   ```

## Product Object Structure

```python
{
    'name': 'Product Title',
    'price': 45999,  # in INR
    'url': 'https://amazon.in/...',
    'source': 'amazon',
    'rating': 4.5,
    'reviews': 250
}
```

## Common Issues

### Issue: "CAPTCHA detected"
**Solution**: This message is informational. The system automatically falls back to Google Shopping.

### Issue: "Google Shopping unavailable"
**Solution**: 
1. Check internet connection
2. Wait a few minutes (rate limiting)
3. Use Google Custom Search API (set `GOOGLE_API_KEY` in .env)

### Issue: No Amazon products found
**Reason**: Google Shopping might not have Amazon listings for that query
**Solution**: Try a different search term or use direct Amazon search during off-peak hours

## Testing

Test the bypass functionality:

```bash
python test_amazon_google_filter.py
```

This will:
1. Show direct Amazon attempt (likely CAPTCHA)
2. Demonstrate Google Shopping fallback
3. Display filtered Amazon products

## Performance

- **Direct Amazon**: 2-5 seconds (when working)
- **Google Shopping**: 3-7 seconds (more reliable)
- **Caching**: Instant (for repeated queries)

## Configuration

No configuration needed! But you can set these in `.env` for API mode:

```env
# Optional: Use Google Custom Search API (no CAPTCHA, has quota)
GOOGLE_API_KEY=your_api_key_here
SEARCH_ENGINE_ID=your_cx_id_here
```

Then use `sources=['web']` to force API usage.

## Debugging

Enable verbose logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Now run your scraper - you'll see detailed logs
```

## Browser Automation

The scraper uses Playwright with stealth mode:
- Rotates user agents
- Hides automation markers
- Uses realistic browser behavior
- Random delays between requests

All of this is automatic - you don't need to configure anything.

## Best Practices

1. **Cache results** - Don't re-scrape the same query repeatedly
2. **Add delays** - Already implemented, but be mindful of rate limits
3. **Handle empty results** - Always check `if products:` before processing
4. **Log failures** - Monitor when both methods fail
5. **Respect quotas** - If using Google API, monitor your daily quota

## Example: Full Integration

```python
from controller import NegotiationController

def search_with_fallback(query, budget=50000):
    """Search with automatic CAPTCHA bypass"""
    controller = NegotiationController(
        query=query,
        budget=budget,
        sources=['amazon', 'flipkart']  # Will use both sources
    )
    
    products = controller.search_products()
    
    if not products:
        print("No products found from any source")
        return []
    
    # Products are automatically sorted by price
    print(f"Found {len(products)} products")
    
    # Show source breakdown
    sources = {}
    for p in products:
        source = p.get('source', 'unknown')
        sources[source] = sources.get(source, 0) + 1
    
    print("Source breakdown:")
    for source, count in sources.items():
        print(f"  {source}: {count} products")
    
    return products

# Usage
products = search_with_fallback("gaming laptop RTX 4060")
```

## Support

If you encounter issues:

1. Check the logs for error messages
2. Try a different search query
3. Wait a few minutes and retry
4. Consider using Google Custom Search API for production

## Summary

✓ **Automatic**: Fallback happens without any code changes  
✓ **Transparent**: Users don't see any difference  
✓ **Reliable**: Multiple strategies ensure results  
✓ **Fast**: Cached results for repeated queries  
✓ **Flexible**: Can force specific methods if needed  

---

**You're all set!** The CAPTCHA bypass works automatically in the background.
