"""
Brute-force Detection Module
Analyzes logs for brute-force attack patterns
"""

import re
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, List, Tuple


class BruteForceDetector:
    """Detects brute-force attacks in log files"""
    
    def __init__(self, config: dict):
        """
        Initialize brute-force detector with configuration
        
        Args:
            config: Dictionary containing brute-force detection settings
        """
        self.config = config
        self.patterns = config.get('patterns', [])
        self.attack_attempts = defaultdict(lambda: defaultdict(list))
        
        # Compile regex patterns
        self.compiled_patterns = []
        for pattern_config in self.patterns:
            self.compiled_patterns.append({
                'name': pattern_config['name'],
                'regex': re.compile(pattern_config['pattern']),
                'threshold': pattern_config['threshold'],
                'window_minutes': pattern_config['window_minutes'],
                'action': pattern_config['action']
            })
    
    def analyze_log_line(self, log_line: str) -> List[Dict]:
        """
        Analyze a single log line for brute-force patterns
        
        Args:
            log_line: Single line from a log file
            
        Returns:
            List of detected brute-force attempts
        """
        detections = []
        
        for pattern in self.compiled_patterns:
            match = pattern['regex'].search(log_line)
            if match:
                # Extract IP address if captured in regex
                ip_address = match.group(1) if match.groups() else "unknown"
                
                now = datetime.now()
                cutoff_time = now - timedelta(minutes=pattern['window_minutes'])
                
                # Add current attempt
                pattern_name = pattern['name']
                self.attack_attempts[pattern_name][ip_address].append(now)
                
                # Remove old attempts
                self.attack_attempts[pattern_name][ip_address] = [
                    t for t in self.attack_attempts[pattern_name][ip_address] 
                    if t > cutoff_time
                ]
                
                count = len(self.attack_attempts[pattern_name][ip_address])
                
                if count >= pattern['threshold']:
                    detections.append({
                        'type': 'brute_force_attack',
                        'pattern_name': pattern_name,
                        'ip_address': ip_address,
                        'attempt_count': count,
                        'window_minutes': pattern['window_minutes'],
                        'action': pattern['action'],
                        'log_line': log_line.strip(),
                        'timestamp': now.isoformat()
                    })
        
        return detections
    
    def analyze_log_file(self, log_file_path: str) -> List[Dict]:
        """
        Analyze entire log file for brute-force patterns
        
        Args:
            log_file_path: Path to log file
            
        Returns:
            List of detected brute-force attempts
        """
        all_detections = []
        
        try:
            with open(log_file_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    detections = self.analyze_log_line(line)
                    all_detections.extend(detections)
        except FileNotFoundError:
            # Log file doesn't exist yet - this is not necessarily an error
            # in continuous monitoring scenarios
            pass
        except Exception as e:
            print(f"Error analyzing log file {log_file_path}: {e}")
        
        return all_detections
    
    def get_blocked_ips(self) -> List[str]:
        """
        Get list of IPs that should be blocked based on brute-force detection
        
        Returns:
            List of IP addresses to block
        """
        blocked_ips = set()
        
        for pattern in self.compiled_patterns:
            if pattern['action'] == 'block':
                pattern_name = pattern['name']
                cutoff_time = datetime.now() - timedelta(minutes=pattern['window_minutes'])
                
                for ip_address, attempts in self.attack_attempts[pattern_name].items():
                    # Filter recent attempts
                    recent_attempts = [t for t in attempts if t > cutoff_time]
                    
                    if len(recent_attempts) >= pattern['threshold']:
                        blocked_ips.add(ip_address)
        
        return list(blocked_ips)
    
    def clear_old_data(self, hours: int = 24):
        """
        Clear attack attempt data older than specified hours
        
        Args:
            hours: Number of hours of data to keep
        """
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        for pattern_name in self.attack_attempts:
            for ip_address in list(self.attack_attempts[pattern_name].keys()):
                self.attack_attempts[pattern_name][ip_address] = [
                    t for t in self.attack_attempts[pattern_name][ip_address]
                    if t > cutoff_time
                ]
                
                # Remove IP if no recent attempts
                if not self.attack_attempts[pattern_name][ip_address]:
                    del self.attack_attempts[pattern_name][ip_address]
