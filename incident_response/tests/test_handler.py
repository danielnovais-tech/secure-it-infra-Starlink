"""
Unit tests for the incident response handler.
"""

import unittest
import os
import yaml
from datetime import datetime
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from handler import IncidentResponseHandler


class TestIncidentResponseHandler(unittest.TestCase):
    """Test cases for IncidentResponseHandler."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.handler = IncidentResponseHandler()
    
    def test_load_configurations(self):
        """Test that YAML configurations are loaded correctly."""
        self.assertGreater(len(self.handler.incidents), 0, "No incidents loaded")
        self.assertIn('malware', self.handler.incidents, "Malware incident not loaded")
        self.assertIn('breach', self.handler.incidents, "Breach incident not loaded")
    
    def test_get_incident_config(self):
        """Test retrieval of incident configuration."""
        malware_config = self.handler.get_incident_config('malware')
        self.assertIsNotNone(malware_config, "Malware config not found")
        self.assertEqual(malware_config['type'], 'malware')
        self.assertEqual(malware_config['severity'], 'high')
        
        breach_config = self.handler.get_incident_config('breach')
        self.assertIsNotNone(breach_config, "Breach config not found")
        self.assertEqual(breach_config['type'], 'breach')
    
    def test_evaluate_conditions_eq(self):
        """Test condition evaluation with equality operator."""
        conditions = [
            {'field': 'severity', 'operator': 'eq', 'value': 'high'},
            {'field': 'confirmed', 'operator': 'eq', 'value': True}
        ]
        event_data = {'severity': 'high', 'confirmed': True}
        
        result = self.handler.evaluate_conditions(conditions, event_data)
        self.assertTrue(result, "Conditions should match")
        
        event_data_no_match = {'severity': 'low', 'confirmed': True}
        result = self.handler.evaluate_conditions(conditions, event_data_no_match)
        self.assertFalse(result, "Conditions should not match")
    
    def test_evaluate_conditions_in(self):
        """Test condition evaluation with 'in' operator."""
        conditions = [
            {'field': 'access_level', 'operator': 'in', 'value': ['admin', 'root']}
        ]
        event_data = {'access_level': 'admin'}
        
        result = self.handler.evaluate_conditions(conditions, event_data)
        self.assertTrue(result, "Condition should match")
        
        event_data_no_match = {'access_level': 'user'}
        result = self.handler.evaluate_conditions(conditions, event_data_no_match)
        self.assertFalse(result, "Condition should not match")
    
    def test_should_trigger_malware(self):
        """Test incident triggering for malware events."""
        malware_config = self.handler.get_incident_config('malware')
        
        event_data = {
            'event_type': 'malware_detected',
            'severity': 'high',
            'confirmed': True
        }
        
        result = self.handler.should_trigger(malware_config, event_data)
        self.assertTrue(result, "Malware incident should trigger")
        
        event_data_no_trigger = {
            'event_type': 'malware_detected',
            'severity': 'low',
            'confirmed': True
        }
        
        result = self.handler.should_trigger(malware_config, event_data_no_trigger)
        self.assertFalse(result, "Malware incident should not trigger for low severity")
    
    def test_should_trigger_breach(self):
        """Test incident triggering for breach events."""
        breach_config = self.handler.get_incident_config('breach')
        
        event_data = {
            'event_type': 'unauthorized_access',
            'severity': 'high',
            'access_level': 'admin'
        }
        
        result = self.handler.should_trigger(breach_config, event_data)
        self.assertTrue(result, "Breach incident should trigger")
    
    def test_handle_malware_incident(self):
        """Test handling a malware incident."""
        event_data = {
            'event_type': 'malware_detected',
            'severity': 'high',
            'confirmed': True,
            'affected_host': 'server-web-01',
            'malware_type': 'ransomware'
        }
        
        result = self.handler.handle_incident('malware', event_data)
        
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['incident_type'], 'malware')
        self.assertIn('actions_executed', result)
        self.assertGreater(len(result['actions_executed']), 0, "No actions executed")
        
        # Check that actions are executed in priority order
        priorities = [action['priority'] for action in result['actions_executed']]
        self.assertEqual(priorities, sorted(priorities), "Actions not in priority order")
    
    def test_handle_breach_incident(self):
        """Test handling a security breach incident."""
        event_data = {
            'event_type': 'unauthorized_access',
            'severity': 'high',
            'access_level': 'admin',
            'compromised_account': 'admin@example.com',
            'source_ip': '192.168.1.100'
        }
        
        result = self.handler.handle_incident('breach', event_data)
        
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['incident_type'], 'breach')
        self.assertIn('actions_executed', result)
        self.assertGreater(len(result['actions_executed']), 0, "No actions executed")
    
    def test_handle_unknown_incident(self):
        """Test handling an unknown incident type."""
        event_data = {'event_type': 'unknown_event'}
        
        result = self.handler.handle_incident('unknown_type', event_data)
        
        self.assertEqual(result['status'], 'error')
        self.assertIn('No configuration found', result['message'])
    
    def test_handle_non_matching_event(self):
        """Test handling an event that doesn't match triggers."""
        event_data = {
            'event_type': 'malware_detected',
            'severity': 'low',  # Below threshold
            'confirmed': True
        }
        
        result = self.handler.handle_incident('malware', event_data)
        
        self.assertEqual(result['status'], 'skipped')
        self.assertIn('do not match', result['message'])
    
    def test_execute_isolation_action(self):
        """Test isolation action execution."""
        action = {
            'action': 'isolate',
            'target': 'test-host',
            'priority': 1,
            'config': {
                'network_isolation': True,
                'disable_user_access': True
            }
        }
        event_data = {'affected_host': 'test-host'}
        
        result = self.handler.execute_action(action, event_data)
        
        self.assertEqual(result['action'], 'isolate')
        self.assertEqual(result['target'], 'test-host')
        self.assertTrue(result['result']['success'])
        self.assertIn('steps_executed', result['result'])
    
    def test_execute_scan_action(self):
        """Test scan action execution."""
        action = {
            'action': 'scan',
            'target': 'test-host',
            'priority': 2,
            'config': {
                'scan_type': 'full_system',
                'update_definitions': True
            }
        }
        event_data = {'affected_host': 'test-host'}
        
        result = self.handler.execute_action(action, event_data)
        
        self.assertEqual(result['action'], 'scan')
        self.assertTrue(result['result']['success'])
        self.assertEqual(result['result']['scan_type'], 'full_system')
    
    def test_execute_notification_action(self):
        """Test notification action execution."""
        action = {
            'action': 'notify',
            'target': 'security_team',
            'priority': 3,
            'config': {
                'channels': ['email', 'sms'],
                'recipients': ['security@example.com'],
                'urgency': 'critical'
            }
        }
        event_data = {'event_type': 'test_event'}
        
        result = self.handler.execute_action(action, event_data)
        
        self.assertEqual(result['action'], 'notify')
        self.assertTrue(result['result']['success'])
        self.assertGreater(len(result['result']['notifications_sent']), 0)
    
    def test_execute_logging_action(self):
        """Test logging action execution."""
        action = {
            'action': 'log',
            'target': 'siem',
            'priority': 4,
            'config': {
                'log_level': 'critical',
                'incident_id': 'auto_generate'
            }
        }
        event_data = {'event_type': 'test_event'}
        
        result = self.handler.execute_action(action, event_data)
        
        self.assertEqual(result['action'], 'log')
        self.assertTrue(result['result']['success'])
        self.assertIn('log_entry', result['result'])
    
    def test_list_incidents(self):
        """Test listing all loaded incidents."""
        incidents = self.handler.list_incidents()
        
        self.assertGreater(len(incidents), 0, "No incidents in list")
        
        for incident in incidents:
            self.assertIn('type', incident)
            self.assertIn('name', incident)
            self.assertIn('severity', incident)
            self.assertIn('description', incident)


