import re

def _filter_results(results, query):
    """SMART filter - lenient for clothing, strict for tech"""
    filtered = []
    query_lower = query.lower()
    
    # Detect query type
    clothing_kw = ['jacket', 'dress', 'shirt', 'pant', 'jeans', 'saree', 'kurta', 
                   'top', 'skirt', 'sweater', 'coat', 'hoodie', 'tshirt', 't-shirt',
                   'women', 'men', 'kids', 'clothing', 'fashion', 'wear', 'shorts',
                   'legging', 'trousers', 'blouse', 'suit', 'blazer']
    
    is_clothing = any(kw in query_lower for kw in clothing_kw)
    
    print(f"DEBUG: Filtering {len(results)} items...")
    print(f"DEBUG: Type: {'CLOTHING (lenient)' if is_clothing else 'TECH (strict)'}")
    
    if is_clothing:
        # CLOTHING: Only remove obvious junk
        junk = ['hanger', 'clip', 'tag', 'label']
        for p in results:
            if not any(j in p['name'].lower() for j in junk):
                filtered.append(p)
        print(f"   ✅ Kept {len(filtered)}/{len(results)} products")
    else:
        # TECH: Strict filtering
        negatives = ['case', 'cover', 'screen protector', 'guard', 'tempered glass']
        
        for p in results:
            title = p['name'].lower()
            is_ok = True
            
            # Remove accessories
            for neg in negatives:
                if neg in title and neg not in query_lower:
                    is_ok = False
                    break
            
            # Category check
            categories = {
                'laptop': ['laptop', 'notebook', 'macbook', 'chromebook'],
                'mobile': ['mobile', 'phone', 'smartphone'],
                'phone': ['mobile', 'phone', 'smartphone'],
            }
            
            for cat, synonyms in categories.items():
                if cat in query_lower:
                    if not any(syn in title for syn in synonyms):
                        is_ok = False
                        break
            
            if is_ok:
                filtered.append(p)
        
        print(f"   ✅ Kept {len(filtered)}/{len(results)} products")
    
    return filtered

# Test
test_results = [
    {'name': 'Women Black Pant', 'price': 1000},
    {'name': 'Women Blue Jeans', 'price': 1500},
    {'name': 'Laptop Case', 'price': 500},
]

print("\n🧪 Test 1: Clothing Query")
filtered = _filter_results(test_results, "women pant")
for p in filtered:
    print(f"   ✅ {p['name']}")

print("\n🧪 Test 2: Tech Query")
filtered = _filter_results(test_results, "laptop")
for p in filtered:
    print(f"   ✅ {p['name']}")
