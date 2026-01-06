"""
Incident Responder Module
Provides automated response to security incidents.
"""

import logging
from typing import Dict, List, Optional, Callable
from datetime import datetime
from enum import Enum


class IncidentSeverity(Enum):
    """Incident severity classifications."""
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class IncidentStatus(Enum):
    """Incident status states."""
    DETECTED = "detected"
    INVESTIGATING = "investigating"
    RESPONDING = "responding"
    CONTAINED = "contained"
    RESOLVED = "resolved"
    CLOSED = "closed"


class IncidentResponder:
    """
    Incident response service for Starlink infrastructure.
    
    Features:
    - Automated incident detection and response
    - Playbook-based response actions
    - Incident tracking and reporting
    """
    
    def __init__(self):
        """Initialize the Incident Responder."""
        self.incidents = []
        self.response_playbooks = {}
        self.automated_responses = []
        self.logger = logging.getLogger(__name__)
        self.logger.info("Incident Responder initialized")
        self._load_default_playbooks()
    
    def _load_default_playbooks(self) -> None:
        """Load default incident response playbooks."""
        # Malware detection playbook
        self.response_playbooks["malware"] = {
            "name": "Malware Response",
            "steps": [
                "isolate_affected_system",
                "capture_forensics",
                "terminate_malicious_process",
                "scan_network_for_spread",
                "remove_malware",
                "restore_from_backup"
            ]
        }
        
        # Intrusion detection playbook
        self.response_playbooks["intrusion"] = {
            "name": "Intrusion Response",
            "steps": [
                "block_source_ip",
                "terminate_suspicious_connections",
                "analyze_access_logs",
                "check_data_exfiltration",
                "reset_compromised_credentials",
                "patch_vulnerability"
            ]
        }
        
        # DDoS attack playbook
        self.response_playbooks["ddos"] = {
            "name": "DDoS Response",
            "steps": [
                "enable_rate_limiting",
                "activate_ddos_mitigation",
                "redirect_to_scrubbing_center",
                "block_attack_sources",
                "scale_infrastructure"
            ]
        }
        
        self.logger.info(f"Loaded {len(self.response_playbooks)} default playbooks")
    
    def create_incident(self, incident_type: str, severity: IncidentSeverity, 
                       description: str, affected_systems: Optional[List[str]] = None) -> str:
        """
        Create a new security incident.
        
        Args:
            incident_type: Type of incident
            severity: Severity level
            description: Incident description
            affected_systems: List of affected systems
        
        Returns:
            Unique incident ID
        """
        incident_id = f"INC-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        incident = {
            "id": incident_id,
            "type": incident_type,
            "severity": severity.value,
            "status": IncidentStatus.DETECTED.value,
            "description": description,
            "affected_systems": affected_systems or [],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "response_actions": []
        }
        
        self.incidents.append(incident)
        self.logger.warning(f"Incident created: {incident_id} - {incident_type} ({severity.value})")
        
        # Auto-respond if severity is high or critical
        if severity in [IncidentSeverity.HIGH, IncidentSeverity.CRITICAL]:
            self.auto_respond(incident_id)
        
        return incident_id
    
    def auto_respond(self, incident_id: str) -> bool:
        """
        Automatically respond to an incident using appropriate playbook.
        
        Args:
            incident_id: ID of the incident to respond to
        
        Returns:
            True if auto-response was initiated
        """
        incident = self._get_incident(incident_id)
        if not incident:
            self.logger.error(f"Incident not found: {incident_id}")
            return False
        
        incident_type = incident["type"]
        playbook = self.response_playbooks.get(incident_type)
        
        if not playbook:
            self.logger.warning(f"No playbook found for incident type: {incident_type}")
            return False
        
        self.logger.info(f"Initiating auto-response for {incident_id} using {playbook['name']}")
        
        # Update incident status
        self._update_incident_status(incident_id, IncidentStatus.RESPONDING)
        
        # Execute playbook steps
        for step in playbook["steps"]:
            self._execute_response_action(incident_id, step)
        
        # Mark as contained
        self._update_incident_status(incident_id, IncidentStatus.CONTAINED)
        
        return True
    
    def _execute_response_action(self, incident_id: str, action: str) -> bool:
        """
        Execute a specific response action.
        
        Args:
            incident_id: ID of the incident
            action: Action to execute
        
        Returns:
            True if action was executed successfully
        """
        self.logger.info(f"Executing response action for {incident_id}: {action}")
        
        action_record = {
            "action": action,
            "executed_at": datetime.now().isoformat(),
            "status": "completed"
        }
        
        # In a real implementation, this would:
        # - Execute actual response actions
        # - Interface with other security modules
        # - Update firewall rules
        # - Isolate systems
        # - Block IPs
        # - etc.
        
        incident = self._get_incident(incident_id)
        if incident:
            incident["response_actions"].append(action_record)
            incident["updated_at"] = datetime.now().isoformat()
        
        return True
    
    def _get_incident(self, incident_id: str) -> Optional[Dict]:
        """
        Get incident by ID.
        
        Args:
            incident_id: ID of the incident
        
        Returns:
            Incident dictionary or None if not found
        """
        for incident in self.incidents:
            if incident["id"] == incident_id:
                return incident
        return None
    
    def _update_incident_status(self, incident_id: str, status: IncidentStatus) -> bool:
        """
        Update incident status.
        
        Args:
            incident_id: ID of the incident
            status: New status
        
        Returns:
            True if status was updated
        """
        incident = self._get_incident(incident_id)
        if incident:
            incident["status"] = status.value
            incident["updated_at"] = datetime.now().isoformat()
            self.logger.info(f"Incident {incident_id} status updated to {status.value}")
            return True
        return False
    
    def add_playbook(self, playbook_name: str, steps: List[str]) -> bool:
        """
        Add a custom response playbook.
        
        Args:
            playbook_name: Name of the playbook
            steps: List of response steps
        
        Returns:
            True if playbook was added successfully
        """
        self.response_playbooks[playbook_name] = {
            "name": playbook_name,
            "steps": steps
        }
        
        self.logger.info(f"Custom playbook added: {playbook_name}")
        return True
    
    def resolve_incident(self, incident_id: str, resolution_notes: str) -> bool:
        """
        Resolve and close an incident.
        
        Args:
            incident_id: ID of the incident
            resolution_notes: Notes about the resolution
        
        Returns:
            True if incident was resolved
        """
        incident = self._get_incident(incident_id)
        if not incident:
            return False
        
        incident["status"] = IncidentStatus.RESOLVED.value
        incident["resolution_notes"] = resolution_notes
        incident["resolved_at"] = datetime.now().isoformat()
        incident["updated_at"] = datetime.now().isoformat()
        
        self.logger.info(f"Incident resolved: {incident_id}")
        return True
    
    def get_incident_summary(self) -> Dict:
        """
        Get summary of all incidents.
        
        Returns:
            Dictionary containing incident statistics
        """
        status_counts = {status.value: 0 for status in IncidentStatus}
        severity_counts = {severity.value: 0 for severity in IncidentSeverity}
        
        for incident in self.incidents:
            status_counts[incident["status"]] += 1
            severity_counts[incident["severity"]] += 1
        
        return {
            "total_incidents": len(self.incidents),
            "by_status": status_counts,
            "by_severity": severity_counts,
            "playbooks_available": len(self.response_playbooks),
            "timestamp": datetime.now().isoformat()
        }
