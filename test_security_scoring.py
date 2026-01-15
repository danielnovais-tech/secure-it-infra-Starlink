"""
Unit tests for the Security Scoring Module
"""

import csv
import json
import os
import tempfile
import unittest
from security_scoring import (
    SecurityLevel, SecurityScorer, AuditEntry, 
    validate_config_schema, ConfigValidationError
)


class TestConfigValidation(unittest.TestCase):
    """Test cases for configuration validation."""
    
    def test_valid_config(self):
        """Test that valid config passes validation."""
        config = {
            "multipliers": {
                "critical": 0.7,
                "elevated": 0.9,
                "normal": 1.0
            }
        }
        # Should not raise
        validate_config_schema(config)
    
    def test_missing_multipliers_key(self):
        """Test that config without multipliers key raises error."""
        config = {"other_key": "value"}
        with self.assertRaises(ConfigValidationError) as context:
            validate_config_schema(config)
        self.assertIn("multipliers", str(context.exception))
    
    def test_invalid_security_level(self):
        """Test that invalid security level raises error."""
        config = {
            "multipliers": {
                "invalid_level": 0.5
            }
        }
        with self.assertRaises(ConfigValidationError) as context:
            validate_config_schema(config)
        self.assertIn("Invalid security level", str(context.exception))
    
    def test_negative_multiplier(self):
        """Test that negative multiplier raises error."""
        config = {
            "multipliers": {
                "critical": -0.5
            }
        }
        with self.assertRaises(ConfigValidationError) as context:
            validate_config_schema(config)
        self.assertIn("non-negative", str(context.exception))
    
    def test_non_numeric_multiplier(self):
        """Test that non-numeric multiplier raises error."""
        config = {
            "multipliers": {
                "critical": "not_a_number"
            }
        }
        with self.assertRaises(ConfigValidationError) as context:
            validate_config_schema(config)
        self.assertIn("must be a number", str(context.exception))


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
    
    def test_invalid_config_raises_error(self):
        """Test that invalid config file raises ConfigValidationError."""
        # Create an invalid config file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            config = {
                "multipliers": {
                    "critical": -0.5  # Negative multiplier
                }
            }
            json.dump(config, f)
            config_path = f.name
        
        try:
            with self.assertRaises(ConfigValidationError):
                SecurityScorer(SecurityLevel.CRITICAL, config_file=config_path)
        finally:
            os.unlink(config_path)
    
    def test_detail_level_summary(self):
        """Test get_audit_trail with summary detail level."""
        scorer = SecurityScorer(SecurityLevel.CRITICAL)
        scorer.calculate_score(100.0)
        
        summary_trail = scorer.get_audit_trail(detail_level="summary")
        self.assertEqual(len(summary_trail), 1)
        self.assertIn("reason", summary_trail[0])
        self.assertIn("adjusted_score", summary_trail[0])
        # Should not include full details
        self.assertNotIn("original_score", summary_trail[0])
    
    def test_detail_level_full(self):
        """Test get_audit_trail with full detail level."""
        scorer = SecurityScorer(SecurityLevel.ELEVATED)
        scorer.calculate_score(100.0)
        
        full_trail = scorer.get_audit_trail(detail_level="full")
        self.assertEqual(len(full_trail), 1)
        self.assertIn("reason", full_trail[0])
        self.assertIn("adjusted_score", full_trail[0])
        self.assertIn("original_score", full_trail[0])
        self.assertIn("timestamp", full_trail[0])
    
    def test_previous_score_comparison(self):
        """Test historical comparison with previous score."""
        scorer = SecurityScorer(SecurityLevel.CRITICAL)
        scorer.calculate_score(100.0, previous_score=120.0)
        
        audit_trail = scorer.get_audit_trail()
        entry = audit_trail[0]
        
        self.assertEqual(entry["previous_score"], 120.0)
        self.assertIn("historical_delta", entry)
        self.assertEqual(entry["historical_delta"], 70.0 - 120.0)
        self.assertIn("decreased", entry["reason"])
    
    def test_export_json(self):
        """Test exporting audit trail to JSON."""
        scorer = SecurityScorer(SecurityLevel.CRITICAL)
        scorer.calculate_score(100.0)
        scorer.calculate_score(200.0)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json_path = f.name
        
        try:
            scorer.export_audit_trail_json(json_path)
            
            with open(json_path, 'r') as f:
                data = json.load(f)
            
            self.assertEqual(data["security_level"], "critical")
            self.assertIn("export_timestamp", data)
            self.assertEqual(len(data["entries"]), 2)
        finally:
            os.unlink(json_path)
    
    def test_export_csv(self):
        """Test exporting audit trail to CSV."""
        scorer = SecurityScorer(SecurityLevel.ELEVATED)
        scorer.calculate_score(100.0)
        scorer.calculate_score(200.0, previous_score=180.0)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            csv_path = f.name
        
        try:
            scorer.export_audit_trail_csv(csv_path)
            
            with open(csv_path, 'r') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
            
            self.assertEqual(len(rows), 2)
            self.assertIn('timestamp', rows[0])
            self.assertIn('adjusted_score', rows[0])
        finally:
            os.unlink(csv_path)


