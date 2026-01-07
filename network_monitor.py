#!/usr/bin/env python3
"""
Network Monitoring System for Starlink Infrastructure
Tracks latency, jitter, packet loss, throughput, and device connections.
Detects unauthorized devices and open ports on critical systems.
"""

import yaml
import subprocess
import socket
import time
import statistics
import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
import ipaddress


class NetworkMonitor:
    """Main network monitoring class that handles all monitoring operations."""
    
    def __init__(self, config_file: str):
        """Initialize the network monitor with a YAML configuration file."""
        self.config = self._load_config(config_file)
        self.results = {}
        
    def _load_config(self, config_file: str) -> Dict[str, Any]:
        """Load and validate YAML configuration."""
        try:
            with open(config_file, 'r') as f:
                config = yaml.safe_load(f)
            self._validate_config(config)
            return config
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file not found: {config_file}")
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML configuration: {e}")
    
    def _validate_config(self, config: Dict[str, Any]) -> None:
        """Validate the configuration structure."""
        required_keys = ['monitoring']
        for key in required_keys:
            if key not in config:
                raise ValueError(f"Missing required configuration key: {key}")
        
        monitoring = config['monitoring']
        if 'targets' not in monitoring:
            raise ValueError("Missing 'targets' in monitoring configuration")
    
    def measure_latency(self, host: str, count: int = 4) -> Dict[str, Any]:
        """Measure network latency using ping."""
        latencies = []
        
        try:
            # Use ping command based on OS
            param = '-n' if os.name == 'nt' else '-c'
            cmd = ['ping', param, str(count), host]
            
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=30
            )
            
            # Parse ping output to extract latency values
            lines = result.stdout.split('\n')
            for line in lines:
                if 'time=' in line:
                    # Extract time value
                    time_part = line.split('time=')[1].split()[0]
                    # Remove 'ms' if present
                    time_value = float(time_part.replace('ms', ''))
                    latencies.append(time_value)
            
            if latencies:
                return {
                    'host': host,
                    'min': min(latencies),
                    'max': max(latencies),
                    'avg': statistics.mean(latencies),
                    'count': len(latencies),
                    'timestamp': datetime.now().isoformat()
                }
            else:
                return {
                    'host': host,
                    'error': 'No latency data collected',
                    'timestamp': datetime.now().isoformat()
                }
                
        except subprocess.TimeoutExpired:
            return {
                'host': host,
                'error': 'Ping timeout',
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'host': host,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def measure_jitter(self, host: str, count: int = 10) -> Dict[str, Any]:
        """Measure network jitter (variation in latency)."""
        latencies = []
        
        try:
            param = '-n' if os.name == 'nt' else '-c'
            cmd = ['ping', param, str(count), host]
            
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=30
            )
            
            lines = result.stdout.split('\n')
            for line in lines:
                if 'time=' in line:
                    time_part = line.split('time=')[1].split()[0]
                    time_value = float(time_part.replace('ms', ''))
                    latencies.append(time_value)
            
            if len(latencies) >= 2:
                # Calculate differences between consecutive latencies
                differences = [abs(latencies[i] - latencies[i-1]) 
                             for i in range(1, len(latencies))]
                
                return {
                    'host': host,
                    'jitter_avg': statistics.mean(differences),
                    'jitter_max': max(differences),
                    'jitter_min': min(differences),
                    'jitter_stdev': statistics.stdev(differences) if len(differences) > 1 else 0,
                    'timestamp': datetime.now().isoformat()
                }
            else:
                return {
                    'host': host,
                    'error': 'Insufficient data for jitter calculation',
                    'timestamp': datetime.now().isoformat()
                }
                
        except Exception as e:
            return {
                'host': host,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def measure_packet_loss(self, host: str, count: int = 20) -> Dict[str, Any]:
        """Measure packet loss percentage."""
        try:
            param = '-n' if os.name == 'nt' else '-c'
            cmd = ['ping', param, str(count), host]
            
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=60
            )
            
            output = result.stdout
            
            # Parse packet loss from output
            for line in output.split('\n'):
                if 'packet loss' in line.lower() or 'loss' in line.lower():
                    # Extract percentage
                    if '%' in line:
                        parts = line.split('%')
                        for part in parts[0].split():
                            try:
                                loss_pct = float(part)
                                return {
                                    'host': host,
                                    'packets_sent': count,
                                    'packet_loss_percent': loss_pct,
                                    'timestamp': datetime.now().isoformat()
                                }
                            except ValueError:
                                continue
            
            return {
                'host': host,
                'error': 'Could not parse packet loss',
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'host': host,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def measure_throughput(self, host: str, port: int = 80, 
                          duration: int = 5) -> Dict[str, Any]:
        """Measure network throughput by attempting a connection."""
        try:
            start_time = time.time()
            bytes_transferred = 0
            
            # Simple throughput test using socket connection
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            
            try:
                sock.connect((host, port))
                # Send a simple HTTP request
                request = f"HEAD / HTTP/1.1\r\nHost: {host}\r\n\r\n"
                sock.sendall(request.encode())
                bytes_transferred += len(request.encode())
                
                # Receive response
                response = sock.recv(4096)
                bytes_transferred += len(response)
                
                elapsed_time = time.time() - start_time
                throughput_mbps = (bytes_transferred * 8) / (elapsed_time * 1_000_000)
                
                return {
                    'host': host,
                    'port': port,
                    'bytes_transferred': bytes_transferred,
                    'duration_seconds': elapsed_time,
                    'throughput_mbps': throughput_mbps,
                    'timestamp': datetime.now().isoformat()
                }
            finally:
                sock.close()
                
        except socket.timeout:
            return {
                'host': host,
                'port': port,
                'error': 'Connection timeout',
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'host': host,
                'port': port,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def scan_open_ports(self, host: str, ports: List[int], 
                       timeout: int = 1) -> Dict[str, Any]:
        """Scan for open ports on a target system."""
        open_ports = []
        closed_ports = []
        
        for port in ports:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(timeout)
                result = sock.connect_ex((host, port))
                sock.close()
                
                if result == 0:
                    open_ports.append(port)
                else:
                    closed_ports.append(port)
            except Exception:
                closed_ports.append(port)
        
        return {
            'host': host,
            'open_ports': open_ports,
            'closed_ports': closed_ports,
            'total_scanned': len(ports),
            'timestamp': datetime.now().isoformat()
        }
    
    def detect_device_connections(self, network: str) -> Dict[str, Any]:
        """Detect active devices on the network (simplified approach)."""
        active_devices = []
        
        try:
            # Parse network CIDR
            network_obj = ipaddress.ip_network(network, strict=False)
            
            # For demonstration, we'll check a subset of IPs
            # In production, use proper network scanning tools
            hosts_to_check = list(network_obj.hosts())[:10]  # Limit for demo
            
            for host in hosts_to_check:
                try:
                    host_str = str(host)
                    # Quick check using ping
                    param = '-n' if os.name == 'nt' else '-c'
                    result = subprocess.run(
                        ['ping', param, '1', '-W', '1', host_str],
                        capture_output=True,
                        timeout=2
                    )
                    
                    if result.returncode == 0:
                        active_devices.append({
                            'ip': host_str,
                            'status': 'active'
                        })
                except Exception:
                    continue
            
            return {
                'network': network,
                'active_devices': active_devices,
                'device_count': len(active_devices),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'network': network,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def check_unauthorized_devices(self, network: str, 
                                   authorized_devices: List[str]) -> Dict[str, Any]:
        """Check for unauthorized devices on the network."""
        detection_result = self.detect_device_connections(network)
        
        if 'error' in detection_result:
            return detection_result
        
        active_ips = [device['ip'] for device in detection_result['active_devices']]
        unauthorized = [ip for ip in active_ips if ip not in authorized_devices]
        
        return {
            'network': network,
            'unauthorized_devices': unauthorized,
            'unauthorized_count': len(unauthorized),
            'total_active': len(active_ips),
            'timestamp': datetime.now().isoformat()
        }
    
    def run_monitoring(self) -> Dict[str, Any]:
        """Execute all monitoring tasks based on configuration."""
        results = {
            'monitoring_start': datetime.now().isoformat(),
            'latency': [],
            'jitter': [],
            'packet_loss': [],
            'throughput': [],
            'open_ports': [],
            'device_connections': [],
            'unauthorized_devices': []
        }
        
        monitoring = self.config['monitoring']
        
        # Monitor each target
        for target in monitoring.get('targets', []):
            host = target['host']
            
            # Latency monitoring
            if target.get('monitor_latency', True):
                results['latency'].append(
                    self.measure_latency(host, target.get('ping_count', 4))
                )
            
            # Jitter monitoring
            if target.get('monitor_jitter', True):
                results['jitter'].append(
                    self.measure_jitter(host, target.get('jitter_count', 10))
                )
            
            # Packet loss monitoring
            if target.get('monitor_packet_loss', True):
                results['packet_loss'].append(
                    self.measure_packet_loss(host, target.get('packet_loss_count', 20))
                )
            
            # Throughput monitoring
            if target.get('monitor_throughput', False):
                port = target.get('throughput_port', 80)
                results['throughput'].append(
                    self.measure_throughput(host, port)
                )
            
            # Open ports scanning
            if target.get('scan_ports', False) and 'ports_to_scan' in target:
                results['open_ports'].append(
                    self.scan_open_ports(host, target['ports_to_scan'])
                )
        
        # Network-wide checks
        if 'network' in monitoring:
            network = monitoring['network'].get('subnet')
            
            # Device connection detection
            if network and monitoring['network'].get('detect_devices', False):
                results['device_connections'].append(
                    self.detect_device_connections(network)
                )
            
            # Unauthorized device detection
            if network and monitoring['network'].get('check_unauthorized', False):
                authorized = monitoring['network'].get('authorized_devices', [])
                results['unauthorized_devices'].append(
                    self.check_unauthorized_devices(network, authorized)
                )
        
        results['monitoring_end'] = datetime.now().isoformat()
        
        return results
    
    def generate_report(self, results: Dict[str, Any], 
                       output_file: Optional[str] = None) -> str:
        """Generate a monitoring report."""
        report = []
        report.append("=" * 80)
        report.append("NETWORK MONITORING REPORT")
        report.append("=" * 80)
        report.append(f"Start Time: {results['monitoring_start']}")
        report.append(f"End Time: {results['monitoring_end']}")
        report.append("")
        
        # Latency section
        if results['latency']:
            report.append("-" * 80)
            report.append("LATENCY MONITORING")
            report.append("-" * 80)
            for item in results['latency']:
                if 'error' in item:
                    report.append(f"Host: {item['host']} - Error: {item['error']}")
                else:
                    report.append(f"Host: {item['host']}")
                    report.append(f"  Min: {item['min']:.2f} ms")
                    report.append(f"  Max: {item['max']:.2f} ms")
                    report.append(f"  Avg: {item['avg']:.2f} ms")
                report.append("")
        
        # Jitter section
        if results['jitter']:
            report.append("-" * 80)
            report.append("JITTER MONITORING")
            report.append("-" * 80)
            for item in results['jitter']:
                if 'error' in item:
                    report.append(f"Host: {item['host']} - Error: {item['error']}")
                else:
                    report.append(f"Host: {item['host']}")
                    report.append(f"  Avg Jitter: {item['jitter_avg']:.2f} ms")
                    report.append(f"  Max Jitter: {item['jitter_max']:.2f} ms")
                    report.append(f"  Std Dev: {item['jitter_stdev']:.2f} ms")
                report.append("")
        
        # Packet loss section
        if results['packet_loss']:
            report.append("-" * 80)
            report.append("PACKET LOSS MONITORING")
            report.append("-" * 80)
            for item in results['packet_loss']:
                if 'error' in item:
                    report.append(f"Host: {item['host']} - Error: {item['error']}")
                else:
                    report.append(f"Host: {item['host']}")
                    report.append(f"  Packets Sent: {item['packets_sent']}")
                    report.append(f"  Packet Loss: {item['packet_loss_percent']:.1f}%")
                report.append("")
        
        # Throughput section
        if results['throughput']:
            report.append("-" * 80)
            report.append("THROUGHPUT MONITORING")
            report.append("-" * 80)
            for item in results['throughput']:
                if 'error' in item:
                    report.append(f"Host: {item['host']}:{item['port']} - Error: {item['error']}")
                else:
                    report.append(f"Host: {item['host']}:{item['port']}")
                    report.append(f"  Throughput: {item['throughput_mbps']:.2f} Mbps")
                    report.append(f"  Bytes Transferred: {item['bytes_transferred']}")
                report.append("")
        
        # Open ports section
        if results['open_ports']:
            report.append("-" * 80)
            report.append("OPEN PORTS SCAN")
            report.append("-" * 80)
            for item in results['open_ports']:
                report.append(f"Host: {item['host']}")
                report.append(f"  Open Ports: {item['open_ports']}")
                report.append(f"  Total Scanned: {item['total_scanned']}")
                report.append("")
        
        # Unauthorized devices section
        if results['unauthorized_devices']:
            report.append("-" * 80)
            report.append("UNAUTHORIZED DEVICES DETECTION")
            report.append("-" * 80)
            for item in results['unauthorized_devices']:
                if 'error' in item:
                    report.append(f"Network: {item['network']} - Error: {item['error']}")
                else:
                    report.append(f"Network: {item['network']}")
                    if item['unauthorized_devices']:
                        report.append(f"  WARNING: {item['unauthorized_count']} unauthorized device(s) detected!")
                        for device in item['unauthorized_devices']:
                            report.append(f"    - {device}")
                    else:
                        report.append("  No unauthorized devices detected")
                report.append("")
        
        # Device connections section
        if results['device_connections']:
            report.append("-" * 80)
            report.append("DEVICE CONNECTIONS")
            report.append("-" * 80)
            for item in results['device_connections']:
                if 'error' in item:
                    report.append(f"Network: {item['network']} - Error: {item['error']}")
                else:
                    report.append(f"Network: {item['network']}")
                    report.append(f"  Active Devices: {item['device_count']}")
                    for device in item['active_devices']:
                        report.append(f"    - {device['ip']} ({device['status']})")
                report.append("")
        
        report.append("=" * 80)
        
        report_text = "\n".join(report)
        
        if output_file:
            with open(output_file, 'w') as f:
                f.write(report_text)
        
        return report_text


def main():
    """Main entry point for the network monitor."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Network Monitoring System for Starlink Infrastructure'
    )
    parser.add_argument(
        'config',
        help='Path to YAML configuration file'
    )
    parser.add_argument(
        '--output', '-o',
        help='Output file for the report (default: print to stdout)',
        default=None
    )
    parser.add_argument(
        '--json',
        help='Output results in JSON format',
        action='store_true'
    )
    
    args = parser.parse_args()
    
    try:
        monitor = NetworkMonitor(args.config)
        print("Starting network monitoring...")
        results = monitor.run_monitoring()
        
        if args.json:
            # Output as JSON
            json_output = json.dumps(results, indent=2)
            if args.output:
                with open(args.output, 'w') as f:
                    f.write(json_output)
                print(f"Results saved to {args.output}")
            else:
                print(json_output)
        else:
            # Output as formatted report
            report = monitor.generate_report(results, args.output)
            if not args.output:
                print(report)
            else:
                print(f"Report saved to {args.output}")
        
        print("Monitoring completed successfully.")
        
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())
