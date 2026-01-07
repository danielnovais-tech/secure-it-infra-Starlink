# secure-it-infra-Starlink

Repository dedicated to security solutions for managed enterprise infrastructures supporting Starlink.

## Overview

This repository provides infrastructure components for reliable and scalable fleet management of Starlink enterprise deployments. It includes:

- **Apache Pulsar**: Distributed messaging and streaming platform for reliability integrations
- **Armada Atlas**: Multi-cluster batch job scheduler for fleet management

## Features

### Apache Pulsar for Reliability Integrations

- **Message Persistence**: Durable storage with configurable retention policies
- **Deduplication**: Exactly-once message delivery semantics
- **Multi-tenancy**: Isolated namespaces for different teams and services
- **Geo-replication**: Cross-datacenter message replication for disaster recovery
- **High Availability**: Fault-tolerant architecture with automatic failover

### Armada Atlas for Fleet Management

- **Multi-cluster Scheduling**: Manage batch jobs across multiple Kubernetes clusters
- **Fair Resource Allocation**: Queue-based fair sharing of cluster resources
- **Priority Scheduling**: Support for job priorities and preemption
- **High Throughput**: Handle thousands of jobs per second
- **Integrated Monitoring**: Web UI for job visibility and cluster management

### Integration Benefits

- **Reliable Event Streaming**: Job events are reliably streamed through Pulsar
- **Complete Audit Trail**: All job lifecycle events are persisted
- **Scalable Architecture**: Horizontal scaling of both compute and messaging layers
- **Production Ready**: Battle-tested components used by large-scale organizations

## Quick Start

Get started quickly with Docker Compose:

```bash
# Start Pulsar
cd pulsar
docker-compose up -d

# Start Armada Atlas
cd ../armada-atlas
docker-compose up -d
```

Access the UIs:
- **Pulsar Manager**: http://localhost:9527
- **Armada Lookout**: http://localhost:8089

For detailed instructions, see the [Quick Start Guide](docs/QUICKSTART.md).

## Documentation

- [Quick Start Guide](docs/QUICKSTART.md) - Get up and running quickly
- [Integration Guide](docs/INTEGRATION.md) - Detailed architecture and integration patterns
- [Security Configuration Guide](docs/SECURITY.md) - **Production security hardening (REQUIRED reading)**
- [Pulsar Documentation](pulsar/README.md) - Apache Pulsar setup and configuration
- [Armada Atlas Documentation](armada-atlas/README.md) - Armada setup and usage

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     Starlink Infrastructure                      │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────────┐
        │         Armada Atlas Server             │
        │      (Fleet Management Control)         │
        └──────────┬──────────────────────────────┘
                   │
                   │ Publishes job events
                   ▼
        ┌─────────────────────────────────────────┐
        │         Apache Pulsar Cluster           │
        │      (Reliable Event Streaming)         │
        └──────────┬──────────────────────────────┘
                   │
                   │ Consumes events
                   ▼
        ┌─────────────────────────────────────────┐
        │      Event Consumers & Analytics        │
        └─────────────────────────────────────────┘
```

## Repository Structure

```
.
├── pulsar/                          # Apache Pulsar configuration
│   ├── docker-compose.yml          # Docker Compose deployment
│   ├── kubernetes-deployment.yaml  # Kubernetes deployment
│   ├── broker.conf                 # Broker configuration
│   └── README.md                   # Pulsar documentation
│
├── armada-atlas/                    # Armada Atlas configuration
│   ├── docker-compose.yml          # Docker Compose deployment
│   ├── kubernetes-deployment.yaml  # Kubernetes deployment
│   ├── config/                     # Configuration files
│   │   ├── armada-server-config.yaml
│   │   ├── armada-executor-config.yaml
│   │   ├── lookout-config.yaml
│   │   └── lookout-ingester-config.yaml
│   └── README.md                   # Armada documentation
│
└── docs/                            # Documentation
    ├── QUICKSTART.md               # Quick start guide
    └── INTEGRATION.md              # Integration guide
```

## Deployment Options

### Docker Compose (Development/Testing)

Suitable for local development and testing:

```bash
# See Quick Start Guide for detailed instructions
cd pulsar && docker-compose up -d
cd ../armada-atlas && docker-compose up -d
```

### Kubernetes (Production)

Suitable for production deployments:

```bash
# Deploy Pulsar
kubectl apply -f pulsar/kubernetes-deployment.yaml

# Deploy Armada
kubectl apply -f armada-atlas/kubernetes-deployment.yaml
```

See individual component READMEs for detailed deployment instructions.

## Security Considerations

⚠️ **IMPORTANT**: The default configurations are for development and testing only!

For production deployments, ensure you:

1. **Enable TLS Encryption**: Encrypt data in transit for both Pulsar and Armada
2. **Configure Authentication**: Use token-based or certificate-based authentication
3. **Enable Authorization**: Implement role-based access control (RBAC)
4. **Secure Secrets**: Use Kubernetes Secrets or a secrets management solution (Vault, AWS Secrets Manager, etc.)
5. **Change Default Passwords**: All default passwords must be changed
6. **Network Policies**: Restrict network access between components
7. **Regular Updates**: Keep all components updated with security patches

**See the comprehensive [Security Configuration Guide](docs/SECURITY.md) for detailed hardening instructions.**

## Monitoring

Both components expose Prometheus metrics:

- **Pulsar Broker**: `http://broker:8080/metrics`
- **Armada Server**: `http://armada-server:9000/metrics`
- **Armada Executor**: `http://armada-executor:9001/metrics`

Key metrics to monitor:
- Job submission and completion rates
- Message ingress/egress throughput
- Resource utilization across clusters
- Event processing lag
- System health and availability

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

See [LICENSE](LICENSE) file for details.

## Support

For issues and questions:

- Apache Pulsar: https://pulsar.apache.org/community
- Armada: https://github.com/G-Research/armada
- Repository Issues: https://github.com/danielnovais-tech/secure-it-infra-Starlink/issues

## References

- [Apache Pulsar](https://pulsar.apache.org/)
- [Armada](https://github.com/G-Research/armada)
- [Kubernetes](https://kubernetes.io/)
- [Starlink](https://www.starlink.com/)
