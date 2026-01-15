# Deployment Guide for Starlink Security Auditor

## Overview
This guide covers deploying the Starlink Security Auditor in various enterprise environments, with special focus on remote/rural Starlink deployments.

## Deployment Scenarios

### 1. Single Server Deployment

**Use Case**: Small office or branch location with Starlink connectivity

**Steps**:
1. Install on the Starlink gateway server:
```bash
cd /opt
sudo git clone https://github.com/danielnovais-tech/secure-it-infra-Starlink.git
cd secure-it-infra-Starlink
sudo chmod +x starlink_security_auditor.py
```

2. Create local configuration:
```bash
sudo cp config.example.json /etc/starlink-security/config.json
sudo nano /etc/starlink-security/config.json
```

3. Schedule regular audits with cron:
```bash
sudo crontab -e
# Add: 0 2 * * * /opt/secure-it-infra-Starlink/starlink_security_auditor.py -c /etc/starlink-security/config.json
```

### 2. Multi-Site Deployment

**Use Case**: Enterprise with multiple Starlink-connected locations

**Central Management Setup**:
1. Deploy auditor on each site
2. Configure central log collection:
```json
{
  "logging": {
    "file": "/var/log/starlink-security/audit.log",
    "remote_syslog": "central-siem.company.com:514"
  }
}
```

3. Centralize reports:
```bash
# On each site, add to cron:
0 3 * * * /opt/secure-it-infra-Starlink/starlink_security_auditor.py && \
  scp security_audit_report.json central-server:/reports/$(hostname)-$(date +\%Y\%m\%d).json
```

### 3. Container Deployment

**Use Case**: Kubernetes or Docker-based infrastructure

**Create Dockerfile**:
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY starlink_security_auditor.py .
COPY config.example.json ./config.json

