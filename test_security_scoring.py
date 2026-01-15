"""
Unit tests for the Security Scoring Module
"""

import json
import os
import tempfile
import unittest
from security_scoring import SecurityLevel, SecurityScorer, AuditEntry


class TestSecurityLevel(unittest.TestCase):
    """Test cases for SecurityLevel enum."""
    
    def test_security_levels_exist(self):
        """Test that all expected security levels are defined."""
        self.assertEqual(SecurityLevel.CRITICAL.value, "critical")
        self.assertEqual(SecurityLevel.ELEVATED.value, "elevated")
        self.assertEqual(SecurityLevel.NORMAL.value, "normal")


class TestAuditEntry(unittest.TestCase):
    """Test cases for AuditEntry class."""
    
    def test_audit_entry_creation(self):
        """Test creating an audit entry."""
        entry = AuditEntry(
            reason="CRITICAL security level multiplier",
            points="-30.0 (0.7x applied)",
            security_level="critical",
            original_score=100.0,
            adjusted_score=70.0
        )
        
        self.assertEqual(entry.reason, "CRITICAL security level multiplier")
        self.assertEqual(entry.points, "-30.0 (0.7x applied)")
        self.assertEqual(entry.security_level, "critical")
        self.assertEqual(entry.original_score, 100.0)
        self.assertEqual(entry.adjusted_score, 70.0)
    
    def test_audit_entry_to_dict(self):
        """Test converting audit entry to dictionary."""
        entry = AuditEntry(
            reason="Test reason",
            points="+10.0",
            security_level="normal",
            original_score=100.0,
            adjusted_score=110.0
        )
        
        result = entry.to_dict()
        self.assertIsInstance(result, dict)
        self.assertEqual(result["reason"], "Test reason")
        self.assertEqual(result["points"], "+10.0")


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
    
    # New boundary tests
    def test_zero_base_score(self):
        """Test that base score of 0 remains 0 regardless of multiplier."""
        for level in SecurityLevel:
            with self.subTest(security_level=level):
                scorer = SecurityScorer(level)
                result = scorer.calculate_score(0.0)
                self.assertEqual(result, 0.0)
    
    def test_very_high_base_score_with_max_cap(self):
        """Test that very high base scores respect max score cap."""
        scorer = SecurityScorer(SecurityLevel.NORMAL)
        base_score = 10000.0
        max_score = 500.0
        
        result = scorer.calculate_score(base_score, max_score=max_score)
        self.assertEqual(result, max_score)
    
    def test_very_high_base_score_without_max_cap(self):
        """Test that very high base scores are calculated correctly without cap."""
        scorer = SecurityScorer(SecurityLevel.CRITICAL)
        base_score = 10000.0
        
        result = scorer.calculate_score(base_score)
        self.assertEqual(result, 7000.0)
    
    # Custom multipliers tests
    def test_custom_multipliers(self):
        """Test using custom multipliers."""
        custom_mult = {
            SecurityLevel.CRITICAL: 0.5,
            SecurityLevel.ELEVATED: 0.8,
        }
        scorer = SecurityScorer(SecurityLevel.CRITICAL, custom_multipliers=custom_mult)
        
        result = scorer.calculate_score(100.0)
        self.assertEqual(result, 50.0)
    
    def test_config_file_multipliers(self):
        """Test loading multipliers from config file."""
        # Create a temporary config file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            config = {
                "multipliers": {
                    "critical": 0.6,
                    "elevated": 0.85,
                    "normal": 1.0
                }
            }
            json.dump(config, f)
            config_path = f.name
        
        try:
            scorer = SecurityScorer(SecurityLevel.CRITICAL, config_file=config_path)
            result = scorer.calculate_score(100.0)
            self.assertEqual(result, 60.0)
        finally:
            os.unlink(config_path)
    
    def test_invalid_config_file_uses_defaults(self):
        """Test that invalid config file falls back to defaults."""
        scorer = SecurityScorer(SecurityLevel.CRITICAL, config_file="/nonexistent/config.json")
        result = scorer.calculate_score(100.0)
        self.assertEqual(result, 70.0)  # Default multiplier
    
    # Audit trail tests
    def test_audit_trail_created(self):
        """Test that audit trail is created for scoring operations."""
        scorer = SecurityScorer(SecurityLevel.CRITICAL)
        scorer.calculate_score(100.0)
        
        audit_trail = scorer.get_audit_trail()
        self.assertEqual(len(audit_trail), 1)
        self.assertEqual(audit_trail[0]["security_level"], "critical")
        self.assertEqual(audit_trail[0]["original_score"], 100.0)
        self.assertEqual(audit_trail[0]["adjusted_score"], 70.0)
    
    def test_audit_trail_multiple_operations(self):
        """Test audit trail with multiple scoring operations."""
        scorer = SecurityScorer(SecurityLevel.ELEVATED)
        scorer.calculate_score(100.0)
        scorer.calculate_score(200.0)
        
        audit_trail = scorer.get_audit_trail()
        self.assertEqual(len(audit_trail), 2)
        self.assertEqual(audit_trail[0]["original_score"], 100.0)
        self.assertEqual(audit_trail[1]["original_score"], 200.0)
    
    def test_audit_trail_clear(self):
        """Test clearing the audit trail."""
        scorer = SecurityScorer(SecurityLevel.NORMAL)
        scorer.calculate_score(100.0)
        scorer.clear_audit_trail()
        
        audit_trail = scorer.get_audit_trail()
        self.assertEqual(len(audit_trail), 0)
    
    def test_audit_trail_includes_reason_and_points(self):
        """Test that audit trail includes reason and points information."""
        scorer = SecurityScorer(SecurityLevel.CRITICAL)
        scorer.calculate_score(100.0)
        
        audit_trail = scorer.get_audit_trail()
        entry = audit_trail[0]
        
        self.assertIn("CRITICAL", entry["reason"])
        self.assertIn("multiplier", entry["reason"])
        self.assertIn("0.7", entry["points"])


if __name__ == '__main__':
    unittest.main()
