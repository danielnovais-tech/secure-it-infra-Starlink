# Quick Start Guide

This guide will help you get started with the VPN Manager for Starlink infrastructure security.

## Prerequisites

Before you begin, ensure you have:

1. **Python 3.7 or higher** installed
2. **OpenVPN** or **WireGuard** installed on your system
3. **Root/sudo permissions** for VPN management (not required for status checks)
4. A valid VPN configuration file

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/danielnovais-tech/secure-it-infra-Starlink.git
   cd secure-it-infra-Starlink
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Basic Configuration

1. **Edit the configuration file:**
   ```bash
   nano config/vpn_config.yaml
   ```

2. **Update these key settings:**
   - `vpn.connection.type`: Set to `"openvpn"` or `"wireguard"`
   - `vpn.connection.config_file`: Path to your VPN config file
   - `vpn.monitoring.check_interval`: How often to check status (seconds)

## Quick Commands

### Check VPN Status
```bash
python main.py status
```

This will show:
- Whether VPN is connected
- Health status
- Connection name
- Timestamp

### Connect to VPN
```bash
sudo python main.py connect
```

**Note:** Requires sudo/root permissions.

### Start Monitoring (Recommended)
```bash
sudo python main.py monitor
```

This will:
- Check VPN status every 30 seconds (configurable)
- Automatically reconnect if VPN drops
- Log all events
- Press Ctrl+C to stop

### Disconnect from VPN
```bash
sudo python main.py disconnect
```

## Example Workflows

### Scenario 1: First-Time Setup for OpenVPN

1. Install OpenVPN:
   ```bash
   sudo apt-get install openvpn  # Ubuntu/Debian
   ```

2. Place your VPN config file:
   ```bash
   sudo cp client.ovpn /etc/openvpn/client.conf
   ```

3. Update config/vpn_config.yaml:
   ```yaml
   vpn:
     enabled: true
     connection:
       type: "openvpn"
       config_file: "/etc/openvpn/client.conf"
   ```

4. Start monitoring:
   ```bash
   sudo python main.py monitor
   ```

### Scenario 2: First-Time Setup for WireGuard

1. Install WireGuard:
   ```bash
   sudo apt-get install wireguard  # Ubuntu/Debian
   ```

2. Place your WireGuard config:
   ```bash
   sudo cp wg0.conf /etc/wireguard/wg0.conf
   ```

3. Update config/vpn_config.yaml:
   ```yaml
   vpn:
     enabled: true
     connection:
       type: "wireguard"
       config_file: "/etc/wireguard/wg0.conf"
   ```

4. Start monitoring:
   ```bash
   sudo python main.py monitor
   ```

### Scenario 3: Running as a System Service

For production use, run the VPN manager as a systemd service:

1. Create service file `/etc/systemd/system/vpn-manager.service`:
   ```ini
   [Unit]
   Description=VPN Manager for Starlink Infrastructure
   After=network.target

   [Service]
   Type=simple
   User=root
   WorkingDirectory=/path/to/secure-it-infra-Starlink
   ExecStart=/usr/bin/python3 /path/to/secure-it-infra-Starlink/main.py monitor
   Restart=always
   RestartSec=10

   [Install]
   WantedBy=multi-user.target
   ```

2. Enable and start the service:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable vpn-manager
   sudo systemctl start vpn-manager
   ```

3. Check service status:
   ```bash
   sudo systemctl status vpn-manager
   ```

## Configuration Tips

### Adjust Monitoring Frequency
For more frequent checks, reduce `check_interval`:
```yaml
monitoring:
  check_interval: 10  # Check every 10 seconds
```

### Increase Retry Attempts
For unreliable connections:
```yaml
monitoring:
  max_reconnect_attempts: 10
  reconnect_delay: 15
```

### Health Check Configuration
Test against multiple hosts:
```yaml
health_check:
  enabled: true
  test_hosts:
    - "8.8.8.8"      # Google DNS
    - "1.1.1.1"      # Cloudflare DNS
    - "internal.corp.example.com"  # Your internal server
  timeout: 5
  failure_threshold: 3
```

### Logging
Enable file logging for troubleshooting:
```yaml
monitoring:
  enable_logging: true
  log_file: "/var/log/vpn_manager.log"
