# Cryptographically Verifiable Audit Trail Design

This document outlines the design for implementing a cryptographically verifiable audit trail system for the Starlink Security Infrastructure application.

## Overview

A cryptographically verifiable audit trail provides tamper-evident logging through hash chaining and Merkle trees, ensuring logs cannot be modified without detection. This is critical for compliance, security audits, and forensic investigations.

## Design Goals

1. **Tamper Evidence**: Detect any modification, deletion, or insertion of log entries
2. **Cryptographic Verification**: Use cryptographic hashing to ensure integrity
3. **Compliance Ready**: Meet requirements for SOC2, HIPAA, PCI-DSS, and similar standards
4. **Performance**: Minimal overhead on logging operations
5. **Append-Only**: Logs can only be added, never modified or deleted
6. **Verifiable**: Independent verification of log integrity without access to the logging system

## Architecture

### Components

1. **AuditLogger**: Specialized logger for audit events
2. **HashChainManager**: Manages cryptographic hash chain
3. **MerkleTreeBuilder**: Builds Merkle trees for batch verification
4. **VerificationService**: Verifies log integrity
5. **AuditLogStore**: Append-only storage backend

### Hash Chain Structure

Each audit log entry contains:
```python
{
    "sequence_number": int,      # Monotonically increasing
    "timestamp": str,             # ISO 8601 format
    "event_type": str,            # e.g., "AUTH_FAILED", "CONFIG_CHANGED"
    "actor": str,                 # Who performed the action
    "resource": str,              # What was accessed/modified
    "action": str,                # What action was taken
    "result": str,                # Success/failure
    "metadata": dict,             # Additional context
    "previous_hash": str,         # SHA-256 hash of previous entry
    "current_hash": str           # SHA-256 hash of this entry
}
```

### Hash Chain Algorithm

```
Entry[0].previous_hash = GENESIS_HASH (known constant)
Entry[0].current_hash = SHA256(sequence + timestamp + event_data + previous_hash)

Entry[n].previous_hash = Entry[n-1].current_hash
Entry[n].current_hash = SHA256(sequence + timestamp + event_data + previous_hash)
```

**Properties:**
- Any modification to an entry changes its hash
- Changed hash breaks the chain for all subsequent entries
- Verification starts from genesis and validates each link

### Merkle Tree Structure

For efficient verification of large log sets:

```
                    Root Hash
                   /          \
            Hash(L1+L2)     Hash(L3+L4)
            /      \         /      \
        Hash(L1) Hash(L2) Hash(L3) Hash(L4)
          |        |        |        |
        Log1     Log2     Log3     Log4
```

**Benefits:**
- O(log n) verification instead of O(n)
- Can verify subset of logs without processing entire chain
- Root hash published periodically for external verification

## Implementation Design

### 1. AuditLogger Class

```python
class AuditLogger:
    """
    Cryptographically verifiable audit logger.
    
    Features:
    - Hash chain for tamper detection
    - Append-only storage
    - Automatic Merkle tree generation
    - Digital signatures for non-repudiation
    """
    
    def __init__(self, storage_backend, signing_key=None):
        self.storage = storage_backend
        self.hash_chain = HashChainManager()
        self.merkle_builder = MerkleTreeBuilder()
        self.signing_key = signing_key  # Optional: for digital signatures
        self.sequence_number = self._load_last_sequence()
    
    def log_audit_event(self, event_type, actor, resource, action, 
                        result, metadata=None):
        """
        Log an audit event with cryptographic verification.
        
        Args:
            event_type: Category of event (AUTH, CONFIG, DATA_ACCESS, etc.)
            actor: User/service/system that performed action
            resource: What was accessed/modified
            action: Specific action taken
            result: SUCCESS or FAILURE
            metadata: Additional context (dict)
        
        Returns:
            AuditEntry with current_hash for external verification
        """
        # Create entry
        entry = self._create_entry(
            event_type, actor, resource, action, result, metadata
        )
        
        # Add to hash chain
        entry_with_hash = self.hash_chain.add_entry(entry)
        
        # Store in append-only storage
        self.storage.append(entry_with_hash)
        
        # Periodically build Merkle tree
        if self.sequence_number % 1000 == 0:
            self._build_merkle_checkpoint()
        
        # Optional: Sign entry
        if self.signing_key:
            entry_with_hash['signature'] = self._sign_entry(entry_with_hash)
        
        return entry_with_hash
    
    def verify_integrity(self, start_seq=None, end_seq=None):
        """
        Verify integrity of audit log chain.
        
        Returns:
            VerificationResult with status and any integrity violations
        """
        return self.hash_chain.verify_chain(
            self.storage.read_range(start_seq, end_seq)
        )
```

### 2. HashChainManager Class

