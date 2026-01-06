# Incident Response System - Usage Examples

This document provides practical examples of how to use the incident response system.

## Example 1: Handling a Malware Detection Event

```python
from incident_response import IncidentResponseHandler

# Initialize the handler
handler = IncidentResponseHandler()

# Simulate a malware detection event
malware_event = {
    'event_type': 'malware_detected',
    'severity': 'high',
    'confirmed': True,
    'affected_host': 'server-web-01',
    'malware_type': 'ransomware',
    'detected_by': 'antivirus',
    'timestamp': '2026-01-06T12:00:00Z'
}

# Handle the incident
result = handler.handle_incident('malware', malware_event)

# Process the results
if result['status'] == 'success':
    print(f"Incident: {result['incident_name']}")
    print(f"Severity: {result['severity']}")
    print(f"Actions executed: {len(result['actions_executed'])}")
    
    for action in result['actions_executed']:
        print(f"\n{action['action'].upper()} ({action['target']}):")
        print(f"  Priority: {action['priority']}")
        print(f"  Result: {action['result']['message']}")
        
        # Display detailed steps for isolation actions
        if 'steps_executed' in action['result']:
            print(f"  Steps executed:")
            for step in action['result']['steps_executed']:
                print(f"    - {step}")
```

**Expected Output:**
```
Incident: Malware Detection
Severity: high
Actions executed: 4

ISOLATE (affected_host):
  Priority: 1
  Result: Successfully isolated affected_host
  Steps executed:
    - Isolated server-web-01 from network
    - All inbound/outbound traffic blocked for server-web-01
    - User access disabled for server-web-01
    - Active sessions terminated on server-web-01
    - Evidence preservation mode enabled for server-web-01
    - System state snapshot created for server-web-01

SCAN (affected_host):
  Priority: 2
  Result: Scan initiated on affected_host
  Steps executed:
    - Initiated full_system scan on server-web-01
    - Full system scan started on server-web-01
    - Scanning all files and processes on server-web-01
    - Updated malware definitions
    - Configured automatic threat quarantine

NOTIFY (security_team):
  Priority: 3
  Result: Sent 6 notifications via 3 channels
  
LOG (siem):
  Priority: 4
  Result: Logged incident to siem
```

## Example 2: Handling a Security Breach

```python
from incident_response import IncidentResponseHandler

handler = IncidentResponseHandler()

# Simulate an unauthorized access event
breach_event = {
    'event_type': 'unauthorized_access',
    'severity': 'high',
    'access_level': 'admin',
    'compromised_account': 'admin@example.com',
    'source_ip': '192.168.1.100',
    'attempted_resources': ['/etc/passwd', '/var/log/auth.log'],
    'timestamp': '2026-01-06T14:30:00Z'
}

result = handler.handle_incident('breach', breach_event)

if result['status'] == 'success':
    # Extract notification details
    for action in result['actions_executed']:
        if action['action'] == 'notify':
            notifications = action['result']['notifications_sent']
            print(f"Sent {len(notifications)} notifications:")
            for notif in notifications:
                print(f"  - {notif['channel']}: {notif['recipient']} (urgency: {notif['urgency']})")
```

## Example 3: Custom Event Processing

```python
# Check if an event would trigger an incident without executing it
def would_trigger_incident(handler, incident_type, event_data):
    config = handler.get_incident_config(incident_type)
    if config:
        return handler.should_trigger(config, event_data)
    return False

# Test various scenarios
events = [
    {
        'event_type': 'malware_detected',
        'severity': 'low',  # Below threshold
        'confirmed': True
    },
    {
        'event_type': 'malware_detected',
        'severity': 'high',  # Above threshold
        'confirmed': True
    }
]

for event in events:
    if would_trigger_incident(handler, 'malware', event):
        print(f"Event with severity {event['severity']} would trigger malware incident")
    else:
        print(f"Event with severity {event['severity']} would NOT trigger malware incident")
```

**Expected Output:**
```
Event with severity low would NOT trigger malware incident
Event with severity high would trigger malware incident
```

## Example 4: Listing Available Incidents

```python
# List all configured incidents
incidents = handler.list_incidents()

print("Available incident response configurations:")
for incident in incidents:
    print(f"\nType: {incident['type']}")
    print(f"Name: {incident['name']}")
    print(f"Severity: {incident['severity']}")
    print(f"Description: {incident['description']}")
```