```

## Troubleshooting

### Permission Denied Errors
Run with sudo:
```bash
sudo python main.py connect
```

### Config File Not Found
Verify the path in config/vpn_config.yaml:
```bash
ls -l /etc/openvpn/client.conf
```

### VPN Not Connecting
Check logs:
```bash
tail -f /var/log/vpn_manager.log
```

Or check system VPN logs:
```bash
# For OpenVPN
sudo journalctl -u openvpn -f

# For WireGuard
sudo journalctl -u wg-quick@wg0 -f
```

### Health Checks Failing
Test connectivity manually:
```bash
ping -c 3 8.8.8.8
```

If ping fails but VPN is up, check firewall rules.

## Next Steps

- Review the full [README.md](README.md) for detailed documentation
- Customize notifications in config/vpn_config.yaml
- Review test suite in tests/ directory
- Set up as systemd service for production use

## Getting Help

For issues or questions:
1. Check the troubleshooting section above
2. Review logs for error messages
3. Open an issue on GitHub with:
   - Your configuration (remove sensitive data)
   - Error messages
   - Steps to reproduce

## Security Best Practices

1. **Protect config files:**
   ```bash
   chmod 600 config/vpn_config.yaml
   ```

2. **Never commit credentials:**
   - Keep VPN credentials in separate files
   - Add credential files to .gitignore

3. **Run with minimal permissions:**
   - Only use sudo when necessary
   - Consider creating a dedicated user for VPN management

4. **Regular updates:**
   ```bash
   sudo apt-get update
   sudo apt-get upgrade openvpn  # or wireguard
   ```

5. **Monitor logs regularly:**
   ```bash
   tail -f /var/log/vpn_manager.log
   ```
# Quick Start Guide - Secure IT Starlink

## Installation

```bash
# Clone the repository
git clone https://github.com/danielnovais-tech/secure-it-infra-Starlink.git
cd secure-it-infra-Starlink

# Install dependencies
pip install -r requirements.txt

# Install the package
pip install -e .
```

## Basic Usage

### 1. Run with Default Configuration

```bash
secure-it-starlink
```

### 2. Run with Custom Configuration

```bash
secure-it-starlink -c configs/production_config.yaml
```

### 3. Check System Status

```bash
secure-it-starlink --status
```

## Quick Examples

### Configuration Management

```python
from secure_it_starlink.config import ConfigurationManager

# Load and merge configurations
config = ConfigurationManager()
config.load_and_merge('configs/production_config.yaml')

# Access configuration values
security_weight = config.get('metrics.security.weight')
log_level = config.get('logging.structured.level')
```

### Metrics Collection

```python
from secure_it_starlink.metrics import MetricsCollector

# Initialize collector
collector = MetricsCollector(config.get('metrics'))

# Collect metrics
metrics = collector.collect_metrics(
    security_data={
        'firewall_status': 95.0,
        'encryption_level': 90.0
    },
    connection_data={
        'uptime_percentage': 99.8,
        'latency': 25.0
    },
    performance_data={
        'cpu_usage': 45.0,
        'memory_usage': 60.0
    }
)

print(f"Composite Score: {metrics['composite_score']}")
```

### Automated Responses

```python
from secure_it_starlink.automated_responses import AutomatedResponseCoordinator

# Initialize coordinator
coordinator = AutomatedResponseCoordinator(config.get('automated_responses'))

# Process security event
event = {
    'type': 'security_threat',
    'severity': 'high',
    'device_id': 'device-001',
    'source_ip': '192.168.1.100',
    'reason': 'Malware detected'
}

actions = coordinator.process_event(event)
print(f"Triggered {len(actions)} automated actions")
```

### Structured Logging

```python
from secure_it_starlink.logging import StructuredLogger

# Initialize logger
logger = StructuredLogger(config.get('logging'))

# Log with structured data
logger.info("Security event detected", 
           event_type='intrusion_attempt',
           source_ip='192.168.1.100',
           severity='high')

# Check correlated events
incidents = logger.get_correlated_events(3600)
```

## Running Tests

```bash
# Run functionality tests
python3 tests/test_functionality.py

