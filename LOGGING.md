# Logging Configuration

This document describes the structured logging features in the Starlink Security Infrastructure application.

## Features

### 1. Configurable Log Levels

Control the verbosity of logs using the `STARLINK_LOG_LEVEL` environment variable:

```bash
# Production (minimal logs)
export STARLINK_LOG_LEVEL=WARNING
python starlink_security.py

# Development (detailed logs)
export STARLINK_LOG_LEVEL=DEBUG
python starlink_security.py

# Default (balanced)
python starlink_security.py  # Uses INFO by default
```

**Available levels:** DEBUG, INFO, WARNING, ERROR, CRITICAL

### 2. Log Rotation & Retention

Logs automatically rotate to prevent disk space issues:

- **Max file size:** 10 MB per log file
- **Backup count:** 7 files (approximately 7 days of logs)
- **Total disk usage:** ~70 MB maximum

When a log file reaches 10 MB, it's renamed to `starlink_security.log.1`, and a new file is created. Older backups are automatically deleted when the count exceeds 7.

### 3. Structured Output Formats

#### Standard Format (Default)

Human-readable format for development and debugging:

```
2026-01-16 19:29:02,029 - starlink-security - INFO - starlink_security:98 - Starlink Security Infrastructure starting...
```

#### JSON Format

Machine-readable format for log management tools (Splunk, ELK, Datadog):

```bash
export STARLINK_LOG_FORMAT=json
python starlink_security.py
```

Output:
```json
{"timestamp": "2026-01-16 19:29:07,668", "logger": "starlink-security", "level": "INFO", "module": "starlink_security", "line": 98, "message": "Starlink Security Infrastructure starting..."}
```

### 4. Correlation IDs & Contextual Metadata

Add request IDs, session IDs, or user IDs for distributed tracing:

```python
# Example usage
extra = {'request_id': 'req-12345', 'user_id': 'user-67890'}
logger.info("Processing request", extra=extra)
```

JSON output includes the metadata:
```json
{"timestamp": "...", "logger": "starlink-security", "level": "INFO", "message": "Processing request", "request_id": "req-12345", "user_id": "user-67890"}
```

### 5. Security Considerations

**Important:** Never log sensitive data such as:
- Passwords or password hashes
- API keys or tokens
- Personal Identifiable Information (PII)
- Credit card numbers
- Session tokens

Always sanitize data before logging.

### 6. Environment-Specific Directories

The application automatically selects appropriate directories:

**Production (with write access to /etc):**
- Config: `/etc/starlink-security`
- Data: `/var/lib/starlink-security`
- Logs: `/var/log/starlink-security`

**Development/Testing (without system access):**
- Config: `./config`
- Data: `./data`
- Logs: `./logs`

## Configuration Summary

| Environment Variable | Default | Options | Description |
|---------------------|---------|---------|-------------|
| `STARLINK_LOG_LEVEL` | `INFO` | DEBUG, INFO, WARNING, ERROR, CRITICAL | Controls log verbosity |
| `STARLINK_LOG_FORMAT` | `standard` | standard, json | Output format |

## Best Practices

1. **Development:** Use `DEBUG` level with `standard` format
   ```bash
   STARLINK_LOG_LEVEL=DEBUG python starlink_security.py
   ```

2. **Production:** Use `INFO` or `WARNING` level with `json` format
   ```bash
   STARLINK_LOG_LEVEL=INFO STARLINK_LOG_FORMAT=json python starlink_security.py
   ```

3. **Troubleshooting:** Temporarily enable `DEBUG` level
   ```bash
   STARLINK_LOG_LEVEL=DEBUG python starlink_security.py
   ```

4. **Monitoring Integration:** Use JSON format to pipe logs to monitoring tools
   ```bash
   STARLINK_LOG_FORMAT=json python starlink_security.py | your-log-shipper
   ```

## Future Enhancements

- Integration with monitoring/alerting systems (Slack, PagerDuty)
- Custom log filters for sensitive data sanitization
- Performance metrics logging
- Distributed tracing integration
