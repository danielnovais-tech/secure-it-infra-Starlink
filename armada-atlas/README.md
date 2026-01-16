# Armada Atlas for Fleet Management

This directory contains the configuration and deployment files for Armada Atlas, a multi-cluster batch job scheduler for fleet management in the Starlink infrastructure.

## Overview

Armada Atlas provides:
- **Multi-cluster scheduling**: Manage jobs across multiple Kubernetes clusters
- **Fair queuing**: Fair resource allocation between teams and projects
- **Priority scheduling**: Support for job priorities and preemption
- **High throughput**: Handle thousands of jobs per second
- **Fleet visibility**: Unified view of all clusters and jobs

## Architecture

The Armada deployment consists of:

1. **Armada Server**: Control plane for job scheduling and cluster coordination
2. **Armada Executor**: Runs on each Kubernetes cluster to execute jobs
3. **Lookout**: Web UI for job monitoring and management
4. **Lookout Ingester**: Processes job events for the UI
5. **Redis**: Job queue and state management
6. **PostgreSQL**: Persistent storage for job history and metadata

## Deployment Options

### Docker Compose (Development/Testing)

```bash
cd armada-atlas
docker-compose up -d
```

This will start:
- Redis on port 6379
- PostgreSQL on port 5432
- Armada Server on ports 50051 (gRPC) and 8080 (HTTP)
- Armada Executor (for local job execution)
- Lookout UI on port 8089

Access the Lookout UI at: http://localhost:8089

### Kubernetes (Production)

```bash
kubectl apply -f armada-atlas/kubernetes-deployment.yaml
```

This deploys:
- Redis with persistent storage
- PostgreSQL StatefulSet with persistent storage
- 2 Armada Server replicas for high availability
- Armada Executor with appropriate RBAC permissions
- Lookout UI with LoadBalancer service

Get the Armada Server endpoint:

```bash
kubectl get svc armada-server -n armada
```

Get the Lookout UI endpoint:

```bash
kubectl get svc lookout -n armada
```

## Configuration

### Server Configuration

Key settings in `config/armada-server-config.yaml`:

- **Scheduling**: Configure job limits, priorities, and preemption
- **Pulsar Integration**: Enable reliable event streaming
- **Fleet Management**: Define cluster pools and resource quotas
- **Authentication**: Configure auth providers (disable anonymous auth in production)

### Executor Configuration

Key settings in `config/armada-executor-config.yaml`:

- **Cluster Identity**: Set unique cluster ID and pool assignment
- **Resource Management**: Define allocatable resources
- **Task Settings**: Configure lease renewal and reporting intervals
- **Pulsar Publishing**: Enable event publishing for reliability

### Pulsar Integration

Armada integrates with Pulsar for reliability:

```yaml
pulsar:
  enabled: true
  URL: "pulsar://broker.pulsar:6650"
  jobsetEventsTopic: "persistent://public/default/armada-jobset-events"
  jobEventsTopic: "persistent://public/default/armada-job-events"
```

This ensures:
- Job events are reliably streamed to Pulsar
- Events survive Armada Server restarts
- Multiple consumers can process events
- Complete audit trail of all job lifecycle events

## Usage

### Installing armadactl CLI

```bash
# Download the latest release
wget https://github.com/G-Research/armada/releases/latest/download/armadactl-linux-amd64

# Make it executable
chmod +x armadactl-linux-amd64
sudo mv armadactl-linux-amd64 /usr/local/bin/armadactl

# Configure connection
armadactl config set server "localhost:50051"
```

### Creating a Queue

```bash
# Create a queue for your team
armadactl create queue my-team-queue \
  --priority-factor 1.0 \
  --resource-limit cpu=100 \
  --resource-limit memory=1000Gi
```

### Submitting a Job

Create a job file `job.yaml`:

```yaml
queue: my-team-queue
jobSetId: my-job-set-1
jobs:
  - priority: 1
    podSpec:
      containers:
        - name: main
          image: ubuntu:22.04
          command:
            - bash
            - -c
            - |
              echo "Hello from Starlink Fleet!"
              sleep 60
              echo "Job completed"
          resources:
            requests:
              memory: "100Mi"
              cpu: "100m"
            limits:
              memory: "100Mi"
              cpu: "100m"
```

Submit the job:

```bash
armadactl submit job.yaml
```

### Monitoring Jobs

```bash
# Watch job status
armadactl watch my-team-queue my-job-set-1

# Get job details
armadactl get jobs --queue my-team-queue --job-set-id my-job-set-1

# Get cluster status
armadactl get cluster-status
```

### Using the Web UI

1. Open Lookout UI: http://localhost:8089 (or LoadBalancer IP)
2. Browse jobs by queue, job set, or time range
3. View job details, logs, and events
4. Monitor cluster utilization and queue statistics

## Fleet Management

### Cluster Pools

Organize clusters into pools for different workload types:

```yaml
fleet:
  pools:
    - name: "starlink-pool"
      clusters:
        - "starlink-cluster-1"
        - "starlink-cluster-2"
        - "starlink-cluster-3"
```

### Resource Quotas

Set resource limits per queue:

```bash
armadactl create queue production \
  --priority-factor 2.0 \
  --resource-limit cpu=500 \
  --resource-limit memory=5000Gi \
  --resource-limit gpu=5
```

### Priority Classes

Configure job priorities in the server config:

```yaml
scheduling:
  preemption:
    enabled: true
    priorityClasses:
      - name: high-priority
        priority: 1000
      - name: medium-priority
        priority: 500
      - name: low-priority
        priority: 100
```

Then submit jobs with priority:

```yaml
jobs:
  - priority: 1000  # High priority
    priorityClassName: high-priority
    podSpec:
      # ... pod configuration
```

## Monitoring

### Metrics

Armada Server exposes metrics at:
```
http://localhost:9000/metrics
```

Armada Executor exposes metrics at:
```
http://localhost:9001/metrics
```

Key metrics to monitor:
- `armada_job_submit_rate`: Job submission rate
- `armada_job_running`: Currently running jobs
- `armada_job_queued`: Jobs waiting to run
- `armada_cluster_capacity`: Available cluster resources
- `armada_cluster_utilization`: Resource usage percentage

### Health Checks

```bash
# Check server health
grpc_health_probe -addr=localhost:50051

# Check cluster connection
armadactl get cluster-status

# View server logs
docker logs -f armada-server
```

## Integration with Pulsar

Armada publishes job events to Pulsar for reliability:

1. **Job submission**: When jobs are submitted
2. **Job scheduling**: When jobs are assigned to clusters
3. **Job running**: When jobs start executing
4. **Job completion**: When jobs finish (success/failure)

Benefits:
- **Reliability**: Events are not lost if Armada Server crashes
- **Audit trail**: Complete history of all job events
- **Integration**: External systems can consume job events
- **Scalability**: Multiple consumers can process events

Example consumer:

```python
import pulsar

client = pulsar.Client('pulsar://localhost:6650')
consumer = client.subscribe(
    topic='persistent://public/default/armada-job-events',
    subscription_name='my-consumer'
)

while True:
    msg = consumer.receive()
    event = json.loads(msg.data())
    print(f"Job event: {event['type']} - Job {event['jobId']}")
    consumer.acknowledge(msg)
```

## Security

### Production Security Checklist

1. **Disable anonymous authentication**:
   ```yaml
   auth:
     anonymousAuth: false
   ```

2. **Enable OIDC authentication**:
   ```yaml
   auth:
     oidc:
       providerUrl: "https://your-oidc-provider.com"
       clientId: "armada-client"
   ```

3. **Use Kubernetes RBAC**:
   - Executor uses ServiceAccount with minimal permissions
   - Jobs run with their own ServiceAccounts

4. **Secure PostgreSQL**:
   - Use strong passwords (stored in Kubernetes Secrets)
   - Enable SSL connections
   - Restrict network access

5. **Network Policies**:
   - Restrict access to Armada Server
   - Isolate executor pods
   - Control egress traffic

## Troubleshooting

### Common Issues

1. **Jobs stuck in pending**
   - Check cluster capacity: `armadactl get cluster-status`
   - Verify executor is running: `kubectl get pods -n armada`
   - Check executor logs: `kubectl logs -n armada deployment/armada-executor`

2. **Executor not connecting to server**
   - Verify server is reachable: `grpc_health_probe -addr=armada-server:50051`
   - Check network policies
   - Verify executor configuration

3. **Lookout UI not showing jobs**
   - Check Lookout Ingester is running
   - Verify PostgreSQL connection
   - Check Pulsar subscription is active

### Logs

```bash
# Server logs
docker logs -f armada-server
kubectl logs -n armada deployment/armada-server

# Executor logs
docker logs -f armada-executor
kubectl logs -n armada deployment/armada-executor

# Lookout logs
docker logs -f lookout
kubectl logs -n armada deployment/lookout
```

## Performance Tuning

### High-Throughput Configuration

For large-scale deployments:

1. **Increase server replicas**:
   ```yaml
   replicas: 5  # In kubernetes-deployment.yaml
   ```

2. **Scale Redis**:
   - Use Redis Cluster for horizontal scaling
   - Increase connection pool size

3. **Optimize PostgreSQL**:
   - Increase `max_connections`
   - Tune `shared_buffers` and `work_mem`
   - Use connection pooling (PgBouncer)

4. **Tune scheduling**:
   ```yaml
   scheduling:
     maxJobsPerCall: 10000  # Increase for high throughput
     lease:
       expiryLoopInterval: 30s  # Reduce for faster lease renewal
   ```

## References

- [Armada Documentation](https://github.com/G-Research/armada)
- [Armada API Reference](https://github.com/G-Research/armada/blob/master/docs/api.md)
- [Armada Operator Guide](https://github.com/G-Research/armada/blob/master/docs/operator.md)
