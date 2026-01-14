"""
Notification action implementation.

Handles notifications to security teams during incident response.
"""

from typing import Dict, Any, List
from datetime import datetime


class NotificationAction:
    """Implements notification actions for incident alerting."""
    
    @staticmethod
    def execute(target: str, config: Dict[str, Any], event_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute notification action.
        
        Args:
            target: Target audience (security_team, incident_response_team, etc.)
            config: Notification configuration
            event_data: Event context data
        
        Returns:
            Action execution result
        """
        channels = config.get('channels', ['email'])
        recipients = config.get('recipients', [])
        urgency = config.get('urgency', 'normal')
        
        notifications = []
        
        # Build notification content
        subject = f"[{urgency.upper()}] Security Incident Alert"
        
        message_parts = [
            f"Incident Type: {event_data.get('event_type', 'Unknown')}",
            f"Severity: {event_data.get('severity', 'Unknown')}",
            f"Timestamp: {event_data.get('timestamp', datetime.utcnow().isoformat())}",
        ]
        
        # Add incident-specific details
        if 'affected_host' in event_data:
            message_parts.append(f"Affected Host: {event_data['affected_host']}")
        if 'compromised_account' in event_data:
            message_parts.append(f"Compromised Account: {event_data['compromised_account']}")
        if 'source_ip' in event_data:
            message_parts.append(f"Source IP: {event_data['source_ip']}")
        if 'malware_type' in event_data:
            message_parts.append(f"Malware Type: {event_data['malware_type']}")
        
        # Include evidence if configured
        if config.get('include_evidence'):
            message_parts.append("\n--- Evidence ---")
            for key, value in event_data.items():
                if key not in ['event_type', 'severity', 'timestamp']:
                    message_parts.append(f"{key}: {value}")
        
        message = "\n".join(message_parts)
        
        # Send notifications via each channel
        for channel in channels:
            for recipient in recipients:
                notification = {
                    'channel': channel,
                    'recipient': recipient,
                    'urgency': urgency,
                    'subject': subject,
                    'message': message,
                    'status': 'sent',
                    'timestamp': datetime.utcnow().isoformat()
                }
                
                # Channel-specific handling
                if channel == 'email':
                    notification['delivery_method'] = 'SMTP'
                elif channel == 'sms':
                    notification['delivery_method'] = 'SMS Gateway'
                elif channel == 'slack':
                    notification['delivery_method'] = 'Slack Webhook'
                elif channel == 'pagerduty':
                    notification['delivery_method'] = 'PagerDuty API'
                    notification['incident_key'] = f"incident-{datetime.utcnow().timestamp()}"
                
                notifications.append(notification)
        
        # Handle escalation
        if config.get('escalation_required'):
            escalation_notification = {
                'channel': 'pagerduty',
                'recipient': 'on-call-engineer',
                'urgency': 'critical',
                'subject': f"ESCALATION: {subject}",
                'message': message,
                'status': 'escalated',
                'timestamp': datetime.utcnow().isoformat()
            }
            notifications.append(escalation_notification)
        
        return {
            'success': True,
            'action': 'notify',
            'target': target,
            'notifications_sent': notifications,
            'total_notifications': len(notifications),
            'channels_used': channels,
            'timestamp': datetime.utcnow().isoformat(),
            'message': f'Sent {len(notifications)} notifications via {len(channels)} channels to {target}'
        }