class TestIntegration(unittest.TestCase):
    """Integration tests for the security scoring system."""
    
    def test_end_to_end_with_config_file(self):
        """Test complete workflow: config loading + scoring + audit export."""
        # Create a config file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            config = {
                "multipliers": {
                    "critical": 0.6,
                    "elevated": 0.8,
                    "normal": 1.0
                }
            }
            json.dump(config, f)
            config_path = f.name
        
        # Create output files
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json_output = f.name
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            csv_output = f.name
        
        try:
            # Initialize scorer with config
            scorer = SecurityScorer(SecurityLevel.CRITICAL, config_file=config_path)
            
            # Perform multiple scoring operations
            score1 = scorer.calculate_score(100.0)
            score2 = scorer.calculate_score(250.0, previous_score=200.0)
            score3 = scorer.calculate_score(500.0, max_score=400.0)
            
            # Verify scores
            self.assertEqual(score1, 60.0)  # 100 * 0.6
            self.assertEqual(score2, 150.0)  # 250 * 0.6
            self.assertEqual(score3, 300.0)  # min(500 * 0.6, 400)
            
            # Verify audit trail
            trail = scorer.get_audit_trail()
            self.assertEqual(len(trail), 3)
            
            # Export to JSON
            scorer.export_audit_trail_json(json_output)
            with open(json_output, 'r') as f:
                json_data = json.load(f)
            self.assertEqual(len(json_data["entries"]), 3)
            
            # Export to CSV
            scorer.export_audit_trail_csv(csv_output)
            with open(csv_output, 'r') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
            self.assertEqual(len(rows), 3)
            
        finally:
            os.unlink(config_path)
            os.unlink(json_output)
            os.unlink(csv_output)
    
    def test_workflow_with_historical_tracking(self):
        """Test workflow with historical score tracking."""
        scorer = SecurityScorer(SecurityLevel.ELEVATED)
        
        # Simulate multiple runs with historical tracking
        previous = None
        for base in [100.0, 120.0, 90.0]:
            current = scorer.calculate_score(base, previous_score=previous)
            previous = current
        
        # Verify audit trail includes historical comparisons
        trail = scorer.get_audit_trail(detail_level="full")
        self.assertEqual(len(trail), 3)
        
        # First entry has no previous score
        self.assertNotIn("previous_score", trail[0])
        
        # Second and third entries have previous scores
        self.assertIn("previous_score", trail[1])
        self.assertIn("historical_delta", trail[1])
        self.assertIn("previous_score", trail[2])
        self.assertIn("historical_delta", trail[2])


if __name__ == '__main__':
    unittest.main()
