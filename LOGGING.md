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
| `STARLINK_ASYNC_LOGGING` | `false` | true, false | Enable async logging for high throughput |
| `STARLINK_SYSLOG_ADDRESS` | None | host:port or /path/to/socket | Send logs to syslog server |
| `STARLINK_HTTP_LOG_ENDPOINT` | None | http://host/path | Send logs to HTTP endpoint |

## Advanced Features

### Per-Module Debug Logging

Enable DEBUG level for specific modules while keeping others at INFO:

```python
import logging

# Set global level to INFO
logging.getLogger().setLevel(logging.INFO)

# Enable DEBUG for specific module
logging.getLogger('starlink-security.auth').setLevel(logging.DEBUG)
logging.getLogger('starlink-security.network').setLevel(logging.DEBUG)

# Now only auth and network modules will show DEBUG logs
```

Example usage:
```bash
# In your application code
auth_logger = logging.getLogger('starlink-security.auth')
network_logger = logging.getLogger('starlink-security.network')

auth_logger.debug("Detailed authentication flow")  # Will be shown
network_logger.debug("Packet details")  # Will be shown
logger.debug("General debug")  # Won't be shown (still at INFO)
```

### Structured Error Codes

Use standardized error codes for easier filtering and alerting:

```python
from starlink_security import ErrorCode, logger

# Security error
logger.error(
    "Unauthorized access attempt detected",
    extra={'error_code': ErrorCode.SEC_002, 'ip_address': '192.168.1.100'}
)

# Authentication error
logger.warning(
    "Invalid credentials provided",
    extra={'error_code': ErrorCode.AUTH_002, 'username': 'user@example.com'}
)
```

**Available Error Codes:**
- **SEC-001**: Security violation detected
- **SEC-002**: Unauthorized access attempt
- **SEC-003**: Data integrity check failed
- **AUTH-001**: Authentication failed
- **AUTH-002**: Invalid credentials
- **AUTH-003**: Token expired
- **AUTH-004**: Permission denied
- **NET-001**: Connection timeout
- **NET-002**: Network unreachable
- **NET-003**: Satellite link down
- **CFG-001**: Invalid configuration
- **CFG-002**: Missing required parameter
- **SYS-001**: Service startup failed
- **SYS-002**: Resource exhausted

### Dynamic Runtime Reconfiguration

Change log level without restarting the application:

**Option 1: Signal-based (Unix/Linux)**
```bash
# Find the process ID
ps aux | grep starlink_security

# Toggle between INFO and DEBUG
kill -USR1 <pid>
```

**Option 2: Programmatic**
```python
from starlink_security import set_log_level

# Change to DEBUG for troubleshooting
set_log_level('DEBUG')

# Change back to INFO
set_log_level('INFO')
```

### Async Logging for High Throughput

Enable async logging to avoid I/O blocking in performance-critical scenarios:

```bash
export STARLINK_ASYNC_LOGGING=true
python starlink_security.py
```

This uses `QueueHandler` + `QueueListener` to process logs in a separate thread.

### Centralized Logging Integration

**Ship logs to Syslog:**
```bash
export STARLINK_SYSLOG_ADDRESS=localhost:514
export STARLINK_LOG_FORMAT=json
python starlink_security.py
```

**Ship logs to HTTP endpoint:**
```bash
export STARLINK_HTTP_LOG_ENDPOINT=http://logs.example.com/ingest
export STARLINK_LOG_FORMAT=json
python starlink_security.py
```

**Combine with existing handlers:**
All configured handlers work simultaneously:
- Local file (with rotation)
- Console output
- Syslog (if configured)
- HTTP endpoint (if configured)

## Sample JSON Log Entries

### Standard Application Log
```json
{
  "timestamp": "2026-01-16 19:29:07,668",
  "logger": "starlink-security",
  "level": "INFO",
  "module": "starlink_security",
  "line": 98,
  "message": "Starlink Security Infrastructure starting..."
}
```

### Log with Correlation IDs
```json
{
  "timestamp": "2026-01-16 19:29:08,123",
  "logger": "starlink-security",
  "level": "INFO",
  "module": "api",
  "line": 42,
  "message": "Processing user request",
  "request_id": "req-12345",
  "user_id": "user-67890",
  "session_id": "sess-abc123"
}
```

### Error with Structured Error Code
```json
{
  "timestamp": "2026-01-16 19:29:09,456",
  "logger": "starlink-security",
  "level": "ERROR",
  "module": "security",
  "line": 156,
  "message": "Unauthorized access attempt detected",
  "error_code": "SEC-002",
  "user_id": "user-67890",
  "ip_address": "192.168.1.100",
  "resource": "/admin/settings"
}
```

### Exception Log
```json
{
  "timestamp": "2026-01-16 19:29:10,789",
  "logger": "starlink-security",
  "level": "ERROR",
  "module": "database",
  "line": 89,
  "message": "Database connection failed",
  "error_code": "SYS-001",
  "exception": "Traceback (most recent call last):\n  File ...\nConnectionError: Unable to connect to database"
}
```

## Best Practices

1. **Development:** Use `DEBUG` level with `standard` format
   ```bash
   STARLINK_LOG_LEVEL=DEBUG python starlink_security.py
   ```

2. **Production:** Use `INFO` or `WARNING` level with `json` format
   ```bash
   STARLINK_LOG_LEVEL=INFO STARLINK_LOG_FORMAT=json python starlink_security.py
   ```

3. **High-Performance Production:** Enable async logging
   ```bash
   STARLINK_LOG_LEVEL=INFO STARLINK_LOG_FORMAT=json STARLINK_ASYNC_LOGGING=true python starlink_security.py
   ```

4. **Troubleshooting Production:** Use signal to temporarily enable DEBUG
   ```bash
   # Find PID
   ps aux | grep starlink_security
   
   # Toggle to DEBUG
   kill -USR1 <pid>
   
   # Toggle back to INFO
   kill -USR1 <pid>
   ```

5. **Monitoring Integration:** Ship to centralized logging with JSON format
   ```bash
   STARLINK_LOG_FORMAT=json \
   STARLINK_SYSLOG_ADDRESS=logs.example.com:514 \
   STARLINK_ASYNC_LOGGING=true \
   python starlink_security.py
   ```

6. **Per-Module Debugging:** Enable DEBUG only for specific modules
   ```python
   import logging
   
   # Keep root at INFO
   logging.getLogger().setLevel(logging.INFO)
   
   # Debug specific modules
   logging.getLogger('starlink-security.auth').setLevel(logging.DEBUG)
   ```

7. **Always include context:** Use error codes and correlation IDs
   ```python
   logger.error(
       "Operation failed",
       extra={
           'error_code': ErrorCode.NET_001,
           'request_id': request_id,
           'operation': 'satellite_connect'
       }
   )
   ```

## Future Enhancements

- ✅ Centralized logging integration (SysLog, HTTP)
- ✅ Dynamic runtime reconfiguration (signal-based)
- ✅ Structured error codes
- ✅ Async logging for performance
- 📝 Audit trail with immutable logging (planned)
- 📝 Integration with monitoring/alerting systems (Slack, PagerDuty)
- 📝 Custom log filters for sensitive data sanitization
- 📝 Performance metrics logging
- 📝 Distributed tracing integration (OpenTelemetry)
