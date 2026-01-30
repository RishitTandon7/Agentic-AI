"""
LLM as Judge - Configuration Module
IEEE A* Conference Submission Artifact

This module contains all deterministic scoring matrices, formulas, and constants.
NO LLM CALLS OR HEURISTICS ARE ALLOWED IN THIS MODULE.

All values are fixed and based on the research methodology defined in the paper.
"""

from typing import Dict, Optional

# ============================================================================
# TIER SCORING MATRICES (DETERMINISTIC MAPPINGS)
# ============================================================================

CPU_TIER_SCORES: Dict[str, float] = {
    "S": 1.00,
    "A": 0.85,
    "B": 0.70,
    "C": 0.50,
    "D": 0.30,
}

GPU_TIER_SCORES: Dict[str, float] = {
    "S": 1.00,
    "A": 0.90,
    "B": 0.75,
    "C": 0.55,
    "D": 0.35,
    "Integrated": 0.20,
}

DISPLAY_TIER_SCORES: Dict[str, float] = {
    "A": 1.00,
    "B": 0.75,
    "C": 0.50,
}

BRAND_RELIABILITY_SCORES: Dict[str, float] = {
    "High": 1.00,
    "Medium": 0.70,
    "Low": 0.40,
}

# ============================================================================
# RAM SCORING (NORMALIZED)
# ============================================================================

def compute_ram_score(ram_gb: Optional[int]) -> float:
    """
    Compute RAM score using min-max normalization.
    
    Reference range: 4GB (min) to 64GB (max)
    Formula: (ram - min) / (max - min), capped at [0, 1]
    
    Args:
        ram_gb: RAM in gigabytes
        
    Returns:
        Normalized score [0, 1]
    """
    if ram_gb is None:
        return 0.0
    
    MIN_RAM = 4
    MAX_RAM = 64
    
    normalized = (ram_gb - MIN_RAM) / (MAX_RAM - MIN_RAM)
    return max(0.0, min(1.0, normalized))


# ============================================================================
# STORAGE SCORING (NORMALIZED)
# ============================================================================

def compute_storage_score(storage_gb: Optional[int]) -> float:
    """
    Compute storage score using min-max normalization.
    
    Reference range: 128GB (min) to 2048GB (max)
    Formula: (storage - min) / (max - min), capped at [0, 1]
    
    Args:
        storage_gb: Storage in gigabytes
        
    Returns:
        Normalized score [0, 1]
    """
    if storage_gb is None:
        return 0.0
    
    MIN_STORAGE = 128
    MAX_STORAGE = 2048
    
    normalized = (storage_gb - MIN_STORAGE) / (MAX_STORAGE - MIN_STORAGE)
    return max(0.0, min(1.0, normalized))


# ============================================================================
# PRICE DEVIATION SCORING
# ============================================================================

def compute_price_score(actual_price: float, market_price: float) -> float:
    """
    Compute price score based on deviation from market price.
    
    Formula: abs(actual - market) / market
    
    Deviation Thresholds:
    - ≤ 5%:  1.00
    - ≤ 10%: 0.85
    - ≤ 25%: 0.60
    - > 25%: 0.30
    
    Args:
        actual_price: Actual product price
        market_price: Market average price
        
    Returns:
        Price score [0.30, 1.00]
    """
    if market_price <= 0:
        return 0.0
    
    deviation = abs(actual_price - market_price) / market_price
    
    if deviation <= 0.05:
        return 1.00
    elif deviation <= 0.10:
        return 0.85
    elif deviation <= 0.25:
        return 0.60
    else:
        return 0.30


# ============================================================================
# REVIEW SENTIMENT SCORING
# ============================================================================

def compute_review_score(
    sentiment_distribution: Dict[str, float],
    review_count: Optional[int] = None,
    use_confidence_scaling: bool = False
) -> float:
    """
    Compute review score from sentiment distribution.
    
    Base Formula: 
        ReviewScore = PositiveSentimentRatio
    
    Optional Confidence Scaling (if use_confidence_scaling=True):
        ReviewScore = PositiveRatio × min(1, log10(N) / 3)
        where N = number of reviews
    
    Args:
        sentiment_distribution: Dict with keys 'positive', 'neutral', 'negative'
        review_count: Number of reviews (required if confidence scaling enabled)
        use_confidence_scaling: Whether to apply confidence scaling
        
    Returns:
        Review score [0, 1]
    """
    positive_ratio = sentiment_distribution.get("positive", 0.0)
    
    if not use_confidence_scaling:
        return positive_ratio
    
    # Apply confidence scaling
    if review_count is None or review_count <= 0:
        return positive_ratio
    
    import math
    confidence_factor = min(1.0, math.log10(review_count) / 3.0)
    return positive_ratio * confidence_factor


