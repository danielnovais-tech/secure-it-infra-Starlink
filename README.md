# secure-it-infra-Starlink

Repository dedicated to security solutions for managed enterprise infrastructures supporting Starlink.

## Overview

This repository contains the **Starlink Security Foundation**, an enterprise security management system for infrastructures using Starlink connectivity. It provides comprehensive security monitoring, event logging, and network management capabilities specifically designed for remote or rural enterprise deployments.

## Features

- **Security Event Logging**: Automatic logging of security events to monthly JSON files
- **Network Monitoring**: Continuous monitoring of network devices and open ports
- **Metrics Tracking**: Real-time tracking of latency, jitter, packet loss, and throughput
- **Security Scoring**: Automated calculation of security scores and connection stability
- **Intelligent Recommendations**: Contextual security recommendations based on current metrics
- **Threat Management**: Active threat tracking and management
- **Graceful Shutdown**: POSIX signal handling for clean daemon operation

## Quick Start

### Installation

```bash
git clone https://github.com/danielnovais-tech/secure-it-infra-Starlink.git
cd secure-it-infra-Starlink
```

No external dependencies required - uses Python 3.7+ standard library only.

### Generate Security Report

```bash
python3 src/starlink_security.py --report
```

### Check Status

```bash
python3 src/starlink_security.py --status
```

### Run Tests

```bash
python3 tests/test_security.py
```

## Documentation

See [IMPLEMENTATION.md](IMPLEMENTATION.md) for detailed documentation including:
- Architecture overview
- Component descriptions
- Event logging format
- Configuration options
- Development guidelines

## Security

- Zero security vulnerabilities (CodeQL verified)
- All events logged with proper exception handling
- Graceful shutdown on SIGTERM/SIGINT
- Falls back to local directories when system paths are inaccessible

## License

See LICENSE file for details.
