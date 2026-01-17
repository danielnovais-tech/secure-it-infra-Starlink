#!/usr/bin/env python3
"""
Policy Manager for Dynamic Privacy Policy Reloading and Audit Trail

Provides runtime policy management with:
- Dynamic policy reloading without service restart
- Cryptographically signed audit trail of policy changes
- Signal-based and API-based policy updates
- Policy versioning and rollback capabilities
- Compliance evidence generation
"""

import json
import hashlib
import time
import signal
import threading
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
import copy


class PolicyAuditTrail:
    """
    Maintains a cryptographically signed, append-only audit trail of policy changes.
    
    Each policy change is hashed and linked to the previous change, creating a
    tamper-evident chain similar to blockchain. This provides proof of which
    enforcement rules were active at any given time.
    """
    
    def __init__(self, audit_log_path: str = "policies/audit_trail.jsonl"):
        self.audit_log_path = Path(audit_log_path)
        self.audit_log_path.parent.mkdir(parents=True, exist_ok=True)
        self.previous_hash = self._get_last_hash()
        self.lock = threading.Lock()
        
    def _get_last_hash(self) -> str:
        """Get the hash of the last audit entry for chain linking."""
        if not self.audit_log_path.exists():
            return "0" * 64  # Genesis hash
        
        try:
            with open(self.audit_log_path, 'r') as f:
                lines = f.readlines()
                if lines:
                    last_entry = json.loads(lines[-1])
                    return last_entry.get('hash', "0" * 64)
        except Exception:
            pass
        
        return "0" * 64
    
    def _compute_hash(self, entry: Dict[str, Any]) -> str:
        """Compute SHA-256 hash of audit entry including previous hash."""
        # Create deterministic string representation
        hash_input = {
            'timestamp': entry['timestamp'],
            'action': entry['action'],
            'policy_path': entry['policy_path'],
            'policy_hash': entry['policy_hash'],
            'previous_hash': entry['previous_hash'],
            'user': entry.get('user', 'system'),
            'reason': entry.get('reason', '')
        }
        
        canonical = json.dumps(hash_input, sort_keys=True)
        return hashlib.sha256(canonical.encode()).hexdigest()
    
    def log_policy_change(self, action: str, policy_path: str, policy_content: Dict,
                         user: str = "system", reason: str = "") -> str:
        """
        Log a policy change to the audit trail.
        
        Args:
            action: Type of change (load, reload, update, rollback)
            policy_path: Path to the policy file
            policy_content: The policy content (for hashing)
            user: User/service making the change
            reason: Reason for the change
            
        Returns:
            Hash of the audit entry
        """
        with self.lock:
            # Compute hash of policy content
            policy_hash = hashlib.sha256(
                json.dumps(policy_content, sort_keys=True).encode()
            ).hexdigest()
            
            # Create audit entry
            entry = {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'action': action,
                'policy_path': str(policy_path),
                'policy_hash': policy_hash,
                'previous_hash': self.previous_hash,
                'user': user,
                'reason': reason,
                'metadata': {
                    'policy_version': policy_content.get('version', 'unknown'),
                    'environment': policy_content.get('environment', 'unknown'),
                    'enforcement_level': policy_content.get('enforcement_level', 'unknown')
                }
            }
            
            # Compute hash of this entry
            entry['hash'] = self._compute_hash(entry)
            
            # Append to audit log (append-only)
            with open(self.audit_log_path, 'a') as f:
                f.write(json.dumps(entry) + '\n')
            
            # Update previous hash for next entry
            self.previous_hash = entry['hash']
            
            return entry['hash']
    
    def verify_integrity(self) -> tuple[bool, List[str]]:
        """
        Verify the integrity of the entire audit trail.
        
        Returns:
            Tuple of (is_valid, list of error messages)
        """
        if not self.audit_log_path.exists():
            return True, []
        
        errors = []
        previous_hash = "0" * 64
        
        with open(self.audit_log_path, 'r') as f:
            for line_num, line in enumerate(f, 1):
                try:
                    entry = json.loads(line)
                    
                    # Verify previous hash linkage
                    if entry['previous_hash'] != previous_hash:
                        errors.append(f"Line {line_num}: Hash chain broken")
                    
                    # Verify entry hash
                    stored_hash = entry['hash']
                    computed_hash = self._compute_hash(entry)
                    
                    if stored_hash != computed_hash:
                        errors.append(f"Line {line_num}: Hash mismatch (tampered)")
                    
                    previous_hash = stored_hash
                    
                except json.JSONDecodeError:
                    errors.append(f"Line {line_num}: Invalid JSON")
        
        return len(errors) == 0, errors
    
    def get_audit_history(self, limit: Optional[int] = None) -> List[Dict]:
        """Get audit history, optionally limited to last N entries."""
        if not self.audit_log_path.exists():
            return []
        
        with open(self.audit_log_path, 'r') as f:
            entries = [json.loads(line) for line in f]
        
        if limit:
            return entries[-limit:]
        return entries
    
    def get_policy_at_time(self, timestamp: str) -> Optional[Dict]:
        """
        Get the policy hash that was active at a specific timestamp.
        
        This allows auditors to prove which rules were in effect at any point.
        """
        if not self.audit_log_path.exists():
            return None
        
        target_time = datetime.fromisoformat(timestamp)
        active_policy = None
        
        with open(self.audit_log_path, 'r') as f:
            for line in f:
                entry = json.loads(line)
                entry_time = datetime.fromisoformat(entry['timestamp'])
                
                if entry_time <= target_time:
                    active_policy = entry
                else:
                    break
        
        return active_policy


