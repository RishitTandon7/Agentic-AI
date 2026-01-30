"""
Quick Demo: Metrics Calculation (No LLM Required)

This demonstrates how to calculate F1, Precision, Recall, and ROC-AUC
directly from scores without running the full LLM pipeline.
"""

from llm_judge_metrics import (
    compute_classification_report,
    evaluate_with_threshold,
    find_optimal_threshold,
    print_classification_report,
    compute_roc_auc
)


print("\n" + "="*80)
print("QUICK DEMO: Metrics Calculation")
print("="*80 + "\n")

# ============================================================================
# EXAMPLE 1: Direct Metrics Calculation
# ============================================================================

print("EXAMPLE 1: Calculate metrics from ground truth and predictions\n")
print("-"*80)

# Ground truth labels (1 = recommend, 0 = don't recommend)
y_true = [1, 1, 0, 0, 1, 0, 1, 0, 1, 1]

# Predicted labels
y_pred = [1, 1, 0, 1, 1, 0, 0, 0, 1, 1]

# Predicted scores (purchase probabilities)
y_scores = [85.2, 92.1, 32.4, 51.2, 88.5, 28.9, 45.0, 22.1, 91.0, 87.3]

print("Ground Truth:  ", y_true)
print("Predictions:   ", y_pred)
print("Scores:        ", [f"{s:.1f}" for s in y_scores])
print()

# Calculate all metrics
report = compute_classification_report(y_true, y_pred, y_scores)

print("RESULTS:")
print("-"*80)
print(f"Precision:     {report['precision']:.4f}")
print(f"Recall:        {report['recall']:.4f}")
print(f"F1 Score:      {report['f1_score']:.4f}")
print(f"Accuracy:      {report['accuracy']:.4f}")
print(f"ROC-AUC:       {report['roc_auc']:.4f}")
print()

print("Confusion Matrix:")
cm = report['confusion_matrix']
print(f"  True Positive:  {cm['true_positive']}")
print(f"  True Negative:  {cm['true_negative']}")
print(f"  False Positive: {cm['false_positive']}")
print(f"  False Negative: {cm['false_negative']}")
print()


# ============================================================================
# EXAMPLE 2: Threshold-Based Evaluation
# ============================================================================

print("\n" + "="*80)
print("EXAMPLE 2: Threshold-Based Evaluation")
print("="*80 + "\n")

# Prepare data in expected format
ground_truth = [{'label': label} for label in y_true]
predictions = [{'purchase_probability': score} for score in y_scores]

# Test different thresholds
print("Testing different thresholds:\n")
print("Threshold   Precision   Recall      F1 Score    Accuracy")
print("-"*70)

for threshold in [30, 40, 50, 60, 70]:
    report = evaluate_with_threshold(ground_truth, predictions, threshold)
    print(f"{threshold:3d}%        {report['precision']:.4f}      "
          f"{report['recall']:.4f}      {report['f1_score']:.4f}      "
          f"{report['accuracy']:.4f}")

print()

# ============================================================================
# EXAMPLE 3: Find Optimal Threshold
# ============================================================================

print("\n" + "="*80)
print("EXAMPLE 3: Optimal Threshold Selection")
print("="*80 + "\n")

optimal_threshold, best_f1 = find_optimal_threshold(
    ground_truth,
    predictions,
    metric='f1'
)

print(f"Optimal Threshold (F1):  {optimal_threshold:.1f}%")
print(f"Best F1 Score:           {best_f1:.4f}")
print()

# Evaluate at optimal threshold
report = evaluate_with_threshold(ground_truth, predictions, optimal_threshold)
print_classification_report(report)


# ============================================================================
# EXAMPLE 4: ROC-AUC Interpretation
# ============================================================================

print("\n" + "="*80)
print("EXAMPLE 4: ROC-AUC Interpretation")
print("="*80 + "\n")

roc_auc = compute_roc_auc(y_true, y_scores)

print(f"ROC-AUC Score: {roc_auc:.4f}\n")

print("Interpretation Guide:")
print("  0.90 - 1.00 : Excellent discrimination")
print("  0.80 - 0.90 : Good discrimination")
print("  0.70 - 0.80 : Acceptable discrimination")
print("  0.60 - 0.70 : Poor discrimination")
print("  0.50 - 0.60 : Very poor discrimination")
print("  0.50        : Random chance (no discrimination)\n")

if roc_auc >= 0.9:
    interpretation = "[OK] Excellent - Model distinguishes very well"
elif roc_auc >= 0.8:
    interpretation = "[OK] Good - Model distinguishes well"
elif roc_auc >= 0.7:
    interpretation = "[OK] Acceptable - Model distinguishes reasonably"
elif roc_auc >= 0.6:
    interpretation = "[WARN] Poor - Model struggles to distinguish"
else:
    interpretation = "[FAIL] Very poor - Model barely better than random"

print(f"Your score: {interpretation}\n")


# ============================================================================
# EXAMPLE 5: For Your Research Paper
# ============================================================================

print("\n" + "="*80)
print("EXAMPLE 5: Paper-Ready Output")
print("="*80 + "\n")

print("LaTeX Table Format:")
print("-"*80)
print(r"\begin{table}[h]")
print(r"\centering")
print(r"\caption{Classification Performance on Test Set}")
print(r"\begin{tabular}{lc}")
print(r"\hline")
print(r"Metric & Value \\")
print(r"\hline")
print(f"Precision & {report['precision']:.4f} \\\\")
print(f"Recall & {report['recall']:.4f} \\\\")
print(f"F1 Score & {report['f1_score']:.4f} \\\\")
print(f"Accuracy & {report['accuracy']:.4f} \\\\")
print(f"ROC-AUC & {report['roc_auc']:.4f} \\\\")
print(r"\hline")
print(r"\end{tabular}")
print(r"\end{table}")
print("-"*80 + "\n")


# ============================================================================
# Summary
# ============================================================================

print("\n" + "="*80)
print("[OK] DEMO COMPLETE")
print("="*80 + "\n")

print("Key Functions Demonstrated:")
print("  1. compute_classification_report()  - All metrics at once")
print("  2. evaluate_with_threshold()        - Test specific threshold")
print("  3. find_optimal_threshold()         - Optimize for metric")
print("  4. compute_roc_auc()                - Threshold-independent metric")
print()

print("For your IEEE paper:")
print("  • Report Precision, Recall, F1 at optimal threshold")
print("  • Always include ROC-AUC (threshold-independent)")
print("  • Show confusion matrix for transparency")
print("  • Test multiple thresholds to show robustness")
print("  • Use larger dataset (100+ samples) for final results")
print()
