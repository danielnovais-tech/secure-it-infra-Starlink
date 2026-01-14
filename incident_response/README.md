# Incident Response System

A YAML-based incident response handler for high-severity security events such as malware detection and security breaches.

## Overview

This system provides automated incident response capabilities for enterprise infrastructures supporting Starlink. It handles high-severity events like malware detection and security breaches with configurable actions including isolation, scanning, and notifications.

## Features

- **YAML-Based Configuration**: Define incidents and response actions using simple YAML files
- **High-Severity Event Handling**: Automated response to malware, breaches, and other critical events
- **Multiple Action Types**:
  - **Isolation**: Network isolation, credential disabling, system quarantine
  - **Scanning**: Full system scans, forensic analysis, memory dumps
  - **Notifications**: Multi-channel alerts (email, SMS, Slack, PagerDuty)
  - **Logging**: SIEM integration, compliance reporting, chain of custody
- **Priority-Based Execution**: Actions execute in configured priority order
- **Condition Matching**: Flexible event condition evaluation
- **Extensible Architecture**: Easy to add new incident types and actions

## Installation

### Requirements

- Python 3.7+
- PyYAML

Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

```python
from incident_response import IncidentResponseHandler

# Initialize the handler
handler = IncidentResponseHandler()

# Define an event
malware_event = {
    'event_type': 'malware_detected',
    'severity': 'high',
    'confirmed': True,
    'affected_host': 'server-web-01',
    'malware_type': 'ransomware'
}

# Handle the incident
result = handler.handle_incident('malware', malware_event)

# Check results
print(f"Status: {result['status']}")
print(f"Actions executed: {len(result['actions_executed'])}")
```

### Running the Example

```bash
cd incident_response
python handler.py
```

This will demonstrate handling both malware and breach incidents with sample events.

## Configuration

### YAML Structure

Incident configurations are stored in `incident_response/config/` as YAML files.

#### Example: Malware Incident Configuration

```yaml
incident:
  name: "Malware Detection"
  type: "malware"
  severity: "high"
  description: "Handles detection and response to malware incidents"
  
  triggers:
    - event_type: "malware_detected"
      conditions:
        - field: "severity"
          operator: "gte"
          value: "high"
        - field: "confirmed"
          operator: "eq"
          value: true
  
  actions:
    - action: "isolate"
      target: "affected_host"
      priority: 1
      config:
        network_isolation: true
        disable_user_access: true
```

### Supported Action Types

#### Isolation
Isolates compromised systems or accounts:
- Network isolation
- User access control
- Credential disabling
- IP blocking

#### Scanning
Performs security scans:
- Full system scan
- Forensic analysis
- Memory dumps
- Network traffic analysis

#### Notifications
Alerts security teams:
- Multi-channel delivery (email, SMS, Slack, PagerDuty)
- Urgency levels
- Escalation support

#### Logging
Records incidents:
- SIEM integration
- Compliance reporting
- Chain of custody
- Timeline preservation

### Condition Operators

- `eq`: Equals
- `gte`: Greater than or equal
- `gt`: Greater than
- `in`: Value in list

## Project Structure

```
incident_response/
├── __init__.py              # Package initialization
├── handler.py               # Main incident response handler
├── actions/                 # Action implementations
│   ├── __init__.py
│   ├── isolation.py         # Isolation actions
│   ├── scanner.py           # Scanning actions
│   ├── notifier.py          # Notification actions
│   └── logger.py            # Logging actions
├── config/                  # YAML incident configurations
│   ├── malware_incident.yaml
│   └── breach_incident.yaml
└── tests/                   # Unit tests
    └── test_handler.py
```

## Pre-Configured Incidents

### Malware Detection
- **Type**: `malware`
- **Triggers**: High-severity confirmed malware
- **Actions**: Isolation → Scan → Notify → Log

### Security Breach
- **Type**: `breach`
- **Triggers**: Unauthorized access, data exfiltration
- **Actions**: Multi-layer isolation → Forensic scan → Critical notifications → SIEM logging

## Testing

Run the test suite:

```bash
cd incident_response/tests
python test_handler.py
```

Or use unittest discovery:

```bash
python -m unittest discover -s incident_response/tests
```

## Example Event Data

### Malware Event
```python
{
    'event_type': 'malware_detected',
    'severity': 'high',
    'confirmed': True,
    'affected_host': 'server-web-01',
    'malware_type': 'ransomware',
    'timestamp': '2024-01-06T12:00:00'
}
```

### Breach Event
```python
{
    'event_type': 'unauthorized_access',
    'severity': 'high',
    'access_level': 'admin',
    'compromised_account': 'admin@example.com',
    'source_ip': '192.168.1.100',
    'timestamp': '2024-01-06T12:00:00'
}
```

## Adding New Incidents

1. Create a new YAML file in `config/`:
```yaml
incident:
  name: "Your Incident"
  type: "your_type"
  severity: "high"
  triggers:
    - event_type: "your_event"
      conditions: [...]
  actions: [...]
```

2. The handler automatically loads all YAML files in the config directory.

3. Trigger the incident:
```python
result = handler.handle_incident('your_type', event_data)
```

## Security Considerations

- Always validate event data before processing
- Ensure proper authentication/authorization for notifications
- Implement rate limiting for automated responses
- Maintain audit logs for all actions
- Follow principle of least privilege for isolation actions
- Encrypt sensitive data in transit and at rest

## License

This project is part of the secure-it-infra-Starlink repository and follows the repository's license.

## Contributing

Contributions are welcome! Please ensure:
- New incidents include comprehensive YAML configurations
- All code includes appropriate unit tests
- Documentation is updated for new features
- Security best practices are followed
