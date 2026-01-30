# 🚀 AURA - Quick Reference Card

## 🎯 Access Points

| URL | Purpose |
|-----|---------|
| `http://localhost:5001/` | Main interface (full features) |
| `http://localhost:5001/search-page` | **NEW** Simple search with product limit |

## 📡 API Endpoints

### Search Products
```bash
POST /search
{
  "query": "gaming laptop",
  "budget": 150000,
  "max_results": 10  # NEW: 3-20 products
}
```

### Negotiate (Batch)
```bash
POST /negotiate_chat
{
  "products": [...],
  "query": "laptop",
  "budget": 150000
}
```

### Negotiate (Streaming) - NEW
```bash
POST /negotiate_stream  # Real-time updates!
{
  "products": [...],
  "query": "laptop",
  "budget": 150000
}
```

## ✨ Key Features

### 1. Product Limit (NEW)
- **Default**: 5 products
- **Range**: 3-20 products
- **Control**: `max_results` parameter

### 2. Auto-Detection (NEW)
- **Clothing**: Myntra, Ajio, Shein, Amazon, Flipkart
- **Tech**: Amazon, Flipkart, Google Shopping
- **Trigger Words**: jacket, dress, laptop, mobile, etc.

### 3. Sources
- `amazon` - Amazon India
- `flipkart` - Flipkart
- `myntra` - Myntra (clothing)
- `ajio` - Ajio (clothing)
- `shein` - Shein (clothing)
- `[]` (empty) - All sources

## 🧪 Quick Tests

### Test 1: Default Search
```bash
curl -X POST http://localhost:5001/search \
  -H "Content-Type: application/json" \
  -d '{"query":"laptop","budget":150000}'
```
**Expected**: 5 products

### Test 2: Custom Limit
```bash
curl -X POST http://localhost:5001/search \
  -H "Content-Type: application/json" \
  -d '{"query":"laptop","max_results":15}'
```
**Expected**: 15 products

### Test 3: Clothing
```bash
curl -X POST http://localhost:5001/search \
  -H "Content-Type: application/json" \
  -d '{"query":"women jacket","budget":5000}'
```
**Expected**: Console shows "👗 Detected clothing query"

## 🎨 Frontend Snippet

```html
<!-- Product Limit Slider -->
<label>
    Products: <span id="count">5</span>
</label>
<input 
    type="range" 
    id="max-results" 
    min="3" 
    max="20" 
    value="5"
    oninput="document.getElementById('count').innerText=this.value"
>

<script>
async function search() {
    const max = document.getElementById('max-results').value;
    
    const res = await fetch('/search', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            query: "laptop",
            max_results: parseInt(max)  // KEY LINE
        })
    });
    
    const data = await res.json();
    console.log(`Got ${data.products.length} products`);
}
</script>
```

## 🔍 Console Keywords

**Success Indicators:**
```
✅ Using DirectSearchScraper
✅ Found 10 real products
👗 Detected clothing query
🛍️ Searching Myntra...
```

**Error Indicators:**
```
❌ NO PRODUCTS FOUND
❌ Scraping error: timeout
⚠️ Google Shopping failed
```

## 📊 Performance

| Action | Time |
|--------|------|
| Search (5 products) | 15-25s |
| Search (15 products) | 25-40s |
| Negotiation | 8-12s |
| Judge Analysis | 2-3s |
| **Total** | **30-55s** |

## 🐛 Quick Fixes

**No Products?**
```python
# Check console for errors
# Try: different query, lower limit, single source
```

**Browser Popup?**
```python
# scraper/direct_scraper.py:58
headless=True  # Must be True
```

**Wrong Product Count?**
```python
# Check request includes max_results
# Backend defaults to 5 if missing
```

## 🚀 Start Server
```bash
python web_app.py
```

## 📚 Full Docs
- `INTEGRATION_GUIDE.md` - Complete guide
- `README.md` - System overview
- `BUG_FIXES.md` - Recent changes
- `STREAMING_GUIDE.md` - Real-time negotiation

---

**Version**: 2.1.0  
**Updated**: Dec 29, 2024  
**Status**: ✅ Production Ready
