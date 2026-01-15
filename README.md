# secure-it-infra-Starlink
Repository dedicated to security solutions for managed enterprise infrastructures supporting Starlink.

## Security Scoring System

This repository includes a security scoring system that adjusts scores based on security levels with advanced features including configurable multipliers, audit trails, and boundary handling.

### Features

- **Security Level Management**: Support for CRITICAL, ELEVATED, and NORMAL security levels
- **Score Adjustment**: Automatic score adjustment based on security level
  - CRITICAL: 70% of base score (0.7x multiplier)
  - ELEVATED: 90% of base score (0.9x multiplier)
  - NORMAL: 100% of base score (no adjustment)
- **Configurable Multipliers**: Override default multipliers via:
  - Custom multipliers dictionary
  - JSON configuration file
  - Environment-based configuration
- **Audit Trail**: Complete audit trail of all scoring operations with:
  - Reason for adjustment
  - Points change details
  - Original and adjusted scores
  - Security level applied
- **Boundary Handling**:
  - Zero scores remain zero regardless of multiplier
  - Optional max score cap for very high scores
  - Graceful handling of unknown security levels (defaults to 1.0x)
- **Input Validation**: Prevents negative base scores with appropriate error handling

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

# Get audit trail
audit_trail = scorer.get_audit_trail()
for entry in audit_trail:
    print(entry)
    # Output: {'reason': 'CRITICAL security level multiplier', 
    #          'points': '-30.0 (0.7x applied)', 
    #          'security_level': 'critical',
    #          'original_score': 100.0,
    #          'adjusted_score': 70.0}
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

All 21 tests should pass.

### Files

- `security_scoring.py`: Main module with SecurityLevel enum, SecurityScorer class, and AuditEntry class
- `test_security_scoring.py`: Comprehensive unit tests (21 test cases)
- `example.py`: Example usage demonstrations including all features
- `config.json`: Sample configuration file for custom multipliers
- `requirements.txt`: Project dependencies (Python 3.12+)

### API Reference

#### SecurityLevel (Enum)
- `CRITICAL`: Critical security level (default 0.7x multiplier)
- `ELEVATED`: Elevated security level (default 0.9x multiplier)
- `NORMAL`: Normal security level (1.0x multiplier)

#### SecurityScorer (Class)
- `__init__(security_level, custom_multipliers=None, config_file=None)`: Initialize scorer
- `calculate_score(base_score, max_score=None)`: Calculate adjusted score
- `get_audit_trail()`: Get list of audit entries
- `clear_audit_trail()`: Clear the audit trail

#### AuditEntry (Class)
- `to_dict()`: Convert audit entry to dictionary format
