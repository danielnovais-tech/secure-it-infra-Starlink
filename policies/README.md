# Privacy Policy Enforcement Profiles

This directory contains privacy enforcement policy files that define rules for validating log entries across different environments. Policies are environment-specific and compliance-framework-aware.

## Available Policies

### Production (`privacy_policy_production.json`)
- **Enforcement**: Strict
- **Compliance**: GDPR, HIPAA, PCI-DSS, SOC2, ISO27001
- **PII/PHI**: Must be tagged and redacted
- **Use**: Production environments, regulatory audits

### Staging (`privacy_policy_staging.json`)
- **Enforcement**: Moderate
- **Compliance**: GDPR, SOC2
- **PII/PHI**: Must be tagged and redacted
- **Use**: Pre-production testing, integration testing

### Development (`privacy_policy_development.json`)
- **Enforcement**: Lenient
- **Compliance**: None
- **PII/PHI**: Warnings only
- **Use**: Local development, debugging

## Usage

```bash
# Validate with production policy
python validate_logs.py \\
  --file logs/app.log \\
  --privacy-policy policies/privacy_policy_production.json

# Generate audit report
python validate_logs.py \\
  --file logs/app.log \\
  --privacy-policy policies/privacy_policy_production.json \\
  --generate-audit-report
```

## Policy Schema

Each policy file follows this structure:

- `enforcement_level`: strict | moderate | lenient
- `pii_fields`: Configuration for PII detection and enforcement
- `phi_fields`: Configuration for PHI (health data) enforcement
- `confidential_fields`: Configuration for secrets/credentials
- `pattern_detection`: Regex patterns for sensitive data detection
- `redaction_markers`: Accepted redaction markers
- `compliance`: Compliance framework requirements
- `reporting`: Audit report configuration

## Creating Custom Policies

1. Copy an existing policy file
2. Modify enforcement rules as needed
3. Update `profile_name` and `description`
4. Test with regression suite:
   ```bash
   python tests/privacy_regression/test_privacy_enforcement.py --policy custom
   ```

## Policy Versioning

Policies use semantic versioning:
- **MAJOR**: Breaking changes to enforcement rules
- **MINOR**: New fields or patterns added
- **PATCH**: Bug fixes, documentation updates

## Documentation

See [POLICY_DRIVEN_PRIVACY.md](../POLICY_DRIVEN_PRIVACY.md) for complete documentation.
