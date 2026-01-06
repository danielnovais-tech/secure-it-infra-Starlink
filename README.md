# secure-it-infra-Starlink
Repository dedicated to security solutions for managed enterprise infrastructures supporting Starlink.

## Features

### Threat Detection System (YAML-based)

A comprehensive threat detection system that provides:

- **Anomaly Detection**: Scans for anomalies in network traffic and system behavior
  - Failed login monitoring
  - Connection rate analysis
  - Bandwidth usage tracking
  - Port scan detection

- **Brute-force Attack Detection**: Analyzes logs for attack patterns
  - SSH brute-force attempts
  - HTTP authentication attacks
  - FTP login attacks
  - Configurable pattern matching with regex

- **Threat Intelligence Integration**: Updates from external threat feeds
  - DShield.org recommended block list
  - Emerging Threats compromised IPs
  - Automatic periodic updates
  - IP reputation checking

## Quick Start

### Installation

```bash
# Install dependencies
pip install -r requirements.txt
```

### Usage

```bash
# Update threat intelligence feeds
python threat_detection/threat_detection.py --update-feeds

# Analyze a log file for brute-force attempts
python threat_detection/threat_detection.py --analyze-log /var/log/auth.log

# Monitor log files continuously
python threat_detection/threat_detection.py --monitor /var/log/auth.log /var/log/syslog

# Run example demonstrations
python examples.py
```

### Configuration

Edit `threat_detection/config/threat_rules.yaml` to customize:
- Detection thresholds
- Brute-force patterns
- Threat intelligence feeds
- Logging and alerts

## Documentation

See [threat_detection/README.md](threat_detection/README.md) for detailed documentation.

## Testing

```bash
# Run all tests
python threat_detection/tests/test_anomaly_detector.py
python threat_detection/tests/test_brute_force_detector.py
python threat_detection/tests/test_threat_intelligence.py
```

## License

See [LICENSE](LICENSE) file for details.
