# secure-it-infra-Starlink
Repository dedicated to security solutions for managed enterprise infrastructures supporting Starlink.

## Network Monitoring System

A comprehensive YAML-based network monitoring solution that tracks critical network metrics and security parameters for Starlink infrastructure.

### Features

- **Latency Monitoring**: Measures network latency (min/max/avg) using ICMP ping
- **Jitter Tracking**: Monitors variation in latency to detect network instability
- **Packet Loss Detection**: Tracks packet loss percentages to identify network issues
- **Throughput Measurement**: Measures network throughput for performance analysis
- **Device Connection Tracking**: Detects active devices on the network
- **Unauthorized Device Detection**: Identifies unauthorized devices by comparing against a whitelist
- **Open Port Scanning**: Scans critical systems for open ports to identify potential security vulnerabilities

### Installation

1. Clone this repository:
```bash
git clone https://github.com/danielnovais-tech/secure-it-infra-Starlink.git
cd secure-it-infra-Starlink
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

### Configuration

Create a YAML configuration file to define your monitoring targets and parameters. See `config.example.yaml` for a complete example.

Example configuration:
```yaml
monitoring:
  targets:
    - host: "8.8.8.8"
      monitor_latency: true
      monitor_jitter: true
      monitor_packet_loss: true
      ping_count: 4
      jitter_count: 10
      packet_loss_count: 20
      
    - host: "192.168.1.1"
      monitor_latency: true
      scan_ports: true
      ports_to_scan: [22, 80, 443]

  network:
    subnet: "192.168.1.0/24"
    detect_devices: true
    check_unauthorized: true
    authorized_devices:
      - "192.168.1.1"
      - "192.168.1.10"
```

### Usage

Run the network monitor with your configuration file:

```bash
python network_monitor.py config.example.yaml
```

Generate a report file:
```bash
python network_monitor.py config.example.yaml --output report.txt
```

Output results in JSON format:
```bash
python network_monitor.py config.example.yaml --json
```

Save JSON results to a file:
```bash
python network_monitor.py config.example.yaml --json --output results.json
```

### Testing

Run the test suite to verify the monitoring system:

```bash
python -m unittest test_network_monitor.py
```

Or run tests with verbose output:
```bash
python -m unittest test_network_monitor.py -v
```

### Configuration Options

#### Target Monitoring Options

- `host`: IP address or hostname to monitor (required)
- `monitor_latency`: Enable latency monitoring (default: true)
- `monitor_jitter`: Enable jitter monitoring (default: true)
- `monitor_packet_loss`: Enable packet loss monitoring (default: true)
- `monitor_throughput`: Enable throughput monitoring (default: false)
- `scan_ports`: Enable port scanning (default: false)
- `ports_to_scan`: List of ports to scan (required if scan_ports is true)
- `ping_count`: Number of pings for latency test (default: 4)
- `jitter_count`: Number of pings for jitter test (default: 10)
- `packet_loss_count`: Number of pings for packet loss test (default: 20)
- `throughput_port`: Port to use for throughput test (default: 80)

#### Network-Wide Options

- `subnet`: Network subnet in CIDR notation (e.g., "192.168.1.0/24")
- `detect_devices`: Enable device detection (default: false)
- `check_unauthorized`: Enable unauthorized device detection (default: false)
- `authorized_devices`: List of authorized IP addresses

### Output Format

The monitoring system generates a comprehensive report including:

1. **Latency Report**: Min, max, and average latency for each target
2. **Jitter Report**: Jitter statistics including average, max, min, and standard deviation
3. **Packet Loss Report**: Percentage of packets lost per target
4. **Throughput Report**: Measured throughput in Mbps
5. **Open Ports Report**: List of open ports detected on critical systems
6. **Unauthorized Devices Report**: Warning alerts for any unauthorized devices detected
7. **Device Connections Report**: List of all active devices on the network

### Security Considerations

- **Port Scanning**: Use port scanning responsibly and only on systems you own or have permission to scan
- **Network Scanning**: Device detection performs network scans which may be detected by intrusion detection systems
- **Authorized Devices**: Keep the authorized devices list up-to-date to ensure accurate unauthorized device detection
- **Permissions**: Some monitoring features may require elevated privileges (e.g., raw socket access for ICMP)

### Requirements

- Python 3.6 or higher
- PyYAML 6.0 or higher
- Network connectivity to target systems
- Appropriate permissions for network operations (ICMP, port scanning)

### License

This project is licensed under the MIT License - see the LICENSE file for details.