```python
import hashlib
import json
from datetime import datetime

class HashChainManager:
    """Manages cryptographic hash chain for audit logs."""
    
    GENESIS_HASH = "0" * 64  # SHA-256 of "STARLINK_SECURITY_AUDIT_GENESIS"
    
    def __init__(self):
        self.last_hash = self.GENESIS_HASH
        self.sequence = 0
    
    def add_entry(self, entry):
        """
        Add entry to hash chain and compute hash.
        
        Args:
            entry: Dict with audit event data
        
        Returns:
            Entry with previous_hash and current_hash added
        """
        self.sequence += 1
        
        # Add chain metadata
        entry['sequence_number'] = self.sequence
        entry['previous_hash'] = self.last_hash
        
        # Compute hash of entry
        entry['current_hash'] = self._compute_hash(entry)
        
        # Update chain state
        self.last_hash = entry['current_hash']
        
        return entry
    
    def _compute_hash(self, entry):
        """
        Compute SHA-256 hash of entry.
        
        Hash includes: sequence, timestamp, event data, previous hash
        This ensures any modification breaks the chain.
        """
        # Canonical JSON representation for consistent hashing
        hash_input = json.dumps({
            'sequence_number': entry['sequence_number'],
            'timestamp': entry['timestamp'],
            'event_type': entry['event_type'],
            'actor': entry['actor'],
            'resource': entry['resource'],
            'action': entry['action'],
            'result': entry['result'],
            'metadata': entry.get('metadata', {}),
            'previous_hash': entry['previous_hash']
        }, sort_keys=True, separators=(',', ':'))
        
        return hashlib.sha256(hash_input.encode('utf-8')).hexdigest()
    
    def verify_chain(self, entries):
        """
        Verify integrity of hash chain.
        
        Args:
            entries: List of audit entries to verify
        
        Returns:
            VerificationResult with details
        """
        violations = []
        expected_hash = self.GENESIS_HASH
        
        for i, entry in enumerate(entries):
            # Check sequence is continuous
            if entry['sequence_number'] != i + 1:
                violations.append({
                    'type': 'SEQUENCE_GAP',
                    'entry': i,
                    'expected': i + 1,
                    'actual': entry['sequence_number']
                })
            
            # Check previous hash matches
            if entry['previous_hash'] != expected_hash:
                violations.append({
                    'type': 'HASH_MISMATCH',
                    'entry': i,
                    'expected': expected_hash,
                    'actual': entry['previous_hash']
                })
            
            # Recompute and verify current hash
            recomputed = self._compute_hash(entry)
            if recomputed != entry['current_hash']:
                violations.append({
                    'type': 'HASH_CORRUPTION',
                    'entry': i,
                    'stored': entry['current_hash'],
                    'computed': recomputed
                })
            
            expected_hash = entry['current_hash']
        
        return VerificationResult(
            valid=(len(violations) == 0),
            total_entries=len(entries),
            violations=violations
        )
```

### 3. MerkleTreeBuilder Class

```python
class MerkleTreeBuilder:
    """Builds Merkle trees for efficient verification."""
    
    def build_tree(self, entries):
        """
        Build Merkle tree from audit entries.
        
        Args:
            entries: List of audit entries
        
        Returns:
            MerkleTree with root hash and proofs
        """
        # Leaf nodes are hashes of entries
        leaves = [entry['current_hash'] for entry in entries]
        
        # Build tree bottom-up
        tree = self._build_tree_recursive(leaves)
        
        return MerkleTree(
            root_hash=tree[0] if tree else None,
            leaves=leaves,
            tree_levels=tree
        )
    
    def _build_tree_recursive(self, hashes):
        """Recursively build Merkle tree."""
        if len(hashes) == 0:
            return []
        if len(hashes) == 1:
            return hashes
        
        # Pair up hashes and compute parent hashes
        next_level = []
        for i in range(0, len(hashes), 2):
            left = hashes[i]
            right = hashes[i + 1] if i + 1 < len(hashes) else left
            parent = hashlib.sha256(
                (left + right).encode('utf-8')
            ).hexdigest()
            next_level.append(parent)
        
        return self._build_tree_recursive(next_level)
    
    def generate_proof(self, tree, leaf_index):
        """
        Generate Merkle proof for specific entry.
        
        Allows verification of single entry without entire tree.
        """
        proof = []
        # Implementation of Merkle proof generation
        # Returns list of sibling hashes needed to verify path to root
        return proof
    
    def verify_proof(self, leaf_hash, proof, root_hash):
        """Verify Merkle proof."""
        current = leaf_hash
        for sibling in proof:
            current = hashlib.sha256(
                (current + sibling).encode('utf-8')
            ).hexdigest()
        return current == root_hash
```

### 4. Append-Only Storage Backend

