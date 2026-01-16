# Pulsar and Armada Atlas Integration Guide

This document describes how Apache Pulsar and Armada Atlas work together to provide reliable fleet management for Starlink infrastructure.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     Starlink Infrastructure                      │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────────┐
        │         Armada Atlas Server             │
        │      (Fleet Management Control)         │
        │                                          │
        │  • Job Scheduling                       │
        │  • Resource Allocation                  │
        │  • Multi-cluster Coordination          │
        └──────────┬──────────────────────────────┘
                   │
                   │ Publishes job events
                   ▼
        ┌─────────────────────────────────────────┐
        │         Apache Pulsar Cluster           │
        │      (Reliable Event Streaming)         │
        │                                          │
        │  • Message Persistence                  │
        │  • Event Deduplication                  │
        │  • Multi-tenant Topics                  │
        └──────────┬──────────────────────────────┘
                   │
                   │ Consumes events
                   ▼
        ┌─────────────────────────────────────────┐
        │      Event Consumers                    │
        │                                          │
        │  • Lookout Ingester (UI)               │
        │  • Audit Systems                        │
        │  • Analytics Pipelines                  │
        │  • External Integrations               │
        └─────────────────────────────────────────┘
```

## Why Pulsar + Armada?

### Reliability Through Event Streaming

1. **Guaranteed Delivery**: Pulsar ensures job events are never lost, even during system failures
2. **Event Deduplication**: Prevents duplicate processing of job events
3. **Audit Trail**: Complete history of all job lifecycle events
4. **Scalability**: Multiple consumers can process events independently

### Fleet Management at Scale

1. **Multi-cluster Scheduling**: Armada manages jobs across multiple Kubernetes clusters
2. **Fair Resource Allocation**: Queues ensure fair sharing of resources
3. **Priority Scheduling**: Critical jobs can preempt lower-priority ones
4. **High Throughput**: Handle thousands of jobs per second

## Integration Points

### 1. Job Event Publishing

Armada publishes events to Pulsar topics:

```yaml
# Armada Server Configuration
pulsar:
  enabled: true
  URL: "pulsar://broker.pulsar:6650"
  jobsetEventsTopic: "persistent://public/default/armada-jobset-events"
  jobEventsTopic: "persistent://public/default/armada-job-events"
```

**Event Types**:
- `JobSubmitted`: New job submitted to queue
- `JobScheduled`: Job assigned to a cluster
- `JobRunning`: Job started execution
- `JobSucceeded`: Job completed successfully
- `JobFailed`: Job failed
- `JobCancelled`: Job was cancelled

### 2. Event Consumption

Multiple consumers can subscribe to job events:

#### Lookout Ingester (Built-in)

```yaml
# Lookout Ingester Configuration
pulsar:
  enabled: true
  url: "pulsar://broker.pulsar:6650"
  jobEventsTopic: "persistent://public/default/armada-job-events"
  subscriptionName: "lookout-ingester"
  subscriptionType: "Shared"
```

#### Custom Consumers

```python
import pulsar
import json

client = pulsar.Client('pulsar://broker.pulsar:6650')

# Subscribe to job events
consumer = client.subscribe(
    topic='persistent://public/default/armada-job-events',
    subscription_name='my-analytics',
    subscription_type=pulsar.SubscriptionType.Shared
)

while True:
    msg = consumer.receive()
    try:
        event = json.loads(msg.data())
        
        # Process event
        if event['type'] == 'JobFailed':
            send_alert(event)
        elif event['type'] == 'JobSucceeded':
            update_metrics(event)
        
        consumer.acknowledge(msg)
    except Exception as e:
        consumer.negative_acknowledge(msg)

client.close()
```

## Deployment Scenarios

### Scenario 1: Development/Testing

Deploy both systems with Docker Compose:

```bash
# Start Pulsar
cd pulsar
docker-compose up -d

# Wait for Pulsar to be ready
sleep 30

