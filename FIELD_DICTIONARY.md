# Log Schema Field Dictionary

This document defines all fields in the Starlink Security structured log schema with ownership and governance information.

## Schema Version: 1.0.0

### Core Required Fields

| Field | Type | Owner | Description | Examples | Privacy |
|-------|------|-------|-------------|----------|---------|
| `schema_version` | string | Platform Team | Version of the log schema (semver) | `1.0.0` | PUBLIC |
| `timestamp` | string (ISO 8601) | Platform Team | When the log was generated | `2026-01-16T19:29:09.456Z` | PUBLIC |
| `logger` | string | Application Team | Logger name that generated the entry | `starlink-security.auth` | PUBLIC |
| `level` | string (enum) | Platform Team | Log severity level | `INFO`, `ERROR`, `DEBUG` | PUBLIC |
| `module` | string | Application Team | Source code module | `starlink_security` | PUBLIC |
| `line` | integer | Application Team | Source code line number | `42`, `156` | PUBLIC |
| `message` | string | Application Team | Human-readable log message | `User login successful` | VARIES |
| `service` | string | Platform Team | Service name in ecosystem | `starlink-security` | PUBLIC |
| `component` | string | Application Team | Component/subsystem within service | `authentication`, `telemetry` | PUBLIC |

### Correlation & Tracing Fields

| Field | Type | Owner | Description | Examples | Privacy |
|-------|------|-------|-------------|----------|---------|
| `correlation_id` | string | Platform Team | ID for tracing across distributed systems | `req-12345`, `trace-abc123` | INTERNAL |
| `request_id` | string | API Team | Request identifier for HTTP/API calls | `req-12345-67890` | INTERNAL |
| `session_id` | string | Auth Team | Session identifier for user sessions | `sess-abc123` | PII |
| `user_id` | string | Auth Team | User identifier (email/username/system ID) | `user@example.com` | PII |

### Privacy & Security Fields

| Field | Type | Owner | Description | Examples | Privacy |
|-------|------|-------|-------------|----------|---------|
| `privacy_tags` | array[string] | Security Team | Data sensitivity/privacy tags | `["PII", "CONFIDENTIAL"]` | PUBLIC |
| `error_code` | string | Platform Team | Standardized error code | `SEC-001`, `AUTH-002` | PUBLIC |
| `ip_address` | string | Infrastructure Team | IP address (IPv4/IPv6) | `192.168.1.100` | PII |

### Environment & Infrastructure Fields

| Field | Type | Owner | Description | Examples | Privacy |
|-------|------|-------|-------------|----------|---------|
| `environment` | string (enum) | Platform Team | Deployment environment | `production`, `staging` | PUBLIC |
| `hostname` | string | Infrastructure Team | Hostname or pod name | `starlink-sec-pod-123` | INTERNAL |
| `process_id` | integer | Platform Team | Process ID | `1234` | INTERNAL |
| `thread_id` | integer | Platform Team | Thread ID | `140234567890` | INTERNAL |

### Operation & Performance Fields

| Field | Type | Owner | Description | Examples | Privacy |
|-------|------|-------|-------------|----------|---------|
| `duration_ms` | number | Application Team | Operation duration in milliseconds | `123.45`, `1500.0` | PUBLIC |
| `status_code` | integer | API Team | HTTP status or operation result code | `200`, `404`, `500` | PUBLIC |
| `resource` | string | Application Team | Resource being accessed/modified | `/api/admin`, `/data/satellite` | INTERNAL |
| `action` | string (enum) | Security Team | Action being performed | `LOGIN`, `UPDATE`, `READ` | PUBLIC |
| `result` | string (enum) | Application Team | Result of the action | `SUCCESS`, `FAILURE` | PUBLIC |

### Error & Debug Fields

