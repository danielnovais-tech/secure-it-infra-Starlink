# Quick Start Guide

This guide will help you get Pulsar and Armada Atlas running quickly for testing and development.

## Prerequisites

- Docker and Docker Compose installed
- At least 8 GB of available RAM
- At least 20 GB of available disk space

For Kubernetes deployments:
- Kubernetes cluster (1.24+)
- kubectl configured
- At least 3 worker nodes with 4 GB RAM each

## Quick Start with Docker Compose

### Step 1: Start Pulsar

```bash
cd pulsar
docker-compose up -d
```

Wait for services to be healthy (2-3 minutes):

```bash
docker-compose ps
```

Verify Pulsar is running:

```bash
curl http://localhost:8080/admin/v2/brokers/health
```

Expected output: `ok`

### Step 2: Start Armada Atlas

```bash
cd ../armada-atlas
docker-compose up -d
```

Wait for services to be healthy (2-3 minutes):

```bash
docker-compose ps
```

### Step 3: Verify Integration

Check that Armada connected to Pulsar:

```bash
docker logs armada-server 2>&1 | grep -i pulsar
```

You should see logs indicating successful Pulsar connection.

### Step 4: Submit a Test Job

Install armadactl:

```bash
# Download (replace with latest version)
wget https://github.com/G-Research/armada/releases/latest/download/armadactl-linux-amd64
chmod +x armadactl-linux-amd64
sudo mv armadactl-linux-amd64 /usr/local/bin/armadactl

# Configure
armadactl config set server "localhost:50051"
```

Create a queue:

```bash
armadactl create queue test-queue
```

Create a job file `test-job.yaml`:

```yaml
queue: test-queue
jobSetId: test-job-set
jobs:
  - priority: 0
    podSpec:
      containers:
        - name: test
          image: ubuntu:22.04
          command:
            - bash
            - -c
            - |
              echo "Hello from Starlink Fleet!"
              echo "Job running at $(date)"
              sleep 10
              echo "Job completed successfully"
          resources:
            requests:
              memory: "64Mi"
              cpu: "0.1"
            limits:
              memory: "64Mi"
              cpu: "0.1"
```

Submit the job:

```bash
armadactl submit test-job.yaml
```

Watch job status:

```bash
armadactl watch test-queue test-job-set
```

### Step 5: View in UIs

**Pulsar Manager**:
- Open http://localhost:9527
- Default credentials: admin/apachepulsar
- View topics and messages

**Armada Lookout**:
- Open http://localhost:8089
- Browse jobs and view status
- No authentication required in dev mode

### Step 6: Verify Event Flow

Check job events in Pulsar:

```bash
docker exec -it pulsar-broker bin/pulsar-admin topics stats \
  persistent://public/default/armada-job-events
```

Consume events:

```bash
docker exec -it pulsar-broker bin/pulsar-client consume \
  persistent://public/default/armada-job-events \
  -s test-consumer \
  -n 10
```

## Quick Start with Kubernetes

### Step 1: Deploy Pulsar

```bash
kubectl apply -f pulsar/kubernetes-deployment.yaml
```

Wait for all pods to be ready:

```bash
kubectl wait --for=condition=ready pod \
  -l app=pulsar -n pulsar --timeout=600s
```

Get broker service endpoint:

```bash
kubectl get svc broker -n pulsar
```

### Step 2: Deploy Armada

```bash
kubectl apply -f armada-atlas/kubernetes-deployment.yaml
```

Wait for all pods to be ready:

```bash
kubectl wait --for=condition=ready pod \
  -l app=armada -n armada --timeout=600s
```

### Step 3: Access Services

Get service endpoints:

```bash
# Armada Server
kubectl get svc armada-server -n armada

# Lookout UI
kubectl get svc lookout -n armada

# Pulsar Manager
kubectl get svc pulsar-manager -n pulsar
```

Port-forward for local access:

```bash
# Armada Server (in one terminal)
kubectl port-forward -n armada svc/armada-server 50051:50051

# Lookout UI (in another terminal)
kubectl port-forward -n armada svc/lookout 8089:8089

# Pulsar Manager (in another terminal)
kubectl port-forward -n pulsar svc/pulsar-manager 9527:9527
```

### Step 4: Submit Jobs

Follow Step 4 from Docker Compose section above.

## Common Commands

### Pulsar

```bash
# List topics
docker exec -it pulsar-broker bin/pulsar-admin topics list public/default

# View topic stats
docker exec -it pulsar-broker bin/pulsar-admin topics stats \
  persistent://public/default/armada-job-events

# Create topic
docker exec -it pulsar-broker bin/pulsar-admin topics create \
  persistent://public/default/my-topic

# Publish test message
docker exec -it pulsar-broker bin/pulsar-client produce \
  persistent://public/default/my-topic \
  -m "Test message"

# Consume messages
docker exec -it pulsar-broker bin/pulsar-client consume \
  persistent://public/default/my-topic \
  -s test-sub -n 10
```

### Armada

```bash
# List queues
armadactl get queues

# Create queue
armadactl create queue my-queue \
  --priority-factor 1.0 \
  --resource-limit cpu=10 \
  --resource-limit memory=10Gi

# Submit job
armadactl submit my-job.yaml

# Watch jobs
armadactl watch my-queue my-job-set

# Cancel jobs
armadactl cancel my-queue my-job-set

# Get cluster status
armadactl get cluster-status
```

## Stopping Services

### Docker Compose

```bash
# Stop services
cd pulsar && docker-compose down
cd ../armada-atlas && docker-compose down

# Stop and remove volumes (WARNING: deletes all data)
cd pulsar && docker-compose down -v
cd ../armada-atlas && docker-compose down -v
```

### Kubernetes

```bash
# Delete deployments
kubectl delete -f armada-atlas/kubernetes-deployment.yaml
kubectl delete -f pulsar/kubernetes-deployment.yaml

# Delete namespaces (WARNING: deletes all data)
kubectl delete namespace armada
kubectl delete namespace pulsar
```

## Troubleshooting

### Services Not Starting

Check logs:

```bash
# Docker Compose
docker-compose logs [service-name]

# Kubernetes
kubectl logs -n [namespace] [pod-name]
```

Common issues:

1. **Insufficient resources**: Check Docker/Kubernetes has enough RAM
2. **Port conflicts**: Ensure ports are not already in use
3. **Network issues**: Verify containers can communicate

### Jobs Not Running

1. Check Armada Server logs:
   ```bash
   docker logs armada-server
   ```

2. Check Executor logs:
   ```bash
   docker logs armada-executor
   ```

3. Verify queue exists:
   ```bash
   armadactl get queues
   ```

### Events Not Appearing in Pulsar

1. Check Armada Server Pulsar connection:
   ```bash
   docker logs armada-server 2>&1 | grep -i pulsar
   ```

2. Verify broker is healthy:
   ```bash
   curl http://localhost:8080/admin/v2/brokers/health
   ```

3. Check topic exists:
   ```bash
   docker exec -it pulsar-broker bin/pulsar-admin topics list public/default
   ```

## Next Steps

- Read the [Integration Guide](INTEGRATION.md) for detailed architecture
- Explore [Pulsar Documentation](../pulsar/README.md)
- Explore [Armada Documentation](../armada-atlas/README.md)
- Configure authentication and TLS for production
- Set up monitoring with Prometheus and Grafana

## Getting Help

- Apache Pulsar: https://pulsar.apache.org/community
- Armada: https://github.com/G-Research/armada/issues
- Starlink Infrastructure: See main README.md