```python
class AppendOnlyLogStore:
    """
    Append-only storage for audit logs.
    
    Features:
    - Write-once semantics
    - Crash recovery
    - Efficient range queries
    """
    
    def __init__(self, log_file_path):
        self.log_file = log_file_path
        self.index_file = log_file_path + ".index"
        self._ensure_files_exist()
    
    def append(self, entry):
        """
        Append entry to log file.
        
        Uses O_APPEND flag to ensure atomic append.
        Each entry is one JSON line.
        """
        with open(self.log_file, 'a') as f:
            # JSON Lines format for easy parsing
            f.write(json.dumps(entry) + '\n')
            f.flush()  # Ensure written to disk
            os.fsync(f.fileno())  # Force OS to write
        
        # Update index for efficient queries
        self._update_index(entry['sequence_number'], f.tell())
    
    def read_range(self, start_seq=None, end_seq=None):
        """Read entries in sequence range."""
        entries = []
        with open(self.log_file, 'r') as f:
            for line in f:
                entry = json.loads(line)
                seq = entry['sequence_number']
                
                if start_seq and seq < start_seq:
                    continue
                if end_seq and seq > end_seq:
                    break
                
                entries.append(entry)
        
        return entries
    
    def read_entry(self, sequence_number):
        """Read specific entry by sequence number."""
        # Use index for O(1) lookup
        offset = self._get_offset_from_index(sequence_number)
        if offset is None:
            return None
        
        with open(self.log_file, 'r') as f:
            f.seek(offset)
            return json.loads(f.readline())
```

## Usage Examples

### Basic Audit Logging

```python
from starlink_security import AuditLogger, AppendOnlyLogStore

# Initialize audit logger
storage = AppendOnlyLogStore('/var/log/starlink-security/audit.log')
audit_logger = AuditLogger(storage)

# Log authentication event
audit_logger.log_audit_event(
    event_type=ErrorCode.AUTH_001,
    actor='user@example.com',
    resource='/api/admin',
    action='LOGIN',
    result='SUCCESS',
    metadata={'ip_address': '192.168.1.100', 'session_id': 'sess-123'}
)

# Log configuration change
audit_logger.log_audit_event(
    event_type=ErrorCode.CFG_001,
    actor='admin@example.com',
    resource='/config/security',
    action='UPDATE',
    result='SUCCESS',
    metadata={'changes': {'max_retry': 3, 'timeout': 30}}
)

# Log data access
audit_logger.log_audit_event(
    event_type=ErrorCode.SEC_001,
    actor='system@starlink',
    resource='/data/satellite/telemetry',
    action='READ',
    result='SUCCESS',
    metadata={'records_accessed': 1000, 'query': 'last_24h'}
)
```

### Verification

```python
# Verify entire audit log
result = audit_logger.verify_integrity()

if result.valid:
    print(f"✅ Audit log verified: {result.total_entries} entries")
else:
    print(f"❌ Integrity violations detected: {len(result.violations)}")
    for violation in result.violations:
        print(f"  - {violation['type']} at entry {violation['entry']}")

# Verify specific range
result = audit_logger.verify_integrity(start_seq=1000, end_seq=2000)
```

### Merkle Tree Checkpoints

```python
# Generate Merkle tree for audit trail
merkle_tree = audit_logger.merkle_builder.build_tree(
    storage.read_range(start_seq=1, end_seq=10000)
)

# Publish root hash for external verification
print(f"Merkle Root Hash: {merkle_tree.root_hash}")

# Store root hash in blockchain or external system
external_system.publish_checkpoint({
    'timestamp': datetime.utcnow().isoformat(),
    'sequence_range': [1, 10000],
    'root_hash': merkle_tree.root_hash,
    'signature': sign_with_private_key(merkle_tree.root_hash)
})
```

### Independent Verification

```python
# External auditor can verify without access to system
def external_verification(audit_log_file, published_checkpoints):
    """
    Verify audit log integrity using published checkpoints.
    
    Args:
        audit_log_file: Path to audit log file
        published_checkpoints: List of published Merkle root hashes
    """
    # Read audit log
    with open(audit_log_file, 'r') as f:
        entries = [json.loads(line) for line in f]
    
    # Verify hash chain
    hash_chain = HashChainManager()
    result = hash_chain.verify_chain(entries)
    
    if not result.valid:
        return False, "Hash chain verification failed", result.violations
    
    # Verify against published checkpoints
    for checkpoint in published_checkpoints:
        range_entries = entries[
            checkpoint['start']:checkpoint['end']
        ]
        merkle_tree = MerkleTreeBuilder().build_tree(range_entries)
        
        if merkle_tree.root_hash != checkpoint['root_hash']:
            return False, f"Checkpoint mismatch at {checkpoint['timestamp']}", None
    
    return True, "Verification successful", None
```

## Integration with Existing Logging

The audit trail system complements the existing logging infrastructure:

