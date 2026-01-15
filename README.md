# secure-it-infra-Starlink
Repository dedicated to security solutions for managed enterprise infrastructures supporting Starlink.

## Security Scoring System

This repository includes a comprehensive security scoring system that adjusts scores based on security levels with advanced features including configurable multipliers, audit trails, export capabilities, historical tracking, and schema validation.

### Features

- **Security Level Management**: Support for CRITICAL, ELEVATED, and NORMAL security levels
- **Score Adjustment**: Automatic score adjustment based on security level
  - CRITICAL: 70% of base score (0.7x multiplier)
  - ELEVATED: 90% of base score (0.9x multiplier)
  - NORMAL: 100% of base score (no adjustment)
- **Configurable Multipliers**: Override default multipliers via:
  - Custom multipliers dictionary
  - JSON configuration file with schema validation
  - Validates multipliers (non-negative, numeric)
  - Warns on unusual values (e.g., multipliers > 2.0)
- **Audit Trail**: Complete audit trail of all scoring operations with:
  - Reason for adjustment
  - Points change details
  - Original and adjusted scores
  - Security level applied
  - ISO timestamps
  - Historical comparison data
  - Configurable detail levels (summary/full)
- **Audit Trail Export**:
  - Export to JSON format for downstream analytics
  - Export to CSV format for dashboards and reporting
  - Preserves all audit metadata
- **Historical Comparison**:
  - Track score changes over time
  - Automatic delta calculation from previous runs
  - Narrative descriptions of changes
- **Boundary Handling**:
  - Zero scores remain zero regardless of multiplier
  - Optional max score cap for very high scores
  - Graceful handling of unknown security levels (defaults to 1.0x)
- **Input Validation**: 
  - Prevents negative base scores with appropriate error handling
  - Schema validation for configuration files
  - Clear error messages for misconfiguration

### Installation

No additional dependencies required. Uses Python 3.12+.

### Usage

#### Basic Usage

```python
from security_scoring import SecurityLevel, SecurityScorer

# Create a scorer with a security level
scorer = SecurityScorer(SecurityLevel.CRITICAL)

# Calculate adjusted score
base_score = 100.0
adjusted_score = scorer.calculate_score(base_score)
print(f"Adjusted Score: {adjusted_score}")  # Output: 70.0
```

#### Using Custom Multipliers

```python
# Define custom multipliers
custom_multipliers = {
    SecurityLevel.CRITICAL: 0.5,
    SecurityLevel.ELEVATED: 0.75,
}

scorer = SecurityScorer(SecurityLevel.CRITICAL, custom_multipliers=custom_multipliers)
score = scorer.calculate_score(100.0)  # Returns 50.0
```

#### Using Configuration File

Create a `config.json` file:
```json
{
  "multipliers": {
    "critical": 0.6,
    "elevated": 0.85,
    "normal": 1.0
  }
}
```

Then use it:
```python
scorer = SecurityScorer(SecurityLevel.CRITICAL, config_file="config.json")
score = scorer.calculate_score(100.0)
```

#### Audit Trail Integration

```python
scorer = SecurityScorer(SecurityLevel.CRITICAL)
scorer.calculate_score(100.0)
scorer.calculate_score(250.0)

# Get audit trail with full detail
audit_trail = scorer.get_audit_trail(detail_level="full")
for entry in audit_trail:
    print(entry)
    # Output includes: reason, points, security_level, original_score,
    #                  adjusted_score, timestamp, and historical_delta

# Get summary view
summary = scorer.get_audit_trail(detail_level="summary")
# Returns only reason and adjusted_score for each entry
```

**Example Output - Full Detail:**
```python
[
  {
    'reason': 'CRITICAL security level multiplier',
    'points': '-30.0 (0.7x applied)',
    'security_level': 'critical',
    'original_score': 100.0,
    'adjusted_score': 70.0,
    'timestamp': '2026-01-15T16:00:00.123456'
  },
  {
    'reason': 'CRITICAL security level multiplier',
    'points': '-75.0 (0.7x applied)',
    'security_level': 'critical',
    'original_score': 250.0,
    'adjusted_score': 175.0,
    'timestamp': '2026-01-15T16:00:01.234567'
  }
]
```

**Example Output - Summary Detail:**
```python
[
  {'reason': 'CRITICAL security level multiplier', 'adjusted_score': 70.0},
  {'reason': 'CRITICAL security level multiplier', 'adjusted_score': 175.0}
]
```

#### Historical Comparison

