"""
LLM as Judge - Metrics Evaluation Example
IEEE A* Conference Submission Artifact

This script demonstrates how to evaluate the system using standard metrics:
- Precision, Recall, F1 Score
- ROC-AUC
- Threshold optimization
- Cross-validation

This is essential for validating the system in your research paper.
"""

from llm_judge_pipeline import evaluate_product
from llm_judge_metrics import (
    evaluate_with_threshold,
    find_optimal_threshold,
    print_classification_report,
    compute_cross_validation_metrics,
    print_cv_metrics
)
import json


# ============================================================================
# EXAMPLE DATASET (Ground Truth)
# ============================================================================

# In a real study, you would have 100+ products with human-labeled ground truth
# Here we show a small example dataset

EXAMPLE_DATASET = [
    {
        "product_description": """
        Dell XPS 15 (2024)
        Intel Core i9-14900HK, RTX 4070, 32GB RAM, 1TB SSD
        15.6" 4K OLED display, Premium build quality
        """,
        "customer_reviews": """
        Review 1 (5/5): Outstanding laptop, best I've ever owned.
        Review 2 (5/5): Incredible performance and display quality.
        Review 3 (4/5): Great laptop but runs hot under load.
        Review 4 (5/5): Worth every penny for creative work.
        """,
        "actual_price": 2799.99,
        "market_price": 2699.00,
        "ground_truth_label": 1,  # Should recommend (good deal)
        "product_name": "Dell XPS 15"
    },
    {
        "product_description": """
        Generic Laptop X200
        Intel Celeron, Integrated Graphics, 4GB RAM, 128GB eMMC
        15.6" 1366x768 TN display, Plastic build
        """,
        "customer_reviews": """
        Review 1 (2/5): Very slow, struggles with basic tasks.
        Review 2 (1/5): Terrible display quality, cheap build.
        Review 3 (2/5): Barely usable, not recommended.
        """,
        "actual_price": 299.99,
        "market_price": 249.99,
        "ground_truth_label": 0,  # Should not recommend (bad deal)
        "product_name": "Generic Laptop X200"
    },
    {
        "product_description": """
        MacBook Pro 16" (2024)
        M3 Max chip, 36GB RAM, 1TB SSD
        Liquid Retina XDR display, Premium aluminum build
        """,
        "customer_reviews": """
        Review 1 (5/5): Best laptop ever, incredible battery life.
        Review 2 (5/5): Worth the price, outstanding performance.
        Review 3 (5/5): Perfect for professional work.
        Review 4 (4/5): Expensive but worth it.
        """,
        "actual_price": 3499.00,
        "market_price": 3499.00,
        "ground_truth_label": 1,  # Should recommend
        "product_name": "MacBook Pro 16"
    },
    {
        "product_description": """
        Budget Laptop B100
        AMD A4, Integrated Graphics, 8GB RAM, 256GB SSD
        14" 1080p display, Basic build quality
        """,
        "customer_reviews": """
        Review 1 (3/5): Okay for basic tasks, nothing special.
        Review 2 (3/5): Works fine for web browsing.
        Review 3 (2/5): Slow performance, mediocre display.
        """,
        "actual_price": 599.99,
        "market_price": 449.99,
        "ground_truth_label": 0,  # Should not recommend (overpriced)
        "product_name": "Budget Laptop B100"
    },
    {
        "product_description": """
        ASUS ROG Strix G16
        Intel i7-13650HX, RTX 4060, 16GB RAM, 512GB SSD
        16" FHD 165Hz display, Gaming-focused design
        """,
        "customer_reviews": """
        Review 1 (4/5): Great gaming laptop, good value.
        Review 2 (5/5): Runs all games smoothly, recommended.
        Review 3 (4/5): Solid performance for the price.
        """,
        "actual_price": 1199.99,
        "market_price": 1349.00,
        "ground_truth_label": 1,  # Should recommend (good price)
        "product_name": "ASUS ROG Strix G16"
    },
    {
        "product_description": """
        Old Laptop 2018
        Intel i5-8250U, Intel UHD 620, 8GB RAM, 256GB HDD
        15.6" 1080p display, Used condition
        """,
        "customer_reviews": """
        Review 1 (2/5): Too old, very slow.
        Review 2 (1/5): Not worth it in 2024.
        Review 3 (2/5): Outdated, poor performance.
        """,
        "actual_price": 399.99,
        "market_price": 299.99,
        "ground_truth_label": 0,  # Should not recommend
        "product_name": "Old Laptop 2018"
    },
]


# ============================================================================
# EXAMPLE 1: Basic Evaluation with Fixed Threshold
# ============================================================================