class TestYAMLConfigurations(unittest.TestCase):
    """Test cases for YAML configuration files."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config_dir = Path(__file__).parent.parent / "config"
    
    def test_malware_config_exists(self):
        """Test that malware configuration file exists and is valid."""
        config_file = self.config_dir / "malware_incident.yaml"
        self.assertTrue(config_file.exists(), "Malware config file not found")
        
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
        
        self.assertIn('incident', config)
        self.assertEqual(config['incident']['type'], 'malware')
        self.assertEqual(config['incident']['severity'], 'high')
        self.assertIn('triggers', config['incident'])
        self.assertIn('actions', config['incident'])
    
    def test_breach_config_exists(self):
        """Test that breach configuration file exists and is valid."""
        config_file = self.config_dir / "breach_incident.yaml"
        self.assertTrue(config_file.exists(), "Breach config file not found")
        
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
        
        self.assertIn('incident', config)
        self.assertEqual(config['incident']['type'], 'breach')
        self.assertEqual(config['incident']['severity'], 'high')
        self.assertIn('triggers', config['incident'])
        self.assertIn('actions', config['incident'])
    
    def test_config_actions_have_priorities(self):
        """Test that all actions have priority values."""
        for config_file in self.config_dir.glob("*.yaml"):
            with open(config_file, 'r') as f:
                config = yaml.safe_load(f)
            
            if config and 'incident' in config:
                actions = config['incident'].get('actions', [])
                for action in actions:
                    self.assertIn('priority', action, 
                                  f"Action in {config_file.name} missing priority")


if __name__ == '__main__':
    unittest.main()
