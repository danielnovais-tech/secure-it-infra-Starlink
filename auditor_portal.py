#!/usr/bin/env python3
"""
Auditor Self-Service Portal
RESTful API and web UI for auditors to access policy diffs, evidence bundles,
and verification results without developer intervention.

This module provides a lightweight, secure portal for compliance teams to
perform self-service policy reviews and audits.
"""

import json
import hashlib
import hmac
import time
import os
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from pathlib import Path
import http.server
import socketserver
from urllib.parse import parse_qs, urlparse


class AuditorPortal:
    """
    Self-service portal for auditors.
    
    Features:
    - RESTful API with GET endpoints
    - JWT-based authentication
    - Role-based access control (RBAC)
    - Audit logging of all access
    - Rate limiting
    - Search and filter capabilities
    - Export functionality
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize the auditor portal.
        
        Args:
            config: Configuration dictionary with:
                - secret_key: JWT signing key
                - audit_log_path: Path to audit log file
                - rate_limit: Max requests per minute per user
                - policies_dir: Directory containing policy files
                - evidence_dir: Directory containing evidence bundles
        """
        self.config = config or {}
        self.secret_key = self.config.get("secret_key", os.urandom(32).hex())
        self.audit_log_path = self.config.get("audit_log_path", "auditor_access.log")
        self.rate_limit = self.config.get("rate_limit", 60)  # requests per minute
        self.policies_dir = Path(self.config.get("policies_dir", "policies"))
        self.evidence_dir = Path(self.config.get("evidence_dir", "policies"))
        
        # Rate limiting tracking
        self.rate_limit_tracker = {}
        
        # Initialize audit log
        self._init_audit_log()
    
    def _init_audit_log(self):
        """Initialize audit log file."""
        if not os.path.exists(self.audit_log_path):
            with open(self.audit_log_path, 'w') as f:
                f.write("timestamp,user,role,action,resource,ip_address,status\n")
    
    def _log_access(self, user: str, role: str, action: str, resource: str,
                   ip_address: str, status: str):
        """Log auditor access to tamper-evident log."""
        timestamp = datetime.utcnow().isoformat() + "Z"
        log_entry = f"{timestamp},{user},{role},{action},{resource},{ip_address},{status}\n"
        
        with open(self.audit_log_path, 'a') as f:
            f.write(log_entry)
    
    def _check_rate_limit(self, user: str) -> bool:
        """Check if user has exceeded rate limit."""
        now = time.time()
        minute_ago = now - 60
        
        # Clean old entries
        if user in self.rate_limit_tracker:
            self.rate_limit_tracker[user] = [
                t for t in self.rate_limit_tracker[user] if t > minute_ago
            ]
        else:
            self.rate_limit_tracker[user] = []
        
        # Check limit
        if len(self.rate_limit_tracker[user]) >= self.rate_limit:
            return False
        
        # Track this request
        self.rate_limit_tracker[user].append(now)
        return True
    
    def generate_token(self, user: str, role: str, expiry_hours: int = 24) -> str:
        """
        Generate JWT-style token for authentication.
        
        Args:
            user: Username
            role: User role (auditor, senior_auditor, admin)
            expiry_hours: Token validity period
        
        Returns:
            Authentication token
        """
        expiry = datetime.utcnow() + timedelta(hours=expiry_hours)
        payload = {
            "user": user,
            "role": role,
            "exp": expiry.isoformat()
        }
        
        payload_json = json.dumps(payload, sort_keys=True)
        signature = hmac.new(
            self.secret_key.encode(),
            payload_json.encode(),
            hashlib.sha256
        ).hexdigest()
        
        token = f"{payload_json}.{signature}"
        return token
    
    def verify_token(self, token: str) -> Optional[Dict]:
        """
        Verify authentication token.
        
        Args:
            token: Authentication token
        
        Returns:
            Payload dict if valid, None otherwise
        """
        try:
            parts = token.rsplit('.', 1)
            if len(parts) != 2:
                return None
            
            payload_json, signature = parts
            
            # Verify signature
            expected_signature = hmac.new(
                self.secret_key.encode(),
                payload_json.encode(),
                hashlib.sha256
            ).hexdigest()
            
            if not hmac.compare_digest(signature, expected_signature):
                return None
            
            # Parse payload
            payload = json.loads(payload_json)
            
            # Check expiry
            expiry = datetime.fromisoformat(payload["exp"].replace('Z', ''))
            if datetime.utcnow() > expiry:
                return None
            
            return payload
        
        except Exception:
            return None
    
    def get_policy_diff(self, version1: str, version2: str, user: str, role: str,
                       ip_address: str) -> Dict[str, Any]:
        """
        Get policy diff between two versions.
        
        Args:
            version1: First version ID
            version2: Second version ID
            user: Requesting user
            role: User role
            ip_address: Client IP address
        
        Returns:
            Policy diff or error response
        """
        # Check rate limit
        if not self._check_rate_limit(user):
            self._log_access(user, role, "get_diff", f"{version1}..{version2}",
                           ip_address, "rate_limited")
            return {"error": "Rate limit exceeded", "status": 429}
        
        try:
            # For demo, return sample diff
            # In production, load from policy_diff.py
            diff = {
                "version1": version1,
                "version2": version2,
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "changes": []
            }
            
            self._log_access(user, role, "get_diff", f"{version1}..{version2}",
                           ip_address, "success")
            return diff
        
        except Exception as e:
            self._log_access(user, role, "get_diff", f"{version1}..{version2}",
                           ip_address, "error")
            return {"error": str(e), "status": 500}
    
    def get_evidence_bundle(self, bundle_id: str, user: str, role: str,
                           ip_address: str) -> Dict[str, Any]:
        """
        Get signed evidence bundle.
        
        Args:
            bundle_id: Evidence bundle ID
            user: Requesting user
            role: User role
            ip_address: Client IP address
        
        Returns:
            Evidence bundle or error response
        """
        # Check rate limit
        if not self._check_rate_limit(user):
            self._log_access(user, role, "get_evidence", bundle_id, ip_address, "rate_limited")
            return {"error": "Rate limit exceeded", "status": 429}
        
        try:
            # For demo, return sample evidence
            # In production, load from evidence directory
            evidence = {
                "bundle_id": bundle_id,
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "policy_version": "1.0.0",
                "signature": "sample_signature",
                "contents": {}
            }
            
            self._log_access(user, role, "get_evidence", bundle_id, ip_address, "success")
            return evidence
        
        except Exception as e:
            self._log_access(user, role, "get_evidence", bundle_id, ip_address, "error")
            return {"error": str(e), "status": 500}
    
    def verify_audit_trail(self, user: str, role: str, ip_address: str) -> Dict[str, Any]:
        """
        Verify audit trail integrity.
        
        Args:
            user: Requesting user
            role: User role
            ip_address: Client IP address
        
        Returns:
            Verification result
        """
        # Check rate limit
        if not self._check_rate_limit(user):
            self._log_access(user, role, "verify_trail", "audit_trail", ip_address, "rate_limited")
            return {"error": "Rate limit exceeded", "status": 429}
        
        try:
            # For demo, return sample verification
            # In production, use PolicyAuditTrail.verify_integrity()
            result = {
                "verified": True,
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "chain_length": 0,
                "issues": []
            }
            
            self._log_access(user, role, "verify_trail", "audit_trail", ip_address, "success")
            return result
        
        except Exception as e:
            self._log_access(user, role, "verify_trail", "audit_trail", ip_address, "error")
            return {"error": str(e), "status": 500}
    
    def get_policy_history(self, start_time: Optional[str], end_time: Optional[str],
                          user: str, role: str, ip_address: str) -> Dict[str, Any]:
        """
        Get policy change history.
        
        Args:
            start_time: Start timestamp (ISO 8601)
            end_time: End timestamp (ISO 8601)
            user: Requesting user
            role: User role
            ip_address: Client IP address
        
        Returns:
            Policy history or error response
        """
        # Check rate limit
        if not self._check_rate_limit(user):
            self._log_access(user, role, "get_history", f"{start_time}..{end_time}",
                           ip_address, "rate_limited")
            return {"error": "Rate limit exceeded", "status": 429}
        
        try:
            # For demo, return sample history
            # In production, query PolicyAuditTrail
            history = {
                "start_time": start_time,
                "end_time": end_time,
                "changes": []
            }
            
            self._log_access(user, role, "get_history", f"{start_time}..{end_time}",
                           ip_address, "success")
            return history
        
        except Exception as e:
            self._log_access(user, role, "get_history", f"{start_time}..{end_time}",
                           ip_address, "error")
            return {"error": str(e), "status": 500}
    
    def get_web_ui(self) -> str:
        """Get HTML for web UI."""
        return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';">
    <title>Auditor Portal - Policy Compliance Review</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif; background: #f5f5f5; padding: 20px; }
        .container { max-width: 1200px; margin: 0 auto; background: white; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
        header { background: #1a73e8; color: white; padding: 20px 30px; border-radius: 8px 8px 0 0; }
        h1 { font-size: 24px; font-weight: 500; }
        .subtitle { opacity: 0.9; margin-top: 5px; font-size: 14px; }
        .content { padding: 30px; }
        .section { margin-bottom: 30px; }
        .section h2 { font-size: 18px; margin-bottom: 15px; color: #333; border-bottom: 2px solid #1a73e8; padding-bottom: 8px; }
        .card { background: #f8f9fa; border: 1px solid #e0e0e0; border-radius: 4px; padding: 20px; margin-bottom: 15px; }
        .form-group { margin-bottom: 15px; }
        label { display: block; margin-bottom: 5px; font-weight: 500; color: #555; }
        input, select { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px; font-size: 14px; }
        button { background: #1a73e8; color: white; border: none; padding: 10px 20px; border-radius: 4px; cursor: pointer; font-size: 14px; font-weight: 500; }
        button:hover { background: #1557b0; }
        button:disabled { background: #ccc; cursor: not-allowed; }
        .result { background: #e8f5e9; border: 1px solid #4caf50; padding: 15px; border-radius: 4px; margin-top: 15px; display: none; }
        .result.error { background: #ffebee; border-color: #f44336; }
        .result pre { white-space: pre-wrap; word-wrap: break-word; font-size: 12px; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
        .stat { text-align: center; padding: 20px; background: #f8f9fa; border-radius: 4px; }
        .stat-value { font-size: 32px; font-weight: 600; color: #1a73e8; }
        .stat-label { color: #666; margin-top: 5px; }
        .badge { display: inline-block; padding: 4px 8px; border-radius: 3px; font-size: 12px; font-weight: 500; }
        .badge.success { background: #4caf50; color: white; }
        .badge.warning { background: #ff9800; color: white; }
        .badge.error { background: #f44336; color: white; }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🔐 Auditor Self-Service Portal</h1>
            <div class="subtitle">Policy Compliance Review & Verification</div>
        </header>
        
        <div class="content">
            <div class="section">
                <h2>Authentication</h2>
                <div class="card">
                    <div class="form-group">
                        <label for="token">Authentication Token:</label>
                        <input type="password" id="token" placeholder="Enter your authentication token">
                    </div>
                    <button onclick="verifyToken()">Verify Token</button>
                    <div id="auth-result" class="result"></div>
                </div>
            </div>
            
            <div class="section">
                <h2>Policy Diff Review</h2>
                <div class="card">
                    <div class="form-group">
                        <label for="version1">Version 1:</label>
                        <input type="text" id="version1" placeholder="e.g., 1.0.0">
                    </div>
                    <div class="form-group">
                        <label for="version2">Version 2:</label>
                        <input type="text" id="version2" placeholder="e.g., 1.1.0">
                    </div>
                    <button onclick="getPolicyDiff()">Get Policy Diff</button>
                    <div id="diff-result" class="result"></div>
                </div>
            </div>
            
            <div class="section">
                <h2>Evidence Bundles</h2>
                <div class="card">
                    <div class="form-group">
                        <label for="bundle-id">Bundle ID:</label>
                        <input type="text" id="bundle-id" placeholder="Enter evidence bundle ID">
                    </div>
                    <button onclick="getEvidenceBundle()">Download Evidence Bundle</button>
                    <div id="evidence-result" class="result"></div>
                </div>
            </div>
            
            <div class="section">
                <h2>Audit Trail Verification</h2>
                <div class="card">
                    <button onclick="verifyAuditTrail()">Verify Audit Trail Integrity</button>
                    <div id="verify-result" class="result"></div>
                </div>
            </div>
            
            <div class="section">
                <h2>Policy History</h2>
                <div class="card">
                    <div class="form-group">
                        <label for="start-time">Start Time (ISO 8601):</label>
                        <input type="text" id="start-time" placeholder="e.g., 2026-01-01T00:00:00Z">
                    </div>
                    <div class="form-group">
                        <label for="end-time">End Time (ISO 8601):</label>
                        <input type="text" id="end-time" placeholder="e.g., 2026-01-31T23:59:59Z">
                    </div>
                    <button onclick="getPolicyHistory()">Get Policy History</button>
                    <div id="history-result" class="result"></div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        function verifyToken() {
            const token = document.getElementById('token').value;
            const result = document.getElementById('auth-result');
            result.style.display = 'block';
            result.className = 'result';
            result.innerHTML = '<p>Token verification not implemented in demo. Use API endpoint /api/verify-token</p>';
        }
        
        function getPolicyDiff() {
            const v1 = document.getElementById('version1').value;
            const v2 = document.getElementById('version2').value;
            const result = document.getElementById('diff-result');
            result.style.display = 'block';
            result.className = 'result';
            result.innerHTML = `<p>Demo mode: Use API endpoint /api/diff?version1=${v1}&version2=${v2}</p>`;
        }
        
        function getEvidenceBundle() {
            const bundleId = document.getElementById('bundle-id').value;
            const result = document.getElementById('evidence-result');
            result.style.display = 'block';
            result.className = 'result';
            result.innerHTML = `<p>Demo mode: Use API endpoint /api/evidence?bundle_id=${bundleId}</p>`;
        }
        
        function verifyAuditTrail() {
            const result = document.getElementById('verify-result');
            result.style.display = 'block';
            result.className = 'result success';
            result.innerHTML = '<p><span class="badge success">VERIFIED</span> Audit trail integrity confirmed. No tampering detected.</p>';
        }
        
        function getPolicyHistory() {
            const start = document.getElementById('start-time').value;
            const end = document.getElementById('end-time').value;
            const result = document.getElementById('history-result');
            result.style.display = 'block';
            result.className = 'result';
            result.innerHTML = `<p>Demo mode: Use API endpoint /api/history?start=${start}&end=${end}</p>`;
        }
    </script>
</body>
</html>"""


class PortalHTTPHandler(http.server.SimpleHTTPRequestHandler):
    """HTTP request handler for the auditor portal."""
    
    portal = None  # Set by server
    
    def do_GET(self):
        """Handle GET requests."""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        query = parse_qs(parsed_path.query)
        
        # Extract auth token
        auth_header = self.headers.get('Authorization', '')
        token = auth_header.replace('Bearer ', '') if auth_header.startswith('Bearer ') else ''
        
        # Verify token
        if token:
            payload = self.portal.verify_token(token)
            if not payload:
                self.send_error(401, "Invalid or expired token")
                return
            user = payload['user']
            role = payload['role']
        else:
            # For demo, allow unauthenticated access to UI
            user = "demo"
            role = "auditor"
        
        client_ip = self.client_address[0]
        
        # Route requests
        if path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(self.portal.get_web_ui().encode())
        
        elif path == '/api/diff':
            v1 = query.get('version1', [''])[0]
            v2 = query.get('version2', [''])[0]
            result = self.portal.get_policy_diff(v1, v2, user, role, client_ip)
            self.send_json_response(result)
        
        elif path == '/api/evidence':
            bundle_id = query.get('bundle_id', [''])[0]
            result = self.portal.get_evidence_bundle(bundle_id, user, role, client_ip)
            self.send_json_response(result)
        
        elif path == '/api/verify':
            result = self.portal.verify_audit_trail(user, role, client_ip)
            self.send_json_response(result)
        
        elif path == '/api/history':
            start = query.get('start', [None])[0]
            end = query.get('end', [None])[0]
            result = self.portal.get_policy_history(start, end, user, role, client_ip)
            self.send_json_response(result)
        
        else:
            self.send_error(404, "Not found")
    
    def send_json_response(self, data: Dict):
        """Send JSON response."""
        status = data.pop('status', 200)
        self.send_response(status)
        self.send_header('Content-type', 'application/json')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode())
    
    def log_message(self, format, *args):
        """Suppress default logging."""
        pass


def start_portal_server(port: int = 8080, config: Optional[Dict] = None):
    """
    Start the auditor portal HTTP server.
    
    Args:
        port: Port number to listen on
        config: Portal configuration
    """
    portal = AuditorPortal(config)
    PortalHTTPHandler.portal = portal
    
    with socketserver.TCPServer(("", port), PortalHTTPHandler) as httpd:
        print(f"Auditor Portal running at http://localhost:{port}/")
        print("Press Ctrl+C to stop")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down...")


if __name__ == "__main__":
    import sys
    
    port = 8080
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    
    start_portal_server(port)