```python
scorer = SecurityScorer(SecurityLevel.ELEVATED)

# Track changes over multiple runs
previous_score = None
for base in [100.0, 120.0, 90.0]:
    current = scorer.calculate_score(base, previous_score=previous_score)
    previous_score = current

# Audit trail includes historical deltas
trail = scorer.get_audit_trail()
# Entry format: "ELEVATED security level multiplier (Score increased by 18.0 compared to last run)"
```

**Example Output:**
```python
[
  {
    'reason': 'ELEVATED security level multiplier',
    'points': '-10.0 (0.9x applied)',
    'security_level': 'elevated',
    'original_score': 100.0,
    'adjusted_score': 90.0,
    'timestamp': '2026-01-15T16:00:00.000000'
  },
  {
    'reason': 'ELEVATED security level multiplier (Score increased by 18.0 compared to last run)',
    'points': '-12.0 (0.9x applied)',
    'security_level': 'elevated',
    'original_score': 120.0,
    'adjusted_score': 108.0,
    'timestamp': '2026-01-15T16:00:01.000000',
    'previous_score': 90.0,
    'historical_delta': 18.0
  },
  {
    'reason': 'ELEVATED security level multiplier (Score decreased by 27.0 compared to last run)',
    'points': '-9.0 (0.9x applied)',
    'security_level': 'elevated',
    'original_score': 90.0,
    'adjusted_score': 81.0,
    'timestamp': '2026-01-15T16:00:02.000000',
    'previous_score': 108.0,
    'historical_delta': -27.0
  }
]
```

#### Exporting Audit Trail

```python
scorer = SecurityScorer(SecurityLevel.CRITICAL)
scorer.calculate_score(100.0, previous_score=120.0)
scorer.calculate_score(250.0, previous_score=180.0)

# Export to JSON for analytics
scorer.export_audit_trail_json("audit_log.json", detail_level="full")

# Export to CSV for dashboards
scorer.export_audit_trail_csv("audit_log.csv")
```

**JSON Export Example Output:**
```json
{
  "security_level": "critical",
  "export_timestamp": "2026-01-15T16:00:00.000000",
  "entries": [
    {
      "reason": "CRITICAL security level multiplier (Score decreased by 50.0 compared to last run)",
      "points": "-30.0 (0.7x applied)",
      "security_level": "critical",
      "original_score": 100.0,
      "adjusted_score": 70.0,
      "timestamp": "2026-01-15T16:00:00.000000",
      "previous_score": 120.0,
      "historical_delta": -50.0
    },
    {
      "reason": "CRITICAL security level multiplier (Score increased by 5.0 compared to last run)",
      "points": "-75.0 (0.7x applied)",
      "security_level": "critical",
      "original_score": 250.0,
      "adjusted_score": 175.0,
      "timestamp": "2026-01-15T16:00:01.000000",
      "previous_score": 180.0,
      "historical_delta": -5.0
    }
  ]
}
```

**CSV Export Example Output:**
```csv
timestamp,reason,points,security_level,original_score,adjusted_score,previous_score,historical_delta
2026-01-15T16:00:00.000000,CRITICAL security level multiplier (Score decreased by 50.0 compared to last run),-30.0 (0.7x applied),critical,100.0,70.0,120.0,-50.0
2026-01-15T16:00:01.000000,CRITICAL security level multiplier (Score increased by 5.0 compared to last run),-75.0 (0.7x applied),critical,250.0,175.0,180.0,-5.0
```

#### Configuration File with Schema Validation

Create a `config.json` file with validation:
```json
{
  "multipliers": {
    "critical": 0.6,
    "elevated": 0.85,
    "normal": 1.0
  }
}
```

The system validates:
- All security levels are valid (critical, elevated, normal)
- All multipliers are numeric
- All multipliers are non-negative
- Warns if multipliers are unusually high (> 2.0)

```python
from security_scoring import SecurityScorer, ConfigValidationError

try:
    scorer = SecurityScorer(SecurityLevel.CRITICAL, config_file="config.json")
    score = scorer.calculate_score(100.0)
except ConfigValidationError as e:
    print(f"Invalid configuration: {e}")
```

#### Boundary Cases

```python
scorer = SecurityScorer(SecurityLevel.CRITICAL)

# Zero score remains zero
zero_score = scorer.calculate_score(0.0)  # Returns 0.0

# Very high score with max cap
capped_score = scorer.calculate_score(10000.0, max_score=500.0)  # Returns 500.0

# Very high score without cap
uncapped_score = scorer.calculate_score(10000.0)  # Returns 7000.0
```