# Start Armada
cd ../armada-atlas
docker-compose up -d
```

### Scenario 2: Production on Kubernetes

Deploy in order:

```bash
# 1. Deploy Pulsar cluster
kubectl apply -f pulsar/kubernetes-deployment.yaml

# 2. Wait for Pulsar to be ready
kubectl wait --for=condition=ready pod -l app=pulsar,component=broker -n pulsar --timeout=300s

# 3. Deploy Armada
kubectl apply -f armada-atlas/kubernetes-deployment.yaml

# 4. Verify integration
kubectl logs -n armada deployment/armada-server | grep -i pulsar
```

### Scenario 3: Multi-Region Deployment

For geo-distributed Starlink infrastructure:

1. **Pulsar Geo-Replication**:
   ```bash
   # Configure replication between regions
   bin/pulsar-admin clusters create region-us-west
   bin/pulsar-admin clusters create region-eu-west
   
   # Enable geo-replication for topics
   bin/pulsar-admin topics set-replication-clusters \
     persistent://public/default/armada-job-events \
     --clusters region-us-west,region-eu-west
   ```

2. **Armada Multi-Cluster**:
   - Deploy Armada Server in each region
   - Configure executors across all Starlink clusters
   - Use geo-replicated Pulsar for cross-region visibility

## Configuration Examples

### Reliable Job Processing

Ensure jobs are processed exactly once:

```yaml
# Armada Server
pulsar:
  enabled: true
  blockIfQueueFull: true  # Block if Pulsar is unavailable
  compressionType: "LZ4"  # Compress events
  batchingMaxMessages: 1000  # Batch for efficiency

# Broker Configuration
brokerDeduplicationEnabled: true  # Prevent duplicate events
managedLedgerDefaultAckQuorum: 2  # Require 2 replicas
```

### High-Throughput Configuration

For large-scale fleet management:

```yaml
# Armada Server
scheduling:
  maxJobsPerCall: 10000  # Schedule many jobs at once

# Pulsar Broker
backlogQuotaDefaultLimitGB: 100  # Allow large backlogs
maxConnectionsPerBroker: 1000  # Handle many connections
```

### Security Configuration

Enable TLS and authentication:

```yaml
# Pulsar Broker
tlsEnabled: true
authenticationEnabled: true
authenticationProviders: org.apache.pulsar.broker.authentication.AuthenticationProviderToken

# Armada Server
pulsar:
  tlsTrustCertsFilePath: /path/to/ca-cert.pem
  authParams: "token:YOUR_TOKEN"
```

## Monitoring Integration

### Metrics Collection

Both systems expose Prometheus metrics:

```yaml
# Prometheus scrape config
scrape_configs:
  - job_name: 'pulsar-broker'
    static_configs:
      - targets: ['broker.pulsar:8080']
    metrics_path: '/metrics'
  
  - job_name: 'armada-server'
    static_configs:
      - targets: ['armada-server.armada:9000']
    metrics_path: '/metrics'
```

### Key Metrics to Monitor

**Pulsar**:
- `pulsar_storage_size`: Storage used by topics
- `pulsar_rate_in`: Message ingress rate
- `pulsar_subscription_back_log`: Unprocessed messages

**Armada**:
- `armada_job_submit_rate`: Job submission rate
- `armada_job_running`: Currently running jobs
- `armada_cluster_capacity`: Available cluster resources

### Alerts

Example Prometheus alerts:

```yaml
groups:
  - name: armada_pulsar_integration
    rules:
      - alert: PulsarBacklogHigh
        expr: pulsar_subscription_back_log{subscription="lookout-ingester"} > 100000
        annotations:
          summary: "High backlog in Armada event processing"
      
      - alert: ArmadaEventPublishingFailed
        expr: rate(armada_pulsar_publish_errors[5m]) > 0
        annotations:
          summary: "Armada failing to publish events to Pulsar"
