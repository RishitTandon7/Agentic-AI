"""
LLM as Judge - Semantic Extraction Layer
IEEE A* Conference Submission Artifact

This module handles ONLY the LLM-based signal extraction.
It is STRICTLY FORBIDDEN from computing scores or making recommendations.

The LLM acts as a semantic labeler, not an evaluator.
"""

import json
import requests
from typing import Dict, Any, Optional


# ============================================================================
# SYSTEM PROMPT (KILLS CREATIVITY, ENFORCES DISCIPLINE)
# ============================================================================

SYSTEM_PROMPT = """You are a laptop specification extractor. Extract ONLY factual information.

Output ONLY valid JSON. No explanations. No markdown. Just the JSON object.

Example output format:
{"cpu_tier": "A", "gpu_tier": "B", "ram_gb": 16, "storage_gb": 512, "display_tier": "B", "brand_reliability": "High", "sentiment_distribution": {"positive": 0.7, "neutral": 0.2, "negative": 0.1}, "review_count": 3, "average_rating": 4.5}"""


# ============================================================================
# IMPROVED DEVELOPER PROMPT
# ============================================================================

DEVELOPER_PROMPT = """Classification rules:

CPU tiers: S (i9/Ryzen9), A (i7/Ryzen7), B (i5/Ryzen5), C (i3/Ryzen3), D (Celeron/old)
GPU tiers: S (4090/4080), A (4070), B (4060/3060), C (old),  D (very old), Integrated (no GPU)
Display: A (4K/OLED), B (1440p/144Hz), C (1080p/basic)
Brand: High (Dell XPS/Apple/ThinkPad/ASUS ROG), Medium (HP/Acer/MSI), Low (generic)

Sentiment from reviews: positive + neutral + negative = 1.0

Output JSON with these exact keys:
cpu_tier, gpu_tier, ram_gb, storage_gb, display_tier, brand_reliability, sentiment_distribution, review_count, average_rating

Use null for missing data. Numbers must be actual numbers, not strings."""


# ============================================================================
# IMPROVED EXTRACTION WITH FALLBACK
# ============================================================================

def extract_signals(
    product_description: str,
    customer_reviews: str,
    model: str = "llama3.2",
    ollama_url: str = "http://localhost:11434/api/generate",
    max_retries: int = 3
) -> Dict[str, Any]:
    """
    Extract structured signals from raw product data using LLM.
    
    Improved version with better prompts and error handling.
    """
    
    # Simplified user prompt
    user_prompt = f"""Product: {product_description}
Reviews: {customer_reviews}

Extract to JSON:"""
    
    # Compact prompt
    full_prompt = f"""{SYSTEM_PROMPT}

{DEVELOPER_PROMPT}

{user_prompt}"""
    
    # Track last error for debugging
    last_error = None
    last_output = None
    
    for attempt in range(max_retries):
        try:
            # Call Ollama
            response = requests.post(
                ollama_url,
                json={
                    "model": model,
                    "prompt": full_prompt,
                    "stream": False,
                    "format": "json",  # Force JSON mode
                    "options": {
                        "temperature": 0.1,
                        "num_predict": 300,
                    }
                },
                timeout=90
            )
            
            if response.status_code != 200:
                raise RuntimeError(f"Ollama error: {response.status_code}")
            
            # Get response
            result = response.json()
            llm_output = result.get("response", "").strip()
            last_output = llm_output
            
            # Clean output (remove markdown if present)
            if "```json" in llm_output:
                llm_output = llm_output.split("```json")[1].split("```")[0].strip()
            elif "```" in llm_output:
                llm_output = llm_output.split("```")[1].split("```")[0].strip()
            
            # Parse JSON
            signals = json.loads(llm_output)
            
            # Fix common issues
            signals = fix_signal_types(signals)
            
            # Validate
            from llm_judge_config import validate_signal_schema
            if validate_signal_schema(signals):
                return signals
            else:
                last_error = "Schema validation failed"
                print(f"[Attempt {attempt + 1}] Schema validation failed")
                
        except json.JSONDecodeError as e:
            last_error = f"JSON error: {e}"
            print(f"[Attempt {attempt + 1}] JSON decode error")
        except Exception as e:
            last_error = str(e)
            print(f"[Attempt {attempt + 1}] Error: {e}")
    
    # All retries failed - return conservative fallback
    print(f"[WARNING] LLM extraction failed after {max_retries} attempts")
    print(f"Last error: {last_error}")
    if last_output:
        print(f"Last output: {last_output[:200]}")
    
    return create_fallback_signals(product_description, customer_reviews)


def fix_signal_types(signals: Dict[str, Any]) -> Dict[str, Any]:
    """Fix common type issues in LLM output."""
    
    # Convert string numbers to actual numbers
    for key in ['ram_gb', 'storage_gb', 'review_count', 'average_rating']:
        if key in signals and isinstance(signals[key], str):
            try:
                if 'rating' in key:
                    signals[key] = float(signals[key])
                else:
                    signals[key] = int(signals[key])
            except:
                signals[key] = None
    
    # Ensure sentiment distribution exists and sums correctly
    if 'sentiment_distribution' not in signals or signals['sentiment_distribution'] is None:
        signals['sentiment_distribution'] = {
            'positive': 0.5,
            'neutral': 0.3,
            'negative': 0.2
        }
    elif isinstance(signals['sentiment_distribution'], dict):
        sent = signals['sentiment_distribution']
        
        # Convert string numbers and handle None values
        for k in ['positive', 'neutral', 'negative']:
            if k not in sent or sent[k] is None:
                sent[k] = 0.0
            elif isinstance(sent[k], str):
                try:
                    sent[k] = float(sent[k])
                except:
                    sent[k] = 0.0
        
        # Normalize to sum to 1.0
        total = sent.get('positive', 0) + sent.get('neutral', 0) + sent.get('negative', 0)
        if total > 0:
            signals['sentiment_distribution'] = {
                'positive': sent.get('positive', 0) / total,
                'neutral': sent.get('neutral', 0) / total,
                'negative': sent.get('negative', 0) / total
            }
        else:
            # All zeros - use neutral default
            signals['sentiment_distribution'] = {
                'positive': 0.5,
                'neutral': 0.3,
                'negative': 0.2
            }
    
    return signals