## Example 5: Data Exfiltration Detection

```python
# Simulate a data exfiltration event
exfiltration_event = {
    'event_type': 'data_exfiltration',
    'severity': 'high',
    'data_volume': 500,  # MB
    'destination_ip': '10.0.0.100',
    'compromised_account': 'user@example.com',
    'timestamp': '2026-01-06T16:00:00Z'
}

result = handler.handle_incident('breach', exfiltration_event)

# Check if isolation was successful
for action in result['actions_executed']:
    if action['action'] == 'isolate':
        if action['result']['success']:
            print(f"Successfully isolated {action['target']}")
            print("Steps taken:")
            for step in action['result']['steps_executed']:
                print(f"  - {step}")
```

## Integration Examples

### Integration with SIEM

```python
import json

# After handling an incident, format for SIEM
result = handler.handle_incident('malware', malware_event)

# Extract log entry for SIEM
for action in result['actions_executed']:
    if action['action'] == 'log' and action['target'] == 'siem':
        siem_entry = action['result']['log_entry']
        
        # Send to SIEM (example)
        print("SIEM Entry:")
        print(json.dumps(siem_entry, indent=2))
```

### Integration with Monitoring System

```python
import requests

def send_to_monitoring(incident_result):
    """Send incident results to monitoring system."""
    if incident_result['status'] == 'success':
        # Extract key metrics
        metrics = {
            'incident_type': incident_result['incident_type'],
            'severity': incident_result['severity'],
            'actions_count': len(incident_result['actions_executed']),
            'timestamp': incident_result['timestamp']
        }
        
        # Send to monitoring API (example)
        # requests.post('https://monitoring.example.com/api/incidents', json=metrics)
        print(f"Would send to monitoring: {metrics}")

result = handler.handle_incident('malware', malware_event)
send_to_monitoring(result)
```

## Testing Event Conditions

```python
# Test different severity levels
severity_tests = ['low', 'medium', 'high', 'critical']

for severity in severity_tests:
    test_event = {
        'event_type': 'malware_detected',
        'severity': severity,
        'confirmed': True,
        'affected_host': 'test-server'
    }
    
    result = handler.handle_incident('malware', test_event)
    print(f"Severity: {severity:8s} -> Status: {result['status']}")
```

**Expected Output:**
```
Severity: low      -> Status: skipped
Severity: medium   -> Status: skipped
Severity: high     -> Status: success
Severity: critical -> Status: success
```

## Advanced Usage: Custom Notification Handling

```python
# Process notifications for different channels
result = handler.handle_incident('breach', breach_event)

for action in result['actions_executed']:
    if action['action'] == 'notify':
        for notification in action['result']['notifications_sent']:
            channel = notification['channel']
            
            if channel == 'email':
                # Send email (example)
                print(f"Sending email to {notification['recipient']}")
                print(f"Subject: {notification['subject']}")
                print(f"Urgency: {notification['urgency']}")
                
            elif channel == 'slack':
                # Send Slack message (example)
                print(f"Posting to Slack: {notification['recipient']}")
                
            elif channel == 'pagerduty':
                # Create PagerDuty incident (example)
                print(f"Creating PagerDuty incident: {notification.get('incident_key')}")
```

## Error Handling

```python
# Handle unknown incident types
try:
    result = handler.handle_incident('unknown_type', {})
    if result['status'] == 'error':
        print(f"Error: {result['message']}")
except Exception as e:
    print(f"Exception occurred: {e}")

# Handle events that don't match triggers
low_severity_event = {
    'event_type': 'malware_detected',
    'severity': 'low',
    'confirmed': False
}

result = handler.handle_incident('malware', low_severity_event)
if result['status'] == 'skipped':
    print(f"Event skipped: {result['message']}")
```

## Performance Monitoring

```python
import time

# Measure incident handling time
start_time = time.time()
result = handler.handle_incident('malware', malware_event)
end_time = time.time()

if result['status'] == 'success':
    print(f"Incident handled in {end_time - start_time:.4f} seconds")
    print(f"Actions executed: {len(result['actions_executed'])}")
    
    # Calculate average time per action
    avg_time = (end_time - start_time) / len(result['actions_executed'])
    print(f"Average time per action: {avg_time:.4f} seconds")
```

---

For more information, see the [main README](README.md).
