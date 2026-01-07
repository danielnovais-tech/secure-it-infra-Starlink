# Architecture Overview

## Core Security Foundation

The Secure IT Infrastructure for Starlink is designed with a modular architecture that provides foundational security components for managing enterprise Starlink deployments.

## Components

### 1. Security Levels (`security_level.py`)

**Purpose**: Define and manage security states across the infrastructure.

**Design Pattern**: Enumeration with Priority Pattern

**Key Features**:
- Four distinct security levels with increasing priority
- Comparison methods for level evaluation
- Numeric priority for automated decision-making

**Use Cases**:
- Automated security response based on threat level
- Access control decisions
- Monitoring and alerting thresholds

### 2. Connection Types (`connection_type.py`)

**Purpose**: Manage different network connectivity modes.

**Design Pattern**: Enumeration with Capability Pattern

**Key Features**:
- Three connection modes tailored for Starlink deployments
- Capability checks (redundancy, satellite-only)
- Clear naming convention for operational clarity

**Use Cases**:
- Network failover management
- Connection health monitoring
- Disaster recovery planning

### 3. Event Queue System (`event_queue.py`)

**Purpose**: Provide event-driven architecture for security monitoring.

**Design Pattern**: Producer-Consumer with Observer Pattern

**Key Features**:
- Thread-safe queue implementation
- Async/sync event handler support
- Event history with filtering
- Multiple event types for different scenarios

**Architecture**:
```
┌─────────────┐
│  Producer   │ ──→ put() ──→ ┌──────────────────┐
└─────────────┘               │ SecurityEventQueue│
                              │  - Queue          │
┌─────────────┐               │  - Handlers       │
│  Producer   │ ──→ put() ──→ │  - History        │
└─────────────┘               └────────┬──────────┘
                                       │
                                   get() / process_events()
                                       │
                                       ↓
                              ┌────────────────┐
                              │  Event Handlers │
                              │  - Logging      │
                              │  - Alerting     │
                              │  - Automated    │
                              │    Response     │
                              └────────────────┘
```

**Use Cases**:
- Real-time security monitoring
- Automated incident response
- Audit trail and compliance
- System health monitoring

### 4. Encryption Manager (`encryption.py`)

**Purpose**: Secure sensitive data at rest and in transit.

**Design Pattern**: Strategy Pattern with Fernet Encryption

**Key Features**:
- Symmetric encryption using Fernet
- Password-based key derivation (PBKDF2HMAC with 480,000 iterations)
- Key rotation support
- Both string and byte encryption

**Security Considerations**:
- Uses SHA-256 for password hashing
- High iteration count for key derivation
- Support for salt storage and reproduction
- Exception handling for invalid decryption

**Use Cases**:
- API key and credential storage
- Configuration data protection
- Sensitive log data encryption
- Secure communication between services

## Integration Patterns

### Pattern 1: Security Monitoring Pipeline

```python
# Setup
queue = SecurityEventQueue()
encryption_manager = EncryptionManager.from_password("secure_pass")

# Register handlers
queue.register_handler(EventType.INTRUSION_DETECTED, alert_security_team)
queue.register_handler(EventType.SECURITY_LEVEL_CHANGE, update_firewall_rules)

# Process events asynchronously
asyncio.create_task(queue.process_events())

# Generate events from monitoring systems
if detect_intrusion():
    queue.put(SecurityEvent(
        event_type=EventType.INTRUSION_DETECTED,
        security_level=SecurityLevel.CRITICAL,
        ...
    ))
```

### Pattern 2: Secure Configuration Management

```python
# Store encrypted credentials
manager = EncryptionManager.from_password(os.environ["MASTER_PASSWORD"])

# Encrypt sensitive config
config = {
    "starlink_api_key": "sk_live_...",
    "endpoint": "https://api.starlink.com"
}
encrypted_config = manager.encrypt_str(json.dumps(config))

# Store salt for later retrieval
store_salt(manager.salt)

# Later: Retrieve and decrypt
manager = EncryptionManager.from_password(
    os.environ["MASTER_PASSWORD"],
    salt=retrieve_salt()
)
config = json.loads(manager.decrypt_str(encrypted_config))
```