# Install system dependencies
RUN apt-get update && apt-get install -y \
    iproute2 \
    iptables \
    net-tools \
    && rm -rf /var/lib/apt/lists/*

CMD ["python3", "starlink_security_auditor.py", "--config", "config.json"]
```

**Build and Run**:
```bash
docker build -t starlink-security-auditor:latest .
docker run --privileged --network host \
  -v /etc:/etc:ro \
  -v /var/log:/var/log:rw \
  starlink-security-auditor:latest
```

### 4. Automated CI/CD Integration

**Use Case**: Include security audits in deployment pipeline

**GitLab CI Example**:
```yaml
security_audit:
  stage: test
  script:
    - python3 starlink_security_auditor.py --config ci-config.json
  artifacts:
    reports:
      junit: security_audit_report.json
  allow_failure: false
```

## Configuration Management

### Environment-Specific Configurations

**Development Environment**:
```json
{
  "audit_scope": {
    "network_security": true,
    "service_vulnerabilities": true,
    "encryption_validation": false,
    "vpn_validation": false
  },
  "logging": {
    "level": "DEBUG"
  }
}
```

**Production Environment**:
```json
{
  "audit_scope": {
    "network_security": true,
    "service_vulnerabilities": true,
    "encryption_validation": true,
    "vpn_validation": true,
    "network_segmentation": true,
    "privilege_checks": true
  },
  "logging": {
    "level": "INFO"
  },
  "starlink_settings": {
    "require_vpn": true
  }
}
```

## Integration Options

### 1. SIEM Integration

**Splunk**:
```bash
# Configure Splunk forwarder
/opt/splunkforwarder/bin/splunk add monitor /var/log/starlink-security/
```

**ELK Stack**:
```yaml
# Filebeat configuration
filebeat.inputs:
- type: log
  paths:
    - /var/log/starlink-security/audit.log
  json.keys_under_root: true
```

### 2. Alerting Integration

**Email Alerts**:
```bash
#!/bin/bash
# audit-and-alert.sh
/opt/secure-it-infra-Starlink/starlink_security_auditor.py
if [ $? -eq 1 ]; then
  mail -s "Security Audit FAILED" admin@company.com < security_audit_report.json
fi
```

**Slack Integration**:
```bash
#!/bin/bash
# audit-and-slack.sh
/opt/secure-it-infra-Starlink/starlink_security_auditor.py
if [ $? -ne 0 ]; then
  curl -X POST -H 'Content-type: application/json' \
    --data '{"text":"Security audit issues detected!"}' \
    $SLACK_WEBHOOK_URL
fi
```

### 3. Ticketing System Integration

**JIRA**:
```python
# Example integration script
import json
from jira import JIRA

with open('security_audit_report.json') as f:
    report = json.load(f)

jira = JIRA('https://jira.company.com', basic_auth=('user', 'token'))

for result in report['audit_results']:
    if result['status'] == 'FAIL':
        jira.create_issue(
            project='SEC',
            summary=f"Security Issue: {result['check_name']}",
            description=result['message'],
            issuetype={'name': 'Bug'}
        )
```

## High Availability Setup

### Active-Passive Configuration

**Primary Server**:
```bash
# Run audits and sync to standby
0 2 * * * /opt/secure-it-infra-Starlink/starlink_security_auditor.py && \
  rsync -avz /var/log/starlink-security/ standby:/var/log/starlink-security/
```

**Standby Server**:
- Keep auditor installed and configured
- Monitor primary health
- Take over if primary fails

## Starlink-Specific Deployment Considerations

### 1. Bandwidth Optimization
- Schedule audits during off-peak hours
- Compress report transmissions
- Use incremental updates

### 2. Latency Handling
- Increase timeout values in config
- Use asynchronous report submission
- Local caching before transmission

### 3. Connectivity Resilience
```bash
#!/bin/bash
# resilient-audit.sh
MAX_RETRIES=3
RETRY_DELAY=300

for i in $(seq 1 $MAX_RETRIES); do
  /opt/secure-it-infra-Starlink/starlink_security_auditor.py
  if [ $? -eq 0 ] || [ $? -eq 2 ]; then
    # Success or warnings only
    scp security_audit_report.json central-server:/reports/ && break
  fi
  sleep $RETRY_DELAY
done
```

### 4. VPN-First Architecture
Ensure VPN is established before running audits:
```bash
#!/bin/bash
# vpn-then-audit.sh
while ! ping -c 1 vpn.company.com &> /dev/null; do
  echo "Waiting for VPN..."
  sleep 10
done

/opt/secure-it-infra-Starlink/starlink_security_auditor.py
```

## Security Hardening for Deployment

### 1. File Permissions
```bash
sudo chown root:root /opt/secure-it-infra-Starlink/starlink_security_auditor.py
sudo chmod 750 /opt/secure-it-infra-Starlink/starlink_security_auditor.py
sudo chown root:root /etc/starlink-security/config.json
sudo chmod 600 /etc/starlink-security/config.json
```

### 2. Log Protection
```bash
sudo mkdir -p /var/log/starlink-security
sudo chown root:adm /var/log/starlink-security
sudo chmod 750 /var/log/starlink-security
```

### 3. Report Security
```bash
# Encrypt reports before transmission
gpg --encrypt --recipient admin@company.com security_audit_report.json
scp security_audit_report.json.gpg central-server:/reports/
```

## Monitoring and Maintenance

### Health Checks
```bash
#!/bin/bash
# audit-health-check.sh
if [ ! -f /var/log/starlink-security/audit.log ]; then
  echo "ERROR: Audit log not found"
  exit 1
fi

# Check if audit ran in last 25 hours
LAST_RUN=$(stat -c %Y /var/log/starlink-security/audit.log)
NOW=$(date +%s)
if [ $((NOW - LAST_RUN)) -gt 90000 ]; then
  echo "WARNING: Audit hasn't run recently"
  exit 2
fi
```

### Log Rotation
```bash
# /etc/logrotate.d/starlink-security
/var/log/starlink-security/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 640 root adm
}
```

## Troubleshooting

### Common Issues

**Issue**: Permission denied errors
**Solution**: 
```bash
# Run with sudo or add user to required groups
sudo usermod -aG adm,systemd-journal audit-user
```

**Issue**: Network checks timeout over Starlink
**Solution**:
```json
{
  "network_checks": {
    "timeout_seconds": 60
  }
}
```

**Issue**: VPN check fails intermittently
**Solution**:
```bash
# Ensure VPN service dependencies
sudo systemctl enable openvpn@client
sudo systemctl start openvpn@client
```

## Rollback Procedures

### Version Rollback
```bash
cd /opt/secure-it-infra-Starlink
git log --oneline  # Find previous version
git checkout <commit-hash>
```

### Configuration Rollback
```bash
# Keep config backups
sudo cp /etc/starlink-security/config.json \
  /etc/starlink-security/config.json.$(date +%Y%m%d)
```

## Upgrade Path

### Minor Updates
```bash
cd /opt/secure-it-infra-Starlink
git pull origin main
# Review changes
python3 starlink_security_auditor.py --help
```

### Major Updates
1. Test in development environment
2. Backup current configuration
3. Review migration guide
4. Update configuration if needed
5. Deploy to production during maintenance window

## Support and Resources

- Documentation: README.md, ARCHITECTURE.md
- Issue Tracking: GitHub Issues
- Configuration Examples: config.example.json
- Community: GitHub Discussions