def example_basic_evaluation():
    """Evaluate the system using a fixed threshold (50%)."""
    
    print("\n" + "█"*80)
    print("EXAMPLE 1: Basic Evaluation with Fixed Threshold")
    print("█"*80 + "\n")
    
    # Run evaluation on all products
    print("Running evaluation on dataset...")
    predictions = []
    
    for i, product in enumerate(EXAMPLE_DATASET):
        print(f"\nEvaluating product {i+1}/{len(EXAMPLE_DATASET)}: {product['product_name']}")
        
        try:
            result = evaluate_product(
                product_description=product['product_description'],
                customer_reviews=product['customer_reviews'],
                actual_price=product['actual_price'],
                market_price=product['market_price'],
                marketplace_score=0.85
            )
            
            predictions.append({
                'product_name': product['product_name'],
                'purchase_probability': result['purchase_probability'],
                'final_score': result['final_score']
            })
            
            print(f"  → Purchase Probability: {result['purchase_probability']:.2f}%")
            
        except Exception as e:
            print(f"  ✗ Error: {e}")
            # Use default score if LLM fails
            predictions.append({
                'product_name': product['product_name'],
                'purchase_probability': 50.0,  # Neutral
                'final_score': 0.5
            })
    
    # Prepare ground truth
    ground_truth = [
        {'label': product['ground_truth_label']}
        for product in EXAMPLE_DATASET
    ]
    
    # Evaluate with threshold = 50%
    print("\n" + "-"*80)
    print("Computing metrics with threshold = 50%...")
    print("-"*80)
    
    report = evaluate_with_threshold(ground_truth, predictions, threshold=50.0)
    print_classification_report(report)
    
    return ground_truth, predictions


# ============================================================================
# EXAMPLE 2: Threshold Optimization
# ============================================================================

def example_threshold_optimization(ground_truth, predictions):
    """Find optimal threshold that maximizes F1 score."""
    
    print("\n" + "█"*80)
    print("EXAMPLE 2: Threshold Optimization")
    print("█"*80 + "\n")
    
    # Optimize for F1 score
    print("Optimizing threshold for F1 score...")
    optimal_threshold, best_f1 = find_optimal_threshold(
        ground_truth,
        predictions,
        metric='f1'
    )
    
    print(f"\n✓ Optimal threshold: {optimal_threshold:.1f}%")
    print(f"✓ Best F1 score: {best_f1:.4f}")
    
    # Evaluate with optimal threshold
    report = evaluate_with_threshold(ground_truth, predictions, threshold=optimal_threshold)
    print_classification_report(report)
    
    # Compare different thresholds
    print("\n" + "-"*80)
    print("Comparison of Different Thresholds")
    print("-"*80)
    print("\nThreshold    Precision  Recall     F1 Score   Accuracy")
    print("-"*60)
    
    for threshold in [30, 40, 50, 60, 70]:
        report = evaluate_with_threshold(ground_truth, predictions, threshold=threshold)
        print(f"{threshold:3d}%         {report['precision']:.4f}     "
              f"{report['recall']:.4f}     {report['f1_score']:.4f}     "
              f"{report['accuracy']:.4f}")
    
    print("-"*60 + "\n")


# ============================================================================
# EXAMPLE 3: Detailed Metrics Analysis
# ============================================================================

def example_detailed_analysis(ground_truth, predictions):
    """Show detailed breakdown of predictions and errors."""
    
    print("\n" + "█"*80)
    print("EXAMPLE 3: Detailed Prediction Analysis")
    print("█"*80 + "\n")
    
    threshold = 50.0
    
    print(f"Analyzing predictions with threshold = {threshold}%\n")
    print("-"*80)
    print("Product                    Score   Pred   Actual   Result")
    print("-"*80)
    
    for i, (product, pred, truth) in enumerate(zip(EXAMPLE_DATASET, predictions, ground_truth)):
        score = pred['purchase_probability']
        predicted_label = 1 if score >= threshold else 0
        actual_label = truth['label']
        
        if predicted_label == actual_label:
            result = "✓ CORRECT"
        else:
            result = "✗ WRONG"
        
        print(f"{product['product_name']:25s} {score:5.1f}%   {predicted_label}      "
              f"{actual_label}      {result}")
    
    print("-"*80 + "\n")


# ============================================================================
# EXAMPLE 4: ROC-AUC Analysis
# ============================================================================

