# Deployment Guide

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Deployment Scenarios](#deployment-scenarios)
5. [Best Practices](#best-practices)
6. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### System Requirements

- **Operating System**: Linux (Ubuntu 20.04+, RHEL 8+, or similar)
- **Python**: 3.8 or higher
- **Memory**: Minimum 2GB RAM
- **Disk Space**: 500MB for installation + logs
- **Network**: Starlink terminal with stable connection

### Dependencies

```bash
# Python 3.8+
python3 --version

# pip package manager
pip3 --version

# Git (for installation from source)
git --version
```

---

## Installation

### Option 1: From PyPI (Recommended for Production)

```bash
pip install secure-it-starlink
```

### Option 2: From Source

```bash
# Clone the repository
git clone https://github.com/danielnovais-tech/secure-it-infra-Starlink.git
cd secure-it-infra-Starlink

# Install in production mode
pip install .

# Or install in development mode
pip install -e .
```

### Option 3: Using Virtual Environment (Recommended)

```bash
# Create virtual environment
python3 -m venv starlink-env
source starlink-env/bin/activate  # On Windows: starlink-env\Scripts\activate

# Install the package
pip install secure-it-starlink

# Or from source
pip install -e /path/to/secure-it-infra-Starlink
```

---

## Configuration

### 1. Basic Configuration

Create a configuration file at `/etc/secure-it-starlink/config.yaml`:

```yaml
# Basic Security Configuration
encryption_enabled: true
cipher_suite: "AES-256-GCM"

authentication:
  mfa_enabled: true
  min_password_length: 12
  session_timeout_minutes: 30

network:
  segmentation_enabled: true
  firewall_enabled: true
  
logging:
  enabled: true
  level: "INFO"
  log_file: "/var/log/secure-it-starlink/security.log"
```

### 2. Environment-Specific Configuration

#### Development

```python
from secure_it_starlink.config import SecurityConfig

config = SecurityConfig({
    "logging": {"level": "DEBUG"},
    "monitoring": {"check_interval_seconds": 10}
})
```

#### Production

```python
from secure_it_starlink.config import SecurityConfig

config = SecurityConfig({
    "logging": {"level": "INFO"},
    "monitoring": {"check_interval_seconds": 60},
    "alerts": {
        "enabled": true,
        "notification_channels": ["email", "sms"]
    }
})
```

### 3. Set File Permissions

```bash
# Create directories
sudo mkdir -p /etc/secure-it-starlink
sudo mkdir -p /var/log/secure-it-starlink

# Set ownership
sudo chown -R starlink-user:starlink-group /etc/secure-it-starlink
sudo chown -R starlink-user:starlink-group /var/log/secure-it-starlink

# Set permissions
sudo chmod 750 /etc/secure-it-starlink
sudo chmod 640 /etc/secure-it-starlink/config.yaml
sudo chmod 750 /var/log/secure-it-starlink
```

---

## Deployment Scenarios

### Scenario 1: Single Starlink Terminal

```python
#!/usr/bin/env python3
from secure_it_starlink import NetworkMonitor, SecurityLogger, SecurityConfig

# Initialize
config = SecurityConfig()
logger = SecurityLogger("/var/log/secure-it-starlink/security.log")
monitor = NetworkMonitor()

# Start monitoring
monitor.start_monitoring()
logger.info("Monitoring started for single Starlink terminal")

# Check connection health periodically
import time
while True:
    health = monitor.check_connection_health()
    if health['status'] != 'healthy':
        logger.warning("Connection issue detected", health)
    time.sleep(60)
```

### Scenario 2: Multiple Terminals with Load Balancing

```python
#!/usr/bin/env python3
from secure_it_starlink import NetworkMonitor, SecurityLogger, AlertManager

monitors = {
    "terminal-1": NetworkMonitor({"terminal_id": "1"}),
    "terminal-2": NetworkMonitor({"terminal_id": "2"})
}

logger = SecurityLogger()
alert_manager = AlertManager()

# Monitor all terminals
for terminal_id, monitor in monitors.items():
    monitor.start_monitoring()
    health = monitor.check_connection_health()
    
    if health['status'] != 'healthy':
        alert_manager.create_alert(
            AlertSeverity.HIGH,
            f"Terminal {terminal_id} Unhealthy",
            f"Connection issue on {terminal_id}"
        )
```

### Scenario 3: Enterprise Infrastructure with Full Security

```python
#!/usr/bin/env python3
from secure_it_starlink import (
    NetworkMonitor, SecurityLogger, AlertManager,
    EncryptionManager, KeyManager, AccessController,
    AuthenticationManager, VulnerabilityScanner
)

# Full security stack
logger = SecurityLogger()
alert_manager = AlertManager()
network_monitor = NetworkMonitor()
encryptor = EncryptionManager()
key_manager = KeyManager()
access_controller = AccessController()
auth_manager = AuthenticationManager()
vuln_scanner = VulnerabilityScanner()

# Setup access control
access_controller.create_policy(
    "starlink-admin",
    resource="infrastructure",
    allowed_actions=["read", "write", "configure"],
    principals=["admin"]
)

# Periodic security scanning
def security_scan():
    config = SecurityConfig().get_config()
    results = vuln_scanner.scan_configuration(config)
    
    if results['vulnerabilities_found'] > 0:
        alert_manager.create_alert(
            AlertSeverity.CRITICAL,
            "Security Vulnerabilities Found",
            f"Found {results['vulnerabilities_found']} issues"
        )

# Run scan daily
import schedule
schedule.every().day.at("02:00").do(security_scan)
```

---

## Best Practices

### 1. Security Hardening

```bash
# Use strong encryption
config.set("cipher_suite", "AES-256-GCM")

# Enable MFA
config.set("authentication.mfa_enabled", True)

# Rotate keys regularly
key_manager.rotate_key("data-encryption-key")

# Enable audit logging
logger = SecurityLogger("/var/log/secure-it-starlink/audit.log")
```

### 2. Monitoring and Alerting

```python
# Set appropriate alert thresholds
alert_manager = AlertManager(alert_threshold=3)

# Configure multiple notification channels
config.update({
    "alerts": {
        "notification_channels": ["email", "sms", "webhook"]
    }
})

# Monitor continuously
monitor.start_monitoring()
```

### 3. Performance Optimization

```python
# Adjust monitoring intervals based on needs
network_monitor = NetworkMonitor({
    "check_interval_seconds": 60  # Production
    # "check_interval_seconds": 10  # Development
})

# Limit log retention
config.set("logging.retention_days", 90)
```

### 4. Backup and Recovery

```bash
# Backup configuration
cp /etc/secure-it-starlink/config.yaml \
   /backup/config.yaml.$(date +%Y%m%d)

# Backup encryption keys
# Store in secure location (encrypted)
```

---

## Troubleshooting

### Common Issues

#### Issue 1: Import Error

**Problem:**
```
ModuleNotFoundError: No module named 'secure_it_starlink'
```

**Solution:**
```bash
# Ensure package is installed
pip install secure-it-starlink

# Or reinstall
pip install --force-reinstall secure-it-starlink
```

#### Issue 2: Permission Denied

**Problem:**
```
PermissionError: [Errno 13] Permission denied: '/var/log/secure-it-starlink/security.log'
```

**Solution:**
```bash
# Fix permissions
sudo chown starlink-user /var/log/secure-it-starlink
sudo chmod 750 /var/log/secure-it-starlink
```

#### Issue 3: Connection Health Check Fails

**Problem:**
Network health checks always fail

**Solution:**
```python
# Check firewall rules
# Ensure outbound connections to 8.8.8.8:80 are allowed

# Use custom target
health = monitor.check_connection_health(target="1.1.1.1")

# Increase timeout
monitor = NetworkMonitor({"connection_timeout": 10})
```

### Logs and Debugging

```bash
# View logs
tail -f /var/log/secure-it-starlink/security.log

# Enable debug logging
config.set("logging.level", "DEBUG")

# Check system status
systemctl status secure-it-starlink  # If running as service
```

---

## Production Deployment Checklist

- [ ] Python 3.8+ installed
- [ ] Virtual environment created
- [ ] Package installed
- [ ] Configuration file created and secured
- [ ] Log directories created with proper permissions
- [ ] Encryption keys generated and backed up
- [ ] User accounts created
- [ ] Access policies configured
- [ ] Monitoring started
- [ ] Alerts configured and tested
- [ ] Firewall rules configured
- [ ] Backups scheduled
- [ ] Documentation updated
- [ ] Team trained on usage

---

## Support

For issues and questions:
- GitHub Issues: https://github.com/danielnovais-tech/secure-it-infra-Starlink/issues
- Documentation: See README.md and API.md
