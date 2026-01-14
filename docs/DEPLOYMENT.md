# Deployment Guide

This guide explains how to safely deploy infrastructure changes to the Secure IT Starlink infrastructure using controlled environments.

## Table of Contents

- [Overview](#overview)
- [Environment Strategy](#environment-strategy)
- [Prerequisites](#prerequisites)
- [Deployment Process](#deployment-process)
- [Safety Mechanisms](#safety-mechanisms)
- [Rollback Procedures](#rollback-procedures)
- [Troubleshooting](#troubleshooting)

## Overview

The infrastructure uses a multi-environment deployment strategy to ensure changes are tested before reaching production. This approach minimizes disruptions and allows for safe experimentation and validation.

## Environment Strategy

### 1. Development (dev)
- **Purpose**: Rapid development and experimentation
- **CIDR**: 10.0.0.0/16
- **Approval**: Not required
- **Use Case**: Testing new features, configurations, and infrastructure changes

### 2. Staging (staging)
- **Purpose**: Pre-production testing and validation
- **CIDR**: 10.1.0.0/16
- **Approval**: Recommended
- **Use Case**: Integration testing, performance testing, and final validation before production

### 3. Production (production)
- **Purpose**: Live infrastructure serving real traffic
- **CIDR**: 10.2.0.0/16
- **Approval**: **Required** with multiple confirmations
- **Use Case**: Production workloads only

## Prerequisites

Before deploying, ensure you have:

1. **Terraform installed** (version >= 1.0)
   ```bash
   terraform --version
   ```

2. **AWS credentials configured**
   ```bash
   aws configure
   ```

3. **Appropriate permissions** for the target environment

4. **Repository cloned locally**
   ```bash
   git clone https://github.com/danielnovais-tech/secure-it-infra-Starlink.git
   cd secure-it-infra-Starlink
   ```

## Deployment Process

### Standard Deployment Flow

Always follow this progression to avoid disruptions:

```
Development → Staging → Production
```

### Step-by-Step Deployment

#### 1. Deploy to Development

```bash
# Plan changes
./scripts/deploy.sh dev plan

# Review the plan output carefully

# Apply changes
./scripts/deploy.sh dev apply
```

#### 2. Test in Development

Validate that your changes work as expected:
- Test all new features
- Verify connectivity
- Check security configurations
- Monitor logs and metrics

#### 3. Deploy to Staging

Once validated in dev:

```bash
# Plan changes
./scripts/deploy.sh staging plan

# Review the plan output carefully

# Apply changes
./scripts/deploy.sh staging apply
```

#### 4. Integration Testing in Staging

Perform comprehensive testing:
- End-to-end testing
- Performance testing
- Security scanning
- Integration with other services

#### 5. Deploy to Production

**CRITICAL**: Only deploy to production after successful staging validation.

```bash
# Plan changes
./scripts/deploy.sh production plan

# CAREFULLY review the plan output
# Share with team if necessary

# Apply changes (requires confirmation)
./scripts/deploy.sh production apply
```

You will be prompted multiple times to confirm production deployments.

### Using GitHub Actions

For automated deployments via CI/CD:

1. Navigate to **Actions** tab in GitHub
2. Select **Deploy to Environments** workflow
3. Click **Run workflow**
4. Choose:
   - Environment (dev/staging/production)
   - Action (plan/apply)
5. Click **Run workflow**

## Safety Mechanisms

### 1. Multi-Environment Isolation

Each environment has:
- Separate VPCs with different CIDR blocks
- Isolated security groups
- Independent state files
- Environment-specific tags

### 2. Confirmation Prompts

Production deployments require:
- Initial confirmation prompt
- Additional confirmation for destructive actions
- Typed confirmation for destroy operations

### 3. Plan Before Apply

The deployment script enforces:
- Terraform plan generation
- Validation checks
- Format verification
- Review before application

### 4. Automated Validation

GitHub Actions workflows automatically:
- Validate Terraform syntax
- Check formatting
- Run security scans (tfsec)
- Perform linting (tflint)
- Generate plans for review

### 5. State Management

- State files track infrastructure state
- Automatic backups before changes
- Rollback capability using state backups

## Rollback Procedures

If issues occur after deployment:

### Option 1: Automated Rollback

```bash
./scripts/rollback.sh <environment>
```

This script will:
1. Show current infrastructure state
2. List available state backups
3. Offer rollback options
4. Restore previous state if selected

### Option 2: Manual Rollback

1. Revert code changes:
   ```bash
   git revert <commit-hash>
   ```

2. Deploy the reverted code:
   ```bash
   ./scripts/deploy.sh <environment> plan
   ./scripts/deploy.sh <environment> apply
   ```

### Option 3: Targeted Fix

If only specific resources are affected:

1. Modify only the problematic resource
2. Run targeted plan:
   ```bash
   cd terraform/environments/<environment>
   terraform plan -target=<resource>
   ```
3. Apply targeted fix:
   ```bash
   terraform apply -target=<resource>
   ```
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

#### 1. Terraform State Lock

**Problem**: State file is locked by another process

**Solution**:
```bash
cd terraform/environments/<environment>
terraform force-unlock <lock-id>
```

#### 2. Validation Failures

**Problem**: `terraform validate` fails

**Solution**:
- Check error messages carefully
- Verify variable definitions
- Ensure module sources are correct
- Run `terraform init` again

#### 3. AWS Credentials Issues

**Problem**: Authentication failures

**Solution**:
```bash
# Verify credentials
aws sts get-caller-identity

# Reconfigure if needed
aws configure
```

#### 4. Plan Shows Unexpected Changes

**Problem**: Terraform plan shows unintended modifications

**Solution**:
- **DO NOT APPLY** until you understand the changes
- Review recent code modifications
- Check for manual changes in AWS console
- Consult with team members
- Consider using `terraform refresh` to sync state

### Getting Help

1. Check Terraform documentation: https://www.terraform.io/docs
2. Review AWS provider documentation: https://registry.terraform.io/providers/hashicorp/aws
3. Check GitHub Issues for similar problems
4. Contact the infrastructure team

## Best Practices

1. **Always plan before apply**: Never skip the planning phase
2. **Test in dev first**: Experiment freely in development
3. **Validate in staging**: Treat staging like production for testing
4. **Communicate production changes**: Notify team before production deployments
5. **Monitor after deployment**: Watch logs and metrics after applying changes
6. **Keep state backups**: Ensure state files are backed up regularly
7. **Document changes**: Update documentation when infrastructure changes
8. **Use version control**: Commit infrastructure changes to git
9. **Review plans carefully**: Understand what will change before applying
10. **Have a rollback plan**: Know how to revert before deploying

## Security Considerations

- Never commit AWS credentials to git
- Use IAM roles with least privilege
- Enable MFA for production deployments (when implemented)
- Regularly review security group rules
- Keep Terraform and provider versions updated
- Run security scans before deployment
- Audit access to production environments
- Encrypt state files (when using remote backend)

## Next Steps

After successful deployment:

1. Configure remote backend for state management (S3 + DynamoDB)
2. Implement environment protection rules in GitHub
3. Set up monitoring and alerting
4. Configure automated backups
5. Implement disaster recovery procedures
6. Document runbooks for common operations

---

**Remember**: The goal is to avoid disruptions. When in doubt, test in dev, validate in staging, then carefully deploy to production.
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
