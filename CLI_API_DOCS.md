# CLI and API Documentation

This document provides comprehensive documentation for the Starlink Metrics CLI tool and REST API.

## Table of Contents

- [CLI Usage](#cli-usage)
- [REST API](#rest-api)
- [Examples](#examples)

---

## CLI Usage

The Starlink Metrics CLI provides a command-line interface for querying metrics, running diagnostics, and generating reports.

### Installation

```bash
# Install dependencies
pip install -r requirements-dev.txt

# Make CLI executable (Unix/Linux/Mac)
chmod +x starlink_cli.py
```

### Available Commands

#### `status` - Show Current Connection Status

Display the current connection status with quality and stability metrics.

```bash
python3 starlink_cli.py status

# JSON output
python3 starlink_cli.py status --json
```

**Output:**
```
============================================================
STARLINK CONNECTION STATUS
============================================================
Status:           Good
Service Level:    Stable
Quality Score:    100/100
Stability Score:  0.879

Metrics:
  Packet Loss:    3.5%
  Latency:        95.0ms
  Alert Level:    none
============================================================
```

#### `check` - Run Comprehensive Diagnostics

Perform detailed diagnostics and get recommendations.

```bash
python3 starlink_cli.py check
```

**Output includes:**
- Connection metrics analysis
- Quality assessment
- Stability assessment
- Actionable recommendations

#### `report` - Generate Metrics Report

Generate a metrics report for a specified time period with SLA compliance checking.

```bash
# 24-hour report (default)
python3 starlink_cli.py report

# Custom time period
python3 starlink_cli.py report --hours 48

# Custom SLA thresholds
python3 starlink_cli.py report --sla-quality 90.0 --sla-stability 0.80

# Export to file
python3 starlink_cli.py report --export /path/to/report.json

# JSON output
python3 starlink_cli.py report --json
```

#### `monitor` - Real-time Monitoring

Monitor connection metrics in real-time with periodic updates.

```bash
# Monitor with default 5-second interval
python3 starlink_cli.py monitor

# Custom update interval
python3 starlink_cli.py monitor --interval 10
```

**Output:**
```
Time         Status       Quality    Stability    Packet Loss  Latency   
--------------------------------------------------------------------------------
14:30:15     Good         100        0.879        3.5%         95ms
14:30:20     Good         100        0.879        3.5%         95ms
```

Press `Ctrl+C` to stop monitoring.

#### `export` - Export Metrics

Export metrics in various formats for integration with monitoring systems.

```bash
# JSON format (default)
python3 starlink_cli.py export

# Prometheus format
python3 starlink_cli.py export --format prometheus

# CloudWatch format
python3 starlink_cli.py export --format cloudwatch --namespace Production/Starlink
```

#### `config` - View Configuration

View current configuration settings.

```bash
python3 starlink_cli.py config --show
```

### CLI Options

| Command | Option | Description |
|---------|--------|-------------|
| `status` | `--json` | Output in JSON format |
| `report` | `--hours N` | Number of hours to include (default: 24) |
| | `--json` | Output in JSON format |
| | `--export FILE` | Export report to file |
| | `--sla-quality N` | SLA quality threshold (default: 85.0) |
| | `--sla-stability N` | SLA stability threshold (default: 0.75) |
| `monitor` | `--interval N` | Update interval in seconds (default: 5) |
| `export` | `--format FMT` | Format: json, prometheus, cloudwatch |
| | `--instance NAME` | Instance label (for Prometheus) |
| | `--namespace NS` | CloudWatch namespace |
| `config` | `--show` | Show current configuration |

---

## REST API

The Starlink Metrics REST API provides programmatic access to all metrics and diagnostic features.

### Starting the API Server

```bash
# Default: http://0.0.0.0:8000
python3 starlink_api.py

# Custom host and port
python3 starlink_api.py --host=127.0.0.1 --port=8080

# Development mode with auto-reload
python3 starlink_api.py --reload
```

### Interactive Documentation

Once the server is running, access:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### API Endpoints

#### GET `/` - API Information

Returns API information and available endpoints.

**Response:**
```json
{
  "name": "Starlink Metrics API",
  "version": "1.0.0",
  "description": "REST API for connection metrics monitoring",
  "endpoints": {
    "health": "/health",
    "current_metrics": "/metrics/current",
    ...
  }
}
```

#### GET `/health` - Health Check

Health check endpoint for monitoring and load balancers.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2026-01-15T01:00:00.000Z",
  "service": "starlink-metrics-api"
}
```

#### GET `/metrics/current` - Current Metrics

Get current raw connection metrics.

**Response:**
```json
{
  "packet_loss": 3.5,
  "latency": 95.0,
  "timestamp": "2026-01-15T01:00:00.000Z"
}
```

#### GET `/metrics/status` - Connection Status

Get current connection status with quality and stability scores.

**Response:**
```json
{
  "status": "Good",
  "quality_score": 100.0,
  "stability_score": 0.879,
  "packet_loss": 3.5,
  "latency": 95.0,
  "service_level": "Stable",
  "alert_level": "none",
  "timestamp": "2026-01-15T01:00:00.000Z"
}
```

#### POST `/metrics/diagnose` - Run Diagnostics

Run comprehensive diagnostics on connection.

**Request Body (optional):**
```json
{
  "packet_loss": 15.0,
  "latency": 250.0
}
```

If no body is provided, uses current metrics.

**Response:**
```json
{
  "status": "Fair",
  "metrics": {
    "packet_loss": 15.0,
    "latency": 250.0,
    "quality_score": 75.0,
    "stability_score": 0.646
  },
  "assessments": {
    "packet_loss": {
      "value": 15.0,
      "status": "warning",
      "threshold": 5.0
    },
    "latency": {
      "value": 250.0,
      "status": "warning",
      "threshold": 150.0
    },
    ...
  },
  "recommendations": [
    "High latency detected - check for network congestion",
    ...
  ],
  "timestamp": "2026-01-15T01:00:00.000Z"
}
```

#### GET `/metrics/report` - Generate Report

Generate metrics report with SLA compliance.

**Query Parameters:**
- `sla_quality` (float): Quality score SLA threshold (default: 85.0)
- `sla_stability` (float): Stability score SLA threshold (default: 0.75)

**Example:**
```
GET /metrics/report?sla_quality=90.0&sla_stability=0.80
```

**Response:**
```json
{
  "period_start": "2026-01-15T00:00:00.000Z",
  "period_end": "2026-01-15T01:00:00.000Z",
  "total_measurements": 10,
  "summary": {
    "quality_score": {"avg": 95.0, "min": 85.0, "max": 100.0},
    "stability_score": {"avg": 0.879, "min": 0.75, "max": 0.95},
    ...
  },
  "service_level_distribution": {
    "Stable": 8,
    "Degraded": 2,
    ...
  },
  "uptime_percentage": 80.0,
  "sla_compliance": {
    "quality_score": {
      "threshold": 90.0,
      "actual": 95.0,
      "compliant": true
    },
    ...
  }
}
```

#### GET `/metrics/export` - Export Metrics

Export metrics in various formats.

**Query Parameters:**
- `format` (string): json, prometheus, cloudwatch (default: json)
- `instance` (string): Instance label for Prometheus (default: "default")
- `namespace` (string): CloudWatch namespace (default: "Starlink/Metrics")

**Examples:**

Prometheus format:
```
GET /metrics/export?format=prometheus&instance=prod-1
```

CloudWatch format:
```
GET /metrics/export?format=cloudwatch&namespace=Production/Starlink
```

#### GET `/config` - Get Configuration

Get current configuration settings.

**Response:**
```json
{
  "quality_thresholds": {
    "packet_loss_threshold": 5.0,
    "latency_threshold": 150.0,
    "packet_loss_penalty": 10.0,
    "latency_penalty": 5.0
  },
  "stability_thresholds": {
    "max_latency": 500.0,
    "packet_loss_weight": 0.7,
    "latency_weight": 0.3,
    "packet_loss_multiplier": 2.0
  },
  "alert_thresholds": {
    "critical_stability": 0.3,
    "degraded_stability": 0.5,
    "stable_stability": 0.7
  }
}
```

#### PUT `/config` - Update Configuration

Update configuration settings.

**Request Body:**
```json
{
  "quality_thresholds": { ... },
  "stability_thresholds": { ... },
  "alert_thresholds": { ... }
}
```

**Note:** Configuration persistence not yet implemented.

#### GET `/prometheus` - Prometheus Metrics Endpoint

Prometheus-compatible metrics endpoint for scraping.

**Response (text/plain):**
```
starlink_connection_quality_score{service="starlink-metrics-api"} 100.0 1705276800000
starlink_connection_stability_score{service="starlink-metrics-api"} 0.879 1705276800000
...
```

---

## Examples

### CLI Examples

**Check connection status:**
```bash
python3 starlink_cli.py status
```

**Run diagnostics:**
```bash
python3 starlink_cli.py check
```

**Generate weekly report with high SLA thresholds:**
```bash
python3 starlink_cli.py report --hours 168 --sla-quality 95.0 --sla-stability 0.90
```

**Monitor connection every 10 seconds:**
```bash
python3 starlink_cli.py monitor --interval 10
```

**Export metrics for Prometheus:**
```bash
python3 starlink_cli.py export --format prometheus > /var/lib/prometheus/starlink_metrics.prom
```

### API Examples

**Using curl:**

```bash
# Get current status
curl http://localhost:8000/metrics/status

# Run diagnostics with custom metrics
curl -X POST http://localhost:8000/metrics/diagnose \
  -H "Content-Type: application/json" \
  -d '{"packet_loss": 12.0, "latency": 180.0}'

# Generate report with custom SLA thresholds
curl "http://localhost:8000/metrics/report?sla_quality=90&sla_stability=0.8"

# Get Prometheus metrics
curl http://localhost:8000/prometheus
```

**Using Python:**

```python
import requests

# Get current status
response = requests.get("http://localhost:8000/metrics/status")
status = response.json()
print(f"Quality: {status['quality_score']}")
print(f"Stability: {status['stability_score']}")

# Run diagnostics
response = requests.post(
    "http://localhost:8000/metrics/diagnose",
    json={"packet_loss": 8.0, "latency": 120.0}
)
diagnostics = response.json()
print("Recommendations:")
for rec in diagnostics['recommendations']:
    print(f"  - {rec}")

# Get report
response = requests.get("http://localhost:8000/metrics/report")
report = response.json()
print(f"Uptime: {report['uptime_percentage']}%")
```

**Using JavaScript/Node.js:**

```javascript
// Get current status
fetch('http://localhost:8000/metrics/status')
  .then(response => response.json())
  .then(data => {
    console.log(`Quality: ${data.quality_score}`);
    console.log(`Stability: ${data.stability_score}`);
  });

// Run diagnostics
fetch('http://localhost:8000/metrics/diagnose', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({packet_loss: 10.0, latency: 200.0})
})
  .then(response => response.json())
  .then(data => {
    console.log('Recommendations:');
    data.recommendations.forEach(rec => console.log(`  - ${rec}`));
  });
```

### Integration Examples

**Prometheus Scraping Configuration:**

Add to `prometheus.yml`:
```yaml
scrape_configs:
  - job_name: 'starlink-metrics'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/prometheus'
    scrape_interval: 30s
```

**Health Check in Docker Compose:**

```yaml
services:
  starlink-api:
    image: starlink-metrics-api
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

**Kubernetes Liveness Probe:**

```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 30
  periodSeconds: 10
```

---

## Error Handling

### CLI Error Codes

- `0`: Success
- `1`: General error or exception

### API Error Responses

**400 Bad Request:**
```json
{
  "error": "Validation error",
  "detail": "packet_loss must be between 0 and 100"
}
```

**422 Unprocessable Entity:**
```json
{
  "detail": [
    {
      "loc": ["body", "packet_loss"],
      "msg": "ensure this value is less than or equal to 100",
      "type": "value_error.number.not_le"
    }
  ]
}
```

---

## Production Deployment

### CLI Deployment

```bash
# Install as command
sudo cp starlink_cli.py /usr/local/bin/starlink-cli
sudo chmod +x /usr/local/bin/starlink-cli

# Create symlink
ln -s /path/to/starlink_cli.py ~/.local/bin/starlink-cli
```

### API Deployment

**Using Uvicorn (Production):**

```bash
uvicorn starlink_api:app --host 0.0.0.0 --port 8000 --workers 4
```

**Using Gunicorn:**

```bash
gunicorn starlink_api:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

**Using Docker:**

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements-dev.txt .
RUN pip install --no-cache-dir -r requirements-dev.txt

COPY starlink_metrics.py observability.py starlink_api.py ./

EXPOSE 8000
CMD ["uvicorn", "starlink_api:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Using systemd:**

Create `/etc/systemd/system/starlink-api.service`:
```ini
[Unit]
Description=Starlink Metrics API
After=network.target

[Service]
Type=simple
User=starlink
WorkingDirectory=/opt/starlink-metrics
ExecStart=/usr/bin/uvicorn starlink_api:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable starlink-api
sudo systemctl start starlink-api
```

---

## Testing

Run tests for CLI and API:

```bash
# Install test dependencies
pip install -r requirements-dev.txt

# Run all tests
pytest test_cli_api.py -v

# Run only CLI tests
pytest test_cli_api.py::TestCLI -v

# Run only API tests
pytest test_cli_api.py::TestAPI -v

# Run with coverage
pytest test_cli_api.py --cov=starlink_cli --cov=starlink_api --cov-report=html
```

---

## Support

For more information, see:
- [README.md](README.md) - Main documentation
- [SETUP.md](SETUP.md) - Deployment guide
- [DEVOPS_CHECKLIST.md](DEVOPS_CHECKLIST.md) - Operations checklist
- [SECURITY.md](SECURITY.md) - Security best practices
