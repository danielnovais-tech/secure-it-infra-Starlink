# Apache Pulsar for Reliability Integrations

This directory contains the configuration and deployment files for Apache Pulsar, a distributed messaging and streaming platform used for reliability integrations in the Starlink infrastructure.

## Overview

Apache Pulsar provides:
- **Message persistence**: Durable message storage with configurable retention
- **Message deduplication**: Ensures exactly-once message delivery
- **Multi-tenancy**: Isolated namespaces for different teams/services
- **Geo-replication**: Cross-datacenter message replication
- **High availability**: Fault-tolerant architecture with automatic failover

## Architecture

The Pulsar deployment consists of:

1. **ZooKeeper**: Coordination service for cluster metadata and configuration
2. **BookKeeper**: Distributed storage system for message persistence
3. **Broker**: Message routing and serving layer
4. **Pulsar Manager**: Web UI for cluster management

## Deployment Options

### Docker Compose (Development/Testing)

```bash
cd pulsar
docker-compose up -d
```

This will start:
- ZooKeeper on port 2181
- Pulsar Broker on ports 6650 (Pulsar protocol) and 8080 (HTTP)
- Pulsar Manager on ports 9527 (UI) and 7750 (backend API)

Access the Pulsar Manager UI at: http://localhost:9527

### Kubernetes (Production)

```bash
kubectl apply -f pulsar/kubernetes-deployment.yaml
```

This deploys:
- 3 ZooKeeper replicas for high availability
- 3 BookKeeper replicas for data redundancy
- 3 Broker replicas for load distribution
- 1 Pulsar Manager instance

The broker service will be exposed via LoadBalancer. Get the external IP:

```bash
kubectl get svc broker -n pulsar
```

## Configuration

### Broker Configuration

The broker is configured for reliability with:

- **Message retention**: 7 days (10080 minutes) by default
- **Deduplication**: Enabled to prevent duplicate messages
- **Replication**: 3 copies of each message (ensemble size)
- **Write quorum**: 2 replicas must acknowledge writes
- **Ack quorum**: 2 replicas must acknowledge before confirming to producer

See `broker.conf` for detailed configuration options.

### Key Configuration Parameters

```yaml
# Message retention
defaultRetentionTimeInMinutes: 10080  # 7 days
defaultRetentionSizeInMB: 1024

# Deduplication for reliability
brokerDeduplicationEnabled: true

# Storage redundancy
managedLedgerDefaultEnsembleSize: 3
managedLedgerDefaultWriteQuorum: 2
managedLedgerDefaultAckQuorum: 2
```

## Usage

### Creating a Topic

```bash
# Using Pulsar Admin CLI
docker exec -it pulsar-broker bin/pulsar-admin topics create persistent://public/default/my-topic

# Or via HTTP API
curl -X PUT http://localhost:8080/admin/v2/persistent/public/default/my-topic
```

### Publishing Messages

```python
import pulsar

client = pulsar.Client('pulsar://localhost:6650')
producer = client.create_producer('persistent://public/default/my-topic')

# Send message with deduplication
producer.send(
    content=b'Hello Starlink!',
    properties={'key': 'value'},
    sequence_id=1  # For deduplication
)

client.close()
```

### Consuming Messages

```python
import pulsar

client = pulsar.Client('pulsar://localhost:6650')
consumer = client.subscribe(
    topic='persistent://public/default/my-topic',
    subscription_name='my-subscription'
)

while True:
    msg = consumer.receive()
    print(f"Received: {msg.data()}")
    consumer.acknowledge(msg)

client.close()
```

## Integration with Armada Atlas

Pulsar is integrated with Armada Atlas for reliable event streaming:

- **Job events**: Armada publishes job lifecycle events to Pulsar
- **Reliability**: Pulsar ensures events are not lost during failures
- **Scalability**: Multiple consumers can process events in parallel
- **Audit trail**: All job events are persisted for compliance

Topics used:
- `persistent://public/default/armada-jobset-events`: Job set events
- `persistent://public/default/armada-job-events`: Individual job events

## Monitoring

### Metrics

Pulsar exposes Prometheus metrics at:
```
http://localhost:8080/metrics
```

Key metrics to monitor:
- `pulsar_storage_size`: Storage used
- `pulsar_rate_in`: Message ingress rate
- `pulsar_rate_out`: Message egress rate
- `pulsar_throughput_in`: Bytes ingress throughput
- `pulsar_throughput_out`: Bytes egress throughput

### Health Checks

```bash
# Check broker health
curl http://localhost:8080/admin/v2/brokers/health

# Check cluster status
docker exec -it pulsar-broker bin/pulsar-admin clusters list
```

## Security

### Production Security Checklist

For production deployments, enable:

1. **TLS Encryption**: Encrypt data in transit
   ```yaml
   tlsEnabled: true
   tlsCertificateFilePath: /path/to/broker-cert.pem
   tlsKeyFilePath: /path/to/broker-key.pem
   ```

2. **Authentication**: Use token-based or mTLS authentication
   ```yaml
   authenticationEnabled: true
   authenticationProviders: org.apache.pulsar.broker.authentication.AuthenticationProviderToken
   ```

3. **Authorization**: Control topic access
   ```yaml
   authorizationEnabled: true
   superUserRoles: admin
   ```

4. **Network policies**: Restrict network access in Kubernetes

## Troubleshooting

### Common Issues

1. **ZooKeeper connection failed**
   - Check ZooKeeper is healthy: `docker exec -it pulsar-zookeeper bin/pulsar-zookeeper-ruok.sh`
   - Verify network connectivity

2. **BookKeeper not ready**
   - Check BookKeeper logs: `docker logs pulsar-bookkeeper`
   - Ensure sufficient disk space

3. **Broker startup issues**
   - Check broker logs: `docker logs pulsar-broker`
   - Verify ZooKeeper and BookKeeper are running

### Logs

```bash
# View broker logs
docker logs -f pulsar-broker

# View BookKeeper logs
docker logs -f pulsar-bookkeeper

# View ZooKeeper logs
docker logs -f pulsar-zookeeper
```

## References

- [Apache Pulsar Documentation](https://pulsar.apache.org/docs/next/)
- [Pulsar Admin API](https://pulsar.apache.org/admin-rest-api/)
- [Pulsar Client Libraries](https://pulsar.apache.org/docs/next/client-libraries/)