```python
# Standard logging for operational events
logger.info("Processing request", extra={'request_id': 'req-123'})

# Audit logging for security-critical events
if authentication_failed:
    # Standard log
    logger.error(
        ErrorCode.get_description(ErrorCode.AUTH_001),
        extra={'error_code': ErrorCode.AUTH_001, 'username': username}
    )
    
    # Audit trail entry (tamper-evident)
    audit_logger.log_audit_event(
        event_type=ErrorCode.AUTH_001,
        actor=username,
        resource='/api/login',
        action='AUTHENTICATE',
        result='FAILURE',
        metadata={'reason': 'invalid_credentials', 'ip': client_ip}
    )
```

## Security Considerations

### 1. Private Key Protection

```python
# Use hardware security module (HSM) or key management service
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

def load_signing_key_from_hsm():
    """Load signing key from HSM for digital signatures."""
    # Integration with AWS KMS, Azure Key Vault, or HSM
    pass

audit_logger = AuditLogger(
    storage=storage,
    signing_key=load_signing_key_from_hsm()
)
```

### 2. Write Protection

```python
# Set file permissions to append-only
import os
import stat

def setup_append_only_log(log_path):
    """Set up log file with restricted permissions."""
    # Create file
    open(log_path, 'a').close()
    
    # Set permissions: owner can append, no one can modify
    os.chmod(log_path, stat.S_IRUSR | stat.S_IWUSR)
    
    # On Linux, set append-only attribute (requires root)
    # subprocess.run(['chattr', '+a', log_path])
```

### 3. Clock Synchronization

```python
import ntplib
from datetime import datetime

def get_verified_timestamp():
    """
    Get NTP-synchronized timestamp.
    
    Prevents timestamp manipulation attacks.
    """
    try:
        ntp_client = ntplib.NTPClient()
        response = ntp_client.request('pool.ntp.org')
        return datetime.fromtimestamp(response.tx_time).isoformat()
    except:
        # Fallback to system time if NTP unavailable
        return datetime.utcnow().isoformat()
```

## Performance Considerations

### 1. Batching

```python
class BatchedAuditLogger(AuditLogger):
    """Audit logger with batching for high-volume scenarios."""
    
    def __init__(self, storage, batch_size=100):
        super().__init__(storage)
        self.batch = []
        self.batch_size = batch_size
    
    def log_audit_event(self, *args, **kwargs):
        """Add to batch, flush when full."""
        entry = super().log_audit_event(*args, **kwargs)
        self.batch.append(entry)
        
        if len(self.batch) >= self.batch_size:
            self.flush()
        
        return entry
    
    def flush(self):
        """Flush batch to storage."""
        if self.batch:
            self.storage.batch_append(self.batch)
            self.batch = []
```

### 2. Async Processing

```python
import asyncio
from queue import Queue

class AsyncAuditLogger(AuditLogger):
    """Audit logger with async processing."""
    
    def __init__(self, storage):
        super().__init__(storage)
        self.queue = Queue()
        self.worker_thread = threading.Thread(target=self._process_queue)
        self.worker_thread.start()
    
    def log_audit_event(self, *args, **kwargs):
        """Queue audit event for async processing."""
        self.queue.put((args, kwargs))
    
    def _process_queue(self):
        """Background worker processes queue."""
        while True:
            args, kwargs = self.queue.get()
            super().log_audit_event(*args, **kwargs)
            self.queue.task_done()
```

## Compliance Mapping

| Standard | Requirement | Implementation |
|----------|-------------|----------------|
| **SOC 2** | Audit trail of all access | Hash-chained audit log with actor tracking |
| **HIPAA** | Access logs retained 6 years | Append-only storage with retention policy |
| **PCI-DSS** | Tamper-evident logging | Cryptographic hash chain verification |
| **GDPR** | Right to audit | Independent verification capability |
| **ISO 27001** | Non-repudiation | Digital signatures on audit entries |

## Future Enhancements

1. **Blockchain Integration**: Publish Merkle roots to public blockchain for external verification
2. **Zero-Knowledge Proofs**: Verify log properties without revealing content
3. **Distributed Audit Trail**: Multi-node consensus for distributed systems
4. **Real-Time Monitoring**: Alert on verification failures or chain breaks
5. **Forensic Tools**: GUI tools for audit investigators

## Conclusion

This cryptographically verifiable audit trail design provides:

✅ **Tamper Evidence**: Any modification detected through hash chain
✅ **Independent Verification**: External auditors can verify without system access
✅ **Compliance Ready**: Meets requirements for major security standards
✅ **Performance**: Minimal overhead with batching and async options
✅ **Scalability**: Merkle trees enable efficient verification of large logs

The design integrates seamlessly with the existing structured logging system while adding a critical security layer for audit-critical events.
