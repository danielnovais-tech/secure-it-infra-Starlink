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
