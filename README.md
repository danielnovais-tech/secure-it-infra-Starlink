# secure-it-infra-Starlink

Repository dedicated to security solutions for managed enterprise infrastructures supporting Starlink.

## VPN Management System

A robust YAML-based VPN management solution with monitoring, auto-reconnection, and health checking capabilities designed specifically for Starlink infrastructure security.

### Features

- **YAML-Based Configuration**: Easy-to-manage configuration file for all VPN settings
- **Multi-VPN Support**: Compatible with OpenVPN and WireGuard
- **Status Monitoring**: Real-time VPN connection status checks
- **Auto-Reconnection**: Automatic reconnection attempts on disconnection with configurable retry logic
- **Health Checking**: Validates VPN connectivity by pinging test hosts
- **Logging**: Comprehensive logging to console and file
- **CLI Interface**: Command-line interface for easy management

### Installation

1. Clone the repository:
```bash
git clone https://github.com/danielnovais-tech/secure-it-infra-Starlink.git
cd secure-it-infra-Starlink
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

### Configuration

The VPN manager uses a YAML configuration file located at `config/vpn_config.yaml`. You can customize:

- VPN connection details (type, config file path)
- Monitoring intervals and retry logic
- Health check settings
- Notification preferences
- Starlink-specific settings

Example configuration:
```yaml
vpn:
  enabled: true
  connection:
    name: "starlink-secure-vpn"
    type: "openvpn"
    config_file: "/etc/openvpn/client.conf"
  monitoring:
    check_interval: 30
    auto_reconnect: true
    max_reconnect_attempts: 5
    reconnect_delay: 10
```

See `config/vpn_config.yaml` for the full configuration schema.

### Usage

#### Command Line Interface

**Monitor VPN with auto-reconnection:**
```bash
python main.py monitor
```

**Check VPN status:**
```bash
python main.py status
```

**Connect to VPN:**
```bash
python main.py connect
```

**Disconnect from VPN:**
```bash
python main.py disconnect
```

**Use custom configuration file:**
```bash
python main.py --config /path/to/config.yaml monitor
```

#### Python API

```python
from vpn_manager import VPNManager

# Initialize manager
manager = VPNManager('config/vpn_config.yaml')

# Check status
status = manager.get_vpn_status()
print(f"Connected: {status['connected']}")
print(f"Healthy: {status['healthy']}")

# Connect to VPN
if manager.connect_vpn():
    print("Connected successfully")

# Start monitoring (blocking)
manager.monitor()
```

### Testing

Run the test suite:
```bash
python -m unittest discover tests
```

Run specific test:
```bash
python -m unittest tests.test_vpn_manager.TestVPNManager.test_load_config
```

### Prerequisites

- Python 3.7+
- OpenVPN or WireGuard installed (depending on your VPN type)
- Appropriate permissions to manage VPN connections (typically root/sudo)

### Architecture

```
secure-it-infra-Starlink/
├── config/
│   └── vpn_config.yaml          # VPN configuration
├── vpn_manager/
│   ├── __init__.py              # Package initialization
│   └── vpn_manager.py           # Core VPN management logic
├── tests/
│   └── test_vpn_manager.py      # Unit tests
├── main.py                      # CLI entry point
├── requirements.txt             # Python dependencies
└── README.md                    # Documentation
```

### How It Works

1. **Configuration Loading**: Reads VPN settings from YAML file
2. **Status Monitoring**: Periodically checks VPN connection status
3. **Health Checking**: Validates connectivity by pinging test hosts
4. **Auto-Reconnection**: Attempts reconnection when VPN drops or becomes unhealthy
5. **Logging**: Records all events for troubleshooting

### Security Considerations

- Store VPN credentials securely (not in the YAML config)
- Use appropriate file permissions for config files (e.g., `chmod 600`)
- Run with minimal required permissions
- Enable logging for audit trails
- Regularly update VPN software

### Troubleshooting

**VPN won't connect:**
- Verify VPN config file path is correct
- Ensure VPN software (OpenVPN/WireGuard) is installed
- Check system permissions
- Review logs for detailed error messages

**Health checks failing:**
- Verify test hosts are reachable
- Check firewall rules
- Adjust timeout values in configuration

**Auto-reconnection not working:**
- Ensure `auto_reconnect` is set to `true` in config
- Check max retry attempts aren't exhausted
- Review logs for specific error messages

### Contributing

Contributions are welcome! Please ensure:
- Code follows existing style
- Tests are included for new features
- Documentation is updated

### License

See LICENSE file for details.

### Support

For issues, questions, or contributions, please open an issue on GitHub.