### Pattern 3: Adaptive Security Level Management

```python
# Monitor and adjust security levels
current_level = SecurityLevel.NORMAL

# Detect anomaly
if anomaly_detected():
    new_level = SecurityLevel.ELEVATED
    
    if new_level.is_higher_than(current_level):
        # Escalate security
        queue.put(SecurityEvent(
            event_type=EventType.SECURITY_LEVEL_CHANGE,
            security_level=new_level,
            data={"previous": str(current_level)}
        ))
        current_level = new_level
        apply_security_level(current_level)
```

## Thread Safety

- **SecurityEventQueue**: Thread-safe using `queue.Queue`
- **EncryptionManager**: Thread-safe for read operations, requires synchronization for key rotation
- **Enums**: Thread-safe (immutable)

## Performance Considerations

1. **Event Queue**:
   - History limited to 1000 events by default (configurable)
   - Async processing prevents blocking
   - Handler exceptions don't stop processing

2. **Encryption**:
   - PBKDF2 iterations (480,000) intentionally slow for security
   - Cache encryption manager instances when possible
   - Use key rotation judiciously (requires re-encryption)

3. **Memory Usage**:
   - Event history is kept in memory (monitor in long-running processes)
   - Consider periodic history clearing for high-volume scenarios

## Extension Points

1. **Custom Event Types**: Extend `EventType` enum for domain-specific events
2. **Security Levels**: Add custom comparison logic if needed
3. **Connection Types**: Add new connection modes for specific scenarios
4. **Event Handlers**: Register multiple handlers per event type
5. **Encryption Backends**: Wrap alternative encryption libraries with same interface

## Testing Strategy

- **Unit Tests**: 62 comprehensive tests covering all components
- **Integration Tests**: Example script demonstrates component interaction
- **Security Tests**: CodeQL scanner for vulnerability detection
- **Edge Cases**: Unicode, empty strings, large data, concurrent access

## Future Enhancements

Potential areas for expansion:
- Persistent event storage (database integration)
- Distributed event queue (Redis, RabbitMQ)
- Multi-tenant security isolation
- Hardware security module (HSM) integration
- Certificate management for asymmetric encryption
- Rate limiting and throttling for event processing
- Metrics and monitoring integration (Prometheus, Grafana)
# Starlink Security Auditor - Architecture Overview

## Design Principles

### 1. Modularity
Each security domain is implemented as an independent module with its own check method. This allows:
- Independent testing of each module
- Easy addition of new security checks
- Flexible configuration of audit scope

### 2. Defense in Depth
The auditor implements multiple layers of security validation:
- Network perimeter (firewall, ports)
- Service configuration (SSH, system services)
- Data protection (encryption)
- Access control (VPN, privileges)
- Network topology (segmentation)

### 3. Starlink-Specific Design
Considerations for satellite-based connectivity:
- VPN as mandatory security layer for remote access
- Resilient to connectivity interruptions
- Optimized for high-latency environments
- Focus on essential security controls

### 4. Enterprise Requirements
- JSON-based configuration for automation
- Structured logging for SIEM integration
- Machine-readable reports for dashboards
- Human-readable output for operators

## Component Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    SecurityAuditor                          │
│                    (Main Orchestrator)                      │
└─────────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   Config     │    │   Logging    │    │  Reporting   │
│   Manager    │    │   System     │    │   Engine     │
└──────────────┘    └──────────────┘    └──────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   Network    │    │   Service    │    │  Encryption  │
│   Security   │    │   Vulns      │    │  Validation  │
└──────────────┘    └──────────────┘    └──────────────┘
        │                   │                   │
        ▼                   ▼                   ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│     VPN      │    │   Network    │    │  Privilege   │
