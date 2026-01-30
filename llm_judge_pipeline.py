"""
LLM as Judge - Complete Evaluation Pipeline
IEEE A* Conference Submission Artifact

This is the main entry point for the evaluation system.
It orchestrates the three-layer architecture:
1. Semantic Extraction (LLM-based)
2. Deterministic Scoring
3. Aggregation

This module implements the public API for product evaluation.
"""

from typing import Dict, Any, Optional
from llm_judge_extraction import extract_signals
from llm_judge_scoring import (
    compute_component_scores,
    aggregate_final_score,
    get_score_breakdown,
)


# ============================================================================
# MAIN EVALUATION PIPELINE
# ============================================================================

def evaluate_product(
    product_description: str,
    customer_reviews: str,
    actual_price: Optional[float] = None,
    market_price: Optional[float] = None,
    marketplace_score: float = 0.75,
    use_review_confidence_scaling: bool = False,
    ollama_model: str = "llama3.2",
    ollama_url: str = "http://localhost:11434/api/generate",
    include_breakdown: bool = False
) -> Dict[str, Any]:
    """
    Complete product evaluation pipeline.
    
    This function orchestrates the full evaluation process:
    1. Extract signals using LLM (classification only)
    2. Compute component scores deterministically
    3. Aggregate final score and purchase probability
    
    The system guarantees:
    - Reproducibility: Same input → same output
    - Modularity: LLM can be swapped without changing scoring
    - Testability: All scoring logic is deterministic and unit-testable
    
    Args:
        product_description: Raw product description text
        customer_reviews: Raw customer review text
        actual_price: Actual product price (optional)
        market_price: Market average price (optional)
        marketplace_score: Marketplace reputation score [0, 1]
        use_review_confidence_scaling: Whether to apply confidence scaling to reviews
        ollama_model: Ollama model to use (default: llama3.2)
        ollama_url: Ollama API endpoint
        include_breakdown: If True, include detailed scoring breakdown
        
    Returns:
        Evaluation result dictionary:
        {
            "signals": {...},              # Extracted signals from LLM
            "component_scores": {...},     # Individual component scores
            "final_score": float,          # Final aggregate score [0, 1]
            "purchase_probability": float, # Purchase probability [0, 100]
            "breakdown": {...}             # Optional: detailed breakdown
        }
        
    Raises:
        ValueError: If LLM fails to extract valid signals
        RuntimeError: If Ollama API is unreachable
    """
    # ========================================================================
    # LAYER 1: Semantic Extraction (LLM-based)
    # ========================================================================
    
    print("[1/3] Extracting signals from LLM...")
    signals = extract_signals(
        product_description=product_description,
        customer_reviews=customer_reviews,
        model=ollama_model,
        ollama_url=ollama_url
    )
    print(f"[OK] Signals extracted")
    
    # ========================================================================
    # LAYER 2: Deterministic Scoring
    # ========================================================================
    
    print("[2/3] Computing component scores...")
    component_scores = compute_component_scores(
        signals=signals,
        actual_price=actual_price,
        market_price=market_price,
        marketplace_score=marketplace_score,
        use_review_confidence_scaling=use_review_confidence_scaling
    )
    print(f"[OK] Component scores computed")
    
    # ========================================================================
    # LAYER 3: Aggregation
    # ========================================================================
    
    print("[3/3] Aggregating final score...")
    final_result = aggregate_final_score(component_scores)
    print(f"[OK] Final score: {final_result['final_score']:.4f}")
    print(f"[OK] Purchase probability: {final_result['purchase_probability']:.2f}%")
    
    # ========================================================================
    # Assemble Output
    # ========================================================================
    
    output = {
        "signals": signals,
        "component_scores": component_scores,
        "final_score": final_result["final_score"],
        "purchase_probability": final_result["purchase_probability"],
    }
    
    if include_breakdown:
        output["breakdown"] = get_score_breakdown(
            signals=signals,
            component_scores=component_scores,
            final_result=final_result
        )
    
    return output


# ============================================================================
# BATCH EVALUATION (FOR ABLATION STUDIES)
# ============================================================================

def evaluate_product_batch(
    products: list[Dict[str, Any]],
    **kwargs
) -> list[Dict[str, Any]]:
    """
    Evaluate multiple products in batch.
    
    Useful for ablation studies, precision/recall calculation, and benchmarking.
    
    Args:
        products: List of product data dictionaries, each containing:
            - product_description: str
            - customer_reviews: str
            - actual_price: float (optional)
            - market_price: float (optional)
        **kwargs: Additional arguments to pass to evaluate_product()
        
    Returns:
        List of evaluation results, one per product
    """
    results = []
    
    for i, product in enumerate(products):
        print(f"\n{'='*60}")
        print(f"Evaluating product {i+1}/{len(products)}")
        print(f"{'='*60}")
        
        result = evaluate_product(
            product_description=product["product_description"],
            customer_reviews=product["customer_reviews"],
            actual_price=product.get("actual_price"),
            market_price=product.get("market_price"),
            **kwargs
        )
        
        results.append(result)
    
    return results


# ============================================================================
# DETERMINISM VERIFICATION
# ============================================================================

def verify_determinism(
    product_description: str,
    customer_reviews: str,
    num_runs: int = 5,
    **kwargs
) -> Dict[str, Any]:
    """
    Verify that the system produces identical outputs for identical inputs.
    
    This is critical for reproducibility in research.
    
    Args:
        product_description: Product description to test
        customer_reviews: Customer reviews to test
        num_runs: Number of evaluation runs to perform
        **kwargs: Additional arguments to pass to evaluate_product()
        
    Returns:
        Dictionary containing:
        {
            "is_deterministic": bool,
            "all_scores": list[float],
            "variance": float
        }
    """
    print(f"Running {num_runs} evaluation passes to verify determinism...")
    
    scores = []
    
    for i in range(num_runs):
        result = evaluate_product(
            product_description=product_description,
            customer_reviews=customer_reviews,
            **kwargs
        )
        scores.append(result["final_score"])
        print(f"  Run {i+1}: {result['final_score']:.6f}")
    
    # Check if all scores are identical
    is_deterministic = len(set(scores)) == 1
    variance = max(scores) - min(scores) if scores else 0.0
    
    print(f"\nDeterminism check: {'[PASS]' if is_deterministic else '[FAIL]'}")
    print(f"Variance: {variance}")
    
    return {
        "is_deterministic": is_deterministic,
        "all_scores": scores,
        "variance": variance,
    }
