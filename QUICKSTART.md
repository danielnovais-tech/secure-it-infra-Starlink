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
