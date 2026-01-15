# Starlink Metrics - Setup Instructions

## Quick Start

### Local Development

1. **Install Dependencies**
   ```bash
   pip install -r requirements-dev.txt
   ```

2. **Run Tests**
   ```bash
   pytest test_starlink_metrics.py test_enhanced_features.py test_observability.py test_integration.py -v
   ```

3. **Run Examples**
   ```bash
   python3 observability_examples.py
   ```

## Docker Deployment

### Build and Run Locally

```bash
# Build the image
docker build -t starlink-metrics:latest .

# Run container
docker run -p 9090:9090 starlink-metrics:latest

# Or use Docker Compose for full stack with Prometheus and Grafana
docker-compose up -d
```

### Access Services

- **Metrics Endpoint**: http://localhost:9090/metrics
- **Prometheus**: http://localhost:9091
- **Grafana**: http://localhost:3000 (admin/admin)

## Kubernetes Deployment

### Prerequisites

- Kubernetes cluster (v1.24+)
- kubectl configured
- Prometheus Operator installed (for ServiceMonitor)

### Deploy to Kubernetes

```bash
# Apply manifests
kubectl apply -f kubernetes/deployment.yaml

# Check deployment status
kubectl get pods -l app=starlink-metrics
kubectl get svc starlink-metrics
kubectl get hpa starlink-metrics-hpa

# View logs
kubectl logs -l app=starlink-metrics --tail=100 -f

# Port forward for local access
kubectl port-forward svc/starlink-metrics 9090:9090
```

### Verify Prometheus Scraping

```bash
# Check ServiceMonitor
kubectl get servicemonitor starlink-metrics

# Verify metrics endpoint
kubectl port-forward svc/starlink-metrics 9090:9090
curl http://localhost:9090/metrics
```

## CI/CD Setup

### GitHub Actions

The repository includes three GitHub Actions workflows:

1. **ci-tests.yml** - Runs tests on every push and PR
   - Tests on Python 3.8-3.12
   - Code coverage reporting
   - Linting and code quality checks
   - Security scanning with CodeQL

2. **pr-automation.yml** - Automated PR comments
   - Posts test results to PRs
   - Shows coverage metrics
   - Displays metrics quality summary

3. **build-publish.yml** - Build and publish artifacts
   - Builds Python package
   - Creates Docker images (multi-arch)
   - Publishes to PyPI on release
   - Pushes Docker images to registry

### Required Secrets

Add these secrets to your GitHub repository (Settings → Secrets):

- `DOCKER_USERNAME` - Docker Hub username
- `DOCKER_PASSWORD` - Docker Hub password or access token
- `PYPI_API_TOKEN` - PyPI API token for publishing packages

### Enable Workflows

1. Navigate to Actions tab in GitHub
2. Enable workflows if prompted
3. Workflows will run automatically on push/PR

## Monitoring Setup

### Prometheus Configuration

Create `prometheus/prometheus.yml`:

```yaml
global:
  scrape_interval: 30s
  evaluation_interval: 30s

scrape_configs:
  - job_name: 'starlink-metrics'
    static_configs:
      - targets: ['starlink-metrics:9090']
        labels:
          environment: 'production'
          datacenter: 'us-west-1'
```

### Grafana Dashboard

1. Access Grafana at http://localhost:3000
2. Add Prometheus data source (http://prometheus:9090)
3. Import dashboard or create custom:
   - Connection Quality Score
   - Stability Score Over Time
   - Service Level Distribution
   - Alert History

### CloudWatch Integration

For AWS CloudWatch monitoring:

```python
import boto3
from observability import MetricsExporter

cloudwatch = boto3.client('cloudwatch', region_name='us-east-1')
exporter = MetricsExporter()

# Export metrics
cloudwatch_data = exporter.export_cloudwatch(status)
cloudwatch.put_metric_data(**cloudwatch_data)
```

## Production Deployment Checklist

### Pre-Deployment

- [ ] All tests passing (74/74)
- [ ] Security scan clean
- [ ] Docker image built and scanned
- [ ] Configuration reviewed
- [ ] Secrets configured
- [ ] Monitoring dashboards ready
- [ ] Alert rules defined
- [ ] Runbook updated

### Deployment

- [ ] Deploy to staging first
- [ ] Run smoke tests
- [ ] Verify metrics scraping
- [ ] Check log output
- [ ] Test alert triggers
- [ ] Gradual rollout to production
- [ ] Monitor error rates

### Post-Deployment

- [ ] Verify all pods running
- [ ] Check Prometheus targets
- [ ] Review Grafana dashboards
- [ ] Test alert notifications
- [ ] Document any issues
- [ ] Update stakeholders

## Troubleshooting

### Container Won't Start

```bash
# Check logs
docker logs <container-id>

# Or in Kubernetes
kubectl logs -l app=starlink-metrics

# Common issues:
# - Missing dependencies: Rebuild image
# - Port conflicts: Change port mapping
# - Permission errors: Check user in Dockerfile
```

### Metrics Not Appearing in Prometheus

```bash
# Check if metrics endpoint is accessible
curl http://localhost:9090/metrics

# Verify Prometheus config
kubectl get configmap prometheus-config -o yaml

# Check Prometheus targets
# Navigate to http://prometheus:9090/targets
```

### High Memory Usage

```bash
# Check current resource usage
kubectl top pods -l app=starlink-metrics

# Increase memory limits in deployment.yaml
# Or optimize history_window_size parameter
```

## Support

- **Documentation**: See README.md, SECURITY.md, DEVOPS_CHECKLIST.md
- **Issues**: https://github.com/danielnovais-tech/secure-it-infra-Starlink/issues
- **Security**: See SECURITY.md for reporting vulnerabilities
