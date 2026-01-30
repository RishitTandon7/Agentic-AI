# Evaluation Metrics Module - Complete Guide

## Overview

The evaluation metrics module provides comprehensive tools for calculating standard classification metrics for the LLM as Judge system:

- **Precision, Recall, F1 Score**
- **ROC-AUC** (Receiver Operating Characteristic - Area Under Curve)
- **Accuracy**
- **Confusion Matrix**
- **Threshold Optimization**

All implementations are **pure Python** with **no sklearn dependency**, ensuring reproducibility and transparency for academic research.

---

## Quick Start

### Installation

No additional dependencies required! The metrics module only uses Python standard library.

### Basic Usage

```python
from llm_judge_metrics import compute_classification_report

# Your data
y_true = [1, 1, 0, 0, 1]  # Ground truth labels
y_pred = [1, 1, 0, 1, 1]  # Model predictions
y_scores = [85.2, 92.1, 32.4, 51.2, 88.5]  # Prediction scores

# Calculate all metrics
report = compute_classification_report(y_true, y_pred, y_scores)

print(f"Precision: {report['precision']:.4f}")
print(f"Recall:    {report['recall']:.4f}")
print(f"F1 Score:  {report['f1_score']:.4f}")
print(f"ROC-AUC:   {report['roc_auc']:.4f}")
```

---

## Files Created

| File | Purpose | Lines |
|------|---------|-------|
| `llm_judge_metrics.py` | Core metrics implementation | ~400 |
| `test_llm_judge_metrics.py` | Unit tests for metrics | ~130 |
| `example_metrics_evaluation.py` | Full LLM pipeline evaluation | ~350 |
| `demo_metrics_quick.py` | Standalone demo (no LLM) | ~200 |

---

## Metrics Explained

### 1. **Precision**

**Formula**: `TP / (TP + FP)`

**Meaning**: Of all products predicted as "recommend", what percentage were actually good?

**Example**: If precision = 0.85, then 85% of recommendations are correct.

```python
from llm_judge_metrics import compute_precision, compute_confusion_matrix

cm = compute_confusion_matrix(y_true, y_pred)
precision = compute_precision(cm)
```

### 2. **Recall (Sensitivity)**

**Formula**: `TP / (TP + FN)`

**Meaning**: Of all actually good products, what percentage did we correctly recommend?

**Example**: If recall = 0.90, then we found 90% of all good products.

```python
from llm_judge_metrics import compute_recall

recall = compute_recall(cm)
```

### 3. **F1 Score**

**Formula**: `2 × (Precision × Recall) / (Precision + Recall)`

**Meaning**: Harmonic mean of precision and recall. Balances both metrics.

**Example**: F1 = 0.875 indicates strong overall performance.

```python
from llm_judge_metrics import compute_f1_score

f1 = compute_f1_score(precision, recall)
```

### 4. **ROC-AUC**

**Formula**: Mann-Whitney U statistic / (n_pos × n_neg)

**Meaning**: Probability that a random positive example scores higher than a random negative example.

**Example**: ROC-AUC = 0.95 means the model almost perfectly ranks good products above bad ones.

**Interpretation Scale**:
- 0.90 - 1.00: Excellent discrimination
- 0.80 - 0.90: Good discrimination
- 0.70 - 0.80: Acceptable discrimination
- 0.60 - 0.70: Poor discrimination
- 0.50 - 0.60: Very poor
- 0.50: Random chance

```python
from llm_judge_metrics import compute_roc_auc

roc_auc = compute_roc_auc(y_true, y_scores)
```

### 5. **Confusion Matrix**

Shows the breakdown of predictions:

| | Predicted: No | Predicted: Yes |
|---|---|---|
| **Actual: No** | True Negative (TN) | False Positive (FP) |
| **Actual: Yes** | False Negative (FN) | True Positive (TP) |

```python
from llm_judge_metrics import compute_confusion_matrix

cm = compute_confusion_matrix(y_true, y_pred)
print(f"TP: {cm['true_positive']}")
print(f"TN: {cm['true_negative']}")
print(f"FP: {cm['false_positive']}")
print(f"FN: {cm['false_negative']}")
```

---

## Quick Demo Results

Running `demo_metrics_quick.py` produces:

```
EXAMPLE 1: Calculate metrics from ground truth and predictions

Ground Truth:   [1, 1, 0, 0, 1, 0, 1, 0, 1, 1]
Predictions:    [1, 1, 0, 1, 1, 0, 0, 0, 1, 1]
Scores:         [85.2, 92.1, 32.4, 51.2, 88.5, 28.9, 45.0, 22.1, 91.0, 87.3]

RESULTS:
Precision:     0.8333
Recall:        0.8333
F1 Score:      0.8333
Accuracy:      0.8000
ROC-AUC:       0.9583

Confusion Matrix:
  True Positive:  5
  True Negative:  3
  False Positive: 1
  False Negative: 1
```

---

## Threshold Optimization

Find the threshold that maximizes a specific metric:

```python
from llm_judge_metrics import find_optimal_threshold

ground_truth = [{'label': 1}, {'label': 0}, ...]
predictions = [{'purchase_probability': 85.2}, {'purchase_probability': 32.4}, ...]

# Optimize for F1 score
optimal_threshold, best_f1 = find_optimal_threshold(
    ground_truth,
    predictions,
    metric='f1'
)

print(f"Optimal threshold: {optimal_threshold}%")
print(f"Best F1 score: {best_f1:.4f}")
```

**Output from demo**:
```
Optimal Threshold (F1):  33.0%
Best F1 Score:           0.9231
```

---

## For Your Research Paper

### 1. **Report All Metrics**

Always include:
- Precision (specificity of recommendations)
- Recall (coverage of good products)
- F1 Score (balanced measure)
- ROC-AUC (threshold-independent)

### 2. **LaTeX Table Format**

```latex
\begin{table}[h]
\centering
\caption{Classification Performance on Test Set}
\begin{tabular}{lc}
\hline
Metric & Value \\
\hline
Precision & 0.8571 \\
Recall & 1.0000 \\
F1 Score & 0.9231 \\
Accuracy & 0.9000 \\
ROC-AUC & 0.9583 \\
\hline
\end{tabular}
\end{table}
```

### 3. **Confusion Matrix Visualization**

```
Confusion Matrix:
  True Positive:     6    (Correct recommendations)
  True Negative:     3    (Correct rejections)
  False Positive:    1    (Bad recommendations)
  False Negative:    0    (Missed opportunities)
  Total:            10
```

### 4. **Threshold Analysis**

Show robustness across thresholds:

```
Threshold   Precision   Recall      F1 Score    Accuracy
 30%        0.7500      1.0000      0.8571      0.8000
 40%        0.8571      1.0000      0.9231      0.9000
 50%        0.8333      0.8333      0.8333      0.8000
 60%        1.0000      0.8333      0.9091      0.9000
 70%        1.0000      0.8333      0.9091      0.9000
```

---

## Testing

All metrics are unit tested:

```bash
python test_llm_judge_metrics.py
```

**Expected output**:
```
Ran 9 tests in 0.002s
OK
```

---

## Example Workflows

### Workflow 1: Quick Metrics (No LLM)

```bash
python demo_metrics_quick.py
```

Demonstrates all metrics with hardcoded examples. **No Ollama required**.

### Workflow 2: Full LLM Evaluation

```bash
python example_metrics_evaluation.py
```

Evaluates real products using the LLM pipeline. **Requires Ollama running**.

### Workflow 3: Custom Dataset

```python
from llm_judge_pipeline import evaluate_product_batch
from llm_judge_metrics import evaluate_with_threshold

# Your dataset
products = [
    {
        "product_description": "...",
        "customer_reviews": "...",
        "actual_price": 1299.99,
        "market_price": 1349.00,
        "ground_truth_label": 1  # 1 = recommend, 0 = don't recommend
    },
    # ... more products
]

# Evaluate all products
results = evaluate_product_batch([
    {
        "product_description": p["product_description"],
        "customer_reviews": p["customer_reviews"],
        "actual_price": p["actual_price"],
        "market_price": p["market_price"]
    }
    for p in products
])

# Extract predictions and ground truth
ground_truth = [{'label': p['ground_truth_label']} for p in products]
predictions = [{'purchase_probability': r['purchase_probability']} for r in results]

# Calculate metrics
report = evaluate_with_threshold(ground_truth, predictions, threshold=50.0)

print(f"Precision: {report['precision']:.4f}")
print(f"Recall: {report['recall']:.4f}")
print(f"F1 Score: {report['f1_score']:.4f}")
print(f"ROC-AUC: {report['roc_auc']:.4f}")
```

---

## Key Functions Reference

| Function | Purpose |
|----------|---------|
| `compute_confusion_matrix()` | Calculate TP, TN, FP, FN |
| `compute_precision()` | Calculate precision |
| `compute_recall()` | Calculate recall |
| `compute_f1_score()` | Calculate F1 score |
| `compute_accuracy()` | Calculate accuracy |
| `compute_roc_auc()` | Calculate ROC-AUC |
| `compute_classification_report()` | All metrics at once |
| `evaluate_with_threshold()` | Evaluate at specific threshold |
| `find_optimal_threshold()` | Find best threshold for metric |
| `print_classification_report()` | Pretty print results |

---

## Best Practices for IEEE Paper

1. **Dataset Size**: Use 100+ products for final results
2. **Cross-Validation**: Report mean ± std across folds
3. **Threshold Selection**: Use validation set, report on test set
4. **ROC-AUC**: Always include (threshold-independent)
5. **Confusion Matrix**: Show for transparency
6. **Baseline Comparison**: Compare against random (50%) and simple heuristics
7. **Statistical Significance**: Use bootstrap or t-tests for confidence intervals

---

## Summary

✅ **9 unit tests passing**  
✅ **No sklearn dependency** (pure Python)  
✅ **Full reproducibility**  
✅ **Paper-ready output formats**  
✅ **Comprehensive documentation**  

**Status**: Ready for IEEE A* submission

---

## Next Steps

1. Collect ground truth dataset (100+ products)
2. Run full evaluation: `python example_metrics_evaluation.py`
3. Report metrics in your paper
4. Include ablation studies (see `ABLATION_STUDY_GUIDE.md`)

---

**Questions?** See `demo_metrics_quick.py` for a working example.