```

## Troubleshooting

### Jobs Not Appearing in Lookout UI

1. Check Pulsar topic has messages:
   ```bash
   docker exec -it pulsar-broker bin/pulsar-admin topics stats \
     persistent://public/default/armada-job-events
   ```

2. Check Lookout Ingester is consuming:
   ```bash
   kubectl logs -n armada deployment/lookout-ingester
   ```

3. Verify subscription exists:
   ```bash
   docker exec -it pulsar-broker bin/pulsar-admin topics subscriptions \
     persistent://public/default/armada-job-events
   ```

### Armada Can't Connect to Pulsar

1. Test connectivity:
   ```bash
   kubectl exec -n armada deployment/armada-server -- \
     nc -zv broker.pulsar 6650
   ```

2. Check Pulsar broker health:
   ```bash
   kubectl get pods -n pulsar -l component=broker
   ```

3. Review Armada logs:
   ```bash
   kubectl logs -n armada deployment/armada-server | grep -i pulsar
   ```

### Event Processing Lag

1. Check subscription backlog:
   ```bash
   bin/pulsar-admin topics stats persistent://public/default/armada-job-events
   ```

2. Scale Lookout Ingester:
   ```bash
   kubectl scale deployment lookout-ingester -n armada --replicas=3
   ```

3. Increase consumer threads:
   ```yaml
   ingestion:
     workerCount: 20  # Increase workers
   ```

## Best Practices

### 1. Topic Organization

Create separate topics for different event types:

```
persistent://public/starlink/job-events           # Job lifecycle events
persistent://public/starlink/cluster-events       # Cluster status events
persistent://public/starlink/resource-events      # Resource utilization events
```

### 2. Subscription Types

Choose appropriate subscription types:

- **Shared**: Multiple consumers process events in parallel (Lookout Ingester)
- **Exclusive**: Single consumer for ordered processing (Audit logs)
- **Failover**: Active-passive consumer setup (Critical alerts)

### 3. Message Retention

Configure retention based on compliance needs:

```yaml
# Pulsar Broker
defaultRetentionTimeInMinutes: 43200  # 30 days for compliance
defaultRetentionSizeInMB: 10240  # 10 GB
```

### 4. Resource Planning

**Pulsar**:
- BookKeeper: 50 GB per replica for message storage
- Broker: 2 GB RAM per broker minimum
- ZooKeeper: 256 MB RAM per node

**Armada**:
- Server: 2 GB RAM + 1 CPU per instance
- Executor: 1 GB RAM + 0.5 CPU per cluster
- PostgreSQL: 20 GB storage for job history

### 5. Disaster Recovery

1. **Backup PostgreSQL** (Armada job history):
   ```bash
   pg_dump armada > armada_backup.sql
   ```

2. **Pulsar Geo-Replication** (automatic failover):
   ```yaml
   replicationClusters: ["region-1", "region-2", "region-3"]
   ```

3. **Regular Testing**:
   - Test failover procedures monthly
   - Verify event replay from Pulsar topics
   - Validate job recovery mechanisms

## Performance Benchmarks

### Expected Throughput

**Pulsar**:
- 1M messages/second ingress (3-node cluster)
- 2M messages/second egress (3-node cluster)
- < 10ms p99 latency

**Armada**:
- 10,000 jobs/second submission rate
- 100,000 concurrent jobs per cluster
- < 100ms scheduling latency

### Tuning for Your Environment

Adjust based on your workload:

```yaml
# High throughput, lower latency
pulsar:
  batchingMaxPublishDelay: 1ms
  compressionType: "NONE"

# Lower throughput, higher efficiency
pulsar:
  batchingMaxPublishDelay: 100ms
  compressionType: "LZ4"
```

## References

- [Apache Pulsar Documentation](https://pulsar.apache.org/docs/)
- [Armada Documentation](https://github.com/G-Research/armada)
- [Pulsar Performance Tuning](https://pulsar.apache.org/docs/next/performance-pulsar-perf/)
- [Armada Performance Guide](https://github.com/G-Research/armada/blob/master/docs/performance.md)
