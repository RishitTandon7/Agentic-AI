"""
LLM as Judge - Example Usage
IEEE A* Conference Submission Artifact

This script demonstrates how to use the evaluation pipeline.
"""

from llm_judge_pipeline import evaluate_product, verify_determinism
import json


# ============================================================================
# EXAMPLE 1: Single Product Evaluation
# ============================================================================

def example_single_evaluation():
    """Evaluate a single laptop product."""
    
    print("\n" + "="*80)
    print("EXAMPLE 1: Single Product Evaluation")
    print("="*80 + "\n")
    
    # Sample product data
    product_description = """
    Dell XPS 15 (2024)
    
    Processor: Intel Core i9-14900HK (14th Gen, 24 cores, up to 5.8 GHz)
    Graphics: NVIDIA GeForce RTX 4070 (8GB GDDR6)
    RAM: 32GB DDR5-5200MHz
    Storage: 1TB PCIe Gen 4 NVMe SSD
    Display: 15.6" 4K OLED touchscreen, 400 nits, DCI-P3 100%, 60Hz
    
    Build: CNC aluminum chassis, carbon fiber palm rest
    Ports: 2x Thunderbolt 4, 2x USB-C, SD card reader, 3.5mm audio
    Battery: 86Wh, up to 10 hours mixed use
    Weight: 1.96 kg
    """
    
    customer_reviews = """
    Review 1 (5/5): Absolutely phenomenal laptop. Build quality is outstanding, 
    performance is blazing fast for video editing and 3D rendering. The OLED display 
    is stunning. Best laptop I've ever owned.
    
    Review 2 (5/5): Worth every penny. The i9 + RTX 4070 combo handles everything 
    I throw at it. Battery life is decent for such a powerful machine.
    
    Review 3 (4/5): Great laptop overall, but it does run warm under heavy load. 
    Fans can get loud during gaming. Otherwise no complaints.
    
    Review 4 (5/5): Premium in every way. Dell really nailed it with this generation.
    
    Review 5 (4/5): Excellent for work and creative tasks. Slightly heavy for travel 
    but that's expected with this performance tier.
    
    Review 6 (3/5): Good laptop but expensive. Display has minor color shift at angles.
    
    Review 7 (5/5): Best productivity laptop on the market right now.
    """
    
    # Evaluate
    result = evaluate_product(
        product_description=product_description,
        customer_reviews=customer_reviews,
        actual_price=2799.99,
        market_price=2699.00,
        marketplace_score=0.95,  # Amazon, high reputation
        use_review_confidence_scaling=False,
        include_breakdown=True
    )
    
    # Display results
    print("\n" + "-"*80)
    print("EVALUATION RESULTS")
    print("-"*80)
    print(json.dumps(result, indent=2, default=str))


# ============================================================================
# EXAMPLE 2: Determinism Verification
# ============================================================================

def example_determinism_check():
    """Verify that the system is deterministic."""
    
    print("\n" + "="*80)
    print("EXAMPLE 2: Determinism Verification")
    print("="*80 + "\n")
    
    product_description = """
    ASUS ROG Strix G16
    Intel Core i7-13650HX, RTX 4060, 16GB RAM, 512GB SSD
    16" FHD 165Hz display
    """
    
    customer_reviews = """
    Review 1: Great gaming laptop, runs all modern games smoothly.
    Review 2: Good value for money, recommended.
    Review 3: Minor cooling issues but otherwise solid.
    """
    
    result = verify_determinism(
        product_description=product_description,
        customer_reviews=customer_reviews,
        actual_price=1299.99,
        market_price=1349.00,
        num_runs=5
    )
    
    if result["is_deterministic"]:
        print("\n✓ REPRODUCIBILITY VERIFIED")
        print("The system produces identical outputs for identical inputs.")
    else:
        print("\n✗ REPRODUCIBILITY FAILED")
        print(f"Detected variance of {result['variance']}")


# ============================================================================
# EXAMPLE 3: Batch Evaluation (Ablation Study)
# ============================================================================

def example_batch_evaluation():
    """Evaluate multiple products for comparison."""
    
    print("\n" + "="*80)
    print("EXAMPLE 3: Batch Evaluation")
    print("="*80 + "\n")
    
    from llm_judge_pipeline import evaluate_product_batch
    
    products = [
        {
            "product_description": "Dell XPS 15: i9-14900HK, RTX 4070, 32GB RAM, 1TB SSD, 4K OLED",
            "customer_reviews": "Mostly positive reviews, premium build quality.",
            "actual_price": 2799.99,
            "market_price": 2699.00,
        },
        {
            "product_description": "MacBook Pro 16: M3 Max, 36GB RAM, 1TB SSD, Liquid Retina XDR",
            "customer_reviews": "Excellent reviews, best-in-class performance and battery.",
            "actual_price": 3499.00,
            "market_price": 3499.00,
        },
        {
            "product_description": "Lenovo Legion 5: Ryzen 7 7735HS, RTX 4060, 16GB RAM, 512GB SSD",
            "customer_reviews": "Good value, some QC issues reported.",
            "actual_price": 1199.99,
            "market_price": 1299.00,
        },
    ]
    
    results = evaluate_product_batch(
        products=products,
        marketplace_score=0.85
    )
    
    # Compare results
    print("\n" + "-"*80)
    print("COMPARISON RESULTS")
    print("-"*80)
    
    for i, result in enumerate(results):
        print(f"\nProduct {i+1}:")
        print(f"  Final Score: {result['final_score']:.4f}")
        print(f"  Purchase Probability: {result['purchase_probability']:.2f}%")
        print(f"  CPU Tier: {result['signals']['cpu_tier']}")
        print(f"  GPU Tier: {result['signals']['gpu_tier']}")


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    print("\n" + "█"*80)
    print("LLM AS JUDGE - DETERMINISTIC EVALUATION SYSTEM")
    print("IEEE A* Conference Submission Artifact")
    print("█"*80)
    
    # Run examples
    try:
        example_single_evaluation()
    except Exception as e:
        print(f"\n✗ Example 1 failed: {e}")
    
    try:
        example_determinism_check()
    except Exception as e:
        print(f"\n✗ Example 2 failed: {e}")
    
    try:
        example_batch_evaluation()
    except Exception as e:
        print(f"\n✗ Example 3 failed: {e}")
    
    print("\n" + "█"*80)
    print("EXAMPLES COMPLETE")
    print("█"*80 + "\n")