# ============================================================================
# SPECIFICATION SCORE AGGREGATION
# ============================================================================

SPEC_WEIGHTS = {
    "cpu": 0.30,
    "gpu": 0.30,
    "ram": 0.20,
    "storage": 0.10,
    "display": 0.10,
}

def compute_specification_score(component_scores: Dict[str, float]) -> float:
    """
    Aggregate component specification scores using fixed weights.
    
    Formula:
        SpecScore = 0.30×CPU + 0.30×GPU + 0.20×RAM + 0.10×Storage + 0.10×Display
    
    Args:
        component_scores: Dict containing individual component scores
        
    Returns:
        Weighted specification score [0, 1]
    """
    spec_score = (
        SPEC_WEIGHTS["cpu"] * component_scores.get("cpu", 0.0) +
        SPEC_WEIGHTS["gpu"] * component_scores.get("gpu", 0.0) +
        SPEC_WEIGHTS["ram"] * component_scores.get("ram", 0.0) +
        SPEC_WEIGHTS["storage"] * component_scores.get("storage", 0.0) +
        SPEC_WEIGHTS["display"] * component_scores.get("display", 0.0)
    )
    return spec_score


# ============================================================================
# FINAL SCORE AGGREGATION (MASTER FORMULA)
# ============================================================================

FINAL_WEIGHTS = {
    "price": 0.25,
    "specs": 0.30,
    "brand": 0.20,
    "reviews": 0.15,
    "marketplace": 0.10,
}

def compute_final_score(component_scores: Dict[str, float]) -> float:
    """
    Compute final aggregate score using master formula.
    
    Formula:
        FinalScore = 0.25×Price + 0.30×Specs + 0.20×Brand + 0.15×Reviews + 0.10×Marketplace
    
    Args:
        component_scores: Dict containing all component scores
        
    Returns:
        Final score [0, 1]
    """
    final_score = (
        FINAL_WEIGHTS["price"] * component_scores.get("price", 0.0) +
        FINAL_WEIGHTS["specs"] * component_scores.get("specs", 0.0) +
        FINAL_WEIGHTS["brand"] * component_scores.get("brand", 0.0) +
        FINAL_WEIGHTS["reviews"] * component_scores.get("reviews", 0.0) +
        FINAL_WEIGHTS["marketplace"] * component_scores.get("marketplace", 0.0)
    )
    return final_score


def compute_purchase_probability(final_score: float) -> float:
    """
    Convert final score to purchase probability percentage.
    
    Formula:
        PurchaseProbability = FinalScore × 100
    
    Args:
        final_score: Final aggregate score [0, 1]
        
    Returns:
        Purchase probability [0, 100]
    """
    return final_score * 100.0


# ============================================================================
# JSON SCHEMA DEFINITION (FOR VALIDATION)
# ============================================================================

ALLOWED_VALUES = {
    "cpu_tier": ["S", "A", "B", "C", "D", None],
    "gpu_tier": ["S", "A", "B", "C", "D", "Integrated", None],
    "display_tier": ["A", "B", "C", None],
    "brand_reliability": ["High", "Medium", "Low", None],
}

def validate_signal_schema(signals: Dict) -> bool:
    """
    Validate that extracted signals conform to the strict schema.
    
    Args:
        signals: Extracted signal dictionary from LLM
        
    Returns:
        True if valid, False otherwise
    """
    # Check CPU tier
    if signals.get("cpu_tier") not in ALLOWED_VALUES["cpu_tier"]:
        return False
    
    # Check GPU tier
    if signals.get("gpu_tier") not in ALLOWED_VALUES["gpu_tier"]:
        return False
    
    # Check display tier
    if signals.get("display_tier") not in ALLOWED_VALUES["display_tier"]:
        return False
    
    # Check brand reliability
    if signals.get("brand_reliability") not in ALLOWED_VALUES["brand_reliability"]:
        return False
    
    # Check sentiment distribution
    sentiment = signals.get("sentiment_distribution", {})
    if not isinstance(sentiment, dict):
        return False
    
    # Sentiment must sum to approximately 1.0 (allow small floating point error)
    total = sentiment.get("positive", 0) + sentiment.get("neutral", 0) + sentiment.get("negative", 0)
    if abs(total - 1.0) > 0.01:
        return False
    
    return True
