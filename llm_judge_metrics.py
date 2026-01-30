"""
LLM as Judge - Evaluation Metrics Module
IEEE A* Conference Submission Artifact

This module implements standard classification metrics for evaluating the system:
- Precision, Recall, F1 Score
- ROC-AUC
- Confusion Matrix
- Classification Report

These metrics are used to validate the system's predictions against ground truth labels.
"""

import json
from typing import List, Dict, Tuple, Optional
import math


# ============================================================================
# BINARY CLASSIFICATION METRICS
# ============================================================================

def compute_confusion_matrix(
    y_true: List[int],
    y_pred: List[int]
) -> Dict[str, int]:
    """
    Compute confusion matrix for binary classification.
    
    Args:
        y_true: Ground truth labels (0 or 1)
        y_pred: Predicted labels (0 or 1)
        
    Returns:
        Dictionary with TP, TN, FP, FN counts
    """
    tp = sum(1 for true, pred in zip(y_true, y_pred) if true == 1 and pred == 1)
    tn = sum(1 for true, pred in zip(y_true, y_pred) if true == 0 and pred == 0)
    fp = sum(1 for true, pred in zip(y_true, y_pred) if true == 0 and pred == 1)
    fn = sum(1 for true, pred in zip(y_true, y_pred) if true == 1 and pred == 0)
    
    return {
        'true_positive': tp,
        'true_negative': tn,
        'false_positive': fp,
        'false_negative': fn,
        'total': len(y_true)
    }


def compute_precision(confusion_matrix: Dict[str, int]) -> float:
    """
    Compute precision from confusion matrix.
    
    Precision = TP / (TP + FP)
    
    Args:
        confusion_matrix: Dictionary with TP, TN, FP, FN
        
    Returns:
        Precision score [0, 1]
    """
    tp = confusion_matrix['true_positive']
    fp = confusion_matrix['false_positive']
    
    if tp + fp == 0:
        return 0.0
    
    return tp / (tp + fp)


def compute_recall(confusion_matrix: Dict[str, int]) -> float:
    """
    Compute recall (sensitivity) from confusion matrix.
    
    Recall = TP / (TP + FN)
    
    Args:
        confusion_matrix: Dictionary with TP, TN, FP, FN
        
    Returns:
        Recall score [0, 1]
    """
    tp = confusion_matrix['true_positive']
    fn = confusion_matrix['false_negative']
    
    if tp + fn == 0:
        return 0.0
    
    return tp / (tp + fn)


def compute_f1_score(precision: float, recall: float) -> float:
    """
    Compute F1 score from precision and recall.
    
    F1 = 2 × (Precision × Recall) / (Precision + Recall)
    
    Args:
        precision: Precision score
        recall: Recall score
        
    Returns:
        F1 score [0, 1]
    """
    if precision + recall == 0:
        return 0.0
    
    return 2 * (precision * recall) / (precision + recall)


def compute_accuracy(confusion_matrix: Dict[str, int]) -> float:
    """
    Compute accuracy from confusion matrix.
    
    Accuracy = (TP + TN) / Total
    
    Args:
        confusion_matrix: Dictionary with TP, TN, FP, FN
        
    Returns:
        Accuracy score [0, 1]
    """
    tp = confusion_matrix['true_positive']
    tn = confusion_matrix['true_negative']
    total = confusion_matrix['total']
    
    if total == 0:
        return 0.0
    
    return (tp + tn) / total


# ============================================================================
# ROC-AUC CALCULATION
# ============================================================================

def compute_roc_auc(
    y_true: List[int],
    y_scores: List[float]
) -> float:
    """
    Compute ROC-AUC score using Mann-Whitney U statistic.
    
    This is a deterministic implementation without sklearn dependency.
    AUC is the probability that a randomly chosen positive example
    has a higher score than a randomly chosen negative example.
    
    Args:
        y_true: Ground truth binary labels (0 or 1)
        y_scores: Predicted scores (continuous, e.g., purchase probability)
        
    Returns:
        ROC-AUC score [0, 1]
    """
    # Count positives and negatives
    n_pos = sum(y_true)
    n_neg = len(y_true) - n_pos
    
    if n_pos == 0 or n_neg == 0:
        return 0.5  # Undefined, return random baseline
    
    # Calculate using Mann-Whitney U statistic
    # Count how many times a positive score is greater than a negative score
    n_correct = 0
    n_ties = 0
    
    for i, (score_i, label_i) in enumerate(zip(y_scores, y_true)):
        if label_i == 1:  # Positive example
            for j, (score_j, label_j) in enumerate(zip(y_scores, y_true)):
                if label_j == 0:  # Negative example
                    if score_i > score_j:
                        n_correct += 1
                    elif score_i == score_j:
                        n_ties += 1
    
    # Calculate AUC (ties count as 0.5)
    auc = (n_correct + 0.5 * n_ties) / (n_pos * n_neg)
    
    return auc


# ============================================================================
# CLASSIFICATION REPORT
# ============================================================================

def compute_classification_report(
    y_true: List[int],
    y_pred: List[int],
    y_scores: Optional[List[float]] = None
) -> Dict[str, float]:
    """
    Compute comprehensive classification metrics.
    
    Args:
        y_true: Ground truth labels (0 or 1)
        y_pred: Predicted labels (0 or 1)
        y_scores: Optional predicted scores for ROC-AUC
        
    Returns:
        Dictionary containing all metrics
    """
    cm = compute_confusion_matrix(y_true, y_pred)
    precision = compute_precision(cm)
    recall = compute_recall(cm)
    f1 = compute_f1_score(precision, recall)
    accuracy = compute_accuracy(cm)
    
    report = {
        'confusion_matrix': cm,
        'precision': precision,
        'recall': recall,
        'f1_score': f1,
        'accuracy': accuracy,
    }
    
    # Add ROC-AUC if scores provided
    if y_scores is not None:
        report['roc_auc'] = compute_roc_auc(y_true, y_scores)
    
    return report


