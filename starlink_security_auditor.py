#!/usr/bin/env python3
"""
Starlink Security Auditor
A comprehensive security auditing tool for Starlink-based enterprise infrastructures.

This tool performs security audits across multiple domains:
- Network security
- Service vulnerabilities
- Encryption status
- VPN configuration
"""

import json
import logging
import subprocess
import socket
import os
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class AuditResult:
    """Represents the result of a security audit check."""
    check_name: str
    status: str  # PASS, FAIL, WARN, INFO
    message: str
    details: Optional[Dict[str, Any]] = None
    recommendation: Optional[str] = None


@dataclass
class AuditReport:
    """Comprehensive audit report."""
    timestamp: str
    hostname: str
    audit_results: List[AuditResult]
    summary: Dict[str, int]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert report to dictionary."""
        return {
            'timestamp': self.timestamp,
            'hostname': self.hostname,
            'audit_results': [asdict(r) for r in self.audit_results],
            'summary': self.summary
        }


class SecurityAuditor:
    """Main security auditor class with modular design."""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize the security auditor with optional configuration."""
        self.config = self._load_config(config_path)
        self.results: List[AuditResult] = []
        self._setup_logging()
        
    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load configuration from JSON file or use defaults."""
        default_config = {
            'audit_scope': {
                'network_security': True,
                'service_vulnerabilities': True,
                'encryption_validation': True,
                'vpn_validation': True,
                'network_segmentation': True,
                'privilege_checks': True
            },
            'starlink_settings': {
                'remote_environment': True,
                'connectivity_resilient': True,
                'require_vpn': True
            },
            'logging': {
                'level': 'INFO',
                'file': 'security_audit.log',
                'console': True
            },
            'reporting': {
                'format': 'json',
                'output_file': 'security_audit_report.json'
            }
        }
        
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    user_config = json.load(f)
                    # Merge user config with defaults
                    default_config.update(user_config)
                    logging.info(f"Loaded configuration from {config_path}")
            except Exception as e:
                logging.warning(f"Failed to load config from {config_path}: {e}")
                
        return default_config
    
    def _setup_logging(self) -> None:
        """Configure logging based on configuration."""
        log_config = self.config.get('logging', {})
        level = getattr(logging, log_config.get('level', 'INFO'))
        
        # Configure root logger
        logging.basicConfig(
            level=level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_config.get('file', 'security_audit.log')),
                logging.StreamHandler() if log_config.get('console', True) else logging.NullHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def _add_result(self, check_name: str, status: str, message: str, 
                   details: Optional[Dict[str, Any]] = None,
                   recommendation: Optional[str] = None) -> None:
        """Add an audit result."""
        result = AuditResult(
            check_name=check_name,
            status=status,
            message=message,
            details=details or {},
            recommendation=recommendation
        )
        self.results.append(result)
        self.logger.info(f"{check_name}: {status} - {message}")
        
    def _run_command(self, command: List[str]) -> tuple[int, str, str]:
        """Safely run a system command and return output."""
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=30
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            self.logger.error(f"Command timed out: {' '.join(command)}")
            return -1, "", "Command timed out"
        except Exception as e:
            self.logger.error(f"Command failed: {e}")
            return -1, "", str(e)
    
    def check_network_security(self) -> None:
        """Comprehensive network security checks."""
        self.logger.info("Running network security checks...")
        
        # Check firewall status
        returncode, stdout, stderr = self._run_command(['sudo', 'ufw', 'status'])
        if returncode == 0:
            if 'Status: active' in stdout:
                self._add_result(
                    'Firewall Status',
                    'PASS',
                    'UFW firewall is active',
                    {'details': stdout.strip()},
                    None
                )
            else:
                self._add_result(
                    'Firewall Status',
                    'FAIL',
                    'UFW firewall is not active',
                    {'details': stdout.strip()},
                    'Enable UFW firewall: sudo ufw enable'
                )
        else:
            # Try iptables as fallback
            returncode, stdout, stderr = self._run_command(['sudo', 'iptables', '-L', '-n'])
            if returncode == 0 and stdout:
                self._add_result(
                    'Firewall Status',
                    'INFO',
                    'iptables firewall detected',
                    {'details': 'iptables rules are configured'},
                    'Review iptables rules for security compliance'
                )
            else:
                self._add_result(
                    'Firewall Status',
                    'WARN',
                    'No firewall detected',
                    None,
                    'Install and configure a firewall (UFW or iptables)'
                )
        
        # Check open ports
        try:
            import socket
            common_ports = [21, 22, 23, 25, 80, 443, 3306, 5432, 8080]
            open_ports = []
            
            for port in common_ports:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex(('127.0.0.1', port))
                if result == 0:
                    open_ports.append(port)
                sock.close()
            
            if open_ports:
                self._add_result(
                    'Open Ports',
                    'INFO',
                    f'Found {len(open_ports)} open ports',
                    {'open_ports': open_ports},
                    'Review open ports and ensure only necessary services are exposed'
                )
            else:
                self._add_result(
                    'Open Ports',
                    'PASS',
                    'No common vulnerable ports open on localhost',
                    None,
                    None
                )
        except Exception as e:
            self._add_result(
                'Open Ports',
                'WARN',
                f'Could not scan ports: {e}',
                None,
                'Manually verify open ports with netstat or ss'
            )
    
    def check_service_vulnerabilities(self) -> None:
        """Check for service vulnerabilities and misconfigurations."""
        self.logger.info("Running service vulnerability checks...")
        
        # Check SSH configuration
        ssh_config = '/etc/ssh/sshd_config'
        if os.path.exists(ssh_config):
            try:
                with open(ssh_config, 'r') as f:
                    config_content = f.read()
                
                issues = []
                recommendations = []
                
                if 'PermitRootLogin yes' in config_content:
                    issues.append('Root login is permitted')
                    recommendations.append('Disable root login: PermitRootLogin no')
                
                if 'PasswordAuthentication yes' in config_content:
                    issues.append('Password authentication is enabled')
                    recommendations.append('Use key-based authentication only')
                
                if 'PermitEmptyPasswords yes' in config_content:
                    issues.append('Empty passwords are permitted')
                    recommendations.append('Disable empty passwords')
                
                if issues:
                    self._add_result(
                        'SSH Configuration',
                        'FAIL',
                        f'SSH has {len(issues)} security issues',
                        {'issues': issues},
                        '; '.join(recommendations)
                    )
                else:
                    self._add_result(
                        'SSH Configuration',
                        'PASS',
                        'SSH configuration follows security best practices',
                        None,
                        None
                    )
            except Exception as e:
                self._add_result(
                    'SSH Configuration',
                    'WARN',
                    f'Could not read SSH config: {e}',
                    None,
                    'Verify SSH configuration manually'
                )
        else:
            self._add_result(
                'SSH Configuration',
                'INFO',
                'SSH not installed or config not found',
                None,
                None
            )
        
        # Check for running services
        returncode, stdout, stderr = self._run_command(['systemctl', 'list-units', '--type=service', '--state=running'])
        if returncode == 0:
            service_count = len([line for line in stdout.split('\n') if '.service' in line])
            self._add_result(
                'Running Services',
                'INFO',
                f'{service_count} services are running',
                {'details': 'Review service list for unnecessary services'},
                'Disable unnecessary services to reduce attack surface'
            )
    
    def check_encryption_status(self) -> None:
        """Verify encryption status across the system."""
        self.logger.info("Running encryption status checks...")
        
        # Check disk encryption
        returncode, stdout, stderr = self._run_command(['lsblk', '-f'])
        if returncode == 0:
            if 'crypto_LUKS' in stdout:
                self._add_result(
                    'Disk Encryption',
                    'PASS',
                    'LUKS disk encryption detected',
                    {'details': 'Full disk encryption is active'},
                    None
                )
            else:
                self._add_result(
                    'Disk Encryption',
                    'WARN',
                    'No LUKS encryption detected',
                    None,
                    'Consider enabling full disk encryption for sensitive data'
                )
        
        # Check SSL/TLS certificates
        cert_dirs = ['/etc/ssl/certs', '/etc/pki/tls/certs']
        cert_found = False
        
        for cert_dir in cert_dirs:
            if os.path.exists(cert_dir):
                cert_files = list(Path(cert_dir).glob('*.pem')) + list(Path(cert_dir).glob('*.crt'))
                if cert_files:
                    cert_found = True
                    self._add_result(
                        'SSL/TLS Certificates',
                        'INFO',
                        f'Found {len(cert_files)} certificates in {cert_dir}',
                        {'cert_directory': cert_dir},
                        'Verify certificates are valid and not expired'
                    )
                    break
        
        if not cert_found:
            self._add_result(
                'SSL/TLS Certificates',
                'WARN',
                'No SSL/TLS certificates found in standard locations',
                None,
                'Ensure SSL/TLS certificates are properly configured for secure communications'
            )
    
    def check_vpn_configuration(self) -> None:
        """Validate VPN configuration for secure remote access."""
        self.logger.info("Running VPN configuration checks...")
        
        # Check for OpenVPN
        returncode, stdout, stderr = self._run_command(['which', 'openvpn'])
        openvpn_installed = returncode == 0
        
        # Check for WireGuard
        returncode, stdout, stderr = self._run_command(['which', 'wg'])
        wireguard_installed = returncode == 0
        
        if openvpn_installed or wireguard_installed:
            vpn_type = []
            if openvpn_installed:
                vpn_type.append('OpenVPN')
            if wireguard_installed:
                vpn_type.append('WireGuard')
            
            self._add_result(
                'VPN Software',
                'PASS',
                f'VPN software installed: {", ".join(vpn_type)}',
                {'vpn_types': vpn_type},
                'Verify VPN is properly configured and active'
            )
            
            # Check if VPN service is running
            if openvpn_installed:
                returncode, stdout, stderr = self._run_command(['systemctl', 'is-active', 'openvpn'])
                if returncode == 0 and 'active' in stdout:
                    self._add_result(
                        'VPN Service Status',
                        'PASS',
                        'OpenVPN service is active',
                        None,
                        None
                    )
                else:
                    self._add_result(
                        'VPN Service Status',
                        'WARN',
                        'OpenVPN service is not active',
                        None,
                        'Start VPN service for secure remote access'
                    )
        else:
            self._add_result(
                'VPN Software',
                'FAIL',
                'No VPN software detected',
                None,
                'Install VPN software (OpenVPN or WireGuard) for secure remote access in Starlink environments'
            )
    
    def check_network_segmentation(self) -> None:
        """Validate network segmentation."""
        self.logger.info("Running network segmentation checks...")
        
        # Check network interfaces
        returncode, stdout, stderr = self._run_command(['ip', 'addr', 'show'])
        if returncode == 0:
            interfaces = [line.split(':')[1].strip() for line in stdout.split('\n') if ': <' in line]
            
            self._add_result(
                'Network Interfaces',
                'INFO',
                f'Found {len(interfaces)} network interfaces',
                {'interfaces': interfaces},
                'Review network segmentation and ensure proper VLAN configuration'
            )
        
        # Check routing table
        returncode, stdout, stderr = self._run_command(['ip', 'route', 'show'])
        if returncode == 0:
            routes = [line for line in stdout.split('\n') if line.strip()]
            self._add_result(
                'Routing Configuration',
                'INFO',
                f'Found {len(routes)} routing entries',
                {'route_count': len(routes)},
                'Verify routing table follows network segmentation policy'
            )
    
    def check_privilege_settings(self) -> None:
        """Check principle of least privilege implementation."""
        self.logger.info("Running privilege checks...")
        
        # Check sudo configuration
        if os.path.exists('/etc/sudoers'):
            self._add_result(
                'Sudo Configuration',
                'INFO',
                'Sudoers file exists',
                None,
                'Review sudoers configuration to ensure least privilege principle'
            )
        
        # Check file permissions on sensitive files
        sensitive_files = [
            '/etc/shadow',
            '/etc/gshadow',
            '/etc/ssh/sshd_config'
        ]
        
        permission_issues = []
        for file_path in sensitive_files:
            if os.path.exists(file_path):
                stat_info = os.stat(file_path)
                mode = oct(stat_info.st_mode)[-3:]
                
                # Shadow files should be 000 or 400
                if 'shadow' in file_path and mode not in ['000', '400']:
                    permission_issues.append(f'{file_path}: {mode} (should be 400 or 000)')
                # SSH config should be 600 or 644
                elif 'ssh' in file_path and mode not in ['600', '644']:
                    permission_issues.append(f'{file_path}: {mode} (should be 600 or 644)')
        
        if permission_issues:
            self._add_result(
                'File Permissions',
                'WARN',
                f'Found {len(permission_issues)} file permission issues',
                {'issues': permission_issues},
                'Correct file permissions on sensitive files'
            )
        else:
            self._add_result(
                'File Permissions',
                'PASS',
                'Sensitive files have appropriate permissions',
                None,
                None
            )
    
    def run_audit(self) -> AuditReport:
        """Run all enabled security audits."""
        self.logger.info("Starting comprehensive security audit...")
        self.results = []
        
        scope = self.config.get('audit_scope', {})
        
        if scope.get('network_security', True):
            self.check_network_security()
        
        if scope.get('service_vulnerabilities', True):
            self.check_service_vulnerabilities()
        
        if scope.get('encryption_validation', True):
            self.check_encryption_status()
        
        if scope.get('vpn_validation', True):
            self.check_vpn_configuration()
        
        if scope.get('network_segmentation', True):
            self.check_network_segmentation()
        
        if scope.get('privilege_checks', True):
            self.check_privilege_settings()
        
        # Generate summary
        summary = {
            'PASS': sum(1 for r in self.results if r.status == 'PASS'),
            'FAIL': sum(1 for r in self.results if r.status == 'FAIL'),
            'WARN': sum(1 for r in self.results if r.status == 'WARN'),
            'INFO': sum(1 for r in self.results if r.status == 'INFO'),
            'total': len(self.results)
        }
        
        report = AuditReport(
            timestamp=datetime.now().isoformat(),
            hostname=socket.gethostname(),
            audit_results=self.results,
            summary=summary
        )
        
        self.logger.info(f"Audit complete. Results: {summary}")
        return report
    
    def save_report(self, report: AuditReport) -> None:
        """Save audit report to file."""
        output_file = self.config.get('reporting', {}).get('output_file', 'security_audit_report.json')
        
        try:
            with open(output_file, 'w') as f:
                json.dump(report.to_dict(), f, indent=2)
            self.logger.info(f"Report saved to {output_file}")
        except Exception as e:
            self.logger.error(f"Failed to save report: {e}")
    
    def print_report(self, report: AuditReport) -> None:
        """Print a human-readable report to console."""
        print("\n" + "="*80)
        print("STARLINK SECURITY AUDIT REPORT")
        print("="*80)
        print(f"Timestamp: {report.timestamp}")
        print(f"Hostname: {report.hostname}")
        print(f"\nSummary:")
        print(f"  Total Checks: {report.summary['total']}")
        print(f"  Passed: {report.summary['PASS']}")
        print(f"  Failed: {report.summary['FAIL']}")
        print(f"  Warnings: {report.summary['WARN']}")
        print(f"  Info: {report.summary['INFO']}")
        print("\n" + "-"*80)
        print("Detailed Results:")
        print("-"*80)
        
        for result in report.audit_results:
            status_symbol = {
                'PASS': '✓',
                'FAIL': '✗',
                'WARN': '⚠',
                'INFO': 'ℹ'
            }.get(result.status, '?')
            
            print(f"\n[{status_symbol}] {result.check_name} - {result.status}")
            print(f"    {result.message}")
            if result.recommendation:
                print(f"    Recommendation: {result.recommendation}")
        
        print("\n" + "="*80)


def main():
    """Main entry point for the security auditor."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Starlink Security Auditor - Comprehensive security auditing for enterprise Starlink infrastructures'
    )
    parser.add_argument(
        '--config',
        '-c',
        help='Path to JSON configuration file',
        default=None
    )
    parser.add_argument(
        '--output',
        '-o',
        help='Output file for audit report (overrides config)',
        default=None
    )
    parser.add_argument(
        '--quiet',
        '-q',
        action='store_true',
        help='Suppress console output (only log to file)'
    )
    
    args = parser.parse_args()
    
    # Initialize auditor
    auditor = SecurityAuditor(config_path=args.config)
    
    # Override output file if specified
    if args.output:
        auditor.config['reporting']['output_file'] = args.output
    
    # Run audit
    report = auditor.run_audit()
    
    # Save report
    auditor.save_report(report)
    
    # Print report unless quiet mode
    if not args.quiet:
        auditor.print_report(report)
    
    # Exit with appropriate code
    if report.summary['FAIL'] > 0:
        sys.exit(1)
    elif report.summary['WARN'] > 0:
        sys.exit(2)
    else:
        sys.exit(0)


if __name__ == '__main__':
    main()
