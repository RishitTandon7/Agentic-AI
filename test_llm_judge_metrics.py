"""
Unit Tests for Evaluation Metrics Module
"""

import unittest
from llm_judge_metrics import (
    compute_confusion_matrix,
    compute_precision,
    compute_recall,
    compute_f1_score,
    compute_accuracy,
    compute_roc_auc,
    compute_classification_report
)


class TestConfusionMatrix(unittest.TestCase):
    """Test confusion matrix calculation."""
    
    def test_perfect_classification(self):
        y_true = [1, 1, 0, 0, 1, 0]
        y_pred = [1, 1, 0, 0, 1, 0]
        
        cm = compute_confusion_matrix(y_true, y_pred)
        
        self.assertEqual(cm['true_positive'], 3)
        self.assertEqual(cm['true_negative'], 3)
        self.assertEqual(cm['false_positive'], 0)
        self.assertEqual(cm['false_negative'], 0)
    
    def test_all_wrong(self):
        y_true = [1, 1, 0, 0]
        y_pred = [0, 0, 1, 1]
        
        cm = compute_confusion_matrix(y_true, y_pred)
        
        self.assertEqual(cm['true_positive'], 0)
        self.assertEqual(cm['true_negative'], 0)
        self.assertEqual(cm['false_positive'], 2)
        self.assertEqual(cm['false_negative'], 2)


class TestMetrics(unittest.TestCase):
    """Test precision, recall, F1 calculation."""
    
    def test_perfect_scores(self):
        cm = {
            'true_positive': 10,
            'true_negative': 10,
            'false_positive': 0,
            'false_negative': 0,
            'total': 20
        }
        
        self.assertEqual(compute_precision(cm), 1.0)
        self.assertEqual(compute_recall(cm), 1.0)
        self.assertEqual(compute_f1_score(1.0, 1.0), 1.0)
        self.assertEqual(compute_accuracy(cm), 1.0)
    
    def test_zero_division(self):
        cm = {
            'true_positive': 0,
            'true_negative': 10,
            'false_positive': 0,
            'false_negative': 0,
            'total': 10
        }
        
        # Should handle division by zero gracefully
        self.assertEqual(compute_precision(cm), 0.0)
        self.assertEqual(compute_recall(cm), 0.0)
    
    def test_known_values(self):
        # TP=8, TN=5, FP=2, FN=1
        cm = {
            'true_positive': 8,
            'true_negative': 5,
            'false_positive': 2,
            'false_negative': 1,
            'total': 16
        }
        
        precision = compute_precision(cm)  # 8/(8+2) = 0.8
        recall = compute_recall(cm)  # 8/(8+1) = 0.888...
        
        self.assertAlmostEqual(precision, 0.8, places=2)
        self.assertAlmostEqual(recall, 0.889, places=2)


class TestROCAUC(unittest.TestCase):
    """Test ROC-AUC calculation."""
    
    def test_perfect_ranking(self):
        y_true = [1, 1, 0, 0]
        y_scores = [0.9, 0.8, 0.3, 0.1]
        
        auc = compute_roc_auc(y_true, y_scores)
        self.assertEqual(auc, 1.0)
    
    def test_random_ranking(self):
        y_true = [1, 0, 1, 0]
        y_scores = [0.5, 0.5, 0.5, 0.5]
        
        auc = compute_roc_auc(y_true, y_scores)
        self.assertAlmostEqual(auc, 0.5, places=1)
    
    def test_inverse_ranking(self):
        y_true = [1, 1, 0, 0]
        y_scores = [0.1, 0.2, 0.8, 0.9]
        
        auc = compute_roc_auc(y_true, y_scores)
        self.assertEqual(auc, 0.0)


class TestClassificationReport(unittest.TestCase):
    """Test full classification report."""
    
    def test_complete_report(self):
        y_true = [1, 1, 0, 0, 1, 0, 1, 0]
        y_pred = [1, 1, 0, 0, 1, 1, 0, 0]
        y_scores = [0.9, 0.8, 0.3, 0.2, 0.85, 0.6, 0.4, 0.1]
        
        report = compute_classification_report(y_true, y_pred, y_scores)
        
        # Check all metrics are present
        self.assertIn('precision', report)
        self.assertIn('recall', report)
        self.assertIn('f1_score', report)
        self.assertIn('accuracy', report)
        self.assertIn('roc_auc', report)
        
        # Check values are in valid range
        self.assertGreaterEqual(report['precision'], 0.0)
        self.assertLessEqual(report['precision'], 1.0)
        self.assertGreaterEqual(report['roc_auc'], 0.0)
        self.assertLessEqual(report['roc_auc'], 1.0)


if __name__ == "__main__":
    print("\n" + "="*60)
    print("METRICS MODULE - UNIT TESTS")
    print("="*60 + "\n")
    
    unittest.main(verbosity=2)