def example_roc_auc_analysis(ground_truth, predictions):
    """Demonstrate ROC-AUC calculation."""
    
    print("\n" + "█"*80)
    print("EXAMPLE 4: ROC-AUC Analysis")
    print("█"*80 + "\n")
    
    from llm_judge_metrics import compute_roc_auc
    
    y_true = [item['label'] for item in ground_truth]
    y_scores = [pred['purchase_probability'] for pred in predictions]
    
    roc_auc = compute_roc_auc(y_true, y_scores)
    
    print(f"ROC-AUC Score: {roc_auc:.4f}\n")
    
    print("Interpretation:")
    if roc_auc >= 0.9:
        print("  ✓ Excellent discrimination (0.9-1.0)")
    elif roc_auc >= 0.8:
        print("  ✓ Good discrimination (0.8-0.9)")
    elif roc_auc >= 0.7:
        print("  • Acceptable discrimination (0.7-0.8)")
    elif roc_auc >= 0.6:
        print("  ⚠ Poor discrimination (0.6-0.7)")
    else:
        print("  ✗ Very poor discrimination (<0.6)")
    
    print("\nNote: ROC-AUC measures the system's ability to rank positive")
    print("examples higher than negative examples, regardless of threshold.\n")


# ============================================================================
# EXAMPLE 5: Summary Statistics for Paper
# ============================================================================

def example_paper_statistics(ground_truth, predictions):
    """Generate statistics suitable for inclusion in research paper."""
    
    print("\n" + "█"*80)
    print("EXAMPLE 5: Statistics for Research Paper")
    print("█"*80 + "\n")
    
    # Find optimal threshold
    optimal_threshold, _ = find_optimal_threshold(ground_truth, predictions, metric='f1')
    
    # Compute metrics at optimal threshold
    report = evaluate_with_threshold(ground_truth, predictions, threshold=optimal_threshold)
    
    # Format for paper
    print("═"*80)
    print("TABLE: Classification Performance Metrics")
    print("═"*80)
    print("\nMetric                    Value        95% CI           N")
    print("-"*80)
    print(f"Precision                 {report['precision']:.4f}       [TBD]          {report['confusion_matrix']['total']}")
    print(f"Recall                    {report['recall']:.4f}       [TBD]          {report['confusion_matrix']['total']}")
    print(f"F1 Score                  {report['f1_score']:.4f}       [TBD]          {report['confusion_matrix']['total']}")
    print(f"Accuracy                  {report['accuracy']:.4f}       [TBD]          {report['confusion_matrix']['total']}")
    print(f"ROC-AUC                   {report['roc_auc']:.4f}       [TBD]          {report['confusion_matrix']['total']}")
    print(f"Optimal Threshold         {optimal_threshold:.1f}%        N/A            N/A")
    print("="*80)
    
    print("\nNote: CI (Confidence Intervals) would be computed via bootstrap")
    print("with a larger dataset (100+ samples recommended).\n")
    
    # LaTeX table format
    print("\nLaTeX Table Format:")
    print("-"*80)
    print(r"\begin{table}[h]")
    print(r"\centering")
    print(r"\caption{Classification Performance Metrics}")
    print(r"\begin{tabular}{lcc}")
    print(r"\hline")
    print(r"Metric & Value & N \\")
    print(r"\hline")
    print(f"Precision & {report['precision']:.4f} & {report['confusion_matrix']['total']} \\\\")
    print(f"Recall & {report['recall']:.4f} & {report['confusion_matrix']['total']} \\\\")
    print(f"F1 Score & {report['f1_score']:.4f} & {report['confusion_matrix']['total']} \\\\")
    print(f"ROC-AUC & {report['roc_auc']:.4f} & {report['confusion_matrix']['total']} \\\\")
    print(r"\hline")
    print(r"\end{tabular}")
    print(r"\end{table}")
    print("-"*80 + "\n")


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    print("\n" + "█"*80)
    print("LLM AS JUDGE - METRICS EVALUATION DEMONSTRATION")
    print("IEEE A* Conference Submission Artifact")
    print("█"*80)
    
    print("\nThis script demonstrates how to evaluate the system using")
    print("standard classification metrics for your research paper.\n")
    
    print("⚠ NOTE: Ollama must be running with llama3.2 model!")
    print("If Ollama is not available, the script will use fallback scores.\n")
    
    try:
        # Run examples
        ground_truth, predictions = example_basic_evaluation()
        example_threshold_optimization(ground_truth, predictions)
        example_detailed_analysis(ground_truth, predictions)
        example_roc_auc_analysis(ground_truth, predictions)
        example_paper_statistics(ground_truth, predictions)
        
        print("\n" + "█"*80)
        print("✓ EVALUATION COMPLETE")
        print("█"*80)
        
        print("\nKey Takeaways for Your Paper:")
        print("1. Use evaluate_with_threshold() for standard metrics")
        print("2. Optimize threshold using find_optimal_threshold()")
        print("3. Report ROC-AUC as threshold-independent metric")
        print("4. Include confusion matrix for transparency")
        print("5. Use larger dataset (100+ samples) for final results\n")
        
    except Exception as e:
        print(f"\n✗ Error during evaluation: {e}")
        print("Make sure Ollama is running: ollama serve")
        print("And llama3.2 is installed: ollama pull llama3.2\n")