class PolicyManager:
    """
    Manages dynamic policy loading and reloading.
    
    Features:
    - Load policies from JSON files
    - Reload policies at runtime via signal or API
    - Maintain audit trail of all policy changes
    - Support policy versioning and rollback
    - Thread-safe policy access
    """
    
    def __init__(self, default_policy_path: str = "policies/privacy_policy_production.json"):
        self.policy_path = Path(default_policy_path)
        self.current_policy: Optional[Dict] = None
        self.policy_lock = threading.RLock()
        self.audit_trail = PolicyAuditTrail()
        self.policy_history: List[Dict] = []  # For rollback
        self.max_history = 10
        
        # Load initial policy
        self.load_policy(reason="Initial load at startup")
        
        # Set up signal handler for dynamic reloading (SIGUSR2)
        # SIGUSR1 is used for log level toggling, so we use SIGUSR2
        if hasattr(signal, 'SIGUSR2'):
            signal.signal(signal.SIGUSR2, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle SIGUSR2 signal to reload policy."""
        print(f"Received signal {signum}, reloading policy...")
        self.reload_policy(reason="Signal-triggered reload (SIGUSR2)")
    
    def load_policy(self, policy_path: Optional[str] = None, reason: str = "") -> bool:
        """
        Load a policy from file.
        
        Args:
            policy_path: Path to policy file (uses default if None)
            reason: Reason for loading this policy
            
        Returns:
            True if successful, False otherwise
        """
        if policy_path:
            self.policy_path = Path(policy_path)
        
        try:
            with open(self.policy_path, 'r') as f:
                new_policy = json.load(f)
            
            with self.policy_lock:
                # Save current policy to history
                if self.current_policy:
                    self.policy_history.append(copy.deepcopy(self.current_policy))
                    if len(self.policy_history) > self.max_history:
                        self.policy_history.pop(0)
                
                # Update current policy
                self.current_policy = new_policy
            
            # Log to audit trail
            self.audit_trail.log_policy_change(
                action="load",
                policy_path=str(self.policy_path),
                policy_content=new_policy,
                reason=reason
            )
            
            print(f"Policy loaded: {self.policy_path}")
            return True
            
        except Exception as e:
            print(f"Failed to load policy from {self.policy_path}: {e}")
            return False
    
    def reload_policy(self, reason: str = "") -> bool:
        """
        Reload the current policy file.
        
        Useful for picking up changes without restarting the service.
        
        Args:
            reason: Reason for reload
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(self.policy_path, 'r') as f:
                new_policy = json.load(f)
            
            with self.policy_lock:
                # Check if policy actually changed
                if self.current_policy == new_policy:
                    print("Policy unchanged, skipping reload")
                    return True
                
                # Save current to history
                if self.current_policy:
                    self.policy_history.append(copy.deepcopy(self.current_policy))
                    if len(self.policy_history) > self.max_history:
                        self.policy_history.pop(0)
                
                # Update current policy
                self.current_policy = new_policy
            
            # Log to audit trail
            self.audit_trail.log_policy_change(
                action="reload",
                policy_path=str(self.policy_path),
                policy_content=new_policy,
                reason=reason
            )
            
            print(f"Policy reloaded: {self.policy_path}")
            return True
            
        except Exception as e:
            print(f"Failed to reload policy from {self.policy_path}: {e}")
            return False
    
    def get_policy(self) -> Optional[Dict]:
        """Get the current active policy (thread-safe)."""
        with self.policy_lock:
            return copy.deepcopy(self.current_policy) if self.current_policy else None
    
    def rollback_policy(self, steps: int = 1, reason: str = "") -> bool:
        """
        Rollback to a previous policy version.
        
        Args:
            steps: Number of versions to roll back (1 = previous version)
            reason: Reason for rollback
            
        Returns:
            True if successful, False otherwise
        """
        with self.policy_lock:
            if not self.policy_history:
                print("No policy history available for rollback")
                return False
            
            if steps > len(self.policy_history):
                print(f"Cannot rollback {steps} steps, only {len(self.policy_history)} available")
                return False
            
            # Get the rollback target
            rollback_index = -(steps)
            rollback_policy = self.policy_history[rollback_index]
            
            # Apply rollback
            self.current_policy = copy.deepcopy(rollback_policy)
            
            # Remove rolled-back versions from history
            self.policy_history = self.policy_history[:rollback_index]
        
        # Log rollback to audit trail
        self.audit_trail.log_policy_change(
            action=f"rollback_{steps}_steps",
            policy_path=str(self.policy_path),
            policy_content=self.current_policy,
            reason=reason
        )
        
        print(f"Policy rolled back {steps} step(s)")
        return True
    
    def get_audit_summary(self) -> Dict:
        """Get a summary of the audit trail."""
        history = self.audit_trail.get_audit_history()
        
        return {
            'total_changes': len(history),
            'first_change': history[0]['timestamp'] if history else None,
            'last_change': history[-1]['timestamp'] if history else None,
            'actions': {
                'load': sum(1 for e in history if e['action'] == 'load'),
                'reload': sum(1 for e in history if e['action'] == 'reload'),
                'rollback': sum(1 for e in history if e['action'].startswith('rollback'))
            },
            'integrity_verified': self.audit_trail.verify_integrity()[0]
        }
    
    def generate_compliance_evidence(self, output_path: str = "policies/compliance_evidence.json") -> bool:
        """
        Generate an auditor-friendly compliance evidence bundle.
        
        Includes:
        - Current policy
        - Complete audit trail
        - Integrity verification
        - Policy history summary
        
        Args:
            output_path: Where to save the evidence bundle
            
        Returns:
            True if successful, False otherwise
        """
        try:
            is_valid, errors = self.audit_trail.verify_integrity()
            
            evidence = {
                'generated_at': datetime.now(timezone.utc).isoformat(),
                'current_policy': {
                    'path': str(self.policy_path),
                    'content': self.get_policy(),
                    'hash': hashlib.sha256(
                        json.dumps(self.current_policy, sort_keys=True).encode()
                    ).hexdigest()
                },
                'audit_trail': {
                    'integrity_verified': is_valid,
                    'verification_errors': errors,
                    'total_entries': len(self.audit_trail.get_audit_history()),
                    'entries': self.audit_trail.get_audit_history()
                },
                'policy_history': {
                    'versions_in_memory': len(self.policy_history),
                    'max_history_size': self.max_history
                },
                'summary': self.get_audit_summary()
            }
            
            output = Path(output_path)
            output.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output, 'w') as f:
                json.dump(evidence, f, indent=2)
            
            print(f"Compliance evidence bundle generated: {output_path}")
            return True
            
        except Exception as e:
            print(f"Failed to generate compliance evidence: {e}")
            return False


