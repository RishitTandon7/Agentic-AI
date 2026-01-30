import google.generativeai as genai
import json
import re
import ollama
from key_manager import KeyManager

class JudgeAgent:
    def __init__(self):
        self.km = KeyManager()

    def evaluate(self, product, user_query="", user_budget=0):
        """
        Evaluates product using LOCAL Llama 3.2 (RTX 4060) -> Fallback Gemini
        Now includes QUERY INTENT MATCHING as primary factor
        """
        # Updated Prompt for 5-Category Professional Analysis
        prompt = f"""
        Act as a Professional E-commerce Product Analyst.
        
        Analyze this product using ACTUAL DATA (not assumptions):
        
        Product Name: {product.get('name')}
        Price: ₹{product.get('price', 0):,}
        Customer Rating: {product.get('rating', 0)}/5.0
        Review Count: {product.get('reviews', 0)}
        Source/Marketplace: {product.get('source', 'Unknown')}
        
        TASK: Evaluate across FIVE dimensions. Provide detailed analytical reasoning for each score.
        
        1. PRICING ANALYSIS (25% weight):
           - Assess value proposition based on price tier (Budget/Mid-Range/Premium/Luxury)
           - Identify risk factors if price is suspiciously low
           - Score: 0-100 (Higher = Better value)
        
        2. CUSTOMER RATING (30% weight):
           - Evaluate satisfaction level from star rating
           - Assess quality consistency and defect likelihood
           - Score: 0-100 (4.5+ stars = 90+, 4.0+ = 80+, 3.5+ = 60+, 3.0+ = 40+, <3.0 = 20)
        
        3. SOCIAL PROOF / REVIEWS (15% weight):
           - Assess statistical reliability of review count
           - Determine market presence and popularity
           - Score: 0-100 (1000+ = 95, 500+ = 85, 100+ = 75, 50+ = 60, 10+ = 50, <10 = 30)
        
        4. BRAND TRUST (20% weight):
           - Identify brand tier (Dell/HP/Lenovo/Asus = Tier-1, Unknown = Lower)
           - Evaluate warranty infrastructure and service network
           - Score: 0-100 (Established brands = 90, Unknown = 60)
        
        5. MARKETPLACE RELIABILITY (10% weight):
           - Assess platform trust (Amazon/Flipkart = 90, Croma/Reliance = 85, Unknown = 70)
           - Evaluate buyer protection and return policies
           - Score: 0-100
        
        CRITICAL: Base scores STRICTLY on the actual data provided above. Do NOT use generic/assumed values.
        
        OUTPUT FORMAT (Valid JSON only):
        {{
            "is_real_product": true,
            "purchase_probability": <weighted_average>,
            "score_breakdown": {{
                "price": {{
                    "score": <0-100>,
                    "explanation": "<2-3 sentences explaining the price tier analysis, risk factors, and value justification>"
                }},
                "rating": {{
                    "score": <0-100>,
                    "explanation": "<2-3 sentences analyzing customer satisfaction, quality indicators, and defect likelihood>"
                }},
                "reviews": {{
                    "score": <0-100>,
                    "explanation": "<2-3 sentences on statistical reliability, market presence, and review confidence>"
                }},
                "brand": {{
                    "score": <0-100>,
                    "explanation": "<2-3 sentences on brand reputation, service network, and warranty infrastructure>"
                }},
                "source": {{
                    "score": <0-100>,
                    "explanation": "<2-3 sentences on marketplace trust, buyer protection, and authenticity guarantees>"
                }},
                "formula": "Weighted Average: Price(25%) × Rating(30%) × Reviews(15%) × Brand(20%) × Source(10%)"
            }},
            "one_line_verdict": "<Professional recommendation: HIGHLY RECOMMENDED (85%+) / RECOMMENDED (70%+) / CONDITIONAL (55%+) / NOT RECOMMENDED (<55%) with brief justification>"
        }}
        """

        # 1. Try LOCAL Llama 3.2 (Fastest/Privacy)
        try:
            response = ollama.chat(model='llama3.2', messages=[
                {'role': 'user', 'content': prompt}
            ], format='json') # Ollama supports JSON mode natively
            
            data = json.loads(response['message']['content'])
            data['one_line_verdict'] += " (⚡ Local Llama 3.2)"
            return data
            
        except Exception as e:
            print(f"Local Llama Error: {e} -> Falling back to Cloud")
            pass # Fallthrough to Gemini

        # 2. Fallback to Gemini 1.5 Flash (Stability)
        try:
            model_name = "gemini-1.5-flash"
            genai.configure(api_key=self.km.get_current_key())
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            
            text = response.text.strip()
            text = re.sub(r'```json\s*|```', '', text).strip()
            
            return json.loads(text)
            
        except Exception as e:
            err_msg = str(e)[:30]
            print(f"Cloud Judge Error: {e}")
            
            # REALISTIC FALLBACK SCORING with DETAILED ANALYSIS
            # Calculate based on ACTUAL product data with professional explanations
            
            # 0. QUERY INTENT MATCHING (Most Important!)
            # How well does this product match what the user searched for?
            query_match_score = 0
            query_explanation = ""
            
            if user_query:
                # Extract meaningful keywords from query
                ignore_words = {'for', 'the', 'with', 'and', 'buy', 'price', 'online', 'in', 'at', 'under', 'best', 'top', 'cheap'}
                query_keywords = [w.lower() for w in user_query.split() if w.lower() not in ignore_words and len(w) > 2]
                
                product_name = product.get('name', '').lower()
                
                # Check how many query keywords appear in product name
                matched = [kw for kw in query_keywords if kw in product_name]
                match_ratio = len(matched) / len(query_keywords) if query_keywords else 0
                
                if match_ratio >= 0.8:  # 80%+ keywords match
                    query_match_score = 95
                    query_explanation = f"Excellent Match: Product contains {len(matched)}/{len(query_keywords)} key requirements from search query ({', '.join(matched[:3])}). Directly addresses user intent. High relevance guaranteed."
                elif match_ratio >= 0.6:  # 60-80%
                    query_match_score = 75
                    query_explanation = f"Good Match: Contains {len(matched)}/{len(query_keywords)} search terms ({', '.join(matched[:3])}). Partially meets requirements but may lack {len(query_keywords)-len(matched)} requested feature(s). Review specifications carefully."
                elif match_ratio >= 0.4:  # 40-60%
                    query_match_score = 55
                    query_explanation = f"Partial Match: Only {len(matched)}/{len(query_keywords)} keywords found ({', '.join(matched[:2]) if matched else 'none'}). Significant deviation from search intent. Missing: {', '.join([k for k in query_keywords if k not in matched][:2])}. Consider alternatives."
                elif match_ratio >= 0.2:  # 20-40%
                    query_match_score = 30
                    query_explanation = f"Weak Match: Minimal alignment ({len(matched)}/{len(query_keywords)} terms). Product may be in same category but lacks critical features requested. Not recommended unless flexible on requirements."
                else:  # <20%
                    query_match_score = 10
                    query_explanation = f"Poor Match: Product does not align with search query. Found {len(matched)}/{len(query_keywords)} requested terms. Likely scraper returned irrelevant result. SKIP this option."
            else:
                # No query provided (shouldn't happen, but handle gracefully)
                query_match_score = 70
                query_explanation = "Query context unavailable for intent matching. Scoring based on general product quality only."
            
            # 1. Price Score (Value Analysis with Budget Context)
            price = product.get('price', 0)
            if price == 0:
                p_score = 10
                p_explanation = f"Critical: No pricing data available. This indicates either a scraping failure or unlisted product. High risk for procurement. Recommend manual verification before proceeding."
            elif price < 1000:
                p_score = 30
                p_explanation = f"Alert: Price point of ₹{price:,} is unusually low for this product category. Potential indicators: (1) Third-party accessory, (2) Refurbished/damaged goods, (3) Pricing error. Risk Level: HIGH. Recommend cross-verification with official sources."
            elif price < 10000:
                p_score = 50
                p_explanation = f"Budget Tier: ₹{price:,} positions this as an entry-level offering. Typical for: basic accessories, older generation tech, or promotional items. Value proposition depends on use case. Acceptable for non-critical applications."
            elif price < 50000:
                p_score = 70
                p_explanation = f"Mid-Range Segment: ₹{price:,} indicates mainstream market positioning. Represents balanced price-performance ratio. Suitable for majority of consumer/business applications. Competitive pricing observed in this bracket."
            elif price < 100000:
                p_score = 85
                p_explanation = f"Premium Category: ₹{price:,} signals high-end specifications and build quality. Expected features: Latest generation components, premium materials, extended warranty coverage. ROI justified for power users and professional workloads."
            else:
                p_score = 90
                p_explanation = f"Luxury/Professional: ₹{price:,} represents top-tier market segment. Characteristics: Cutting-edge technology, flagship specifications, brand prestige. Target demographic: Enterprise clients, content creators, enthusiasts. Investment-grade product with long lifecycle expected."
            
            # 2. Rating Score (Customer Satisfaction)
            rating = product.get('rating', 0)
            if rating >= 4.5:
                r_score = 95
                r_explanation = f"Exceptional: {rating}/5.0 rating demonstrates outstanding customer satisfaction (top 10% of products). Indicates: Reliable performance, minimal defect rate, strong post-sales support. Customer retention likelihood: VERY HIGH."
            elif rating >= 4.0:
                r_score = 80
                r_explanation = f"Above Average: {rating}/5.0 places product in upper quartile. Generally positive reception with minor reported issues. Acceptable quality-to-price ratio. Most customers would recommend. Defect rate: Low to Moderate."
            elif rating >= 3.5:
                r_score = 60
                r_explanation = f"Mixed Reception: {rating}/5.0 suggests polarized customer experiences. Common issues may include: Inconsistent quality control, missing features vs. marketing, or support gaps. Thorough research of negative reviews recommended before purchase."
            elif rating >= 3.0:
                r_score = 40
                r_explanation = f"Below Expectations: {rating}/5.0 indicates significant customer dissatisfaction. Red flags: Quality issues, poor durability, or misleading specifications. Consider alternatives unless discounted heavily. Return rate likely elevated."
            else:
                r_score = 20
                r_explanation = f"Critical Issues: {rating}/5.0 reflects severe product shortcomings. Indicators: Widespread failures, false advertising, or safety concerns. HIGH RISK. Not recommended for purchase. Manufacturer reputation may be compromised."
            
            # 3. Reviews Count (Social Proof & Reliability)
            reviews = product.get('reviews', 0)
            if reviews > 1000:
                rev_score = 95
                rev_explanation = f"High Confidence: {reviews:,} reviews provide statistically significant sample size. Rating reliability: EXCELLENT. Product has established market presence. Large user base enables accurate quality assessment. Low variance expected in individual experience."
            elif reviews > 500:
                rev_score = 85
                rev_explanation = f"Strong Validation: {reviews:,} customer reviews indicate popular product with solid market traction. Sample size sufficient for trend analysis. Rating stability: Good. Anomalous reviews have minimal impact on overall score."
            elif reviews > 100:
                rev_score = 75
                rev_explanation = f"Moderate Validation: {reviews:,} reviews offer reasonable confidence in rating accuracy. Adequate for initial assessment but vulnerable to review manipulation. Cross-reference with professional reviews for comprehensive evaluation."
            elif reviews > 50:
                rev_score = 60
                rev_explanation = f"Limited Data: {reviews} reviews provide baseline indicators but lack statistical robustness. Rating may fluctuate with additional feedback. Early product lifecycle or niche market typical. Proceed with standard caution."
            elif reviews > 10:
                rev_score = 50
                rev_explanation = f"Minimal Feedback: Only {reviews} customer reviews available. Insufficient for confident quality assessment. Possible reasons: New product launch, low sales volume, or marketplace listing. Higher uncertainty in purchase decision."
            else:
                rev_score = 30
                rev_explanation = f"Insufficient Data: {reviews} review(s) cannot validate product quality reliably. Major risk: No established track record. Could indicate: Brand new listing, unpopular item, or marketplace manipulation. Exercise extreme caution."
            
            # 4. Brand Recognition (Trust & Warranty)
            name = product.get('name', '').lower()
            trusted_brands = {
                'dell': 'Tier-1 Enterprise', 'hp': 'Tier-1 Enterprise', 'lenovo': 'Tier-1 Enterprise',
                'asus': 'Tier-1 Consumer/Gaming', 'apple': 'Tier-1 Premium', 'samsung': 'Tier-1 Consumer',
                'lg': 'Tier-1 Electronics', 'sony': 'Tier-1 Premium', 'msi': 'Tier-2 Gaming',
                'acer': 'Tier-2 Consumer', 'razer': 'Tier-2 Gaming'
            }
            
            brand_found = next((brand for brand in trusted_brands if brand in name), None)
            if brand_found:
                b_score = 90
                b_explanation = f"Established Brand: {brand_found.upper()} ({trusted_brands[brand_found]}) ensures: (1) Quality Assurance through rigorous QC, (2) Nationwide service network, (3) Genuine warranty coverage, (4) Spare parts availability. Brand equity provides protection against substandard manufacturing. Resale value: Higher than generic alternatives."
            else:
                b_score = 60
                b_explanation = f"Unverified Manufacturer: Brand not recognized in premium/established database. Implications: (1) Limited service infrastructure, (2) Uncertain warranty fulfillment, (3) Potential quality variance, (4) Lower resale value. Due diligence required: Check manufacturer credentials, warranty terms, and service center proximity before purchase."
            
            # 5. Source Trust (Marketplace Reliability)
            source = product.get('source', '').lower()
            if 'amazon' in source:
                src_score = 90
                src_explanation = f"Amazon.in: Tier-1 e-commerce platform. Benefits: (1) A-to-Z Guarantee protection, (2) 30-day return policy, (3) Customer service responsiveness, (4) Authenticity verification programs. Payment security: High. Delivery reliability: Excellent. Counterfeit risk: Low (for Amazon fulfilled items)."
            elif 'flipkart' in source:
                src_score = 90
                src_explanation = f"Flipkart: Leading Indian e-commerce giant. Advantages: (1) Buyer protection policies, (2) Localized customer support, (3) Wide delivery network, (4) Secure payment gateway. Quality assurance for Flipkart Assured products. Return process: Streamlined. Trust factor: High for domestic market."
            elif 'croma' in source or 'reliance' in source:
                src_score = 85
                src_explanation = f"Authorized Retailer: Tata/Reliance backed platform ensures: (1) Genuine products only, (2) Official manufacturer warranty, (3) Physical store pickup option, (4) Dedicated after-sales service. Premium positioning with slightly higher prices offset by reliability guarantee."
            else:
                src_score = 70
                src_explanation = f"Source: {source}. Unverified marketplace. Recommendations: (1) Check website SSL certificate, (2) Verify payment gateway security, (3) Review return policy terms, (4) Search for online customer feedback. Proceed only if seller has established reputation. COD payment preferred for first transaction."
            
            # WEIGHTED AVERAGE with Query Intent as PRIMARY factor
            avg_prob = int(
                (query_match_score * 0.35) +  # INTENT MATCH (Most Important!)
                (r_score * 0.25) +             # Customer Rating
                (p_score * 0.15) +             # Price Value
                (rev_score * 0.10) +           # Social Proof
                (b_score * 0.10) +             # Brand Trust
                (src_score * 0.05)             # Marketplace
            )
            
            # Overall assessment
            if avg_prob >= 85:
                verdict = f"HIGHLY RECOMMENDED ({avg_prob}%): Product perfectly aligns with search intent and exceeds quality benchmarks. Strong customer validation and institutional backing. Proceed with confidence."
            elif avg_prob >= 70:
                verdict = f"RECOMMENDED ({avg_prob}%): Good alignment with search requirements. Minor gaps in features or validation do not outweigh overall positive indicators. Suitable for purchase after detail review."
            elif avg_prob >= 55:
                verdict = f"CONDITIONAL ({avg_prob}%): Partial match to search intent or mixed quality signals. Acceptable for budget buyers or flexible requirements. Recommended: (1) Verify missing features acceptable, (2) Compare alternatives, (3) Read recent reviews."
            else:
                verdict = f"NOT RECOMMENDED ({avg_prob}%): Poor alignment with search query or significant quality concerns. Product either doesn't match what you searched for or has reliability issues. Explore better-matched alternatives."
            
            return {
                "is_real_product": True,
                "purchase_probability": avg_prob,
                "score_breakdown": {
                    "query_match": {"score": query_match_score, "explanation": query_explanation},
                    "rating": {"score": r_score, "explanation": r_explanation},
                    "price": {"score": p_score, "explanation": p_explanation},
                    "reviews": {"score": rev_score, "explanation": rev_explanation},
                    "brand": {"score": b_score, "explanation": b_explanation},
                    "source": {"score": src_score, "explanation": src_explanation},
                    "formula": "Intent Match(35%) × Rating(25%) × Price(15%) × Reviews(10%) × Brand(10%) × Source(5%)"
                },
                "one_line_verdict": verdict
            }
