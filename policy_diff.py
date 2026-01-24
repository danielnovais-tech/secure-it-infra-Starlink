#!/usr/bin/env python3
"""
Policy Diff and Signed Evidence Bundle Generator

Provides:
- Field-level policy comparison with human-readable and machine-readable outputs
- Signed evidence bundles for independent verification
- Granular rollback by timestamp or policy ID
- Observability metrics for policy operations
"""

import json
import hashlib
import subprocess
import tempfile
import threading
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict


@dataclass
class FieldChange:
    """Represents a single field-level change between policies."""
    field_path: str
    old_value: Any
    new_value: Any
    change_type: str  # 'added', 'removed', 'modified'
    
    def to_dict(self) -> Dict:
        return asdict(self)


class PolicyDiffer:
    """
    Generates field-level diffs between policy versions.
    
    Supports both human-readable and machine-readable output formats.
    """
    
    def __init__(self):
        self.changes: List[FieldChange] = []
        
    def diff(self, old_policy: Dict, new_policy: Dict, 
             base_path: str = "") -> List[FieldChange]:
        """
        Compare two policies and generate field-level changes.
        
        Args:
            old_policy: Previous policy version
            new_policy: New policy version
            base_path: Base path for nested fields (internal use)
            
        Returns:
            List of FieldChange objects
        """
        changes = []
        
        # Find all keys in both policies
        all_keys = set(old_policy.keys()) | set(new_policy.keys())
        
        for key in sorted(all_keys):
            current_path = f"{base_path}.{key}" if base_path else key
            
            # Key removed
            if key not in new_policy:
                changes.append(FieldChange(
                    field_path=current_path,
                    old_value=old_policy[key],
                    new_value=None,
                    change_type='removed'
                ))
                
            # Key added
            elif key not in old_policy:
                changes.append(FieldChange(
                    field_path=current_path,
                    old_value=None,
                    new_value=new_policy[key],
                    change_type='added'
                ))
                
            # Both present - check if modified
            else:
                old_val = old_policy[key]
                new_val = new_policy[key]
                
                # Recursively diff nested dicts
                if isinstance(old_val, dict) and isinstance(new_val, dict):
                    changes.extend(self.diff(old_val, new_val, current_path))
                    
                # Recursively diff lists
                elif isinstance(old_val, list) and isinstance(new_val, list):
                    list_changes = self._diff_lists(old_val, new_val, current_path)
                    changes.extend(list_changes)
                    
                # Value changed
                elif old_val != new_val:
                    changes.append(FieldChange(
                        field_path=current_path,
                        old_value=old_val,
                        new_value=new_val,
                        change_type='modified'
                    ))
        
        return changes
    
    def _diff_lists(self, old_list: List, new_list: List, 
                   base_path: str) -> List[FieldChange]:
        """Diff two lists and generate changes."""
        changes = []
        
        # Simple list comparison
        if old_list != new_list:
            # Check for added/removed items
            old_set = set(map(str, old_list))
            new_set = set(map(str, new_list))
            
            added = new_set - old_set
            removed = old_set - new_set
            
            if added or removed:
                changes.append(FieldChange(
                    field_path=base_path,
                    old_value=old_list,
                    new_value=new_list,
                    change_type='modified'
                ))
        
        return changes
    
    def format_human_readable(self, changes: List[FieldChange]) -> str:
        """
        Format changes as human-readable text.
        
        Args:
            changes: List of field changes
            
        Returns:
            Formatted string for human consumption
        """
        if not changes:
            return "No changes detected between policies."
        
        lines = []
        lines.append("=" * 80)
        lines.append("POLICY DIFF SUMMARY")
        lines.append("=" * 80)
        lines.append(f"Total changes: {len(changes)}")
        lines.append("")
        
        # Group by change type
        added = [c for c in changes if c.change_type == 'added']
        removed = [c for c in changes if c.change_type == 'removed']
        modified = [c for c in changes if c.change_type == 'modified']
        
        if added:
            lines.append(f"ADDED FIELDS ({len(added)}):")
            lines.append("-" * 80)
            for change in added:
                lines.append(f"  + {change.field_path}")
                lines.append(f"      Value: {self._format_value(change.new_value)}")
                lines.append("")
        
        if removed:
            lines.append(f"REMOVED FIELDS ({len(removed)}):")
            lines.append("-" * 80)
            for change in removed:
                lines.append(f"  - {change.field_path}")
                lines.append(f"      Was: {self._format_value(change.old_value)}")
                lines.append("")
        
        if modified:
            lines.append(f"MODIFIED FIELDS ({len(modified)}):")
            lines.append("-" * 80)
            for change in modified:
                lines.append(f"  ~ {change.field_path}")
                lines.append(f"      Old: {self._format_value(change.old_value)}")
                lines.append(f"      New: {self._format_value(change.new_value)}")
                lines.append("")
        
        lines.append("=" * 80)
        return "\n".join(lines)
    
    def _format_value(self, value: Any) -> str:
        """Format a value for display."""
        if value is None:
            return "(none)"
        if isinstance(value, (dict, list)):
            return json.dumps(value, indent=2)
        return str(value)
    
    def format_machine_readable(self, changes: List[FieldChange]) -> Dict:
        """
        Format changes as machine-readable JSON.
        
        Args:
            changes: List of field changes
            
        Returns:
            Dictionary suitable for JSON serialization
        """
        return {
            'summary': {
                'total_changes': len(changes),
                'added': len([c for c in changes if c.change_type == 'added']),
                'removed': len([c for c in changes if c.change_type == 'removed']),
                'modified': len([c for c in changes if c.change_type == 'modified'])
            },
            'changes': [c.to_dict() for c in changes],
            'generated_at': datetime.now(timezone.utc).isoformat()
        }