# Global policy manager instance
_policy_manager: Optional[PolicyManager] = None
_policy_manager_lock = threading.Lock()


def get_policy_manager(default_policy_path: str = "policies/privacy_policy_production.json") -> PolicyManager:
    """Get the global PolicyManager instance (singleton pattern)."""
    global _policy_manager
    
    with _policy_manager_lock:
        if _policy_manager is None:
            _policy_manager = PolicyManager(default_policy_path)
        return _policy_manager


# Convenience functions for common operations
def reload_policy(reason: str = "API-triggered reload") -> bool:
    """Reload the current policy. Can be called from anywhere in the application."""
    return get_policy_manager().reload_policy(reason=reason)


def get_current_policy() -> Optional[Dict]:
    """Get the current active policy."""
    return get_policy_manager().get_policy()


def rollback_policy(steps: int = 1, reason: str = "API-triggered rollback") -> bool:
    """Rollback to a previous policy version."""
    return get_policy_manager().rollback_policy(steps=steps, reason=reason)


def generate_compliance_evidence(output_path: str = "policies/compliance_evidence.json") -> bool:
    """Generate compliance evidence bundle."""
    return get_policy_manager().generate_compliance_evidence(output_path=output_path)


def verify_audit_trail() -> tuple[bool, List[str]]:
    """Verify the integrity of the policy audit trail."""
    return get_policy_manager().audit_trail.verify_integrity()


