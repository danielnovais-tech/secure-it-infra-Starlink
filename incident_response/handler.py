"""
Incident Response Handler

This module provides YAML-based incident response handling for high-severity 
security events such as malware detection and security breaches.
"""

import yaml
import logging
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class IncidentResponseHandler:
    """Handles incident response based on YAML configurations."""
    
    def __init__(self, config_dir: Optional[Union[str, Path]] = None):
        """
        Initialize the incident response handler.
        
        Args:
            config_dir: Directory containing YAML incident configurations.
                       Defaults to './config' relative to this file.
        """
        if config_dir is None:
            config_dir = Path(__file__).parent / "config"
        self.config_dir = Path(config_dir)
        self.incidents: Dict[str, Dict[str, Any]] = {}
        self.load_configurations()
    
    def load_configurations(self) -> None:
        """Load all YAML incident configurations from the config directory."""
        if not self.config_dir.exists():
            raise FileNotFoundError(f"Configuration directory not found: {self.config_dir}")
        
        yaml_files = list(self.config_dir.glob("*.yaml")) + list(self.config_dir.glob("*.yml"))
        
        for yaml_file in yaml_files:
            try:
                with open(yaml_file, 'r') as f:
                    config = yaml.safe_load(f)
                    if config and 'incident' in config:
                        incident = config['incident']
                        incident_type = incident.get('type')
                        if incident_type:
                            self.incidents[incident_type] = incident
                            logger.info(f"Loaded incident configuration: {incident.get('name')} ({incident_type})")
            except Exception as e:
                logger.error(f"Error loading {yaml_file}: {e}")
    
    def get_incident_config(self, incident_type: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve incident configuration by type.
        
        Args:
            incident_type: Type of incident (e.g., 'malware', 'breach')
        
        Returns:
            Incident configuration dictionary or None if not found
        """
        return self.incidents.get(incident_type)
    
    def evaluate_conditions(self, conditions: List[Dict[str, Any]], event_data: Dict[str, Any]) -> bool:
        """
        Evaluate if event data matches trigger conditions.
        
        Args:
            conditions: List of condition dictionaries
            event_data: Event data to evaluate
        
        Returns:
            True if all conditions match, False otherwise
        """
        # Severity level mapping for comparisons
        severity_levels = {
            'low': 1,
            'medium': 2,
            'high': 3,
            'critical': 4
        }
        
        for condition in conditions:
            field = condition.get('field')
            operator = condition.get('operator')
            expected_value = condition.get('value')

            if not isinstance(field, str) or not field:
                return False
            if not isinstance(operator, str) or not operator:
                return False

            actual_value = event_data.get(field)
            
            if operator == 'eq' and actual_value != expected_value:
                return False
            elif operator == 'gte':
                # Special handling for severity levels
                if field == 'severity' and isinstance(actual_value, str) and isinstance(expected_value, str):
                    actual_level = severity_levels.get(actual_value.lower(), 0)
                    expected_level = severity_levels.get(expected_value.lower(), 0)
                    if actual_level < expected_level:
                        return False
                elif isinstance(actual_value, (int, float)) and isinstance(expected_value, (int, float)):
                    if actual_value < expected_value:
                        return False
                elif isinstance(actual_value, str) and isinstance(expected_value, str):
                    if actual_value < expected_value:
                        return False
                else:
                    return False
            elif operator == 'gt':
                if not (
                    isinstance(actual_value, (int, float))
                    and isinstance(expected_value, (int, float))
                    and actual_value > expected_value
                ):
                    return False
            elif operator == 'in':
                if not isinstance(expected_value, (list, tuple, set)):
                    return False
                if actual_value not in expected_value:
                    return False
        
        return True
    
    def should_trigger(self, incident_config: Dict[str, Any], event_data: Dict[str, Any]) -> bool:
        """
        Determine if an incident should be triggered based on event data.
        
        Args:
            incident_config: Incident configuration
            event_data: Event data including type and fields
        
        Returns:
            True if incident should be triggered, False otherwise
        """
        event_type = event_data.get('event_type')
        triggers = incident_config.get('triggers', [])
        
        for trigger in triggers:
            if trigger.get('event_type') == event_type:
                conditions = trigger.get('conditions', [])
                if self.evaluate_conditions(conditions, event_data):
                    return True
        
        return False
    
    def handle_incident(self, incident_type: str, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle an incident by executing configured actions.
        
        Args:
            incident_type: Type of incident to handle
            event_data: Event data that triggered the incident
        
        Returns:
            Dictionary containing incident response details
        """
        incident_config = self.get_incident_config(incident_type)
        
        if not incident_config:
            return {
                'status': 'error',
                'message': f'No configuration found for incident type: {incident_type}'
            }
        
        # Check if the event should trigger this incident
        if not self.should_trigger(incident_config, event_data):
            return {
                'status': 'skipped',
                'message': 'Event conditions do not match incident triggers',
                'incident': incident_config.get('name')
            }
        
        # Execute actions in priority order
        actions = sorted(
            incident_config.get('actions', []),
            key=lambda x: x.get('priority', 999)
        )
        
        executed_actions = []
        timestamp = datetime.utcnow().isoformat()
        
        for action in actions:
            action_result = self.execute_action(action, event_data)
            executed_actions.append(action_result)
        
        return {
            'status': 'success',
            'incident_type': incident_type,
            'incident_name': incident_config.get('name'),
            'severity': incident_config.get('severity'),
            'timestamp': timestamp,
            'actions_executed': executed_actions,
            'event_data': event_data
        }
    
    def execute_action(self, action: Dict[str, Any], event_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a specific incident response action.
        
        Args:
            action: Action configuration
            event_data: Event data for context
        
        Returns:
            Dictionary containing action execution results
        """
        action_type = action.get('action')
        target_raw = action.get('target')
        config_raw = action.get('config', {})
        priority = action.get('priority')

        if not isinstance(action_type, str) or not action_type:
            return {
                'action': action_type,
                'target': target_raw,
                'priority': priority,
                'result': {'success': False, 'message': 'Missing or invalid action type'},
                'timestamp': datetime.utcnow().isoformat()
            }

        target = target_raw if isinstance(target_raw, str) else (str(target_raw) if target_raw is not None else "unknown")
        config: Dict[str, Any] = config_raw if isinstance(config_raw, dict) else {}
        
        # Simulate action execution based on type
        if action_type == 'isolate':
            result = self._execute_isolation(target, config, event_data)
        elif action_type == 'scan':
            result = self._execute_scan(target, config, event_data)
        elif action_type == 'notify':
            result = self._execute_notification(target, config, event_data)
        elif action_type == 'log':
            result = self._execute_logging(target, config, event_data)
        else:
            result = {'success': False, 'message': f'Unknown action type: {action_type}'}
        
        return {
            'action': action_type,
            'target': target,
            'priority': priority,
            'result': result,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def _execute_isolation(self, target: str, config: Dict[str, Any], event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute isolation action."""
        steps = []
        
        if config.get('network_isolation'):
            steps.append(f"Isolated {target} from network")
        if config.get('disable_user_access'):
            steps.append(f"Disabled user access to {target}")
        if config.get('disable_credentials'):
            steps.append(f"Disabled credentials for {target}")
        if config.get('revoke_tokens'):
            steps.append(f"Revoked authentication tokens for {target}")
        if config.get('block_ip'):
            ip = event_data.get('source_ip', 'unknown')
            steps.append(f"Blocked IP address: {ip}")
        if config.get('segment_isolation'):
            steps.append(f"Isolated network segment: {target}")
        if config.get('firewall_lockdown'):
            steps.append(f"Activated firewall lockdown for {target}")
        
        return {
            'success': True,
            'target': target,
            'steps_executed': steps,
            'message': f'Successfully isolated {target}'
        }
    
    def _execute_scan(self, target: str, config: Dict[str, Any], event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute scan action."""
        scan_type_value = config.get('scan_type', 'standard')
        scan_type = scan_type_value if isinstance(scan_type_value, str) else str(scan_type_value)
        steps = [f"Initiated {scan_type} scan on {target}"]
        
        if config.get('update_definitions'):
            steps.append("Updated threat definitions")
        if config.get('quarantine_threats'):
            steps.append("Configured automatic threat quarantine")
        if config.get('memory_dump'):
            steps.append("Captured memory dump for forensics")
        if config.get('network_traffic_analysis'):
            steps.append("Started network traffic analysis")
        if config.get('artifact_collection'):
            steps.append("Collecting forensic artifacts")
        
        return {
            'success': True,
            'target': target,
            'scan_type': scan_type,
            'steps_executed': steps,
            'message': f'Scan initiated on {target}'
        }
    
    def _execute_notification(self, target: str, config: Dict[str, Any], event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute notification action."""
        channels = config.get('channels', [])
        recipients = config.get('recipients', [])
        urgency = config.get('urgency', 'normal')
        
        notifications_sent = []
        for channel in channels:
            for recipient in recipients:
                notifications_sent.append({
                    'channel': channel,
                    'recipient': recipient,
                    'urgency': urgency,
                    'status': 'sent'
                })
        
        return {
            'success': True,
            'target': target,
            'notifications_sent': notifications_sent,
            'message': f'Sent {len(notifications_sent)} notifications via {len(channels)} channels'
        }
    
    def _execute_logging(self, target: str, config: Dict[str, Any], event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute logging action."""
        log_level = config.get('log_level', 'info')
        
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': log_level,
            'target': target,
            'event_data': event_data
        }
        
        if config.get('incident_id') == 'auto_generate':
            log_entry['incident_id'] = f"INC-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        
        if config.get('include_metadata'):
            log_entry['metadata'] = event_data
        
        return {
            'success': True,
            'target': target,
            'log_entry': log_entry,
            'message': f'Logged incident to {target}'
        }
    
    def list_incidents(self) -> List[Dict[str, Any]]:
        """
        List all loaded incident configurations.
        
        Returns:
            List of incident summary dictionaries
        """
        return [
            {
                'type': incident_type,
                'name': config.get('name'),
                'severity': config.get('severity'),
                'description': config.get('description')
            }
            for incident_type, config in self.incidents.items()
        ]


def main():
    """Example usage of the incident response handler."""
    handler = IncidentResponseHandler()
    
    print("\n=== Loaded Incident Configurations ===")
    for incident in handler.list_incidents():
        print(f"- {incident['name']} ({incident['type']}): {incident['severity']} severity")
    
    print("\n=== Example 1: Malware Detection ===")
    malware_event = {
        'event_type': 'malware_detected',
        'severity': 'high',
        'confirmed': True,
        'affected_host': 'server-web-01',
        'malware_type': 'ransomware',
        'timestamp': datetime.utcnow().isoformat()
    }
    
    result = handler.handle_incident('malware', malware_event)
    print(f"Status: {result['status']}")
    print(f"Incident: {result.get('incident_name')}")
    print(f"Actions executed: {len(result.get('actions_executed', []))}")
    for action in result.get('actions_executed', []):
        print(f"  - {action['action']} on {action['target']}: {action['result']['message']}")
    
    print("\n=== Example 2: Security Breach ===")
    breach_event = {
        'event_type': 'unauthorized_access',
        'severity': 'high',
        'access_level': 'admin',
        'compromised_account': 'admin@example.com',
        'source_ip': '192.168.1.100',
        'timestamp': datetime.utcnow().isoformat()
    }
    
    result = handler.handle_incident('breach', breach_event)
    print(f"Status: {result['status']}")
    print(f"Incident: {result.get('incident_name')}")
    print(f"Actions executed: {len(result.get('actions_executed', []))}")
    for action in result.get('actions_executed', []):
        print(f"  - {action['action']} on {action['target']}: {action['result']['message']}")


if __name__ == '__main__':
    main()
