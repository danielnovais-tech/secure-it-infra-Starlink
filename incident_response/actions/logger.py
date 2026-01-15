"""
Logging action implementation.

Handles logging and SIEM integration during incident response.
"""

from typing import Dict, Any, List
from datetime import datetime
import json

# Compliance retention period (7 years in days)
COMPLIANCE_RETENTION_DAYS = 365 * 7  # 2555 days


class LoggingAction:
    """Implements logging actions for incident tracking and compliance."""
    
    @staticmethod
    def execute(target: str, config: Dict[str, Any], event_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute logging action.
        
        Args:
            target: Target logging system (siem, file, database)
            config: Logging configuration
            event_data: Event context data
        
        Returns:
            Action execution result
        """
        log_level = config.get('log_level', 'info')
        
        # Generate incident ID
        incident_id = config.get('incident_id')
        if incident_id == 'auto_generate':
            incident_id = f"INC-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        
        # Build log entry
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'incident_id': incident_id,
            'log_level': log_level,
            'target_system': target,
            'event_type': event_data.get('event_type'),
            'severity': event_data.get('severity')
        }
        
        # Include metadata
        if config.get('include_metadata'):
            log_entry['metadata'] = event_data
        
        # Timeline preservation
        if config.get('preserve_timeline'):
            log_entry['timeline'] = {
                'event_detected': event_data.get('timestamp'),
                'response_initiated': datetime.utcnow().isoformat()
            }
        
        # Chain of custody
        if config.get('chain_of_custody'):
            log_entry['chain_of_custody'] = {
                'handler': 'incident_response_system',
                'action': 'automated_response',
                'evidence_preserved': True,
                'custody_timestamp': datetime.utcnow().isoformat()
            }
        
        # Compliance reporting
        if config.get('compliance_reporting'):
            log_entry['compliance'] = {
                'reporting_required': True,
                'frameworks': ['SOC2', 'ISO27001', 'GDPR'],
                'retention_period_days': COMPLIANCE_RETENTION_DAYS
            }
        
        # SIEM-specific fields
        if target == 'siem':
            log_entry['siem_fields'] = {
                'source': 'incident_response_handler',
                'category': 'security_incident',
                'action_taken': 'automated_response',
                'priority': _map_severity_to_priority(event_data.get('severity', 'medium'))
            }
        
        # Structured logging output
        log_output = json.dumps(log_entry, indent=2)
        
        return {
            'success': True,
            'action': 'log',
            'target': target,
            'incident_id': incident_id,
            'log_entry': log_entry,
            'log_output': log_output,
            'timestamp': datetime.utcnow().isoformat(),
            'message': f'Incident logged to {target} with ID {incident_id}'
        }


def _map_severity_to_priority(severity: str) -> int:
    """Map severity level to numeric priority."""
    severity_map = {
        'critical': 1,
        'high': 2,
        'medium': 3,
        'low': 4,
        'info': 5
    }
    return severity_map.get(severity.lower(), 3)
