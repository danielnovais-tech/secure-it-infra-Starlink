# Schema Evolution & Privacy Enforcement Playbook

This document describes how to evolve the structured log schema over time while maintaining backward compatibility and enforcing privacy requirements.

## Table of Contents

1. [Schema Evolution Process](#schema-evolution-process)
2. [Privacy Tag Enforcement](#privacy-tag-enforcement)
3. [Backward Compatibility Testing](#backward-compatibility-testing)
4. [Field Deprecation](#field-deprecation)
5. [Migration Strategies](#migration-strategies)
6. [Operational Procedures](#operational-procedures)

## Schema Evolution Process

### Version Numbering

The schema follows **semantic versioning (semver)**:

- **MAJOR version** (1.0.0 → 2.0.0): Breaking changes
  - Removing required fields
  - Changing field types
  - Removing enum values
  - Making optional fields required

- **MINOR version** (1.0.0 → 1.1.0): Backward-compatible additions
  - Adding optional fields
  - Adding new enum values
  - Relaxing validation constraints

- **PATCH version** (1.0.0 → 1.0.1): Documentation and clarifications
  - Fixing typos in descriptions
  - Adding examples
  - Clarifying field intent

### Schema Change Workflow

```
1. Proposal
   ├─ Create RFC document
   ├─ Identify impact (breaking vs. non-breaking)
   └─ Estimate migration effort

2. Review & Approval
   ├─ Field owner review (1-3 business days)
   ├─ Platform team review (required)
   └─ Security team review (for privacy-sensitive changes)

3. Implementation
   ├─ Update schema file
   ├─ Update field dictionary
   ├─ Add backward compatibility tests
   └─ Update documentation

4. Testing
   ├─ Validate against historical samples
   ├─ Test with lenient mode
   └─ Run full validation suite

5. Deployment
   ├─ Publish new schema version
   ├─ Notify all teams (2 weeks notice for breaking changes)
   ├─ Deploy with grace period
   └─ Monitor adoption metrics
```

## Privacy Tag Enforcement

### Overview

The validator includes privacy tag enforcement to ensure sensitive data is properly handled, especially in production environments.

### Privacy Tags

| Tag | Definition | Enforcement Level |
|-----|------------|-------------------|
| `PII` | Personally Identifiable Information | STRICT in production |
| `PHI` | Protected Health Information | STRICT everywhere |
| `CONFIDENTIAL` | Business confidential data | MODERATE |
| `INTERNAL` | Internal use only | MODERATE |
| `PUBLIC` | Publicly shareable | None |
| `REDACTED` | Data has been redacted | Exempts from PII/PHI checks |
| `ENCRYPTED` | Data is encrypted | Exempts from pattern checks |

### PII-Suspect Fields

The following fields are automatically checked for PII tagging:

```python
PII_SUSPECT_FIELDS = {
    'user_id', 'email', 'username', 'name', 'phone', 'ssn',
    'ip_address', 'session_id', 'user_agent', 'address',
    'location', 'coordinates', 'device_id'
}
```

### PHI-Suspect Fields

```python
PHI_SUSPECT_FIELDS = {
    'patient_id', 'medical_record', 'diagnosis', 'prescription',
    'health_data', 'biometric'
}
```

### Sensitive Patterns

The validator scans for these patterns in production logs:

- **Email**: `\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b`
- **SSN**: `\b\d{3}-\d{2}-\d{4}\b`
- **Credit Card**: `\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b`
- **Phone**: `\b\d{3}[-.]?\d{3}[-.]?\d{4}\b`
- **IPv4**: `\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b`

### Usage Examples

#### Strict Mode (Production)

```bash
# Reject logs with unredacted PII in production
python validate_logs.py --file logs/production.log \
    --enforce-privacy \
    --environment production \
    --strict
```

**Example Rejection:**

```json
{
  "schema_version": "1.0.0",
  "timestamp": "2026-01-16T20:00:00Z",
  "logger": "starlink-security",
  "level": "INFO",
  "module": "auth",
  "line": 42,
  "message": "User login",
  "service": "starlink-security",
  "component": "authentication",
  "user_id": "john.doe@example.com",  // ❌ Email detected in production
  "environment": "production"
  // ❌ Missing privacy_tags
}
```

**Error:**
```
Field 'user_id' likely contains PII but missing PII or REDACTED tag (privacy_tags: [])
Field 'user_id' in production environment appears to contain unredacted PII: 'john.doe@example.co...'
```

#### Lenient Mode (Development)

```bash
# Allow unredacted PII in development with warnings
python validate_logs.py --file logs/development.log \
    --enforce-privacy \
    --environment development \
    --lenient
```

**Example Warning:**

```json
{
  "schema_version": "1.0.0",
  "timestamp": "2026-01-16T20:00:00Z",
  "logger": "starlink-security",
  "level": "DEBUG",
  "module": "auth",
  "line": 42,
  "message": "Debugging user session",
  "service": "starlink-security",
  "component": "authentication",
  "user_id": "developer@localhost",
  "environment": "development",
  "privacy_tags": []
}
```

**Warning:**
```
⚠️  Field 'user_id' likely contains PII but missing PII or REDACTED tag (privacy_tags: [])
```

#### Correct Example

```json
{
  "schema_version": "1.0.0",
  "timestamp": "2026-01-16T20:00:00Z",
  "logger": "starlink-security",
  "level": "INFO",
  "module": "auth",
  "line": 42,
  "message": "User login successful",
  "service": "starlink-security",
  "component": "authentication",
  "user_id": "user-12345",  // ✅ Redacted ID
  "environment": "production",
  "privacy_tags": ["PII", "REDACTED"]  // ✅ Properly tagged
}
```

### Privacy Enforcement Rules

1. **Production/Staging Environments**:
   - PII-suspect fields MUST have `PII` or `REDACTED` tag
   - PHI-suspect fields MUST have `PHI` or `REDACTED` tag
   - Message field is scanned for sensitive patterns
   - Violations are ERRORS (fail validation)

2. **Development/Test Environments**:
   - PII/PHI tagging recommended but not required
   - Violations are WARNINGS (with `--lenient`)

3. **Redaction Markers**:
   - Fields containing `***`, `REDACTED`, `[REDACTED]`, `XXX`, `####` are considered redacted
   - `ENCRYPTED` tag bypasses pattern matching

## Backward Compatibility Testing

### Purpose

Ensures that schema changes don't break existing log processing, dashboards, or alerts by validating historical log samples against the new schema.

### Directory Structure

```
tests/
└── fixtures/
    └── legacy_logs/
        ├── v0.9.0/
        │   ├── sample_auth_logs.json
        │   ├── sample_api_logs.json
        │   └── sample_system_logs.log
        ├── v1.0.0/
        │   └── complete_samples.json
        └── edge_cases/
            ├── minimal_required_fields.json
            └── all_optional_fields.json
```

### Running Backward Compatibility Tests

```bash
# Test all legacy samples against current schema
python validate_logs.py \
    --test-backward-compatibility \
    --samples tests/fixtures/legacy_logs \
    --lenient
```

**Output:**

```
📊 Backward Compatibility Test Results:
   Compatible: 15
   Incompatible: 2
   Total Samples: 17

❌ Incompatible Samples:

   File: tests/fixtures/legacy_logs/v0.9.0/old_format.json
   Errors:
     - Entry 0: Missing required field: 'schema_version'
     - Entry 0: Missing required field: 'service'
   Warnings:
     - Entry 0: Field 'log_level' does not match pattern...
```

### Creating Test Samples

1. **Collect Representative Samples**:
   ```bash
   # Extract samples from production logs
   head -100 /var/log/starlink-security/production.log > \
       tests/fixtures/legacy_logs/v1.0.0/prod_samples.log
   ```

2. **Organize by Version**:
   - Create directory for each schema version
   - Include at least 3-5 representative samples per version
   - Cover different log levels, components, and edge cases

3. **Document Expected Behavior**:
   ```json
   // tests/fixtures/legacy_logs/README.md
   {
     "v0.9.0": {
       "status": "deprecated",
       "expected_result": "incompatible",
       "notes": "Missing required fields: schema_version, service"
     },
     "v1.0.0": {
       "status": "current",
       "expected_result": "compatible",
       "notes": "All samples should validate"
     }
   }
   ```

### Interpreting Results

- **Compatible**: Sample validates successfully against current schema
- **Incompatible**: Sample has validation errors
  - In **strict mode**: All errors fail the test
  - In **lenient mode**: Only missing required fields fail

### CI Integration

```yaml
# .github/workflows/schema-validation.yml
name: Schema Validation

on: [push, pull_request]

jobs:
  backward-compatibility:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Test Backward Compatibility
        run: |
          python validate_logs.py \
            --test-backward-compatibility \
            --samples tests/fixtures/legacy_logs \
            --lenient
      
      - name: Report Results
        if: failure()
        run: echo "Schema changes broke backward compatibility!"
```

## Field Deprecation

### Deprecation Timeline

**Phase 1: Announcement (Release N)**
- Mark field as deprecated in schema
- Add `"deprecated": true` to field definition
- Update field dictionary with deprecation notice
- Notify all teams

**Phase 2: Warning Period (Release N+1)**
- Validator emits warnings for deprecated field usage
- Field remains functional
- Minimum duration: 90 days

**Phase 3: Removal (Release N+2)**
- Remove field from schema (MAJOR version bump)
- Validator errors on deprecated field usage
- Provide migration guide

### Example Deprecation

**Release 1.0.0** (Current):
```json
{
  "user_name": {
    "type": "string",
    "description": "User name (DEPRECATED: use 'user_id' instead)",
    "deprecated": true,
    "maxLength": 256
  }
}
```

**Release 1.1.0** (Warning Period):
```bash
# Validator output
⚠️  Field 'user_name' is deprecated and will be removed in v2.0.0
   Please use 'user_id' instead
```

**Release 2.0.0** (Removal):
```bash
# Validator output
❌ Field 'user_name' is not allowed (removed in v2.0.0)
   Migration guide: https://docs.starlink-security.com/migration/v2.0.0
```

### Deprecation Checklist

- [ ] Add deprecation notice to schema
- [ ] Update field dictionary
- [ ] Create GitHub issue tracking deprecation
- [ ] Notify all teams (minimum 2 weeks notice)
- [ ] Add deprecation warning to validator
- [ ] Create migration guide
- [ ] Monitor usage metrics
- [ ] Remove after grace period (minimum 90 days)

## Migration Strategies

### Strategy 1: Dual Writing (Recommended)

Support both old and new fields during transition period.

```python
# Application code
logger.info(
    "User action",
    extra={
        # New field (preferred)
        'user_id': 'user-12345',
        # Old field (deprecated, for backward compatibility)
        'user_name': 'user-12345',
        # Both fields present during migration
    }
)
```

### Strategy 2: Field Mapping

Use middleware to transform old format to new format.

```python
def migrate_log_entry(old_entry):
    """Migrate v0.9.0 log to v1.0.0 format."""
    new_entry = old_entry.copy()
    
    # Add required fields
    new_entry['schema_version'] = '1.0.0'
    new_entry['service'] = 'starlink-security'
    new_entry['component'] = infer_component(old_entry)
    
    # Rename fields
    if 'user_name' in old_entry:
        new_entry['user_id'] = old_entry['user_name']
        del new_entry['user_name']
    
    # Add privacy tags
    new_entry['privacy_tags'] = infer_privacy_tags(new_entry)
    
    return new_entry
```

### Strategy 3: Schema Transformation Pipeline

For large-scale migrations, use a transformation pipeline.

```bash
# Migration script
#!/bin/bash

# Read old logs, transform, validate, write new logs
cat old_format.log | \
    python transform_logs.py --from v0.9.0 --to v1.0.0 | \
    python validate_logs.py --stdin --strict | \
    tee new_format.log
```

## Operational Procedures

### Monthly Schema Review

- Review field usage metrics
- Identify unused or underutilized fields
- Propose deprecations for next quarter
- Update field dictionary

### Quarterly Cleanup

- Remove deprecated fields (if grace period elapsed)
- Archive old schema versions
- Update backward compatibility test samples
- Review and update privacy tag compliance

### Breaking Change Deployment

1. **T-14 days**: Announce breaking change
2. **T-7 days**: Deploy new schema to staging
3. **T-3 days**: Final testing and validation
4. **T-0 days**: Deploy to production
5. **T+7 days**: Monitor for errors, provide support
6. **T+30 days**: Remove compatibility shims

### Emergency Rollback

If a schema change causes critical issues:

```bash
# 1. Revert to previous schema version
cp schemas/structured-log-v1.0.0.json schemas/structured-log-v1.1.0.json

# 2. Update default schema path
sed -i 's/v1.1.0/v1.0.0/g' validate_logs.py

# 3. Notify teams
echo "Schema rolled back to v1.0.0 due to compatibility issues"

# 4. Root cause analysis
# 5. Fix and re-deploy with extended testing
```

## Best Practices

1. **Always Test Backward Compatibility**
   - Run tests before every schema change
   - Maintain representative sample set
   - Use lenient mode during migrations

2. **Enforce Privacy in CI**
   - Production logs must pass privacy validation
   - Development logs can use lenient mode
   - Never commit unredacted PII to version control

3. **Gradual Rollout**
   - Deploy schema changes to 10% of services first
   - Monitor for errors
   - Gradually increase to 100% over 1-2 weeks

4. **Version Everything**
   - Schema files
   - Validator code
   - Migration scripts
   - Documentation

5. **Communicate Early and Often**
   - 2-week notice minimum for breaking changes
   - Provide migration guides
   - Host office hours for questions
   - Monitor Slack/email for issues

## Tools & Automation

### Validator Modes Summary

| Mode | Use Case | Behavior |
|------|----------|----------|
| **Strict** | CI/Production | Fail on first error |
| **Lenient** | Development/Migration | Warnings instead of errors |
| **Privacy Enforcement** | Production logs | Reject unredacted PII |
| **Backward Compatibility** | Schema changes | Validate against historical samples |

### Example CI Pipeline

```yaml
# Complete validation pipeline
validate-all:
  script:
    # 1. Schema syntax validation
    - python -m json.tool schemas/structured-log-v1.0.0.json > /dev/null
    
    # 2. Backward compatibility
    - python validate_logs.py --test-backward-compatibility --samples tests/fixtures/legacy_logs
    
    # 3. Privacy enforcement (staging/prod logs)
    - python validate_logs.py --file logs/staging.log --enforce-privacy --environment staging --strict
    
    # 4. Standard validation
    - python validate_logs.py --file logs/application.log --strict
```

## Troubleshooting

### Common Issues

**Issue**: Backward compatibility test fails after minor version bump
**Solution**: Check if new required fields were added (should be MAJOR version bump)

**Issue**: Privacy validation flags legitimate uses
**Solution**: Add `REDACTED` or appropriate privacy tag, or use lenient mode in dev/test

**Issue**: Migration breaks existing dashboards
**Solution**: Use dual writing strategy to support both old and new fields during transition

## References

- JSON Schema Specification: https://json-schema.org/
- Field Dictionary: `FIELD_DICTIONARY.md`
- CI Integration Guide: `CI_INTEGRATION.md`
- Logging Documentation: `LOGGING.md`
- Privacy Tags: `FIELD_DICTIONARY.md#privacy-tag-definitions`
