# Starlink Network Monitoring System

A real-time monitoring solution for Starlink satellite internet connections in enterprise infrastructures. This system provides continuous monitoring of network conditions, dynamic metrics collection, and event detection based on network performance.

## Features

- **Real-time Monitoring**: Continuous polling of Starlink's status API endpoint
- **Dynamic Metrics Collection**: Automatically updates metrics based on current network conditions
- **Event Detection**: Identifies and logs network events such as:
  - High latency
  - Low throughput (downlink/uplink)
  - Obstructions
  - State changes
- **Linux Compatibility**: Designed for Linux systems with proper signal handling (SIGINT, SIGTERM)
- **Systemd Integration**: Can run as a system service with automatic restart
- **Persistent Storage**: Saves metrics history to JSON files
- **Configurable Thresholds**: Customizable alert thresholds via environment variables

## Requirements

- Linux operating system
- Python 3.7 or higher
- Network access to Starlink dish (default: 192.168.100.1)

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/danielnovais-tech/secure-it-infra-Starlink.git
cd secure-it-infra-Starlink
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment (Optional)

Copy the example configuration and customize as needed:

```bash
cp config.env.example .env
# Edit .env with your preferred settings
```

## Usage

### Running Directly

Run the monitoring application directly:

```bash
python3 src/starlink_monitor.py
```

The application will:
- Start monitoring the Starlink connection
- Poll the API every 5 seconds (configurable)
- Log metrics and events to console and log files
- Save current metrics to `data/current_metrics.json`
- Append metrics history to `data/metrics_history.jsonl`

### Running as a System Service

For production deployments, install as a systemd service:

#### 1. Install the Application

```bash
sudo mkdir -p /opt/starlink-monitor
sudo cp -r . /opt/starlink-monitor/
sudo chown -R starlink:starlink /opt/starlink-monitor
```

#### 2. Create System User

```bash
sudo useradd -r -s /bin/false starlink
```

#### 3. Create Required Directories

```bash
sudo mkdir -p /var/log/starlink-monitor
sudo mkdir -p /var/lib/starlink-monitor
sudo mkdir -p /etc/starlink-monitor
sudo chown starlink:starlink /var/log/starlink-monitor
sudo chown starlink:starlink /var/lib/starlink-monitor
```

#### 4. Install Configuration

```bash
sudo cp config.env.example /etc/starlink-monitor/config.env
# Edit configuration as needed
sudo nano /etc/starlink-monitor/config.env
```

#### 5. Install Systemd Service

```bash
sudo cp starlink-monitor.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable starlink-monitor
sudo systemctl start starlink-monitor
```

#### 6. Check Status

```bash
sudo systemctl status starlink-monitor
sudo journalctl -u starlink-monitor -f
```

### Stopping the Service

For graceful shutdown, the application handles SIGINT and SIGTERM signals:

```bash
# If running directly
Ctrl+C

# If running as service
sudo systemctl stop starlink-monitor
```

## Configuration

Configuration is managed through environment variables. You can set these in:
- `.env` file (for development)
- `/etc/starlink-monitor/config.env` (for production)
- System environment variables

### Available Options

| Variable | Default | Description |
|----------|---------|-------------|
| `STARLINK_API_ENDPOINT` | `http://192.168.100.1/api/status` | Starlink API endpoint URL |
| `API_TIMEOUT` | `10` | API request timeout in seconds |
| `UPDATE_INTERVAL` | `5` | Metrics update interval in seconds |
| `MAX_RETRIES` | `3` | Maximum retries for failed API calls |
| `LATENCY_THRESHOLD` | `100` | High latency alert threshold (ms) |
| `DOWNLINK_THRESHOLD` | `50` | Low downlink alert threshold (Mbps) |
| `UPLINK_THRESHOLD` | `10` | Low uplink alert threshold (Mbps) |
| `OBSTRUCTION_THRESHOLD` | `5` | Obstruction alert threshold (%) |

## Architecture

### Components

1. **starlink_monitor.py**: Main application with signal handling and monitoring loop
2. **starlink_api.py**: API client for real Starlink status endpoint (replaces simulations)
3. **metrics_collector.py**: Dynamic metrics collection and event detection
4. **config.py**: Configuration management with Linux path compatibility

### Data Flow

```
Starlink API → API Client → Metrics Collector → Event Detection
                                    ↓
                          File Storage (JSON)
                                    ↓
                          Logging System
```

### Linux Compatibility

- **Directory Paths**: Uses Linux-standard paths (`/var/log`, `/var/lib`) when available
- **Signal Handling**: Properly handles SIGINT and SIGTERM for graceful shutdown
- **Systemd Integration**: Full systemd service support with auto-restart
- **File Permissions**: Follows Linux security best practices

## Monitoring Outputs

### Log Files

- **Location**: `/var/log/starlink-monitor/starlink_monitor.log` (or `logs/` in repo)
- **Format**: Timestamped entries with log levels
- **Rotation**: Managed by system log rotation

### Metrics Files

- **Current Metrics**: `data/current_metrics.json` - Latest snapshot
- **History**: `data/metrics_history.jsonl` - JSONL format with all historical data

### Example Metrics Output

```json
{
  "current_metrics": {
    "timestamp": "2026-01-07T00:00:00.000000",
    "state": "CONNECTED",
    "latency_ms": 45.2,
    "downlink_mbps": 150.5,
    "uplink_mbps": 25.3,
    "obstruction_percent": 0.5,
    "uptime": 86400
  },
  "recent_events": [
    {
      "timestamp": "2026-01-07T00:00:00.000000",
      "type": "STATE_CHANGE",
      "severity": "INFO",
      "message": "State changed from SEARCHING to CONNECTED"
    }
  ],
  "status": {
    "state": "CONNECTED",
    "latency_ms": 45.2,
    "downlink_mbps": 150.5,
    "uplink_mbps": 25.3,
    "obstruction_percent": 0.5
  }
}
```

## Security Considerations

- Service runs with minimal privileges (NoNewPrivileges=true)
- Protected system directories (ProtectSystem=strict)
- Private temporary directory (PrivateTmp=true)
- Limited write access to log and data directories only
- No new user namespaces (security hardening)

## Troubleshooting

### Cannot Connect to Starlink API

- Verify network connectivity to Starlink dish: `ping 192.168.100.1`
- Check if API endpoint is correct in configuration
- Ensure firewall allows connections to Starlink dish

### Permission Denied Errors

- Ensure directories have correct ownership: `sudo chown -R starlink:starlink /var/log/starlink-monitor /var/lib/starlink-monitor`
- Check SELinux/AppArmor policies if applicable

### Service Won't Start

- Check logs: `sudo journalctl -u starlink-monitor -n 50`
- Verify Python dependencies: `pip install -r requirements.txt`
- Ensure configuration file exists: `/etc/starlink-monitor/config.env`

## Contributing

Contributions are welcome! Please ensure:
- Code follows PEP 8 style guidelines
- All changes maintain Linux compatibility
- Security best practices are followed
- Documentation is updated

## License

See LICENSE file for details.