# ============================================================================
# EVALUATION WITH THRESHOLD
# ============================================================================

def evaluate_with_threshold(
    ground_truth: List[Dict],
    predictions: List[Dict],
    threshold: float = 50.0
) -> Dict[str, float]:
    """
    Evaluate predictions against ground truth using a threshold.
    
    This converts continuous purchase probabilities to binary predictions
    and computes standard classification metrics.
    
    Args:
        ground_truth: List of dicts with 'label' key (0 or 1)
        predictions: List of dicts with 'purchase_probability' key
        threshold: Threshold for converting probability to binary prediction
        
    Returns:
        Classification report with all metrics
    """
    # Extract labels and scores
    y_true = [item['label'] for item in ground_truth]
    y_scores = [pred['purchase_probability'] for pred in predictions]
    
    # Convert scores to binary predictions using threshold
    y_pred = [1 if score >= threshold else 0 for score in y_scores]
    
    # Compute metrics
    report = compute_classification_report(y_true, y_pred, y_scores)
    report['threshold'] = threshold
    
    return report


# ============================================================================
# THRESHOLD OPTIMIZATION
# ============================================================================

def find_optimal_threshold(
    ground_truth: List[Dict],
    predictions: List[Dict],
    metric: str = 'f1'
) -> Tuple[float, float]:
    """
    Find optimal threshold that maximizes a specific metric.
    
    Args:
        ground_truth: List of dicts with 'label' key
        predictions: List of dicts with 'purchase_probability' key
        metric: Metric to optimize ('f1', 'precision', 'recall', 'accuracy')
        
    Returns:
        Tuple of (optimal_threshold, best_metric_value)
    """
    # Test thresholds from 0 to 100 in steps of 1
    thresholds = range(0, 101, 1)
    
    best_threshold = 50.0
    best_value = 0.0
    
    for threshold in thresholds:
        report = evaluate_with_threshold(ground_truth, predictions, threshold)
        
        if metric == 'f1':
            value = report['f1_score']
        elif metric == 'precision':
            value = report['precision']
        elif metric == 'recall':
            value = report['recall']
        elif metric == 'accuracy':
            value = report['accuracy']
        else:
            raise ValueError(f"Unknown metric: {metric}")
        
        if value > best_value:
            best_value = value
            best_threshold = threshold
    
    return best_threshold, best_value


# ============================================================================
# PRETTY PRINTING
# ============================================================================

def print_classification_report(report: Dict[str, float]) -> None:
    """
    Pretty print classification report.
    
    Args:
        report: Dictionary containing metrics
    """
    print("\n" + "="*60)
    print("CLASSIFICATION REPORT")
    print("="*60)
    
    # Confusion Matrix
    cm = report['confusion_matrix']
    print("\nConfusion Matrix:")
    print(f"  True Positive:  {cm['true_positive']:4d}")
    print(f"  True Negative:  {cm['true_negative']:4d}")
    print(f"  False Positive: {cm['false_positive']:4d}")
    print(f"  False Negative: {cm['false_negative']:4d}")
    print(f"  Total:          {cm['total']:4d}")
    
    # Metrics
    print("\nMetrics:")
    print(f"  Precision:      {report['precision']:.4f}")
    print(f"  Recall:         {report['recall']:.4f}")
    print(f"  F1 Score:       {report['f1_score']:.4f}")
    print(f"  Accuracy:       {report['accuracy']:.4f}")
    
    if 'roc_auc' in report:
        print(f"  ROC-AUC:        {report['roc_auc']:.4f}")
    
    if 'threshold' in report:
        print(f"\nThreshold:        {report['threshold']:.1f}%")
    
    print("="*60 + "\n")


# ============================================================================
# CROSS-VALIDATION METRICS
# ============================================================================

def compute_cross_validation_metrics(
    fold_reports: List[Dict[str, float]]
) -> Dict[str, Dict[str, float]]:
    """
    Aggregate metrics across cross-validation folds.
    
    Args:
        fold_reports: List of classification reports from each fold
        
    Returns:
        Dictionary with mean and std for each metric
    """
    metrics = ['precision', 'recall', 'f1_score', 'accuracy']
    
    results = {}
    
    for metric in metrics:
        values = [report[metric] for report in fold_reports if metric in report]
        
        if values:
            mean = sum(values) / len(values)
            variance = sum((x - mean) ** 2 for x in values) / len(values)
            std = math.sqrt(variance)
            
            results[metric] = {
                'mean': mean,
                'std': std,
                'min': min(values),
                'max': max(values)
            }
    
    # Add ROC-AUC if available
    if 'roc_auc' in fold_reports[0]:
        values = [report['roc_auc'] for report in fold_reports]
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        std = math.sqrt(variance)
        
        results['roc_auc'] = {
            'mean': mean,
            'std': std,
            'min': min(values),
            'max': max(values)
        }
    
    return results


def print_cv_metrics(cv_results: Dict[str, Dict[str, float]]) -> None:
    """
    Pretty print cross-validation results.
    
    Args:
        cv_results: Results from compute_cross_validation_metrics()
    """
    print("\n" + "="*60)
    print("CROSS-VALIDATION RESULTS")
    print("="*60)
    print("\nMetric           Mean     Std      Min      Max")
    print("-"*60)
    
    for metric, stats in cv_results.items():
        metric_name = metric.replace('_', ' ').title()
        print(f"{metric_name:15s} {stats['mean']:.4f}   {stats['std']:.4f}   "
              f"{stats['min']:.4f}   {stats['max']:.4f}")
    
    print("="*60 + "\n")