class SignedEvidenceGenerator:
    """
    Generates cryptographically signed evidence bundles.
    
    Supports PGP/GPG signatures for independent verification by auditors.
    """
    
    def __init__(self, gpg_key_id: Optional[str] = None):
        """
        Initialize evidence generator.
        
        Args:
            gpg_key_id: GPG key ID for signing (optional)
        """
        self.gpg_key_id = gpg_key_id
        self.gpg_available = self._check_gpg()
        
    def _check_gpg(self) -> bool:
        """Check if GPG is available."""
        try:
            result = subprocess.run(['gpg', '--version'], 
                                   capture_output=True, 
                                   timeout=5)
            return result.returncode == 0
        except (subprocess.SubprocessError, FileNotFoundError):
            return False
    
    def generate_evidence_bundle(self, 
                                 policy_history: List[Dict],
                                 audit_trail: List[Dict],
                                 diff_results: Optional[Dict] = None) -> Dict:
        """
        Generate comprehensive evidence bundle.
        
        Args:
            policy_history: List of policy versions
            audit_trail: List of audit trail entries
            diff_results: Optional diff results between versions
            
        Returns:
            Evidence bundle dictionary
        """
        bundle = {
            'metadata': {
                'generated_at': datetime.now(timezone.utc).isoformat(),
                'bundle_version': '1.0.0',
                'generator': 'PolicyManager v1.0',
                'signed': self.gpg_available and self.gpg_key_id is not None
            },
            'policy_history': policy_history,
            'audit_trail': audit_trail,
            'integrity': self._compute_bundle_integrity(policy_history, audit_trail)
        }
        
        if diff_results:
            bundle['diffs'] = diff_results
        
        # Compute bundle hash
        bundle_hash = self._hash_bundle(bundle)
        bundle['metadata']['bundle_hash'] = bundle_hash
        
        return bundle
    
    def _compute_bundle_integrity(self, policy_history: List[Dict], 
                                  audit_trail: List[Dict]) -> Dict:
        """Compute integrity information for the bundle."""
        return {
            'policy_count': len(policy_history),
            'audit_entry_count': len(audit_trail),
            'policy_hashes': [
                hashlib.sha256(json.dumps(p, sort_keys=True).encode()).hexdigest()
                for p in policy_history
            ],
            'audit_chain_valid': self._verify_audit_chain(audit_trail)
        }
    
    def _verify_audit_chain(self, audit_trail: List[Dict]) -> bool:
        """Verify the integrity of the audit chain."""
        if not audit_trail:
            return True
        
        for i in range(1, len(audit_trail)):
            expected_prev = audit_trail[i-1].get('hash', '')
            actual_prev = audit_trail[i].get('previous_hash', '')
            if expected_prev != actual_prev:
                return False
        
        return True
    
    def _hash_bundle(self, bundle: Dict) -> str:
        """Compute SHA-256 hash of the bundle."""
        # Create a copy without the hash field
        bundle_copy = {k: v for k, v in bundle.items() 
                      if k != 'signature' and 
                      (k != 'metadata' or 'bundle_hash' not in str(v))}
        canonical = json.dumps(bundle_copy, sort_keys=True)
        return hashlib.sha256(canonical.encode()).hexdigest()
    
    def sign_bundle(self, bundle: Dict) -> Tuple[Dict, Optional[str]]:
        """
        Sign evidence bundle with GPG.
        
        Args:
            bundle: Evidence bundle to sign
            
        Returns:
            Tuple of (bundle with signature metadata, detached signature)
        """
        if not self.gpg_available:
            return bundle, None
        
        if not self.gpg_key_id:
            return bundle, None
        
        try:
            # Create temporary file with bundle
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', 
                                            delete=False) as f:
                json.dump(bundle, f, indent=2)
                temp_path = f.name
            
            # Sign with GPG
            result = subprocess.run(
                ['gpg', '--detach-sign', '--armor', 
                 '--local-user', self.gpg_key_id,
                 '--output', '-', temp_path],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # Clean up temp file
            Path(temp_path).unlink()
            
            if result.returncode == 0:
                signature = result.stdout
                bundle['signature'] = {
                    'algorithm': 'PGP/GPG',
                    'key_id': self.gpg_key_id,
                    'created_at': datetime.now(timezone.utc).isoformat()
                }
                return bundle, signature
            
        except (subprocess.SubprocessError, OSError) as e:
            print(f"Warning: Failed to sign bundle: {e}")
        
        return bundle, None
    
    def verify_signature(self, bundle_path: str, signature_path: str) -> bool:
        """
        Verify a signed evidence bundle.
        
        Args:
            bundle_path: Path to evidence bundle JSON
            signature_path: Path to detached signature
            
        Returns:
            True if signature is valid
        """
        if not self.gpg_available:
            return False
        
        try:
            result = subprocess.run(
                ['gpg', '--verify', signature_path, bundle_path],
                capture_output=True,
                timeout=30
            )
            return result.returncode == 0
        except (subprocess.SubprocessError, OSError):
            return False


class PolicyMetrics:
    """
    Track observability metrics for policy operations.
    """
    
    def __init__(self):
        self.metrics = {
            'policy_reload_count': 0,
            'policy_rollback_count': 0,
            'policy_verification_failures': 0,
            'audit_chain_breaks': 0,
            'evidence_bundles_generated': 0,
            'diffs_generated': 0,
            'last_reload_timestamp': None,
            'last_rollback_timestamp': None
        }
        self.lock = threading.Lock()
    
    def increment(self, metric_name: str):
        """Increment a counter metric."""
        with self.lock:
            if metric_name in self.metrics:
                self.metrics[metric_name] += 1
    
    def set_timestamp(self, metric_name: str):
        """Set a timestamp metric."""
        with self.lock:
            if metric_name in self.metrics:
                self.metrics[metric_name] = datetime.now(timezone.utc).isoformat()
    
    def get_metrics(self) -> Dict:
        """Get all metrics."""
        with self.lock:
            return self.metrics.copy()
    
    def export_prometheus(self) -> str:
        """Export metrics in Prometheus format."""
        lines = []
        lines.append("# HELP policy_reload_count Number of policy reloads")
        lines.append("# TYPE policy_reload_count counter")
        lines.append(f"policy_reload_count {self.metrics['policy_reload_count']}")
        
        lines.append("# HELP policy_rollback_count Number of policy rollbacks")
        lines.append("# TYPE policy_rollback_count counter")
        lines.append(f"policy_rollback_count {self.metrics['policy_rollback_count']}")
        
        lines.append("# HELP policy_verification_failures Number of verification failures")
        lines.append("# TYPE policy_verification_failures counter")
        lines.append(f"policy_verification_failures {self.metrics['policy_verification_failures']}")
        
        lines.append("# HELP audit_chain_breaks Number of audit chain integrity breaks")
        lines.append("# TYPE audit_chain_breaks counter")
        lines.append(f"audit_chain_breaks {self.metrics['audit_chain_breaks']}")
        
        return "\n".join(lines)


if __name__ == '__main__':
    # Example usage
    print("Policy Diff and Signed Evidence Bundle Generator")
    print("=" * 80)
    
    # Example: Diff two policies
    old_policy = {
        "enforcement_level": "strict",
        "pii_fields": ["email", "user_id"],
        "retention": {"pii": "90 days"}
    }
    
    new_policy = {
        "enforcement_level": "moderate",
        "pii_fields": ["email", "user_id", "ip_address"],
        "phi_fields": ["patient_id"],
        "retention": {"pii": "90 days", "phi": "7 years"}
    }
    
    differ = PolicyDiffer()
    changes = differ.diff(old_policy, new_policy)
    
    print(differ.format_human_readable(changes))
    print("\nMachine-readable format:")
    print(json.dumps(differ.format_machine_readable(changes), indent=2))
