"""
LLM as Judge - Unit Tests
IEEE A* Conference Submission Artifact
"""

import unittest
from llm_judge_config import *
from llm_judge_scoring import compute_component_scores, aggregate_final_score


class TestScoringMatrices(unittest.TestCase):
    """Test scoring matrices."""
    
    def test_cpu_tier_scores(self):
        self.assertEqual(CPU_TIER_SCORES["S"], 1.00)
        self.assertEqual(CPU_TIER_SCORES["D"], 0.30)
    
    def test_gpu_tier_scores(self):
        self.assertEqual(GPU_TIER_SCORES["S"], 1.00)
        self.assertEqual(GPU_TIER_SCORES["Integrated"], 0.20)


class TestNormalizedScores(unittest.TestCase):
    """Test RAM and storage scoring."""
    
    def test_ram_score_boundaries(self):
        self.assertEqual(compute_ram_score(4), 0.0)
        self.assertEqual(compute_ram_score(64), 1.0)
    
    def test_storage_score_boundaries(self):
        self.assertEqual(compute_storage_score(128), 0.0)
        self.assertEqual(compute_storage_score(2048), 1.0)


class TestPriceScore(unittest.TestCase):
    """Test price deviation scoring."""
    
    def test_price_thresholds(self):
        self.assertEqual(compute_price_score(1000, 1000), 1.00)
        self.assertEqual(compute_price_score(1099, 1000), 0.85)
        self.assertEqual(compute_price_score(1300, 1000), 0.30)


class TestSignalValidation(unittest.TestCase):
    """Test signal validation."""
    
    def test_valid_signal(self):
        valid = {
            "cpu_tier": "S", "gpu_tier": "A", "display_tier": "A",
            "brand_reliability": "High",
            "sentiment_distribution": {"positive": 0.7, "neutral": 0.2, "negative": 0.1}
        }
        self.assertTrue(validate_signal_schema(valid))
    
    def test_invalid_sentiment_sum(self):
        invalid = {
            "cpu_tier": "S", "gpu_tier": "A", "display_tier": "A",
            "brand_reliability": "High",
            "sentiment_distribution": {"positive": 0.5, "neutral": 0.2, "negative": 0.1}
        }
        self.assertFalse(validate_signal_schema(invalid))


class TestDeterminism(unittest.TestCase):
    """Test determinism."""
    
    def test_determinism(self):
        signals = {
            "cpu_tier": "A", "gpu_tier": "B", "ram_gb": 16, "storage_gb": 512,
            "display_tier": "B", "brand_reliability": "Medium",
            "sentiment_distribution": {"positive": 0.6, "neutral": 0.3, "negative": 0.1}
        }
        
        results = [compute_component_scores(signals, 1000.0, 1000.0) for _ in range(10)]
        for result in results[1:]:
            self.assertEqual(results[0], result)


if __name__ == "__main__":
    unittest.main(verbosity=2)