│Configuration │    │Segmentation  │    │   Checks     │
└──────────────┘    └──────────────┘    └──────────────┘
```

## Security Check Modules

### Network Security Module
**Purpose**: Validate network perimeter security
**Checks**:
- Firewall status and rules
- Open port scanning
- Network interface configuration

**Dependencies**: 
- ufw/iptables
- socket library
- ip command

### Service Vulnerability Module
**Purpose**: Assess service configurations for security issues
**Checks**:
- SSH hardening (root login, password auth)
- Running services inventory
- Service-specific misconfigurations

**Dependencies**:
- systemctl
- SSH config files

### Encryption Validation Module
**Purpose**: Verify data protection mechanisms
**Checks**:
- Disk encryption (LUKS)
- SSL/TLS certificates
- Encryption at rest and in transit

**Dependencies**:
- lsblk
- Certificate directories

### VPN Configuration Module
**Purpose**: Ensure secure remote access (critical for Starlink)
**Checks**:
- VPN software installation (OpenVPN/WireGuard)
- VPN service status
- VPN configuration files

**Dependencies**:
- openvpn/wg
- systemctl

### Network Segmentation Module
**Purpose**: Validate network topology security
**Checks**:
- Network interface enumeration
- Routing table analysis
- VLAN configuration

**Dependencies**:
- ip command

### Privilege Checks Module
**Purpose**: Enforce least privilege principle
**Checks**:
- Sudoers configuration
- Sensitive file permissions
- User account policies

**Dependencies**:
- File system access

## Data Flow

```
1. Configuration Loading
   ├─ Load JSON config or use defaults
   ├─ Validate configuration
   └─ Setup logging

2. Audit Execution
   ├─ Initialize result collection
   ├─ For each enabled check:
   │  ├─ Execute check method
   │  ├─ Collect results
   │  └─ Log outcomes
   └─ Generate summary

3. Report Generation
   ├─ Compile all results
   ├─ Calculate summary statistics
   ├─ Format for output (JSON/console)
   └─ Save to file

4. Exit
   └─ Return appropriate exit code
```

## Extensibility Points

### Adding New Security Checks

1. **Create Check Method**:
```python
def check_new_security_domain(self) -> None:
    """New security domain check."""
    self.logger.info("Running new security checks...")
    
    # Perform security validation
    result = self._run_command(['some', 'command'])
    
    # Add result
    self._add_result(
        'Check Name',
        'PASS/FAIL/WARN/INFO',
        'Descriptive message',
        {'details': 'additional info'},
        'Actionable recommendation'
    )
```

2. **Update Configuration Schema**:
```json
{
  "audit_scope": {
    "new_security_domain": true
  }
}
```

3. **Integrate in run_audit()**:
```python
if scope.get('new_security_domain', False):
    self.check_new_security_domain()
```

### Custom Result Handlers

Extend report generation by subclassing:
```python
class CustomSecurityAuditor(SecurityAuditor):
    def save_report(self, report: AuditReport) -> None:
        # Custom report format (CSV, XML, etc.)
        super().save_report(report)
        # Additional custom processing
```

## Error Handling

### Command Execution Errors
- Timeout protection (30s default)
- Graceful fallback for missing commands
- Error logging with context

### Permission Errors
- Informative messages when sudo required
- Partial audit capability without root
- Clear recommendations for required permissions

### Configuration Errors
- Validation with meaningful error messages
- Fallback to defaults on invalid config
- Configuration merge strategy

## Security Considerations

### Least Privilege Execution
- Only requires root for specific checks
- Graceful degradation without sudo
- Clear documentation of permission requirements

### Safe Command Execution
- Timeout protection against hanging commands
- Output sanitization
- No shell injection vulnerabilities

### Data Protection
- No sensitive data in logs (passwords, keys)
- Secure handling of audit results
- Configurable log retention

## Performance

### Optimization Strategies
- Parallel check execution where possible
- Timeout limits on slow operations
- Efficient command chaining

### Resource Usage
- Minimal memory footprint
- Low CPU usage
- Network bandwidth conscious (important for Starlink)

## Future Enhancements

### Planned Features
1. Database integration for historical tracking
2. Web dashboard for centralized monitoring
3. Alert integration (email, Slack, PagerDuty)
4. Compliance framework mapping (CIS, NIST, PCI-DSS)
5. Automated remediation scripts
6. Container security checks (Docker, Kubernetes)
7. Cloud provider integration (AWS, Azure, GCP)

### Starlink-Specific Enhancements
1. Bandwidth usage monitoring
2. Latency testing and validation
3. Failover configuration checks
4. Multi-site deployment support
5. Satellite handoff optimization validation
