# secure-it-infra-Starlink
Repository dedicated to security solutions for managed enterprise infrastructures supporting Starlink.

## Overview

This project provides a Network Security Monitor for Starlink infrastructure that tracks key network and security metrics including:
- Latency (ms)
- Jitter (ms)
- Packet Loss (%)
- Throughput (Mbps)

## Features

- **Real-time Metrics Monitoring**: Continuously monitors network performance metrics
- **Security Scanning**: Periodic security threat scanning
- **Alert Monitoring**: Detects anomalies and triggers warnings for high latency and packet loss
- **Graceful Shutdown**: Properly manages module lifecycles with error handling

## Usage

Run the network security monitor:

```bash
python main.py
```

Or import as a module:

```python
from src.network_security_monitor import NetworkSecurityMonitor
import asyncio

async def run():
    monitor = NetworkSecurityMonitor()
    try:
        await monitor.start()
    finally:
        await monitor.stop()

asyncio.run(run())
```

## Architecture

The system consists of three main monitoring modules:
1. **Metrics Updater**: Updates network metrics every 5 seconds
2. **Security Scanner**: Performs periodic security scans
3. **Alert Monitor**: Checks for anomalies and triggers warnings

## Requirements

- Python 3.7+
- No external dependencies (uses only Python standard library)
