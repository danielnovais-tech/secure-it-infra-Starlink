# Threat Detection System

A comprehensive YAML-based threat detection system for Starlink infrastructure security. This system provides real-time anomaly detection, brute-force attack analysis, and threat intelligence feed integration.

## Features

### 1. Anomaly Detection
- **Failed Login Monitoring**: Detects excessive failed login attempts from single IP addresses
- **Connection Rate Analysis**: Identifies abnormal connection rates that may indicate attacks
- **Bandwidth Usage Monitoring**: Tracks unusual bandwidth consumption patterns
- **Port Scan Detection**: Identifies port scanning activities

### 2. Brute-force Attack Detection
- **Log Analysis**: Scans log files for brute-force attack patterns
- **Pattern Matching**: Uses configurable regex patterns to detect:
  - SSH brute-force attempts
  - HTTP authentication attacks
  - FTP login attacks
- **Automatic Blocking**: Can automatically block IPs based on detection thresholds

### 3. Threat Intelligence Integration
- **DShield Feed**: Integration with DShield.org's recommended block list
- **Emerging Threats**: Real-time updates from Emerging Threats compromised IP list
- **Automatic Updates**: Configurable update intervals for threat feeds
- **IP Reputation Checking**: Cross-reference events against known threat databases

## Installation

1. Clone the repository:
```bash
git clone https://github.com/danielnovais-tech/secure-it-infra-Starlink.git
cd secure-it-infra-Starlink
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

The system is configured via YAML file at `threat_detection/config/threat_rules.yaml`.

### Key Configuration Sections:

#### Anomaly Detection
```yaml
anomaly_detection:
  enabled: true
  thresholds:
    failed_login_threshold: 5
    failed_login_window_minutes: 10
    connection_rate_threshold: 100
    connection_rate_window_seconds: 60
```

#### Brute-force Detection
```yaml
brute_force_detection:
  enabled: true
  patterns:
    - name: "SSH Brute-force"
      pattern: "Failed password for .* from (\\d+\\.\\d+\\.\\d+\\.\\d+)"
      threshold: 5
      window_minutes: 10
      action: "block"
```

#### Threat Intelligence Feeds
```yaml
threat_intelligence:
  enabled: true
  update_interval_hours: 6
  feeds:
    dshield:
      enabled: true
      url: "https://www.dshield.org/block.txt"
    emerging_threats:
      enabled: true
      url: "https://rules.emergingthreats.net/blockrules/compromised-ips.txt"
```

## Usage

### Update Threat Intelligence Feeds
```bash
python threat_detection/threat_detection.py --update-feeds
```

### Analyze a Log File
```bash
python threat_detection/threat_detection.py --analyze-log /var/log/auth.log
```

### Continuous Monitoring
```bash
python threat_detection/threat_detection.py --monitor /var/log/auth.log /var/log/syslog
```

### Custom Configuration
```bash
python threat_detection/threat_detection.py --config /path/to/custom_config.yaml --update-feeds
```

## Architecture

### Components

1. **Anomaly Detector** (`modules/anomaly_detector.py`)
   - Tracks events in time windows
   - Applies threshold-based detection
   - Returns anomaly alerts

2. **Brute-force Detector** (`modules/brute_force_detector.py`)
   - Parses log files line-by-line
   - Matches regex patterns
   - Maintains attempt counters per IP

3. **Threat Intelligence Updater** (`modules/threat_intelligence.py`)
   - Downloads feeds from external sources
   - Parses multiple feed formats
   - Maintains blocklist of known threat IPs

4. **Main System** (`threat_detection.py`)
   - Orchestrates all components
   - Manages configuration
   - Provides logging and alerting

### Data Flow

```
Log Files → Brute-force Detector → Threats
Events → Anomaly Detector → Anomalies
External Feeds → Threat Intelligence → Known Threats
                    ↓
            Threat Detection System
                    ↓
        Logging, Alerts, IP Blocking
```

## API Usage

### Programmatic Integration

```python
from threat_detection.threat_detection import ThreatDetectionSystem

# Initialize system
system = ThreatDetectionSystem()

# Update threat feeds
system.update_threat_intelligence()

# Analyze an event
event = {
    'type': 'failed_login',
    'ip_address': '192.168.1.100',
    'timestamp': '2026-01-06T12:00:00'
}
threats = system.analyze_event(event)

# Analyze log file
detections = system.analyze_log_file('/var/log/auth.log')

# Get blocked IPs
blocked_ips = system.get_blocked_ips()
```

## Testing

Run the test suite:
```bash
python -m pytest threat_detection/tests/
```

## Logs

Logs are stored at `threat_detection/logs/threat_detection.log` with automatic rotation:
- Max size: 10MB per file
- Backup count: 5 files
- Format: `timestamp - name - level - message`

## Security Considerations

1. **Network Access**: System requires internet access to download threat intelligence feeds
2. **Log Permissions**: Ensure read access to system log files
3. **IP Blocking**: Integration with firewall/iptables recommended for automatic blocking
4. **Rate Limiting**: Configure appropriate thresholds to avoid false positives

## Customization

### Adding New Brute-force Patterns

Edit `threat_rules.yaml`:
```yaml
brute_force_detection:
  patterns:
    - name: "Custom Pattern"
      pattern: "your regex pattern with IP capture group (\\d+\\.\\d+\\.\\d+\\.\\d+)"
      threshold: 5
      window_minutes: 10
      action: "block"
```

### Adding New Threat Feeds

Edit `threat_rules.yaml`:
```yaml
threat_intelligence:
  feeds:
    custom_feed:
      enabled: true
      url: "https://example.com/threat-feed.txt"
      format: "plain_ip_list"
      description: "Custom threat feed"
```

## Troubleshooting

### Common Issues

1. **Cannot download threat feeds**
   - Check internet connectivity
   - Verify URLs are accessible
   - Check firewall rules

2. **Log files not found**
   - Verify log file paths in configuration
   - Ensure proper read permissions

3. **High false positive rate**
   - Adjust thresholds in configuration
   - Review pattern matching rules
   - Increase time windows

## License

See [LICENSE](../LICENSE) file for details.

## Contributing

Contributions are welcome! Please submit pull requests or open issues for bugs and feature requests.

## Support

For support and questions, please open an issue on GitHub.