| Field | Type | Owner | Description | Examples | Privacy |
|-------|------|-------|-------------|----------|---------|
| `exception` | string | Application Team | Exception stacktrace | `Traceback (most recent call last)...` | VARIES |
| `metadata` | object | Application Team | Additional context-specific data | `{"satellite_id": "sat-1234"}` | VARIES |
| `tags` | array[string] | Application Team | Arbitrary categorization tags | `["security", "audit"]` | PUBLIC |

## Field Ownership & Governance

### Platform Team
- **Responsibility**: Core schema structure, versioning, validation
- **Contact**: platform-team@starlink-security.example.com
- **Decision Authority**: Schema version changes, required field additions
- **SLA**: Schema change requests reviewed within 2 business days

### Security Team
- **Responsibility**: Privacy tags, error codes, audit requirements
- **Contact**: security-team@starlink-security.example.com
- **Decision Authority**: Privacy tag definitions, error code standards
- **SLA**: Security field changes reviewed within 1 business day

### Application Team
- **Responsibility**: Application-specific fields, message content
- **Contact**: app-team@starlink-security.example.com
- **Decision Authority**: Component names, message formats, metadata structure
- **SLA**: Application field requests reviewed within 3 business days

### Infrastructure Team
- **Responsibility**: Infrastructure-related fields (hostname, IP addresses)
- **Contact**: infra-team@starlink-security.example.com
- **Decision Authority**: Infrastructure field additions
- **SLA**: Infrastructure field requests reviewed within 2 business days

### API Team
- **Responsibility**: API-related fields (request_id, status_code)
- **Contact**: api-team@starlink-security.example.com
- **Decision Authority**: API field standards
- **SLA**: API field requests reviewed within 2 business days

### Auth Team
- **Responsibility**: Authentication/authorization fields (user_id, session_id)
- **Contact**: auth-team@starlink-security.example.com
- **Decision Authority**: User identity field standards
- **SLA**: Auth field requests reviewed within 1 business day (security-critical)

## Privacy Tag Definitions

| Tag | Definition | Retention | Access Level | Example Use Cases |
|-----|------------|-----------|--------------|-------------------|
| `PII` | Personally Identifiable Information | 90 days | Restricted | user_id, email, ip_address |
| `PHI` | Protected Health Information | 7 years | Highly Restricted | Medical/health data |
| `CONFIDENTIAL` | Business confidential data | 1 year | Restricted | Configuration changes, system secrets |
| `INTERNAL` | Internal use only | 180 days | Internal | Service names, internal IPs |
| `PUBLIC` | Publicly shareable data | Unlimited | Public | Error codes, log levels |
| `REDACTED` | Data has been redacted/sanitized | Unlimited | Internal | Sanitized passwords, tokens |
| `ENCRYPTED` | Data is encrypted in the log | Per encryption key | Authorized | Encrypted sensitive data |

## Error Code Ownership

| Prefix | Category | Owner | Examples |
|--------|----------|-------|----------|
| `SEC-*` | Security violations | Security Team | SEC-001, SEC-002, SEC-003 |
| `AUTH-*` | Authentication/Authorization | Auth Team | AUTH-001, AUTH-002, AUTH-003 |
| `NET-*` | Network errors | Infrastructure Team | NET-001, NET-002, NET-003 |
| `CFG-*` | Configuration errors | Platform Team | CFG-001, CFG-002 |
| `SYS-*` | System errors | Platform Team | SYS-001, SYS-002 |

## Change Management Process

### Adding a New Field

1. **Proposal**: Submit PR with field definition and justification
2. **Review**: Relevant team reviews based on ownership (see SLAs above)
3. **Approval**: Requires approval from field owner and Platform Team
4. **Documentation**: Update this field dictionary and schema
5. **Migration**: If breaking change, increment schema version and provide migration guide
6. **Rollout**: Coordinate rollout with all logging services

### Modifying an Existing Field

