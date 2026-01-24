"""
Access Control Module - Role-Based Access Control (RBAC)
Enterprise RBAC implementation for managed infrastructure
"""

import logging

# Configure logging
logger = logging.getLogger(__name__)

class RBACManager:
    """Manages role-based access control for enterprise infrastructure"""
    
    def __init__(self):
        self.roles = {}
        self.user_roles = {}
        self.permissions = {}
        
        # Initialize default enterprise roles
        self._initialize_default_roles()
        
    def _initialize_default_roles(self):
        """Initialize default enterprise security roles"""
        default_roles = {
            'admin': {
                'description': 'Full system administrator',
                'permissions': ['read', 'write', 'delete', 'configure', 'audit']
            },
            'security_analyst': {
                'description': 'Security monitoring and analysis',
                'permissions': ['read', 'audit', 'monitor', 'alert']
            },
            'network_engineer': {
                'description': 'Network configuration and management',
                'permissions': ['read', 'write', 'configure_network', 'monitor']
            },
            'compliance_officer': {
                'description': 'Compliance monitoring and reporting',
                'permissions': ['read', 'audit', 'generate_reports']
            },
            'viewer': {
                'description': 'Read-only access',
                'permissions': ['read']
            }
        }
        
        for role_name, role_config in default_roles.items():
            self.create_role(role_name, role_config['description'], role_config['permissions'])
    
    def create_role(self, role_name, description, permissions):
        """
        Create a new role
        
        Args:
            role_name: Name of the role
            description: Role description
            permissions: List of permissions
        """
        self.roles[role_name] = {
            'description': description,
            'permissions': permissions
        }
        return role_name
    
    def assign_role(self, user_id, role_name):
        """
        Assign a role to a user
        
        Args:
            user_id: User identifier
            role_name: Role to assign
            
        Returns:
            True if successful
            
        Raises:
            ValueError: If role does not exist
        """
        if role_name not in self.roles:
            logger.error(
                "Failed to assign role to user",
                extra={
                    'user_id': user_id,
                    'role_name': role_name,
                    'reason': 'role_not_found',
                    'available_roles': list(self.roles.keys())
                }
            )
            raise ValueError(f"Role {role_name} does not exist")
            
        if user_id not in self.user_roles:
            self.user_roles[user_id] = []
            
        if role_name not in self.user_roles[user_id]:
            self.user_roles[user_id].append(role_name)
            logger.info(
                "Role assigned successfully",
                extra={
                    'user_id': user_id,
                    'role_name': role_name,
                    'permissions': self.roles[role_name]['permissions']
                }
            )
        else:
            logger.warning(
                "Role already assigned to user",
                extra={
                    'user_id': user_id,
                    'role_name': role_name
                }
            )
        return True
    
    def check_permission(self, user_id, permission):
        """
        Check if user has specific permission
        
        Args:
            user_id: User identifier
            permission: Permission to check
            
        Returns:
            Boolean indicating if user has permission
        """
        if user_id not in self.user_roles:
            logger.warning(
                "Permission check failed - user has no roles",
                extra={
                    'user_id': user_id,
                    'permission': permission,
                    'reason': 'no_roles_assigned'
                }
            )
            return False
            
        for role in self.user_roles[user_id]:
            if permission in self.roles[role]['permissions']:
                logger.debug(
                    "Permission check succeeded",
                    extra={
                        'user_id': user_id,
                        'permission': permission,
                        'granted_by_role': role
                    }
                )
                return True
        
        # Permission denied - log for audit trail
        logger.warning(
            "Permission check failed - permission denied",
            extra={
                'user_id': user_id,
                'permission': permission,
                'user_roles': self.user_roles[user_id],
                'reason': 'permission_not_in_roles'
            }
        )
        return False
    
    def get_user_permissions(self, user_id):
        """Get all permissions for a user"""
        if user_id not in self.user_roles:
            return []
            
        permissions = set()
        for role in self.user_roles[user_id]:
            permissions.update(self.roles[role]['permissions'])
        return list(permissions)
    
    def configure_starlink_access_policy(self):
        """
        Configure access policies specific to Starlink connectivity
        
        Ensures secure access for remote/rural deployments
        """
        return {
            'require_vpn': True,
            'require_mfa': True,
            'allowed_connection_types': ['starlink', 'fiber', 'cellular_backup'],
            'session_timeout': 3600,  # 1 hour for remote connections
            'idle_timeout': 900,  # 15 minutes
            'concurrent_sessions': 3,
            'ip_whitelisting': True
        }
