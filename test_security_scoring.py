"""
Unit tests for the Security Scoring Module
"""

import unittest
from security_scoring import SecurityLevel, SecurityScorer


class TestSecurityLevel(unittest.TestCase):
    """Test cases for SecurityLevel enum."""
    
    def test_security_levels_exist(self):
        """Test that all expected security levels are defined."""
        self.assertEqual(SecurityLevel.CRITICAL.value, "critical")
        self.assertEqual(SecurityLevel.ELEVATED.value, "elevated")
        self.assertEqual(SecurityLevel.NORMAL.value, "normal")


class TestSecurityScorer(unittest.TestCase):
    """Test cases for SecurityScorer class."""
    
    def test_critical_level_adjustment(self):
        """Test score adjustment for CRITICAL security level."""
        scorer = SecurityScorer(SecurityLevel.CRITICAL)
        base_score = 100.0
        adjusted_score = scorer.calculate_score(base_score)
        self.assertEqual(adjusted_score, 70.0)
    
    def test_elevated_level_adjustment(self):
        """Test score adjustment for ELEVATED security level."""
        scorer = SecurityScorer(SecurityLevel.ELEVATED)
        base_score = 100.0
        adjusted_score = scorer.calculate_score(base_score)
        self.assertEqual(adjusted_score, 90.0)
    
    def test_normal_level_no_adjustment(self):
        """Test that NORMAL security level doesn't adjust the score."""
        scorer = SecurityScorer(SecurityLevel.NORMAL)
        base_score = 100.0
        adjusted_score = scorer.calculate_score(base_score)
        self.assertEqual(adjusted_score, 100.0)
    
    def test_critical_with_different_base_scores(self):
        """Test CRITICAL level with various base scores."""
        scorer = SecurityScorer(SecurityLevel.CRITICAL)
        
        test_cases = [
            (50.0, 35.0),
            (200.0, 140.0),
            (1000.0, 700.0),
            (0.0, 0.0),
        ]
        
        for base, expected in test_cases:
            with self.subTest(base_score=base):
                result = scorer.calculate_score(base)
                self.assertAlmostEqual(result, expected, places=2)
    
    def test_elevated_with_different_base_scores(self):
        """Test ELEVATED level with various base scores."""
        scorer = SecurityScorer(SecurityLevel.ELEVATED)
        
        test_cases = [
            (50.0, 45.0),
            (200.0, 180.0),
            (1000.0, 900.0),
            (0.0, 0.0),
        ]
        
        for base, expected in test_cases:
            with self.subTest(base_score=base):
                result = scorer.calculate_score(base)
                self.assertAlmostEqual(result, expected, places=2)
    
    def test_scorer_initialization(self):
        """Test that SecurityScorer can be initialized with each security level."""
        for level in SecurityLevel:
            scorer = SecurityScorer(level)
            self.assertEqual(scorer.security_level, level)
    
    def test_multiple_calculations(self):
        """Test that multiple calculations with the same scorer produce consistent results."""
        scorer = SecurityScorer(SecurityLevel.CRITICAL)
        base_score = 100.0
        
        result1 = scorer.calculate_score(base_score)
        result2 = scorer.calculate_score(base_score)
        
        self.assertEqual(result1, result2)
    
    def test_negative_base_score_raises_error(self):
        """Test that negative base scores raise ValueError."""
        scorer = SecurityScorer(SecurityLevel.NORMAL)
        
        with self.assertRaises(ValueError) as context:
            scorer.calculate_score(-10.0)
        
        self.assertIn("non-negative", str(context.exception))


if __name__ == '__main__':
    unittest.main()