1. **Impact Analysis**: Assess impact on existing logs, dashboards, alerts
2. **Proposal**: Submit PR with modification and migration plan
3. **Review**: Field owner + Platform Team review
4. **Backward Compatibility**: Maintain compatibility or increment schema version
5. **Communication**: Notify all teams 2 weeks before change
6. **Migration**: Execute migration plan for existing logs if needed

### Deprecating a Field

1. **Proposal**: Submit PR with deprecation notice and timeline
2. **Review**: Field owner + Platform Team review
3. **Timeline**: Minimum 90 days deprecation period
4. **Documentation**: Mark as deprecated in schema and docs
5. **Monitoring**: Track usage of deprecated field
6. **Removal**: Remove from schema in next major version

## Schema Versioning

### Version Format: MAJOR.MINOR.PATCH

- **MAJOR**: Breaking changes (required field changes, field removal)
- **MINOR**: New optional fields, enum value additions
- **PATCH**: Documentation updates, clarifications

### Current Version: 1.0.0

### Version History

| Version | Date | Changes | Migration Required |
|---------|------|---------|-------------------|
| 1.0.0 | 2026-01-16 | Initial schema release | N/A |

### Upcoming Changes

None currently planned.

## Best Practices

### For Application Developers

1. **Always include schema_version**: Set to current schema version (1.0.0)
2. **Tag PII appropriately**: Add `["PII"]` to privacy_tags when logging user-identifiable data
3. **Use standard error codes**: Don't create ad-hoc codes, use ErrorCode class
4. **Include correlation IDs**: Always pass correlation_id for distributed tracing
5. **Minimize metadata**: Only include necessary context in metadata field
6. **Sanitize sensitive data**: Never log passwords, tokens, or secrets

### For Data Engineers

1. **Validate on ingest**: Use validate_logs.py to reject invalid entries
2. **Handle schema versions**: Support multiple schema versions during transitions
3. **Respect privacy tags**: Apply appropriate retention/access policies
4. **Monitor schema drift**: Alert on non-conforming logs

### For Security Team

1. **Audit privacy tags**: Regularly review logs for proper PII tagging
2. **Review error codes**: Ensure error codes are used consistently
3. **Monitor sensitive data**: Alert on potential sensitive data leakage
4. **Enforce encryption**: Require encryption for sensitive log fields

## Compliance & Retention

### GDPR Compliance

- **PII**: Automatically redact/delete after 90 days
- **Right to erasure**: Implement user_id-based log deletion
- **Access logs**: Track who accesses logs containing PII

### SOC 2 Compliance

- **Audit logs**: Retain logs with security events for 1 year
- **Access control**: Implement RBAC for log access
- **Encryption**: Encrypt logs at rest and in transit

### PCI-DSS Compliance

- **Cardholder data**: Never log full credit card numbers
- **Access logs**: Retain access logs for 1 year minimum
- **Tampering**: Use cryptographic verification (see AUDIT_TRAIL_DESIGN.md)

## Tools & Automation

### Validation

```bash
# Validate logs in CI
python validate_logs.py --file logs/application.log --strict

# Validate stdin (for real-time validation)
tail -f logs/application.log | python validate_logs.py --stdin
```

### Linting

```bash
# Future: Linter to check for common issues
# - Missing privacy tags on PII fields
# - Non-standard error codes
# - Message quality (too long, unclear)
```

### Migration

```bash
# Future: Migration tool for schema version changes
# python migrate_logs.py --from 1.0.0 --to 2.0.0 --input old.log --output new.log
```

## Contact & Support

- **Schema Questions**: platform-team@starlink-security.example.com
- **Field Requests**: Submit PR to this repository
- **Security Concerns**: security-team@starlink-security.example.com
- **Emergency Changes**: platform-oncall@starlink-security.example.com

## References

- JSON Schema Specification: https://json-schema.org/
- Schema File: `schemas/structured-log-v1.0.0.json`
- Validator: `validate_logs.py`
- Logging Documentation: `LOGGING.md`
- Audit Trail Design: `AUDIT_TRAIL_DESIGN.md`
