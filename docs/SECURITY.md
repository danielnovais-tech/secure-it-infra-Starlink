# Security Configuration Guide

## ⚠️ IMPORTANT SECURITY NOTICE

The default configurations in this repository are designed for **development and testing only**. They contain default credentials and security settings that are **NOT suitable for production use**.

Before deploying to production, you **MUST** configure proper security measures as outlined in this guide.

## Critical Security Items

### 1. Database Passwords

**Current Issue**: PostgreSQL passwords are hardcoded in configuration files.

**Solution for Production**:

#### Kubernetes

Use Kubernetes Secrets with randomly generated passwords:

```bash
# Generate a secure random password
POSTGRES_PASSWORD=$(openssl rand -base64 32)

# Create secret
kubectl create secret generic armada-postgres-secret \
  --from-literal=password="$POSTGRES_PASSWORD" \
  -n armada

# Reference in ConfigMaps using environment variable substitution
```

Update `armada-server-config.yaml`:

```yaml
postgres:
  connection:
    host: postgres
    port: 5432
    user: armada
    password: ${POSTGRES_PASSWORD}  # Will be injected from secret
    dbname: armada
    sslmode: require  # Enable SSL in production
```

#### Docker Compose

Use Docker secrets or environment variables:

```yaml
services:
  postgres:
    environment:
      POSTGRES_PASSWORD_FILE: /run/secrets/postgres_password
    secrets:
      - postgres_password

secrets:
  postgres_password:
    file: ./secrets/postgres_password.txt
```

### 2. Authentication and Authorization

**Current Issue**: Anonymous authentication is enabled in Armada.

**Solution for Production**:

#### Armada Server

Disable anonymous auth and enable OIDC:

```yaml
# armada-server-config.yaml
auth:
  anonymousAuth: false
  
  # OpenID Connect configuration
  oidc:
    providerUrl: "https://your-oidc-provider.com"
    clientId: "armada-client"
    clientSecret: "${OIDC_CLIENT_SECRET}"  # From secret
    scopes: ["openid", "profile", "email", "groups"]
    groupsClaim: "groups"
  
  # Define admin roles
  superUserRoles:
    - "admin"
    - "platform-team"
```

#### Pulsar Broker

Enable token-based authentication:

```yaml
# broker.conf
authenticationEnabled=true
authenticationProviders=org.apache.pulsar.broker.authentication.AuthenticationProviderToken

# Authorization
authorizationEnabled=true
superUserRoles=admin,service-accounts

# Token settings
tokenSecretKey=file:///path/to/secret.key
# or
tokenPublicKey=file:///path/to/public.key
```

Generate tokens:

```bash
# Generate secret key
bin/pulsar tokens create-secret-key --output /path/to/secret.key

# Create token for a role
bin/pulsar tokens create \
  --secret-key file:///path/to/secret.key \
  --subject armada-service
```

### 3. TLS/SSL Encryption

**Current Issue**: TLS is not enabled in default configurations.

**Solution for Production**:

#### Pulsar TLS Configuration

```yaml
# broker.conf
tlsEnabled=true
tlsCertificateFilePath=/path/to/broker-cert.pem
tlsKeyFilePath=/path/to/broker-key.pem
tlsTrustCertsFilePath=/path/to/ca-cert.pem

# Enforce TLS
brokerServicePortTls=6651
webServicePortTls=8443
tlsRequireTrustedClientCertOnConnect=false
```

#### Armada Server TLS

```yaml
# armada-server-config.yaml
tls:
  enabled: true
  certFile: /path/to/server-cert.pem
  keyFile: /path/to/server-key.pem
  caFile: /path/to/ca-cert.pem

pulsar:
  tlsEnabled: true
  tlsTrustCertsFilePath: /path/to/pulsar-ca-cert.pem
```

#### Generate Self-Signed Certificates (Development)

```bash
# CA certificate
openssl req -x509 -newkey rsa:4096 -sha256 -days 3650 -nodes \
  -keyout ca-key.pem -out ca-cert.pem -subj "/CN=My CA"

# Server certificate
openssl req -newkey rsa:4096 -nodes \
  -keyout server-key.pem -out server-req.pem -subj "/CN=server"

openssl x509 -req -in server-req.pem -CA ca-cert.pem -CAkey ca-key.pem \
  -CAcreateserial -out server-cert.pem -days 365 -sha256
```

