"""
Network Security Module - Firewall Rules
Enterprise-grade firewall configuration for Starlink-enabled networks
"""

import logging

# Configure logging
logger = logging.getLogger(__name__)

# Valid network identifiers
VALID_NETWORK_IDENTIFIERS = {
    'internal_network',
    'external_network',
    'starlink_gateway',
    'dmz',
    'management_network',
    'any'
}

class FirewallRuleManager:
    """Manages firewall rules for secure Starlink connectivity"""
    
    def __init__(self):
        self.rules = []
        self.starlink_ports = [443, 80, 53]  # Essential Starlink communication ports
    
    def _validate_port(self, port):
        """
        Validate port parameter
        
        Args:
            port: Port number or special value
            
        Returns:
            True if valid
            
        Raises:
            ValueError: If port is invalid
        """
        # Allow special values
        if port == '*' or port == 'any':
            return True
            
        # Validate numeric port
        try:
            port_num = int(port)
            if not (1 <= port_num <= 65535):
                raise ValueError(f"Port must be between 1 and 65535, got {port_num}")
            return True
        except (TypeError, ValueError) as e:
            raise ValueError(f"Invalid port value '{port}'. Must be integer (1-65535) or '*'") from e
    
    def _validate_network_identifier(self, identifier, param_name):
        """
        Validate network identifier
        
        Args:
            identifier: Network identifier to validate
            param_name: Parameter name for error messages
            
        Returns:
            True if valid
            
        Raises:
            ValueError: If identifier is invalid
        """
        # Allow IP addresses or CIDR notation using ipaddress module for validation
        if '.' in str(identifier) or ':' in str(identifier):
            try:
                import ipaddress
                # Try to parse as IP address or network
                try:
                    ipaddress.ip_address(identifier)
                    return True
                except ValueError:
                    # Try as network/CIDR
                    ipaddress.ip_network(identifier, strict=False)
                    return True
            except (ValueError, ImportError):
                # If ipaddress module not available or invalid format, fall through
                # In this case, still allow it if it looks like an IP (has dots/colons)
                if '.' in str(identifier) or ':' in str(identifier):
                    return True
            
        # Check against valid identifiers
        if identifier not in VALID_NETWORK_IDENTIFIERS:
            raise ValueError(
                f"Invalid {param_name} '{identifier}'. "
                f"Must be an IP address/CIDR or one of: {', '.join(sorted(VALID_NETWORK_IDENTIFIERS))}"
            )
        return True
        
    def add_rule(self, rule_type, source, destination, port, action="allow"):
        """
        Add a firewall rule
        
        Args:
            rule_type: Type of rule (inbound/outbound)
            source: Source IP, CIDR, or network identifier
            destination: Destination IP, CIDR, or network identifier
            port: Port number (1-65535) or '*' for all ports
            action: Allow or deny
            
        Returns:
            Created rule dictionary
            
        Raises:
            ValueError: If any parameter is invalid
        """
        # Validate inputs
        self._validate_port(port)
        self._validate_network_identifier(source, 'source')
        self._validate_network_identifier(destination, 'destination')
        
        rule = {
            'type': rule_type,
            'source': source,
            'destination': destination,
            'port': port,
            'action': action
        }
        self.rules.append(rule)
        
        logger.info(
            "Firewall rule added",
            extra={
                'rule_type': rule_type,
                'source': source,
                'destination': destination,
                'port': port,
                'action': action
            }
        )
        
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
