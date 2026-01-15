# secure-it-infra-Starlink
Repository dedicated to security solutions for managed enterprise infrastructures supporting Starlink.

## Security Scoring System

This repository includes a security scoring system that adjusts scores based on security levels.

### Features

- **Security Level Management**: Support for CRITICAL, ELEVATED, and NORMAL security levels
- **Score Adjustment**: Automatic score adjustment based on security level
  - CRITICAL: 70% of base score (0.7x multiplier)
  - ELEVATED: 90% of base score (0.9x multiplier)
  - NORMAL: 100% of base score (no adjustment)

### Installation

No additional dependencies required. Uses Python 3.12+.

### Usage

```python
from security_scoring import SecurityLevel, SecurityScorer

# Create a scorer with a security level
scorer = SecurityScorer(SecurityLevel.CRITICAL)

# Calculate adjusted score
base_score = 100.0
adjusted_score = scorer.calculate_score(base_score)
print(f"Adjusted Score: {adjusted_score}")  # Output: 70.0
```

### Running Examples

```bash
python3 example.py
```

### Running Tests

```bash
python3 -m unittest test_security_scoring.py -v
```

### Files

- `security_scoring.py`: Main module with SecurityLevel enum and SecurityScorer class
- `test_security_scoring.py`: Comprehensive unit tests
- `example.py`: Example usage demonstrations
