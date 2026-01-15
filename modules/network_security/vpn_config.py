"""
Network Security Module - VPN Configuration
Secure VPN setup for Starlink-enabled remote infrastructure
"""

class VPNManager:
    """Manages VPN configurations for secure remote access over Starlink"""
    
    def __init__(self):
        self.vpn_config = {
            'protocol': 'wireguard',  # Modern, efficient protocol for satellite links
            'encryption': 'AES-256-GCM',
            'authentication': 'certificate-based',
            'compression': True,  # Important for satellite bandwidth optimization
        }
        self.active_tunnels = []
        
    def create_tunnel(self, endpoint, subnet, bandwidth_limit=None):
        """
        Create a secure VPN tunnel
        
        Args:
            endpoint: Remote endpoint address
            subnet: Internal subnet to route
            bandwidth_limit: Optional bandwidth limit for Starlink optimization
        """
        tunnel = {
            'endpoint': endpoint,
            'subnet': subnet,
            'protocol': self.vpn_config['protocol'],
            'encryption': self.vpn_config['encryption'],
            'bandwidth_limit': bandwidth_limit,
            'status': 'active'
        }
        self.active_tunnels.append(tunnel)
        return tunnel
    
    def optimize_for_starlink(self):
        """
        Optimize VPN settings for Starlink satellite connectivity
        
        Returns configuration optimized for high-latency, variable-bandwidth links
        """
        return {
            'mtu': 1420,  # Optimal MTU for Starlink
            'keepalive': 25,  # Maintain connection through Starlink handoffs
            'tcp_optimizations': {
                'window_scaling': True,
                'timestamps': True,
                'selective_ack': True
            },
            'qos_enabled': True,
            'priority_traffic': ['ssh', 'https', 'dns']
        }
    
    def configure_multi_site(self, sites):
        """
        Configure multi-site VPN for rural/remote locations
        
        Args:
            sites: List of site configurations
        """
        mesh_config = {
            'topology': 'full-mesh',
            'failover': 'automatic',
            'sites': sites,
            'routing': 'dynamic'
        }
        return mesh_config
    
    def get_tunnel_status(self):
        """Get status of all active VPN tunnels"""
        return self.active_tunnels