### Running Examples

```bash
python3 example.py
```

### Running Tests

```bash
python3 -m unittest test_security_scoring.py -v
```

All 34 tests should pass, including:
- Config schema validation tests
- Audit trail export tests (JSON/CSV)
- Historical comparison tests
- Detail level tests
- Integration tests

### Files

- `security_scoring.py`: Main module with SecurityLevel enum, SecurityScorer class, AuditEntry class, and config validation
- `test_security_scoring.py`: Comprehensive unit tests (34 test cases) including integration tests
- `example.py`: Example usage demonstrations including all features (8 scenarios)
- `config.json`: Sample configuration file for custom multipliers
- `requirements.txt`: Project dependencies (Python 3.12+)

### API Reference

#### SecurityLevel (Enum)
- `CRITICAL`: Critical security level (default 0.7x multiplier)
- `ELEVATED`: Elevated security level (default 0.9x multiplier)
- `NORMAL`: Normal security level (1.0x multiplier)

#### SecurityScorer (Class)
- `__init__(security_level, custom_multipliers=None, config_file=None)`: Initialize scorer
  - Raises `ConfigValidationError` if config file is invalid
- `calculate_score(base_score, max_score=None, previous_score=None)`: Calculate adjusted score
  - `previous_score`: Optional previous score for historical comparison
- `get_audit_trail(detail_level="full")`: Get list of audit entries
  - `detail_level`: "summary" or "full"
- `clear_audit_trail()`: Clear the audit trail
- `export_audit_trail_json(filepath, detail_level="full")`: Export audit trail to JSON
- `export_audit_trail_csv(filepath)`: Export audit trail to CSV

#### AuditEntry (Class)
- `to_dict(detail_level="full")`: Convert audit entry to dictionary format
  - Returns different fields based on detail_level

#### Utility Functions
- `validate_config_schema(config)`: Validate configuration dictionary
  - Raises `ConfigValidationError` for invalid configs

### Integration Tests

The test suite includes integration tests that verify the complete workflow:

```python
# Example integration test workflow
scorer = SecurityScorer(SecurityLevel.CRITICAL, config_file="config.json")
score1 = scorer.calculate_score(100.0)
score2 = scorer.calculate_score(250.0, previous_score=200.0)
score3 = scorer.calculate_score(500.0, max_score=400.0)
scorer.export_audit_trail_json("output.json")
scorer.export_audit_trail_csv("output.csv")
```

This ensures the entire pipeline (config loading → scoring → audit tracking → export) works correctly.

## Roadmap

### ✅ Implemented (Current Release)

- **Core Functionality**
  - Security level enumeration (CRITICAL, ELEVATED, NORMAL)
  - Score adjustment with configurable multipliers
  - Dictionary-based multiplier lookup
  
- **Configuration & Validation**
  - JSON configuration file support
  - Schema validation with `ConfigValidationError`
  - Custom multiplier overrides
  - Non-negative multiplier validation
  - Warnings for unusual values

- **Audit Trail System**
  - Complete audit logging with timestamps
  - Historical comparison tracking
  - Configurable verbosity levels (summary/full)
  - Export to JSON format
  - Export to CSV format
  
- **Robustness**
  - Input validation (negative score prevention)
  - Graceful handling of unknown security levels
  - Optional max score capping
  - Boundary case handling (zero scores, very high scores)
  
- **Testing & Quality**
  - 34 comprehensive unit tests
  - Integration tests for complete workflows
  - CodeQL security scanning (0 vulnerabilities)
  - Python 3.12+ compatibility

### 🔮 Planned (Future Enhancements)

- **Internationalization (i18n)**
  - Multi-language support for audit trail messages
  - Localized error messages
  
- **Dashboard Integration**
  - Real-time monitoring connectors
  - Grafana/Prometheus integration
  - REST API endpoints
  
- **Performance Optimization**
  - Benchmarking under high-volume scoring
  - Batch scoring operations
  - Async scoring support
  
- **Advanced Features**
  - Custom scoring algorithms
  - Machine learning-based threat level prediction
  - Automated threshold tuning
  
- **Enterprise Features**
  - Role-based access control
  - Multi-tenancy support
  - Compliance reporting (SOC2, ISO 27001)

### 💡 Contributions Welcome

We welcome contributions in any of the planned areas or new feature suggestions. Please open an issue to discuss major changes before submitting a pull request.