For production, use certificates from a trusted CA (Let's Encrypt, etc.).

### 4. Network Security

#### Kubernetes Network Policies

Restrict network access between components:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: armada-server-policy
  namespace: armada
spec:
  podSelector:
    matchLabels:
      component: server
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          component: executor
    - podSelector:
        matchLabels:
          component: lookout
    ports:
    - protocol: TCP
      port: 50051
  egress:
  - to:
    - namespaceSelector:
        matchLabels:
          name: pulsar
    ports:
    - protocol: TCP
      port: 6650
  - to:
    - podSelector:
        matchLabels:
          component: postgres
    ports:
    - protocol: TCP
      port: 5432
```

### 5. Secret Management

Use a dedicated secrets management solution:

#### HashiCorp Vault

```bash
# Store secrets in Vault
vault kv put secret/armada/postgres password="$SECURE_PASSWORD"

# Use Vault injector in Kubernetes
apiVersion: v1
kind: Pod
metadata:
  annotations:
    vault.hashicorp.com/agent-inject: "true"
    vault.hashicorp.com/role: "armada"
    vault.hashicorp.com/agent-inject-secret-postgres: "secret/armada/postgres"
```

#### AWS Secrets Manager

```yaml
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: armada-postgres-secret
spec:
  secretStoreRef:
    name: aws-secrets-manager
  target:
    name: armada-postgres-secret
  data:
  - secretKey: password
    remoteRef:
      key: prod/armada/postgres
      property: password
```

### 6. Resource Limits and Quotas

Prevent resource exhaustion attacks:

```yaml
# Kubernetes ResourceQuota
apiVersion: v1
kind: ResourceQuota
metadata:
  name: armada-quota
  namespace: armada
spec:
  hard:
    requests.cpu: "100"
    requests.memory: 200Gi
    persistentvolumeclaims: "10"

# LimitRange for pods
apiVersion: v1
kind: LimitRange
metadata:
  name: armada-limits
  namespace: armada
spec:
  limits:
  - max:
      cpu: "4"
      memory: 8Gi
    min:
      cpu: "100m"
      memory: 128Mi
    type: Container
```

### 7. Audit Logging

Enable audit logging for compliance:

#### Pulsar Audit Logging

```yaml
# broker.conf
# Log all admin operations
brokerClientAuthenticationPlugin=org.apache.pulsar.client.impl.auth.AuthenticationToken
brokerClientAuthenticationParameters=token:${ADMIN_TOKEN}

# Custom audit handler
transactionLogConfig=file:///path/to/audit-log-config.yaml
```

#### Armada Audit Logging

```yaml
# armada-server-config.yaml
logging:
  level: "info"
  format: "json"
  
audit:
  enabled: true
  logFile: "/var/log/armada/audit.log"
  
  # Events to log
  events:
    - "JobSubmitted"
    - "JobCancelled"
    - "QueueCreated"
    - "QueueDeleted"
    - "PermissionGranted"
    - "PermissionRevoked"
```

### 8. Image Security

Use verified, minimal images:

```yaml
# Use specific versions, not 'latest'
image: apachepulsar/pulsar:3.2.0  # Not :latest

# Consider using distroless or minimal base images
image: gcr.io/distroless/java17-debian11

# Scan images for vulnerabilities
# Use tools like Trivy, Clair, or Snyk
```

### 9. Database Security

#### PostgreSQL Security Hardening

```yaml
# postgresql.conf
ssl = on
ssl_cert_file = '/path/to/server.crt'
ssl_key_file = '/path/to/server.key'
ssl_ca_file = '/path/to/root.crt'

# Require encrypted connections
hostssl all all 0.0.0.0/0 cert clientcert=verify-full

# Limit connections
max_connections = 100

# Enable logging
log_connections = on
log_disconnections = on
log_statement = 'all'
```

#### Redis Security

```yaml
# redis.conf
requirepass ${REDIS_PASSWORD}
rename-command FLUSHDB ""
rename-command FLUSHALL ""
rename-command CONFIG ""

# Enable TLS
tls-port 6380
port 0
tls-cert-file /path/to/redis.crt
tls-key-file /path/to/redis.key
tls-ca-cert-file /path/to/ca.crt
```

### 10. Monitoring and Alerting

Set up security monitoring:

```yaml
# Prometheus alerts
groups:
  - name: security
    rules:
      - alert: UnauthorizedAccess
        expr: rate(armada_auth_failures[5m]) > 10
        annotations:
          summary: "High rate of authentication failures"
      
      - alert: SuspiciousActivity
        expr: rate(pulsar_admin_operations[5m]) > 100
        annotations:
          summary: "Unusual admin activity detected"
```

## Production Deployment Checklist

Before deploying to production, verify:

- [ ] All default passwords have been changed
- [ ] Anonymous authentication is disabled
- [ ] TLS/SSL is enabled for all connections
- [ ] Authentication and authorization are configured
- [ ] Network policies are in place
- [ ] Secrets are managed securely (Vault, Secrets Manager, etc.)
- [ ] Resource limits and quotas are configured
- [ ] Audit logging is enabled
- [ ] Container images are scanned for vulnerabilities
- [ ] Database connections use SSL/TLS
- [ ] Monitoring and alerting are configured
- [ ] Regular backups are scheduled
- [ ] Incident response procedures are documented
- [ ] Security patches are applied regularly
- [ ] Access is restricted to authorized personnel only

## Security Best Practices

1. **Principle of Least Privilege**: Grant minimum necessary permissions
2. **Defense in Depth**: Use multiple layers of security controls
3. **Regular Updates**: Keep all components patched and updated
4. **Security Scanning**: Regularly scan for vulnerabilities
5. **Access Auditing**: Log and review all access attempts
6. **Encryption**: Encrypt data at rest and in transit
7. **Secret Rotation**: Regularly rotate credentials and tokens
8. **Incident Response**: Have a plan for security incidents
9. **Regular Reviews**: Conduct periodic security assessments
10. **Training**: Ensure team members understand security requirements

## Security Resources

- [Pulsar Security Documentation](https://pulsar.apache.org/docs/next/security-overview/)
- [Kubernetes Security Best Practices](https://kubernetes.io/docs/concepts/security/)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [CIS Kubernetes Benchmark](https://www.cisecurity.org/benchmark/kubernetes)
- [PostgreSQL Security](https://www.postgresql.org/docs/current/security.html)

## Reporting Security Issues

If you discover a security vulnerability:

1. **DO NOT** create a public GitHub issue
2. Email security concerns to: security@your-domain.com
3. Include detailed information about the vulnerability
4. Allow reasonable time for a fix before public disclosure

## Compliance

Consider these compliance frameworks based on your requirements:

- **SOC 2**: System and Organization Controls
- **ISO 27001**: Information Security Management
- **GDPR**: General Data Protection Regulation (EU)
- **HIPAA**: Health Insurance Portability and Accountability Act (US)
- **PCI DSS**: Payment Card Industry Data Security Standard

Consult with security and compliance teams to ensure requirements are met.