# Run usage examples
python3 examples/usage_examples.py
```

## Configuration Files

- `configs/default_config.yaml` - Default configuration with all settings
- `configs/development_config.yaml` - Development environment overrides
- `configs/production_config.yaml` - Production environment overrides

## Key Features

1. **Comprehensive Metrics**
   - Security scoring (0-100)
   - Connection stability monitoring
   - Performance tracking

2. **Automated Responses**
   - Threat containment (device isolation, IP blocking)
   - Policy enforcement (bandwidth limits, access control)
   - Failover activation (backup link switching)

3. **Detailed Logging**
   - JSON-structured logs
   - Event correlation
   - Pattern detection (brute force, data exfiltration)

4. **Configuration Management**
   - YAML-based configuration
   - Deep merging support
   - Environment-specific overrides

## Next Steps

1. Review the comprehensive [README.md](README.md) for detailed documentation
2. Explore [examples/usage_examples.py](examples/usage_examples.py) for more examples
3. Customize configuration files for your environment
4. Integrate with your existing monitoring infrastructure

## Support

For issues or questions, please open an issue on GitHub.
# Quick Start Guide - Starlink Security Auditor

## Getting Started in 5 Minutes

### 1. Clone and Setup
```bash
git clone https://github.com/danielnovais-tech/secure-it-infra-Starlink.git
cd secure-it-infra-Starlink
chmod +x starlink_security_auditor.py
```

### 2. Run Your First Audit
```bash
# Basic audit (non-root checks only)
python3 starlink_security_auditor.py

# Full audit with sudo (recommended)
sudo python3 starlink_security_auditor.py
```

### 3. View Results
The audit will display results in the console and create two files:
- `security_audit_report.json` - Detailed JSON report
- `security_audit.log` - Audit execution log

### 4. Customize Configuration (Optional)
```bash
# Copy example config
cp config.example.json my-config.json

# Edit as needed
nano my-config.json

# Run with custom config
sudo python3 starlink_security_auditor.py --config my-config.json
```

## Understanding the Output

### Status Levels
- **✓ PASS**: Security check passed
- **✗ FAIL**: Critical security issue found
- **⚠ WARN**: Security concern that should be addressed
- **ℹ INFO**: Informational finding for review

### Exit Codes
- `0`: All checks passed
- `1`: One or more critical failures
- `2`: Warnings present (no critical failures)

## Common First Steps

### 1. Address Critical Failures
```bash
# Enable firewall
sudo ufw enable
sudo ufw allow 22/tcp
sudo ufw allow 443/tcp

# Install VPN (choose one)
sudo apt-get install openvpn  # For OpenVPN
sudo apt-get install wireguard  # For WireGuard

# Harden SSH
sudo nano /etc/ssh/sshd_config
# Set: PasswordAuthentication no
# Set: PermitRootLogin no
sudo systemctl restart sshd
```

### 2. Schedule Regular Audits
```bash
# Add to crontab
sudo crontab -e

# Add this line for daily audits at 2 AM
0 2 * * * /path/to/starlink_security_auditor.py --quiet
```

### 3. Review Security Best Practices
```bash
# Read the comprehensive guide
cat SECURITY_BEST_PRACTICES.md
```

## Next Steps

1. **Review the full README**: `cat README.md`
2. **Understand the architecture**: `cat ARCHITECTURE.md`
3. **Plan your deployment**: `cat DEPLOYMENT.md`
4. **Implement recommendations**: Act on FAIL and WARN findings
5. **Schedule regular audits**: Automate weekly security checks

## Need Help?

- **Documentation**: All .md files in this repository
- **Configuration**: See `config.example.json` for all options
- **Issues**: Open an issue on GitHub

## Quick Reference

### Command Line Options
```bash
# Show help
python3 starlink_security_auditor.py --help

# Custom config file
python3 starlink_security_auditor.py --config /path/to/config.json

# Custom output file
python3 starlink_security_auditor.py --output /path/to/report.json

# Quiet mode (no console output)
python3 starlink_security_auditor.py --quiet
```

### Configuration Scope
Enable/disable specific checks in your config file:
```json
{
  "audit_scope": {
    "network_security": true,
    "service_vulnerabilities": true,
    "encryption_validation": true,
    "vpn_validation": true,
    "network_segmentation": true,
    "privilege_checks": true
  }
}
```

## Starlink-Specific Tips

1. **Always use VPN**: Critical for satellite link security
2. **Monitor regularly**: Weekly audits recommended
3. **Act quickly**: Address FAIL findings within 24 hours
4. **Plan for latency**: Starlink connections may have higher latency
5. **Backup connectivity**: Consider failover for critical systems

---

**Ready to secure your Starlink infrastructure? Run your first audit now!**

```bash
sudo python3 starlink_security_auditor.py
```
