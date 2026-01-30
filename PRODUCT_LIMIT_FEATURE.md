# User-Configurable Product Limit Feature

## ✅ Backend Complete!

Users can now control how many products they want to see.

---

## How It Works

### Default Behavior:
- **5 products per source** (e.g., 5 from Myntra + 5 from Ajio = 10 total, deduplicated to max 5)
- Final result: **5 unique products**

### User Can Change:
Send `max_results` in the request:
```json
{
  "query": "laptop",
  "budget": 150000,
  "sources": ["amazon"],
  "max_results": 10  // User wants 10 products
}
```

Result: **10 unique products from Amazon**

---

## Frontend Integration (Add to index.html)

### Option 1: Simple Dropdown

Add this to your search form:

```html
<!-- Add after budget input -->
<div class="form-group">
    <label for="max-results">Number of Products:</label>
    <select id="max-results" name="max_results">
        <option value="5" selected>5 products</option>
        <option value="10">10 products</option>
        <option value="15">15 products</option>
        <option value="20">20 products</option>
    </select>
</div>
```

### Option 2: Slider (More Modern)

```html
<div class="form-group">
    <label for="max-results">
        Products: <span id="results-count">5</span>
    </label>
    <input 
        type="range" 
        id="max-results" 
        name="max_results" 
        min="3" 
        max="20" 
        value="5" 
        step="1"
        oninput="document.getElementById('results-count').innerText = this.value"
    >
</div>
```

### JavaScript Update

Update your search function:

```javascript
async function handleSearch() {
    const query = document.getElementById('query').value;
    const budget = document.getElementById('budget').value;
    const sources = getSelectedSources(); // Your existing function
    const maxResults = parseInt(document.getElementById('max-results').value);
    
    const response = await fetch('/search', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            query: query,
            budget: budget,
            sources: sources,
            max_results: maxResults  // NEW PARAMETER
        })
    });
    
    const data = await response.json();
    displayProducts(data.products);
}
```

---

## Testing

### Test 1: Default (5 products)
```bash
curl -X POST http://localhost:5001/search \
  -H "Content-Type: application/json" \
  -d '{"query": "laptop", "budget": 150000, "sources": ["amazon"]}'
  
# Should return: 5 products
```

### Test 2: Custom (10 products)
```bash
curl -X POST http://localhost:5001/search \
  -H "Content-Type: application/json" \
  -d '{"query": "laptop", "budget": 150000, "sources": ["amazon"], "max_results": 10}'
  
# Should return: 10 products
```

### Test 3: Clothing (5 per source)
```bash
curl -X POST http://localhost:5001/search \
  -H "Content-Type: application/json" \
  -d '{"query": "women jacket", "budget": 5000, "max_results": 3}'
  
# Should return: 3 products total (from Myntra + Ajio + Shein, deduplicated)
```

---

## How Deduplication Works

### Example with max_results=5:

**Input:**
- Amazon: 5 products
- Flipkart: 5 products
- **Total**: 10 products

**Deduplication:**
- 2 products have same URL (listed on both)
- **Unique**: 8 products

**Final Output:**
- Sorted by price
- **Limited to 5** (user's max_results)

---

## Console Output

You'll now see:

```
👗 Detected clothing query. Using clothing platforms...
🛍️ Searching Myntra: fleece jacket (limit: 5)
   Found 5 products
🛍️ Searching Ajio: fleece jacket (limit: 5)
   Found 3 products
🛍️ Searching Shein: fleece jacket (limit: 5)
   Found 4 products
✅ Total before dedup: 12 products
✅ After deduplication: 10 products
✅ Returning top 5 to user (max_results=5)
```

---

## Benefits

1. **Faster searches**: Fewer products to scrape
2. **User control**: Let them decide how many options they want
3. **Better UX**: Don't overwhelm with 20 products if they only want 5

---

## Recommended Limits

| Use Case | Recommended max_results |
|----------|------------------------|
| Quick search | 5 |
| Standard search | 10 |
| Comparison shopping | 15 |
| Exhaustive search | 20 |

---

## Next Steps

1. Add the dropdown/slider to your frontend
2. Update the JavaScript to send `max_results`
3. Test with different values
4. Restart Flask and enjoy!

---

**Status**: ✅ Ready to use
**Default**: 5 products
**Range**: 3-20 products recommended
