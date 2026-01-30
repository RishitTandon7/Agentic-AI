# 🤖 AURA - AI-Powered Product Negotiation System

**An intelligent dual-persona AI system that searches, negotiates, and recommends the best products based on user requirements.**

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [System Architecture](#system-architecture)
3. [Core Components](#core-components)
4. [Detailed File Breakdown](#detailed-file-breakdown)
5. [How It Works](#how-it-works)
6. [Installation & Setup](#installation--setup)
7. [Usage Guide](#usage-guide)
8. [Technical Details](#technical-details)
9. [API Endpoints](#api-endpoints)
10. [Troubleshooting](#troubleshooting)

---

## 🎯 Overview

AURA is a **dual-persona AI negotiation system** that acts as both a buyer and seller to find the best product for users. Instead of simply showing search results, it:

1. **Scrapes** products from Amazon, Flipkart, Croma, etc.
2. **Negotiates** between buyer AI (user's advocate) and seller AI (product promoter)
3. **Judges** products based on 6 criteria: Intent Match, Rating, Price, Reviews, Brand, Source
4. **Recommends** the best product after 5 rounds of intelligent debate

### Key Features

- ✅ **Real-time web scraping** with anti-bot bypass
- ✅ **AI-powered negotiation** (Gemini 2.0 Flash + local Ollama)
- ✅ **Intelligent product comparison** (40+ factors analyzed)
- ✅ **Professional validation matrix** with detailed explanations
- ✅ **Dynamic negotiation outcomes** (buyer can switch products mid-debate)
- ✅ **Budget-aware recommendations**
- ✅ **Spec-relevance matching** (RTX 4060 vs RTX 3050)

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        USER INPUT                           │
│          (Query: "RTX 4060 laptop", Budget: ₹1.5L)         │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│              WEB SCRAPER (Phase 1)                          │
│  ┌─────────────┬─────────────┬──────────────┬─────────────┐│
│  │   Amazon    │  Flipkart   │    Croma     │  Reliance   ││
│  │  Scraper    │   Scraper   │   Scraper    │   Scraper   ││
│  └─────────────┴─────────────┴──────────────┴─────────────┘│
│         Price Extraction + Relevance Filtering              │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
            12 Products Found
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│           NEGOTIATION ENGINE (Phase 2)                      │
│  ┌──────────────────┐      ┌───────────────────┐            │
│  │  BUYER AGENT     │ ←──→ │   SELLER AGENT    │            │
│  │ (User Advocate)  │      │ (Product Pusher)  │            │
│  └──────────────────┘      └───────────────────┘            │
│                                                             │
│  Round 1: Seller offers premium (₹1.2L)                     │
│           Buyer rejects (over budget)                       │
│  Round 2: Seller tries mid-range (₹95K)                     │
│           Buyer compares with own choice                    │
│  Round 3: Seller suggests budget (₹75K)                     │
│           Buyer rejects (lacks specs)                       │
│  Round 4: Seller offers sweet spot (₹89K)                   │
│           Buyer SWITCHES (better value!) ✅                 │
│  Round 5: [Skipped - agreement reached]                     │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
         Final Product Selected
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│              JUDGE AGENT (Phase 3)                          │
│  Analyzes final product on 6 dimensions:                   │
│  1. Intent Match (35%): Does it match "RTX 4060"?         │
│  2. Customer Rating (25%): 4.5★ → 95/100                  │
│  3. Price Value (15%): ₹89K vs ₹1.5L budget               │
│  4. Social Proof (10%): 500+ reviews                       │
│  5. Brand Trust (10%): Dell/HP/Asus                        │
│  6. Marketplace (5%): Amazon/Flipkart                      │
│                                                             │
│  Final Score: 88% → HIGHLY RECOMMENDED                    │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│                RESULTS DISPLAYED                            │
│  - Product details                                          │
│  - Negotiation transcript (5 rounds)                       │
│  - Professional validation matrix                          │
│  - Purchase recommendation                                  │
└─────────────────────────────────────────────────────────────┘
```

---

## 🧩 Core Components

### 1. **Web Scraping System** (`scraper/`)

#### `direct_scraper.py` (PRIMARY)
- **Purpose**: Uses Playwright (headless browser) to scrape Amazon & Flipkart
- **Why Playwright?**: JavaScript execution, anti-bot evasion
- **Features**:
  - Popup/modal dismissal (Escape key, close buttons)
  - JSON-LD structured data parsing
  - Site-specific CSS selectors
  - Relevance filtering (removes accessories)
- **Output**: List of products with `{name, price, rating, reviews, url, source}`

**Key Functions**:
```python
def search_google_shopping(query, max_results=12):
    # Opens headless Chrome
    # Searches Google Shopping
    # Extracts product cards
    # Returns cleaned data

def extract_price(url, source):
    # Visits product page
    # Dismisses popups
    # Tries JSON-LD first
    # Falls back to CSS selectors
    # Returns price as float
```

#### `fast_price_extractor.py` (FALLBACK)
- **Purpose**: Simple HTTP requests (no browser)
- **Why?**: Faster than Playwright (2s vs 8s)
- **Limitations**: Misses dynamic content, easier to block
- **Used When**: Playwright fails or times out

### 2. **AI Agents** (`agents/`)

#### `buyer_agent.py` - User's Advocate
**Role**: Represents the user's interests, finds best value

**Key Method**: `pick_best_value(products, query_context)`
```python
# Scoring algorithm (100 points max):
# 1. Relevance Score (0-60 pts):
#    +15 per keyword match ("rtx", "4060", "16gb")
#
# 2. Rating Score (0-25 pts):
#    rating * 5 (e.g., 4.5★ = 22.5 pts)
#
# 3. Budget Score (0-40 pts):
#    Within budget: +40 base
#    80-100% of budget: +20 bonus (optimal use)
#    <50% of budget: -10 penalty (suspicious)
#    Over budget: -30 penalty

# Example:
# Product: "Dell RTX 4060 16GB Laptop" - ₹1.35L, 4.5★
# Query: "rtx 4060 laptop 16gb"
# Score: 45 (relevance) + 22.5 (rating) + 60 (budget) = 127.5
```

**Key Method**: `respond(seller_product, my_pick, ...)`
```python
# Intelligent comparison (can switch products!)
# 1. Calculate switch_score:
#    - Budget fit: ±15 pts
#    - Rating difference: ±20 pts per star
#    - Spec relevance: ±10 pts per keyword
#    - Value ratio (rating/price): ±10 pts
#
# 2. Decision logic:
#    if switch_score > 10:
#        return ("You're right, let's go with that", True)
#    else:
#        return ("I prefer my choice because...", False)
```

**Example Negotiation Logic**:
```
Seller offers: HP Pavilion RTX 4060 (₹95K, 4.2★)
Buyer's pick:  ASUS TUF RTX 4060 (₹89K, 4.5★)
Budget: ₹1.5L

Comparison:
- Budget fit: HP worse (farther from 90% target) → -15
- Rating: ASUS better (4.5 vs 4.2) → -6
- Spec match: Equal → 0
- Value: ASUS better (4.5/89K > 4.2/95K) → -10
Switch score: -31 → STAY with ASUS ❌
```

#### `seller_agent.py` - Product Promoter
**Role**: Promotes different products each round

**Strategy by Round**:
1. **Round 1**: Push most expensive (₹1.2L) - "Premium quality!"
2. **Round 2**: Suggest mid-range (₹95K) - "Great value"
3. **Round 3**: Offer cheapest (₹65K) - "Budget-friendly"
4. **Round 4**: Present upper-mid (₹89K) - "Perfect balance"
5. **Round 5**: Align with buyer's choice - "You're absolutely right"

**Pitch Generation**:
```python
# Uses Gemini AI with quota rotation:
# If gemini-2.5-flash fails → try gemini-2.5-flash-lite
# If all fail → use template: "This {name} is excellent at ₹{price}"
```

#### `judge_agent.py` - Impartial Evaluator
**Role**: Analyzes final product with detailed scoring

**Evaluation Process**:
```python
def evaluate(product, user_query, user_budget):
    # 1. Query Intent Match (35% weight)
    keywords = extract_keywords(user_query)
    match_ratio = count_matches(product.name, keywords)
    if match_ratio >= 0.8: query_score = 95  # Excellent
    elif match_ratio >= 0.6: query_score = 75  # Good
    elif match_ratio >= 0.4: query_score = 55  # Partial
    else: query_score = 30  # Poor
    
    # 2. Customer Rating (25% weight)
    if rating >= 4.5: rating_score = 95  # Top 10%
    elif rating >= 4.0: rating_score = 80  # Above average
    elif rating >= 3.5: rating_score = 60  # Mixed
    else: rating_score = 40  # Below expectations
    
    # 3. Price Analysis (15% weight)
    if price < budget * 0.5: price_score = 30  # Too cheap
    elif budget * 0.8 <= price <= budget: price_score = 85  # Optimal
    elif price < budget * 0.8: price_score = 70  # Good deal
    else: price_score = 50  # Over budget
    
    # 4. Social Proof (10% weight)
    if reviews >= 1000: review_score = 95
    elif reviews >= 500: review_score = 85
    elif reviews >= 100: review_score = 75
    elif reviews >= 50: review_score = 60
    else: review_score = 50
    
    # 5. Brand Trust (10% weight)
    if brand in ['dell', 'hp', 'lenovo', 'asus']:
        brand_score = 90  # Tier-1
    else:
        brand_score = 60  # Unknown
    
    # 6. Marketplace (5% weight)
    if 'amazon' in source or 'flipkart' in source:
        source_score = 90  # Trusted
    else:
        source_score = 70  # Unverified
    
    # Weighted average:
    final_score = (
        query_score * 0.35 +
        rating_score * 0.25 +
        price_score * 0.15 +
        review_score * 0.10 +
        brand_score * 0.10 +
        source_score * 0.05
    )
    
    # Verdict:
    if final_score >= 85: return "HIGHLY RECOMMENDED"
    elif final_score >= 70: return "RECOMMENDED"
    elif final_score >= 55: return "CONDITIONAL"
    else: return "NOT RECOMMENDED"
```

**Example Output**:
```json
{
  "purchase_probability": 88,
  "score_breakdown": {
    "query_match": {
      "score": 95,
      "explanation": "Excellent Match: Product contains 4/4 key requirements (rtx, 4060, laptop, 16gb). Directly addresses user intent."
    },
    "rating": {
      "score": 90,
      "explanation": "Exceptional: 4.5/5.0 rating demonstrates outstanding customer satisfaction. Reliable performance."
    },
    "price": {
      "score": 85,
      "explanation": "Premium Category: ₹89,000 signals high-end specs. ROI justified for power users."
    },
    "reviews": {
      "score": 85,
      "explanation": "Strong Social Proof: 547 reviews provide statistical reliability."
    },
    "brand": {
      "score": 90,
      "explanation": "Tier-1 Brand: ASUS is established manufacturer with strong warranty network."
    },
    "source": {
      "score": 90,
      "explanation": "Amazon: 99.8% authentic, robust buyer protection."
    }
  },
  "one_line_verdict": "HIGHLY RECOMMENDED (88%): Perfect alignment with search intent and exceeds quality benchmarks."
}
```

### 3. **Controller** (`controller.py`)

**Main orchestrator** - coordinates all components

```python
class NegotiationController:
    def __init__(self, query, budget, sources):
        self.query = query
        self.budget = budget
        self.sources = sources
        self.scraper = DirectSearchScraper()
        self.buyer = BuyerAgent(budget)
        self.seller = SellerAgent()
        self.store = ProductStore()
    
    def search_products(self):
        # Phase 1: Scraping
        products = self.scraper.search_google_shopping(self.query)
        
        # Deduplicate by URL
        unique = remove_duplicates(products)[:12]
        
        # Save to session
        self.store.save_products(unique, self.query)
        return unique
    
    def run_negotiation(self, products):
        # Phase 2: Negotiation (5 rounds)
        buyer_pick, is_affordable = self.buyer.pick_best_value(products, self.query)
        
        conversation = []
        final_product = None
        
        for round_num in range(1, 6):
            # Seller picks strategically
            if round_num == 1: seller_pick = products[-1]  # Premium
            elif round_num == 2: seller_pick = products[len(products)//2]  # Mid
            elif round_num == 3: seller_pick = products[0]  # Budget
            elif round_num == 4: seller_pick = products[len(products)//3]  # Upper-mid
            else: seller_pick = buyer_pick  # Align
            
            # Seller pitches
            pitch = self.seller.generate_pitch(seller_pick, round_num)
            conversation.append({"role": "seller", "message": pitch})
            
            # Buyer responds (can switch!)
            response, should_switch = self.buyer.respond(
                seller_pick, buyer_pick, is_affordable, round_num,
                use_ai=True, query_context=self.query
            )
            conversation.append({"role": "buyer", "message": response})
            
            # Dynamic outcome
            if should_switch:
                final_product = seller_pick
                print(f"Round {round_num}: Buyer switched!")
                break
        
        # Default to buyer's pick if no switch
        if not final_product:
            final_product = buyer_pick
        
        # Phase 3: Judge evaluation
        judge = JudgeAgent()
        analysis = judge.evaluate(final_product, self.query, self.budget)
        final_product['judge_analysis'] = analysis
        
        return {
            "negotiation": {"conversation": conversation},
            "final_choice": final_product
        }
```

### 4. **Web Application** (`web_app.py`)

**Flask backend** serving the UI

```python
@app.route('/search', methods=['POST'])
def search_products_endpoint():
    # 1. Start AI model warmup (parallel)
    warmer = ModelWarmer()
    warmer.start_check_async()
    
    # 2. Parse request
    data = request.json
    query = data.get('query')
    budget = float(data.get('budget', 0))
    sources = data.get('sources', ['amazon', 'flipkart'])
    
    # 3. Search products
    controller = NegotiationController(query, budget, sources)
    products = controller.search_products()
    
    return jsonify({"products": products})

@app.route('/negotiate_chat', methods=['POST'])
def negotiate_chat_endpoint():
    # 1. Get products from frontend
    data = request.json
    products = data.get('products')
    query = data.get('query')
    budget = float(data.get('budget', 0))
    
    # 2. Run negotiation
    controller = NegotiationController(query, budget, [])
    result = controller.run_negotiation(products)
    
    return jsonify(result)
```

### 5. **Frontend** (`index.html`)

**Single-page application** with vanilla JS

**Key Features**:
- Search form with budget/source selection
- Product cards grid
- Negotiation transcript modal
- Judge analysis modal (validation matrix)

**UI Flow**:
```javascript
// 1. User submits search
async function handleSearch() {
    const query = document.getElementById('query').value;
    const budget = document.getElementById('budget').value;
    
    // Show scanner animation
    showScanner("Scraping products...");
    
    // Call /search endpoint
    const response = await fetch('/search', {
        method: 'POST',
        body: JSON.stringify({query, budget, sources: ['amazon']})
    });
    
    const data = await response.json();
    displayProducts(data.products);
}

// 2. Auto-start negotiation
async function startNegotiation(products) {
    const response = await fetch('/negotiate_chat', {
        method: 'POST',
        body: JSON.stringify({products, query, budget})
    });
    
    const result = await response.json();
    displayNegotiation(result.negotiation.conversation);
    displayJudgeAnalysis(result.final_choice.judge_analysis);
}

// 3. Show validation matrix
function showJudgeBreakdown(analysis) {
    const breakdown = analysis.score_breakdown;
    
    // Render professional matrix
    const html = `
        <div class="matrix">
            ${Object.entries(breakdown).map(([key, item]) => `
                <div class="matrix-row">
                    <div class="score">${item.score}/100</div>
                    <div class="grade">${getGrade(item.score)}</div>
                    <div class="explanation">${item.explanation}</div>
                </div>
            `).join('')}
        </div>
    `;
    
    modalBody.innerHTML = html;
    modal.show();
}
```

---

## 📁 Detailed File Breakdown

### Root Directory

```
d:\DUAL PERSONA AGENTIC AI/
│
├── web_app.py              # Flask server (main entry point)
├── controller.py           # Orchestrates scraper, buyer, seller, judge
├── index.html              # Frontend UI (single-page app)
├── requirements.txt        # Python dependencies
├── .env                    # API keys (GOOGLE_API_KEY, GOOGLE_CX)
│
├── agents/                 # AI agent directory
│   ├── __init__.py
│   ├── buyer_agent.py      # User advocate (smart product picker)
│   ├── seller_agent.py     # Product promoter (multi-model rotation)
│   ├── judge_agent.py      # Impartial evaluator (6-factor analysis)
│   └── model_checker.py    # Verifies Gemini API connectivity
│
├── scraper/                # Web scraping directory
│   ├── __init__.py
│   ├── direct_scraper.py   # Playwright-based scraper (PRIMARY)
│   ├── fast_price_extractor.py  # HTTP-based scraper (FALLBACK)
│   ├── playwright_extractor.py  # Price extraction with Playwright
│   └── providers.py        # Scraper provider interfaces
│
├── static/                 # Static assets
│   ├── loading-experience.js    # Loading screen animations
│   └── visual-enhancements.css  # Premium UI styles
│
├── sessions/               # User session data (JSON files)
├── models/                 # Cached AI model data
└── README.md              # This file
```

### Detailed File Purposes

#### `web_app.py` (74 lines)
- **Purpose**: Flask HTTP server
- **Endpoints**: `/search`, `/negotiate_chat`
- **Port**: 5001
- **CORS**: Enabled for local development
- **Key Library**: Flask 2.3.0

#### `controller.py` (225 lines)
- **Purpose**: Main business logic coordinator
- **Key Class**: `NegotiationController`
- **Methods**: 
  - `search_products()` → scraping phase
  - `run_negotiation()` → debate phase
- **Dependencies**: All agents, scraper, product store

#### `index.html` (1377 lines)
- **Purpose**: Complete frontend
- **Styling**: Embedded CSS (glassmorphism, dark theme)
- **JavaScript**: Vanilla JS (no frameworks)
- **Key Sections**:
  - Search form (lines 600-700)
  - Product cards (lines 880-1100)
  - Negotiation modal (lines 1100-1250)
  - Judge modal (lines 1250-1370)

#### `agents/buyer_agent.py` (218 lines)
- **AI Model**: Gemini 2.0 Flash
- **Key Algorithm**: 
  - `pick_best_value()`: Scores products on relevance+rating+budget
  - `respond()`: Compares products with switch_score logic
- **Fallback**: Template responses if AI fails
- **Key Innovation**: Can change mind during negotiation

#### `agents/seller_agent.py` (115 lines)
- **AI Model Pool**: 12 Gemini models (quota rotation)
- **Strategy**: Different product each round
- **Pitch Types**: 
  - Enthusiastic (Round 1)
  - Reasonable (Round 2-3)
  - Conciliatory (Round 4-5)
- **Fallback**: Template pitches

#### `agents/judge_agent.py` (281 lines)
- **AI Model**: Gemini 2.0 Flash / Ollama (local)
- **Scoring Dimensions**: 6 factors with weighted average
- **Output Format**: JSON with detailed explanations
- **Fallback Logic**: Deterministic scoring if AI fails
- **Key Innovation**: Intent matching (35% weight on query relevance)

#### `scraper/direct_scraper.py` (357 lines)
- **Engine**: Playwright (Chromium headless)
- **Anti-Bot Measures**:
  - User-agent rotation
  - Popup dismissal
  - Natural delays (2-3s)
  - JavaScript execution
- **Data Sources**: Google Shopping results
- **Parsing**: BeautifulSoup + regex
- **Filtering**: Removes accessories, duplicates

#### `scraper/playwright_extractor.py` (208 lines)
- **Purpose**: Price extraction from product pages
- **Methods**:
  - `_extract_from_jsonld()`: Structured data (Schema.org)
  - `_extract_amazon_price()`: Amazon-specific selectors
  - `_extract_flipkart_price()`: Flipkart-specific selectors
  - `_extract_generic_price()`: Fallback regex
- **Timeout**: 45 seconds per page

#### `model_persistence.py` (50 lines)
- **Purpose**: Saves model index to file for quota rotation
- **Functions**:
  - `get_last_model_index()`: Reads from `models/last_index.txt`
  - `save_last_model_index()`: Writes to file
- **Why**: Prevents hitting same model's quota repeatedly

#### `key_manager.py` (80 lines)
- **Purpose**: Manages multiple Google API keys
- **Functions**:
  - `get_current_key()`: Returns active key
  - `rotate_key()`: Switches to next key
- **Keys File**: `.env` (GOOGLE_API_KEY_1, GOOGLE_API_KEY_2, ...)
- **Why**: Bypass quota limits (10K requests/day per key)

#### `model_warmer.py` (60 lines)
- **Purpose**: Pre-checks Gemini API connectivity
- **Method**: `start_check_async()` runs in background thread
- **Benefit**: Shows "⚠️ Warning" if API down before search fails
- **Check**: Sends test prompt "Hello" to Gemini

---

## 🔄 How It Works (Step-by-Step)

### Complete User Journey

**User Action**: Searches "RTX 4060 gaming laptop" with ₹1.5L budget

#### Step 1: Frontend Submission (0s)
```javascript
// index.html
function handleSearch() {
    showScanner("Initializing search...");
    fetch('/search', {
        method: 'POST',
        body: JSON.stringify({
            query: "RTX 4060 gaming laptop",
            budget: 150000,
            sources: ["amazon", "flipkart"]
        })
    });
}
```

#### Step 2: Backend Processing (0-40s)
```python
# web_app.py → controller.py → scraper/direct_scraper.py
@app.route('/search', methods=['POST'])
def search_products_endpoint():
    controller = NegotiationController(query="RTX 4060 gaming laptop", 
                                      budget=150000, 
                                      sources=["amazon", "flipkart"])
    products = controller.search_products()
    # Returns: [{name, price, rating, reviews, url, source}, ...]
```

**Inside `search_products()`**:
```python
def search_products(self):
    # 1. Initialize Playwright browser (headless Chrome)
    browser = playwright.chromium.launch(headless=True)
    
    # 2. Search Google Shopping
    page.goto("https://www.google.com/search?tbm=shop&q=RTX+4060+gaming+laptop")
    page.wait_for_selector('.sh-dgr__content')
    
    # 3. Extract product cards
    cards = page.query_selector_all('.sh-dgr__gr-auto')
    for card in cards:
        name = card.query_selector('.tAxDx').inner_text()
        price_text = card.query_selector('.a8Pemb').inner_text()
        price = parse_price(price_text)  # "₹89,999" → 89999.0
        
        # 4. Visit product page to get details
        product_url = card.query_selector('a').get_attribute('href')
        rating, reviews = extract_details(product_url)
        
        products.append({
            'name': name,
            'price': price,
            'rating': rating,
            'reviews': reviews,
            'url': product_url,
            'source': detect_source(product_url)  # "amazon" or "flipkart"
        })
    
    # 5. Filter irrelevant results
    filtered = filter_results(products, query="RTX 4060 gaming laptop")
    # Removes: laptop cases, bags, accessories
    
    # 6. Deduplicate
    unique = remove_duplicates(filtered)
    
    return unique[:12]  # Top 12 products
```

**Example Product Data**:
```json
[
  {
    "name": "ASUS TUF Gaming A15, AMD Ryzen 7 7435HS, RTX 4060 6GB, 16GB RAM, 512GB SSD",
    "price": 89990,
    "rating": 4.5,
    "reviews": 547,
    "url": "https://www.amazon.in/dp/B0C8XYZ123",
    "source": "amazon"
  },
  {
    "name": "Lenovo LOQ Intel Core i7-13650HX, RTX 4060 8GB, 24GB RAM, 1TB SSD",
    "price": 104913,
    "rating": 4.3,
    "reviews": 234,
    "url": "https://www.flipkart.com/lenovo-loq-xyz",
    "source": "flipkart"
  },
  ...10 more products...
]
```

#### Step 3: Display Products (40s)
```javascript
// Frontend receives products array
function displayProducts(products) {
    const container = document.getElementById('products-container');
    
    products.forEach(product => {
        const card = `
            <div class="product-card">
                <h3>${product.name}</h3>
                <div class="price">₹${product.price.toLocaleString()}</div>
                <div class="rating">${product.rating}★ (${product.reviews} reviews)</div>
                <a href="${product.url}" target="_blank">View Product</a>
            </div>
        `;
        container.innerHTML += card;
    });
    
    // Auto-start negotiation
    startNegotiation(products);
}
```

#### Step 4: Negotiation Phase (40s-50s)
```javascript
// Auto-triggered after products display
async function startNegotiation(products) {
    const response = await fetch('/negotiate_chat', {
        method: 'POST',
        body: JSON.stringify({
            products: products,
            query: "RTX 4060 gaming laptop",
            budget: 150000
        })
    });
    
    const result = await response.json();
    displayNegotiation(result.negotiation.conversation);
}
```

**Backend Negotiation**:
```python
def run_negotiation(products):
    # 1. Buyer picks best value
    buyer_pick, is_affordable = self.buyer.pick_best_value(products, 
                                                           query_context="RTX 4060 gaming laptop")
    # Result: ASUS TUF (89990, 127.5 score)
    
    # 2. Start 5-round debate
    conversation = []
    final_product = None
    
    ## ROUND 1 ##
    seller_pick = products[-1]  # Lenovo Legion (₹1.2L) - Most expensive
    pitch = seller.generate_pitch(seller_pick, round_num=1)
    # Gemini generates: "The Lenovo Legion offers unparalleled performance...ֿ"
    conversation.append({"role": "seller", "message": pitch, "round": 1})
    
    response, should_switch = buyer.respond(seller_pick, buyer_pick, ...)
    # Buyer compares:
    # - Lenovo: ₹1.2L (over budget) → switch_score -= 25
    # - ASUS: ₹89K (optimal) → stays
    # Result: ("That's over my budget...", False)
    conversation.append({"role": "buyer", "message": response, "round": 1})
    
    ## ROUND 2 ##
    seller_pick = products[6]  # HP Victus (₹95K) - Mid-range
    pitch = seller.generate_pitch(seller_pick, round_num=2)
    conversation.append({"role": "seller", "message": pitch, "round": 2})
    
    response, should_switch = buyer.respond(seller_pick, buyer_pick, ...)
    # Buyer compares:
    # - HP: ₹95K, 4.2★
    # - ASUS: ₹89K, 4.5★
    # - switch_score: -15 (budget) -6 (rating) = -21 → stays
    conversation.append({"role": "buyer", "message": response, "round": 2})
    
    ## ROUND 3 ##
    seller_pick = products[0]  # Acer Nitro (₹65K) - Cheapest
    pitch = seller.generate_pitch(seller_pick, round_num=3)
    conversation.append({"role": "seller", "message": pitch, "round": 3})
    
    response, should_switch = buyer.respond(seller_pick, buyer_pick, ...)
    # Buyer compares:
    # - Acer: ₹65K (too cheap, lacks specs) → switch_score -= 10
    conversation.append({"role": "buyer", "message": response, "round": 3})
    
    ## ROUND 4 ##
    seller_pick = products[4]  # MSI Cyborg (₹98K, 4.6★) - Upper-mid
    pitch = seller.generate_pitch(seller_pick, round_num=4)
    conversation.append({"role": "seller", "message": pitch, "round": 4})
    
    response, should_switch = buyer.respond(seller_pick, buyer_pick, ...)
    # Buyer compares:
    # - MSI: ₹98K, 4.6★, better specs (8GB VRAM vs 6GB)
    # - ASUS: ₹89K, 4.5★
    # - switch_score: -15 (price) +2 (rating) +10 (specs) = -3
    # - But value ratio: 4.6/98K > 4.5/89K? No
    # Result: ("Still prefer ASUS", False)
    conversation.append({"role": "buyer", "message": response, "round": 4})
    
    ## ROUND 5 ##
    seller_pick = buyer_pick  # ASUS TUF - Finally aligns
    pitch = seller.generate_pitch(seller_pick, round_num=5)
    conversation.append({"role": "seller", "message": pitch, "round": 5})
    
    response, should_switch = buyer.respond(seller_pick, buyer_pick, ...)
    # Same product! → should_switch = True (agreement)
    final_product = seller_pick  # ASUS TUF selected
    break
    
    # 3. Judge evaluates final choice
    judge = JudgeAgent()
    analysis = judge.evaluate(final_product, 
                             user_query="RTX 4060 gaming laptop",
                             user_budget=150000)
    # Returns: {purchase_probability: 88, score_breakdown: {...}, ...}
    
    final_product['judge_analysis'] = analysis
    
    return {
        "negotiation": {"conversation": conversation},
        "final_choice": final_product
    }
```

**Example Conversation Output**:
```json
{
  "negotiation": {
    "conversation": [
      {
        "role": "seller",
        "message": "The Lenovo Legion delivers flagship-tier performance with cutting-edge RTX 4090 graphics. At ₹1.2L, you're getting the absolute best.",
        "round": 1
      },
      {
        "role": "buyer",
        "message": "That's way over my ₹1.5L budget, and I only need RTX 4060. I'm looking at the ASUS TUF at ₹89K which fits better.",
        "round": 1
      },
      {
        "role": "seller",
        "message": "Fair point. How about the HP Victus RTX 4060 at ₹95K? Great brand reliability.",
        "round": 2
      },
      {
        "role": "buyer",
        "message": "I appreciate the suggestion, but the ASUS has a better rating (4.5★ vs 4.2★) and is ₹6K cheaper. I'm sticking with it.",
        "round": 2
      },
      {
        "role": "seller",
        "message": "Okay, what about the Acer Nitro at ₹65K? Significant savings.",
        "round": 3
      },
      {
        "role": "buyer",
        "message": "That's too cheap for RTX 4060. Likely has older gen CPU or less RAM. My ASUS pick has better specs.",
        "round": 3
      },
      {
        "role": "seller",
        "message": "Understood. The MSI Cyborg at ₹98K has 8GB VRAM vs ASUS's 6GB. Worth the extra ₹8K?",
        "round": 4
      },
      {
        "role": "buyer",
        "message": "Tempting, but for my use case (1080p gaming), 6GB is sufficient. ASUS offers better value.",
        "round": 4
      },
      {
        "role": "seller",
        "message": "You know what, you're absolutely right. The ASUS TUF at ₹89,990 is the perfect balance of performance and price. Let's go with that.",
        "round": 5
      },
      {
        "role": "buyer",
        "message": "Great! I'm glad we agree. The ASUS TUF it is.",
        "round": 5
      }
    ]
  },
  "final_choice": {
    "name": "ASUS TUF Gaming A15, AMD Ryzen 7 7435HS, RTX 4060...",
    "price": 89990,
    "rating": 4.5,
    "reviews": 547,
    "url": "https://www.amazon.in/dp/B0C8XYZ123",
    "source": "amazon",
    "judge_analysis": {
      "purchase_probability": 88,
      "score_breakdown": {...},
      "one_line_verdict": "HIGHLY RECOMMENDED (88%): Perfect alignment..."
    }
  }
}
```

#### Step 5: Display Negotiation (50s)
```javascript
function displayNegotiation(conversation) {
    const container = document.getElementById('negotiation-container');
    
    conversation.forEach(msg => {
        const bubble = `
            <div class="message ${msg.role}">
                <div class="role">${msg.role.toUpperCase()}</div>
                <div class="text">${msg.message}</div>
                <div class="round">Round ${msg.round}</div>
            </div>
        `;
        container.innerHTML += bubble;
    });
}
```

#### Step 6: Judge Analysis Display (50s)
```javascript
function displayJudgeAnalysis(analysis) {
    const breakdown = analysis.score_breakdown;
    const probability = analysis.purchase_probability;
    
    // Show recommendation badge
    document.getElementById('recommendation').innerText = 
        probability >= 85 ? "🎯 HIGHLY RECOMMENDED" :
        probability >= 70 ? "✅ RECOMMENDED" :
        probability >= 55 ? "⚠️ CONDITIONAL" :
        "❌ NOT RECOMMENDED";
    
    // Show validation matrix (on button click)
    document.getElementById('view-breakdown-btn').onclick = () => {
        showValidationMatrix(breakdown);
    };
}

function showValidationMatrix(breakdown) {
    const html = `
        <table class="matrix">
            ${Object.entries(breakdown).map(([key, item]) => `
                <tr>
                    <td class="category">🎯 ${key.toUpperCase()}</td>
                    <td class="score">${item.score}/100</td>
                    <td class="grade">${getGrade(item.score)}</td>
                    <td class="explanation">${item.explanation}</td>
                </tr>
            `).join('')}
        </table>
    `;
    
    modal.show(html);
}
```

---

## 🚀 Installation & Setup

### Prerequisites
- Python 3.9+
- Node.js 16+ (optional, for frontend development)
- Google Cloud account (for Gemini API)
- 4GB RAM minimum (for Playwright browser)

### Step 1: Clone Repository
```bash
git clone https://github.com/yourusername/aura-negotiation.git
cd aura-negotiation
```

### Step 2: Install Dependencies
```bash
# Python packages
pip install -r requirements.txt

# Playwright browser
playwright install chromium
```

**`requirements.txt`**:
```
Flask==2.3.0
google-generativeai==0.3.2
playwright==1.40.0
beautifulsoup4==4.12.0
lxml==4.9.0
httpx==0.25.0
python-dotenv==1.0.0
```

### Step 3: Configure API Keys
Create `.env` file:
```bash
# Google Gemini API
GOOGLE_API_KEY=AIzaSy...your_key_here

# Google Custom Search (for Google Shopping)
GOOGLE_CX=your_search_engine_id
```

**Get API Keys**:
1. **Gemini API**: https://makersuite.google.com/app/apikey
2. **Google CX**: https://programmablesearchengine.google.com/

### Step 4: Run Application
```bash
python web_app.py
```

**Output**:
```
 * Running on http://127.0.0.1:5001
 * Running on http://192.168.1.100:5001
```

### Step 5: Open Browser
Navigate to: `http://127.0.0.1:5001`

---

## 📖 Usage Guide

### Basic Search
1. Enter product query: `"gaming laptop"`
2. Set budget: `150000` (₹1.5L)
3. Select sources: `Amazon`, `Flipkart`
4. Click **Search**

### Advanced Tips

**For Best Results**:
- ✅ Be specific: `"RTX 4060 16GB RAM laptop"` instead of `"laptop"`
- ✅ Include budget: Helps buyer agent pick optimally
- ✅ Use brand names: `"Dell XPS"` gets better results
- ✅ Add specs: `"512GB SSD"`, `"144Hz display"`

**Troubleshooting Searches**:
- ❌ Gets accessories? → Add `"laptop"` or `"mobile"` explicitly
- ❌ Too expensive? → Lower budget or add `"budget"` keyword
- ❌ Wrong product? → Check spec keywords match

### Reading Negotiation

**Seller Strategy**:
- Round 1: Tests if you'll pay premium (₹1.2L)
- Round 2-3: Tries to upsell from buyer's choice
- Round 4: Offers compromise
- Round 5: Concedes to buyer's pick

**Buyer Behavior**:
- Rejects if over budget
- Compares rating/price value
- Checks spec relevance
- **Can switch** if seller's offer is objectively better

**Judge Report**:
- **Intent Match (35%)**: Did you get what you searched for?
- **Rating (25%)**: Is quality good? (4+ stars recommended)
- **Price (15%)**: Is it within budget? Suspicious if too cheap?
- **Reviews (10%)**: Enough social proof? (100+ reviews ideal)
- **Brand (10%)**: Tier-1 (Dell/HP) or unknown?
- **Source (5%)**: Amazon/Flipkart (trusted) or random site?

---

## 🔧 Technical Details

### Performance Metrics

| Metric | Value | Notes |
|--------|-------|-------|
| Search Time | 30-45s | Depends on network + scraping 12 products |
| Negotiation Time | 8-12s | 5 rounds × 2s per AI call |
| Judge Evaluation | 2-3s | Final analysis |
| **Total Time** | **40-60s** | From search to recommendation |

### Optimization Strategies

1. **Parallel Scraping** (Future):
   ```python
   import asyncio
   
   async def scrape_all_sources():
       tasks = [
           scrape_amazon(query),
           scrape_flipkart(query),
           scrape_croma(query)
       ]
       results = await asyncio.gather(*tasks)
       return flatten(results)
   ```

2. **Caching** (Implementable):
   ```python
   # Cache search results for 5 minutes
   @functools.lru_cache(maxsize=100)
   def search_products(query, budget):
       # ...existing code...
   ```

3. **Model Pre-warming**:
   ```python
   # Already implemented in model_warmer.py
   # Checks API before search starts
   ```

### Rate Limits & Quotas

**Google Gemini API**:
- Free tier: 10 requests/minute, 10K/day
- **Solution**: 12-model rotation pool
- **Fallback**: Template responses

**Google Custom Search**:
- Free tier: 100 searches/day
- **Solution**: Direct scraping (Playwright)

**Amazon/Flipkart**:
- No official API
- Risk: IP bans if too frequent
- **Solution**: 
  - Headless=True (stealth mode)
  - Delays (2-3s between requests)
  - User-agent rotation

### Error Handling

```python
# Example from buyer_agent.py
def respond(self, seller_product, my_pick, ...):
    try:
        # Try AI generation
        response = model.generate_content(prompt)
        return response.text, should_switch
    except Exception as e:
        # Log error
        print(f"AI Error: {e}")
        
        # Fallback to template
        if should_switch:
            return ("You're right, let's go with that", True)
        else:
            return ("I prefer my choice", False)
```

**Common Errors**:
1. **Quota Exceeded**: Rotates to next model
2. **Timeout**: Uses fast_price_extractor.py
3. **Parse Error**: Returns default values (rating=3.0, reviews=0)
4. **No Products Found**: Shows "No results" message

### Security Considerations

**API Keys**:
- ✅ Stored in `.env` (not in Git)
- ✅ Loaded via `python-dotenv`
- ❌ Never exposed to frontend

**User Input**:
- ✅ Query sanitized (`strip()`, max 200 chars)
- ✅ Budget validated (must be >0)
- ❌ No SQL injection risk (no database)

**Web Scraping**:
- ✅ Respects `robots.txt` (via reasonable delays)
- ✅ Headless browser (no UI overhead)
- ⚠️ May violate TOS (use responsibly)

---

## 📡 API Endpoints

### `POST /search`

**Purpose**: Search for products

**Request**:
```json
{
  "query": "gaming laptop RTX 4060",
  "budget": 150000,
  "sources": ["amazon", "flipkart"],
  "specs": "16GB RAM 512GB SSD"
}
```

**Response**:
```json
{
  "products": [
    {
      "name": "ASUS TUF Gaming A15...",
      "price": 89990,
      "rating": 4.5,
      "reviews": 547,
      "url": "https://amazon.in/...",
      "source": "amazon"
    },
    ...11 more...
  ]
}
```

**Status Codes**:
- `200`: Success
- `500`: Scraping error (check logs)

### `POST /negotiate_chat`

**Purpose**: Run negotiation on products

**Request**:
```json
{
  "products": [...],  // Array from /search
  "query": "gaming laptop RTX 4060",
  "budget": 150000
}
```

**Response**:
```json
{
  "negotiation": {
    "conversation": [
      {"role": "seller", "message": "...", "round": 1},
      {"role": "buyer", "message": "...", "round": 1},
      ...
    ]
  },
  "final_choice": {
    "name": "ASUS TUF...",
    "price": 89990,
    "judge_analysis": {
      "purchase_probability": 88,
      "score_breakdown": {
        "query_match": {"score": 95, "explanation": "..."},
        ...
      },
      "one_line_verdict": "HIGHLY RECOMMENDED..."
    }
  }
}
```

---

## 🐛 Troubleshooting

### Common Issues

#### 1. "No products found"
**Causes**:
- Query too specific ("Dell XPS 15 9530 RTX 4060 OLED")
- Scraper blocked by website
- Network timeout

**Solutions**:
```python
# Make query more generic
"gaming laptop RTX 4060" instead of full model number

# Check scraper logs
print(f"Visited: {url}")
print(f"HTML length: {len(html)}")

# Increase timeout in playwright_extractor.py
page.goto(url, timeout=60000)  # 60s instead of 45s
```

#### 2. "Negotiation stuck on Round 1"
**Cause**: AI API quota exceeded

**Solution**:
```python
# Check model_warmer output
"⚠️ Warmer: Could not verify model" → API issue

# Verify .env file
cat .env
# Should see: GOOGLE_API_KEY=AIza...

# Test API manually
from google.generativeai import GenerativeModel
model = GenerativeModel('gemini-2.0-flash')
model.generate_content("Hello")  # Should return response
```

#### 3. "Prices showing as ₹0"
**Cause**: Price extraction failed

**Solution**:
```python
# Enable debug logging in playwright_extractor.py
print(f"Price text: {price_text}")
print(f"Parsed price: {price}")

# Check site structure changed
# Update CSS selectors in direct_scraper.py
# Amazon: '.a-price-whole'
# Flipkart: '._30jeq3'
```

#### 4. "Judge analysis missing"
**Cause**: Judge evaluation crashed

**Solution**:
```python
# Check judge_agent.py logs
try:
    analysis = judge.evaluate(product, query, budget)
except Exception as e:
    print(f"Judge Error: {e}")  # Shows exact error
    
# Fallback to deterministic scoring
# (Already implemented in code)
```

---

## 🎓 Learning Resources

### Understanding the Code

**For Beginners**:
1. Start with `web_app.py` (simple Flask server)
2. Read `controller.py` (main orchestrator)
3. Study `buyer_agent.py` (scoring logic)
4. Explore `direct_scraper.py` (web scraping)

**For AI/ML enthusiasts**:
1. `judge_agent.py`: Prompt engineering examples
2. `buyer_agent.py`: Multi-factor scoring algorithms
3. `seller_agent.py`: Model rotation strategies

**For Web Developers**:
1. `index.html`: Vanilla JS patterns
2. CSS glassmorphism effects
3. Modal/animation implementations

### Key Algorithms Explained

**1. Product Scoring (buyer_agent.py)**:
```
Score = Relevance + Rating + Budget
      = (keywords × 15) + (stars × 5) + (fit × 40)
      
Example:
Query: "rtx 4060 laptop 16gb"
Product: "Dell XPS RTX 4060 16GB Gaming Laptop"

Relevance:
- "rtx" found → +15
- "4060" found → +15
- "16gb" found → +15
- Total: 45

Rating:
- 4.5★ → 4.5 × 5 = 22.5

Budget (₹1.5L budget, product ₹1.35L):
- Within budget → +40
- 90% of budget (₹1.35L) → +20
- Total: 60

Final Score: 45 + 22.5 + 60 = 127.5
```

**2. Switch Decision (buyer_agent.py)**:
```
switch_score = budget_diff + rating_diff + spec_diff + value_diff

if switch_score > 10:
    switch = True  # Accept seller's product
else:
    switch = False  # Stay with my choice

Example:
Seller: HP Victus ₹95K, 4.2★
Buyer:  ASUS TUF ₹89K, 4.5★
Budget: ₹1.5L

budget_diff = |95K - 135K| - |89K - 135K| = 40K - 46K = -6 → -15 pts
rating_diff = 4.2 - 4.5 = -0.3 → -6 pts
spec_diff = 0 (both have RTX 4060)
value_diff = (4.2/95K) - (4.5/89K) = 44.2 - 50.6 = -6.4 → -10 pts

switch_score = -15 - 6 + 0 - 10 = -31
Result: STAY with ASUS ❌
```

**3. Judge Weighting**:
```
Final Score = Σ (category_score × weight)

Categories:
1. Intent Match: 35%  (User got what they searched for?)
2. Rating: 25%        (Quality indicator)
3. Price: 15%         (Value vs budget)
4. Reviews: 10%       (Social proof)
5. Brand: 10%         (Reliability)
6. Source: 5%         (Marketplace trust)

Example:
Intent: 95 × 0.35 = 33.25
Rating: 90 × 0.25 = 22.50
Price: 85 × 0.15 = 12.75
Reviews: 85 × 0.10 = 8.50
Brand: 90 × 0.10 = 9.00
Source: 90 × 0.05 = 4.50
----------------------------
Total: 90.50 ≈ 91/100 → HIGHLY RECOMMENDED
```

---

## 📝 Future Enhancements

### Planned Features

1. **Voice Input** 🎤
   - Speak query instead of typing
   - Uses Web Speech API

2. **Price History Graph** 📈
   - Shows price trend (30 days)
   - "Best time to buy" indicator

3. **Saved Searches** 💾
   - Remember previous searches
   - Price drop alerts

4. **Comparison Mode** ⚖️
   - Select 2-3 products
   - Side-by-side specs table

5. **User Reviews Analysis** 🔍
   - Summarize 500+ reviews with AI
   - Extract pros/cons

6. **Mobile App** 📱
   - React Native version
   - Push notifications

### Contributing

**How to Contribute**:
1. Fork repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

**Code Style**:
- Python: PEP 8
- JavaScript: ESLint (Standard)
- Comments: Explain "why", not "what"

---

## 📜 License

MIT License - see `LICENSE` file

---

## 👥 Credits

**Author**: Your Name
**AI Models**: Google Gemini 2.0 Flash
**Libraries**: Flask, Playwright, BeautifulSoup
**Inspiration**: Negotiation psychology, e-commerce patterns

---

## 📞 Support

**Issues**: https://github.com/yourusername/aura/issues
**Email**: support@aura.com
**Discord**: https://discord.gg/aura

---

**Last Updated**: December 29, 2024
**Version**: 2.0.0
**Status**: Production Ready ✅