def create_fallback_signals(description: str, reviews: str) -> Dict[str, Any]:
    """Create reasonable fallback signals when LLM fails."""
    
    desc_lower = description.lower()
    reviews_lower = reviews.lower()
    
    # Simple rule-based extraction
    cpu_tier = "B"  # Default mid-range
    if any(x in desc_lower for x in ['i9', 'ryzen 9', '14900']):
        cpu_tier = "S"
    elif any(x in desc_lower for x in ['i7', 'ryzen 7']):
        cpu_tier = "A"
    elif any(x in desc_lower for x in ['i3', 'ryzen 3', 'celeron', 'pentium']):
        cpu_tier = "C"
    elif any(x in desc_lower for x in ['a4', 'old', '2018', '8250u']):
        cpu_tier = "D"
    
    gpu_tier = "Integrated"
    if any(x in desc_lower for x in ['4090', '4080']):
        gpu_tier = "S"
    elif any(x in desc_lower for x in ['4070', '3080']):
        gpu_tier = "A"
    elif any(x in desc_lower for x in ['4060', '3060']):
        gpu_tier = "B"
    elif any(x in desc_lower for x in ['rtx', 'radeon rx']):
        gpu_tier = "C"
    
    # Extract RAM
    ram_gb = 16  # Default
    if '32gb' in desc_lower or '36gb' in desc_lower:
        ram_gb = 32
    elif '4gb' in desc_lower:
        ram_gb = 4
    elif '8gb' in desc_lower:
        ram_gb = 8
    
    # Extract storage
    storage_gb = 512  # Default
    if '1tb' in desc_lower:
        storage_gb = 1024
    elif '128gb' in desc_lower or '128' in desc_lower:
        storage_gb = 128
    elif '256gb' in desc_lower:
        storage_gb = 256
    
    # Display tier
    display_tier = "B"
    if '4k' in desc_lower or 'oled' in desc_lower or 'retina xdr' in desc_lower:
        display_tier = "A"
    elif '720p' in desc_lower or 'tn' in desc_lower:
        display_tier = "C"
    
    # Brand
    brand_reliability = "Medium"
    if any(x in desc_lower for x in ['dell xps', 'macbook', 'thinkpad', 'asus rog']):
        brand_reliability = "High"
    elif any(x in desc_lower for x in ['generic', 'budget']):
        brand_reliability = "Low"
    
    # Sentiment from reviews
    positive_count = reviews_lower.count('5/5') + reviews_lower.count('great') + reviews_lower.count('excellent')
    negative_count = reviews_lower.count('1/5') + reviews_lower.count('2/5') + reviews_lower.count('slow') + reviews_lower.count('bad')
    neutral_count = reviews_lower.count('3/5') + reviews_lower.count('okay')
    
    total = max(positive_count + negative_count + neutral_count, 1)
    
    return {
        "cpu_tier": cpu_tier,
        "gpu_tier": gpu_tier,
        "ram_gb": ram_gb,
        "storage_gb": storage_gb,
        "display_tier": display_tier,
        "brand_reliability": brand_reliability,
        "sentiment_distribution": {
            "positive": positive_count / total,
            "neutral": neutral_count / total,
            "negative": negative_count / total
        },
        "review_count": max(positive_count + negative_count + neutral_count, 1),
        "average_rating": 3.0 if negative_count > positive_count else 4.0
    }


# ============================================================================
# TIER CLASSIFICATION GUIDELINES (FOR DOCUMENTATION)
# ============================================================================

"""
CPU Tier Classification Guidelines:
- S: Latest-gen flagship (Intel i9-14900K, AMD Ryzen 9 7950X3D)
- A: High-end current-gen (Intel i7-14700K, AMD Ryzen 7 7800X3D)
- B: Mid-range (Intel i5-14600K, AMD Ryzen 5 7600X)
- C: Entry-level (Intel i3, AMD Ryzen 3)
- D: Budget/older gen

GPU Tier Classification Guidelines:
- S: RTX 4090, RX 7900 XTX
- A: RTX 4080, RX 7900 XT
- B: RTX 4070, RX 7800 XT
- C: RTX 4060, RX 7600
- D: GTX 1660, older budget cards
- Integrated: iGPU (Intel UHD, AMD Radeon Graphics)

Display Tier Classification Guidelines:
- A: 4K, 144Hz+, HDR, OLED/Mini-LED
- B: 1440p, 120Hz+, IPS
- C: 1080p, 60Hz, TN/basic IPS

Brand Reliability Classification Guidelines:
- High: Dell XPS, Apple MacBook, ThinkPad, ASUS ROG
- Medium: HP Pavilion, Acer Aspire, MSI
- Low: Generic/unknown brands, frequent complaint history
"""
