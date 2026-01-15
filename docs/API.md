# API Reference

## Table of Contents

- [Network Security](#network-security)
- [Encryption & Key Management](#encryption--key-management)
- [Security Logging & Alerting](#security-logging--alerting)
- [Vulnerability Scanning](#vulnerability-scanning)
- [Access Control & Authentication](#access-control--authentication)
- [Configuration Security](#configuration-security)

---

## Network Security

### NetworkMonitor

Monitor network connections and traffic for Starlink infrastructure.

#### Methods

##### `__init__(config: Optional[Dict[str, Any]] = None)`
Initialize the Network Monitor.

**Parameters:**
- `config`: Optional configuration dictionary for monitoring parameters

##### `start_monitoring() -> None`
Start network monitoring.

##### `stop_monitoring() -> None`
Stop network monitoring.

##### `check_connection_health(target: str = "8.8.8.8") -> Dict[str, Any]`
Check the health of network connection.

**Parameters:**
- `target`: Target IP or hostname to check connectivity

**Returns:**
Dictionary containing connection health metrics

##### `get_connection_stats() -> Dict[str, Any]`
Get aggregated connection statistics.

**Returns:**
Dictionary containing connection statistics

##### `get_logs(limit: Optional[int] = None) -> List[Dict[str, Any]]`
Get connection logs.

**Parameters:**
- `limit`: Maximum number of logs to return

**Returns:**
List of connection log entries

### ConnectionValidator

Validate and verify Starlink network connections.

#### Methods

##### `__init__(allowed_networks: Optional[List[str]] = None)`
Initialize the Connection Validator.

**Parameters:**
- `allowed_networks`: List of allowed network CIDR ranges

##### `validate_connection(source_ip: str, destination: str) -> Dict[str, bool]`
Validate a network connection.

**Parameters:**
- `source_ip`: Source IP address
- `destination`: Destination address

**Returns:**
Dictionary containing validation results

##### `add_allowed_network(network: str) -> None`
Add a network to the allowed list.

**Parameters:**
- `network`: Network CIDR range to allow

---

## Encryption & Key Management

### EncryptionManager

Manage encryption and decryption operations.

#### Methods

##### `__init__(key: Optional[bytes] = None)`
Initialize the Encryption Manager.

**Parameters:**
- `key`: Optional encryption key. If not provided, a new key is generated.

##### `encrypt(data: str) -> str`
Encrypt data.

**Parameters:**
- `data`: Plain text data to encrypt

**Returns:**
Base64-encoded encrypted data

##### `decrypt(encrypted_data: str) -> str`
Decrypt data.

**Parameters:**
- `encrypted_data`: Base64-encoded encrypted data

**Returns:**
Decrypted plain text data

##### `get_key() -> str`
Get the encryption key.

**Returns:**
Base64-encoded encryption key

##### `rotate_key(new_key: Optional[bytes] = None) -> str`
Rotate the encryption key.

**Parameters:**
- `new_key`: Optional new key. If not provided, a new key is generated.

**Returns:**
Base64-encoded new encryption key

### KeyManager

Manage cryptographic keys for the infrastructure.

#### Methods

##### `__init__(master_password: Optional[str] = None)`
Initialize the Key Manager.

**Parameters:**
- `master_password`: Optional master password for key derivation

##### `generate_key(key_id: str, key_type: str = "symmetric") -> Dict[str, Any]`
Generate a new cryptographic key.

**Parameters:**
- `key_id`: Unique identifier for the key
- `key_type`: Type of key to generate (symmetric, asymmetric)

**Returns:**
Dictionary containing key information

##### `get_key(key_id: str) -> Optional[Dict[str, Any]]`
Retrieve a key by ID.

**Parameters:**
- `key_id`: Key identifier

**Returns:**
Key information dictionary or None if not found

##### `rotate_key(key_id: str) -> Dict[str, Any]`
Rotate an existing key.

**Parameters:**
- `key_id`: Key identifier to rotate

**Returns:**
New key information dictionary

##### `revoke_key(key_id: str) -> bool`
Revoke a key.

**Parameters:**
- `key_id`: Key identifier to revoke

**Returns:**
True if key was revoked, False otherwise

---

## Security Logging & Alerting

### SecurityLogger

Comprehensive security event logger.

#### Methods

##### `__init__(log_file: Optional[str] = None)`
Initialize the Security Logger.

**Parameters:**
- `log_file`: Optional file path for persistent logging

##### `log(level: LogLevel, message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]`
Log a security event.

**Parameters:**
- `level`: Log severity level
- `message`: Log message
- `context`: Additional context data

**Returns:**
The created log entry

##### Convenience Methods
- `debug(message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]`
- `info(message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]`
- `warning(message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]`
- `error(message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]`
- `critical(message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]`

### AlertManager

Manage security alerts and notifications.

#### Methods

##### `__init__(alert_threshold: Optional[int] = None)`
Initialize the Alert Manager.

**Parameters:**
- `alert_threshold`: Minimum number of events to trigger an alert

##### `create_alert(severity: AlertSeverity, title: str, description: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]`
Create a new security alert.

**Parameters:**
- `severity`: Alert severity level
- `title`: Alert title
- `description`: Detailed description
- `context`: Additional context data

**Returns:**
The created alert

##### `acknowledge_alert(alert_id: str) -> bool`
Acknowledge an alert.

**Parameters:**
- `alert_id`: Alert identifier

**Returns:**
True if alert was acknowledged, False otherwise

##### `resolve_alert(alert_id: str, resolution: str = "") -> bool`
Resolve an alert.

**Parameters:**
- `alert_id`: Alert identifier
- `resolution`: Resolution notes

**Returns:**
True if alert was resolved, False otherwise

---

## Vulnerability Scanning

### VulnerabilityScanner

Scan for common security vulnerabilities.

#### Methods

##### `__init__()`
Initialize the Vulnerability Scanner.

##### `scan_configuration(config: Dict[str, Any]) -> Dict[str, Any]`
Scan a configuration for vulnerabilities.

**Parameters:**
- `config`: Configuration dictionary to scan

**Returns:**
Scan results with identified vulnerabilities

##### `get_vulnerability_summary() -> Dict[str, Any]`
Get summary of all vulnerabilities found.

**Returns:**
Summary statistics of vulnerabilities

### PortScanner

Scan network ports for security assessment.

#### Methods

##### `__init__()`
Initialize the Port Scanner.

##### `scan_port(host: str, port: int, timeout: float = 1.0) -> Dict[str, Any]`
Scan a single port.

**Parameters:**
- `host`: Target host
- `port`: Port number to scan
- `timeout`: Connection timeout in seconds

**Returns:**
Port scan result

##### `scan_ports(host: str, ports: Optional[List[int]] = None, timeout: float = 1.0) -> Dict[str, Any]`
Scan multiple ports on a host.

**Parameters:**
- `host`: Target host
- `ports`: List of ports to scan. If None, scans common ports.
- `timeout`: Connection timeout in seconds

**Returns:**
Comprehensive scan results

---

## Access Control & Authentication

### AccessController

Control access to infrastructure resources.

#### Methods

##### `__init__()`
Initialize the Access Controller.

##### `create_policy(policy_id: str, resource: str, allowed_actions: List[str], principals: List[str]) -> Dict[str, Any]`
Create an access control policy.

**Parameters:**
- `policy_id`: Unique policy identifier
- `resource`: Resource identifier
- `allowed_actions`: List of allowed actions
- `principals`: List of principal identifiers

**Returns:**
Created policy

##### `check_access(principal: str, resource: str, action: str) -> Dict[str, Any]`
Check if access is allowed.

**Parameters:**
- `principal`: Principal identifier
- `resource`: Resource identifier
- `action`: Requested action

**Returns:**
Access decision with details

### AuthenticationManager

Manage user authentication and sessions.

#### Methods

##### `__init__(session_timeout_minutes: int = 30)`
Initialize the Authentication Manager.

**Parameters:**
- `session_timeout_minutes`: Session timeout in minutes

##### `create_user(username: str, password: str, roles: Optional[List[str]] = None) -> Dict[str, Any]`
Create a new user.

**Parameters:**
- `username`: Username
- `password`: Plain text password (will be hashed)
- `roles`: Optional list of roles

**Returns:**
Created user information

##### `authenticate(username: str, password: str) -> Optional[str]`
Authenticate a user and create a session.

**Parameters:**
- `username`: Username
- `password`: Password

**Returns:**
Session token if authentication successful, None otherwise

##### `validate_session(session_token: str) -> Optional[str]`
Validate a session token.

**Parameters:**
- `session_token`: Session token to validate

**Returns:**
Username if session is valid, None otherwise

---

## Configuration Security

### ConfigScanner

Scan and validate security configurations.

#### Methods

##### `__init__()`
Initialize the Configuration Scanner.

##### `scan(config: Dict[str, Any]) -> Dict[str, Any]`
Scan a configuration for security issues.

**Parameters:**
- `config`: Configuration dictionary to scan

**Returns:**
Scan results with findings

##### `add_rule(rule_name: str, rule_func: Callable[[Any], Dict[str, Any]]) -> None`
Add a custom security scanning rule.

**Parameters:**
- `rule_name`: Name of the rule
- `rule_func`: Function that takes config and returns check result

### SecurityConfig

Manage security configuration settings.

#### Methods

##### `__init__(config: Optional[Dict[str, Any]] = None)`
Initialize Security Configuration.

**Parameters:**
- `config`: Optional initial configuration

##### `get(key: str, default: Any = None) -> Any`
Get a configuration value.

**Parameters:**
- `key`: Configuration key (supports dot notation)
- `default`: Default value if key not found

**Returns:**
Configuration value

##### `set(key: str, value: Any) -> None`
Set a configuration value.

**Parameters:**
- `key`: Configuration key (supports dot notation)
- `value`: Value to set

##### `validate() -> Dict[str, Any]`
Validate the current configuration.

**Returns:**
Validation results