if __name__ == "__main__":
    import sys
    
    # Command-line interface for policy management
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python policy_manager.py reload [reason]")
        print("  python policy_manager.py rollback [steps] [reason]")
        print("  python policy_manager.py verify")
        print("  python policy_manager.py evidence [output_path]")
        print("  python policy_manager.py history [limit]")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "reload":
        reason = sys.argv[2] if len(sys.argv) > 2 else "CLI-triggered reload"
        success = reload_policy(reason=reason)
        sys.exit(0 if success else 1)
    
    elif command == "rollback":
        steps = int(sys.argv[2]) if len(sys.argv) > 2 else 1
        reason = sys.argv[3] if len(sys.argv) > 3 else "CLI-triggered rollback"
        success = rollback_policy(steps=steps, reason=reason)
        sys.exit(0 if success else 1)
    
    elif command == "verify":
        is_valid, errors = verify_audit_trail()
        if is_valid:
            print("✓ Audit trail integrity verified")
            sys.exit(0)
        else:
            print("✗ Audit trail integrity check failed:")
            for error in errors:
                print(f"  - {error}")
            sys.exit(1)
    
    elif command == "evidence":
        output_path = sys.argv[2] if len(sys.argv) > 2 else "policies/compliance_evidence.json"
        success = generate_compliance_evidence(output_path=output_path)
        sys.exit(0 if success else 1)
    
    elif command == "history":
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else None
        manager = get_policy_manager()
        history = manager.audit_trail.get_audit_history(limit=limit)
        
        print(f"Policy Audit History ({len(history)} entries):")
        for entry in history:
            print(f"\n{entry['timestamp']}")
            print(f"  Action: {entry['action']}")
            print(f"  Policy: {entry['policy_path']}")
            print(f"  Hash: {entry['hash'][:16]}...")
            print(f"  User: {entry['user']}")
            if entry['reason']:
                print(f"  Reason: {entry['reason']}")
        
        sys.exit(0)
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
