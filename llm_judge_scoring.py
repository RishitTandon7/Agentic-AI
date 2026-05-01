"""
LLM as Judge - Deterministic Scoring Layer
IEEE A* Conference Submission Artifact

This module implements ALL scoring logic using fixed matrices and formulas.
NO LLM CALLS ARE ALLOWED IN THIS MODULE.

All functions are pure and deterministic.
Identical inputs ALWAYS produce identical outputs.
"""

from typing import Dict, Any, Optional
from llm_judge_config import (
    CPU_TIER_SCORES,
    GPU_TIER_SCORES,
    DISPLAY_TIER_SCORES,
    BRAND_RELIABILITY_SCORES,
    compute_ram_score,
    compute_storage_score,
    compute_price_score,
    compute_review_score,
    compute_specification_score,
    compute_final_score,
    compute_purchase_probability,
)


# ============================================================================
# COMPONENT SCORE COMPUTATION (DETERMINISTIC)
# ============================================================================

def compute_component_scores(
    signals: Dict[str, Any],
    actual_price: Optional[float] = None,
    market_price: Optional[float] = None,
    marketplace_score: float = 0.75,  # Default if not provided
    use_review_confidence_scaling: bool = False
) -> Dict[str, float]:
    """
    Compute all component scores from extracted signals.
    
    This function is COMPLETELY DETERMINISTIC and contains NO LLM calls.
    All scoring is based on fixed matrices and formulas.
    
    Args:
        signals: Extracted signals from LLM (from extract_signals())
        actual_price: Actual product price (optional, for price scoring)
        market_price: Market average price (optional, for price scoring)
        marketplace_score: Marketplace reputation score [0, 1] (default: 0.75)
        use_review_confidence_scaling: Whether to scale review score by confidence
        
    Returns:
        Dictionary containing all component scores:
        {
            "cpu": float,
            "gpu": float,
            "ram": float,
            "storage": float,
            "display": float,
            "specs": float,  # aggregated spec score
            "brand": float,
            "reviews": float,
            "price": float,
            "marketplace": float,
        }
    """
    component_scores = {}
    
    # ========================================================================
    # Individual Component Scores
    # ========================================================================
    
    # CPU Score
    cpu_tier = signals.get("cpu_tier")
    component_scores["cpu"] = CPU_TIER_SCORES.get(cpu_tier, 0.0)
    
    # GPU Score
    gpu_tier = signals.get("gpu_tier")
    component_scores["gpu"] = GPU_TIER_SCORES.get(gpu_tier, 0.0)
    
    # RAM Score
    ram_gb = signals.get("ram_gb")
    component_scores["ram"] = compute_ram_score(ram_gb)
    
    # Storage Score
    storage_gb = signals.get("storage_gb")
    component_scores["storage"] = compute_storage_score(storage_gb)
    
    # Display Score
    display_tier = signals.get("display_tier")
    component_scores["display"] = DISPLAY_TIER_SCORES.get(display_tier, 0.0)
    
    # ========================================================================
    # Aggregated Specification Score
    # ========================================================================
    
    component_scores["specs"] = compute_specification_score(component_scores)
    
    # ========================================================================
    # Brand Reliability Score
    # ========================================================================
    
    brand_reliability = signals.get("brand_reliability")
    component_scores["brand"] = BRAND_RELIABILITY_SCORES.get(brand_reliability, 0.0)
    
    # ========================================================================
    # Review Score
    # ========================================================================
    
    sentiment_dist = signals.get("sentiment_distribution", {})
    review_count = signals.get("review_count")
    
    component_scores["reviews"] = compute_review_score(
        sentiment_distribution=sentiment_dist,
        review_count=review_count,
        use_confidence_scaling=use_review_confidence_scaling
    )
    
    # ========================================================================
    # Price Score
    # ========================================================================
    
    if actual_price is not None and market_price is not None:
        component_scores["price"] = compute_price_score(actual_price, market_price)
    else:
        component_scores["price"] = 0.0  # Missing price data
    
    # ========================================================================
    # Marketplace Score
    # ========================================================================
    
    component_scores["marketplace"] = marketplace_score
    
    return component_scores


# ============================================================================
# FINAL SCORE AGGREGATION (DETERMINISTIC)
# ============================================================================

def aggregate_final_score(component_scores: Dict[str, float], category: str = "Laptop") -> Dict[str, float]:
    """
    Aggregate component scores into final score and purchase probability.
    
    This function implements the master formula with fixed weights.
    It is COMPLETELY DETERMINISTIC.
    
    Args:
        component_scores: All component scores from compute_component_scores()
        category: Product category (for weighting)
        
    Returns:
        Dictionary containing:
        {
            "final_score": float [0, 1],
            "purchase_probability": float [0, 100]
        }
    """
    final_score = compute_final_score(component_scores, category)
    purchase_probability = compute_purchase_probability(final_score)
    
    return {
        "final_score": final_score,
        "purchase_probability": purchase_probability,
    }


# ============================================================================
# TRANSPARENCY UTILITIES (FOR REPRODUCIBILITY)
# ============================================================================

def get_score_breakdown(
    signals: Dict[str, Any],
    component_scores: Dict[str, float],
    final_result: Dict[str, float],
    category: str = "Laptop"
) -> Dict[str, Any]:
    """
    Generate a detailed breakdown of all scoring steps for transparency.
    
    This is useful for reproducibility checks and ablation studies.
    
    Args:
        signals: Extracted signals
        component_scores: Component scores
        final_result: Final aggregated scores
        
    Returns:
        Complete scoring breakdown with all intermediate values
    """
    from llm_judge_config import SPEC_WEIGHTS, CATEGORY_WEIGHTS
    
    # Map high-level categories to weights
    if category in ["Earphones", "Hair dryer", "Headphones", "Mobile"]:
        curr_weights = CATEGORY_WEIGHTS.get("Electronics")
    elif category in ["Hair oil", "Bracelet", "Fry pan", "Lifestyle", "Fashion"]:
        curr_weights = CATEGORY_WEIGHTS.get("Lifestyle")
    else:
        curr_weights = CATEGORY_WEIGHTS.get(category, CATEGORY_WEIGHTS["Laptop"])

    breakdown = {
        "extracted_signals": signals,
        "component_scores": component_scores,
        "specification_aggregation": {
            "weights": SPEC_WEIGHTS,
            "weighted_components": {
                "cpu": SPEC_WEIGHTS["cpu"] * component_scores.get("cpu", 0.0),
                "gpu": SPEC_WEIGHTS["gpu"] * component_scores.get("gpu", 0.0),
                "ram": SPEC_WEIGHTS["ram"] * component_scores.get("ram", 0.0),
                "storage": SPEC_WEIGHTS["storage"] * component_scores.get("storage", 0.0),
                "display": SPEC_WEIGHTS["display"] * component_scores.get("display", 0.0),
            },
            "total": component_scores.get("specs", 0.0),
        },
        "final_aggregation": {
            "weights": curr_weights,
            "weighted_components": {
                "price": curr_weights["price"] * component_scores.get("price", 0.0),
                "specs": curr_weights["specs"] * component_scores.get("specs", 0.0),
                "brand": curr_weights["brand"] * component_scores.get("brand", 0.0),
                "reviews": curr_weights["reviews"] * component_scores.get("reviews", 0.0),
                "marketplace": curr_weights["marketplace"] * component_scores.get("marketplace", 0.0),
            },
            "total": final_result["final_score"],
        },
        "final_output": final_result,
    }
    
    return breakdown
