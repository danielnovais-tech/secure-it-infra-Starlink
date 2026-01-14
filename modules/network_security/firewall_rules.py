"""
Network Security Module - Firewall Rules
Enterprise-grade firewall configuration for Starlink-enabled networks
"""

class FirewallRuleManager:
    """Manages firewall rules for secure Starlink connectivity"""
    
    def __init__(self):
        self.rules = []
        self.starlink_ports = [443, 80, 53]  # Essential Starlink communication ports
        
    def add_rule(self, rule_type, source, destination, port, action="allow"):
        """
        Add a firewall rule
        
        Args:
            rule_type: Type of rule (inbound/outbound)
            source: Source IP or range
            destination: Destination IP or range
            port: Port number
            action: Allow or deny
        """
        rule = {
            'type': rule_type,
            'source': source,
            'destination': destination,
            'port': port,
            'action': action
        }
        self.rules.append(rule)
        return rule
    
    def configure_starlink_access(self):
        """Configure firewall rules specifically for Starlink connectivity"""
        rules = []
        for port in self.starlink_ports:
            rule = self.add_rule(
                rule_type='outbound',
                source='internal_network',
                destination='starlink_gateway',
                port=port,
                action='allow'
            )
            rules.append(rule)
        return rules
    
    def block_unauthorized_access(self, ip_list):
        """Block specific IP addresses or ranges"""
        blocked_rules = []
        for ip in ip_list:
            rule = self.add_rule(
                rule_type='inbound',
                source=ip,
                destination='internal_network',
                port='*',
                action='deny'
            )
            blocked_rules.append(rule)
        return blocked_rules
    
    def enable_geo_fencing(self, allowed_regions):
        """
        Enable geo-fencing for rural/remote deployments
        
        Args:
            allowed_regions: List of allowed geographical regions
        """
        return {
            'enabled': True,
            'allowed_regions': allowed_regions,
            'enforcement': 'strict'
        }
    
    def get_all_rules(self):
        """Retrieve all configured firewall rules"""
        return self.rules
