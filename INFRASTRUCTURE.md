# Secure IT Infrastructure for Starlink Connectivity

This repository provides infrastructure-as-code (IaC) for securing enterprise Starlink connectivity with comprehensive monitoring, threat detection, policy enforcement, incident response, VPN management, and backup/failover mechanisms.

## Features

### 🔍 Monitoring
- CloudWatch dashboards and metrics for real-time visibility
- Centralized logging with S3 and CloudWatch Logs
- VPC Flow Logs for network traffic analysis
- Automated alerts via SNS for critical events
- Custom metric filters for security events

### 🛡️ Threat Detection
- AWS GuardDuty for intelligent threat detection
- AWS Security Hub for centralized security findings
- WAF (Web Application Firewall) with managed rule sets
- Rate limiting and DDoS protection
- Automated threat alerts and notifications

### 📋 Policy Enforcement
- IAM password policies with strict requirements
- AWS Config for compliance monitoring
- Automated compliance checks (CIS, PCI-DSS)
- Security group enforcement
- Systems Manager patch management
- Encrypted storage requirements

### 🚨 Incident Response
- Automated incident response workflows
- Lambda-based threat remediation
- Step Functions for incident orchestration
- Resource isolation capabilities
- Real-time notification to response team
- Incident tracking and logging

### 🔐 VPN Management
- Site-to-Site VPN with Starlink connectivity
- Dual VPN tunnels for high availability
- IKEv2 with AES-256 encryption
- BGP routing for dynamic failover
- Transit Gateway for advanced routing
- VPN configuration stored in Secrets Manager
- Real-time VPN health monitoring

### 💾 Backup & Failover
- AWS Backup with automated schedules
- Multi-region backup replication
- Point-in-time recovery
- Route53 health checks
- Automated failover procedures
- Configuration backup to S3
- DynamoDB for state management

## Architecture

```
                    ┌─────────────────┐
                    │   Starlink      │
                    │   Terminal      │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │  Customer GW    │
                    │  (VPN Endpoint) │
                    └────────┬────────┘
                             │
              ┌──────────────┴──────────────┐
              │      AWS Site-to-Site VPN   │
              │    (Dual Tunnels - HA)      │
              └──────────────┬──────────────┘
                             │
                    ┌────────▼────────┐
                    │   VPC Gateway   │
                    │  Transit GW     │
                    └────────┬────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
   ┌────▼─────┐       ┌─────▼──────┐      ┌─────▼──────┐
   │ Public   │       │  Private   │      │  Private   │
   │ Subnets  │       │  Subnets   │      │  Subnets   │
   └──────────┘       └────────────┘      └────────────┘
        │                    │                    │
        │              ┌─────▼──────────────┐    │
        │              │   Monitoring       │    │
        │              │   - CloudWatch     │    │
        │              │   - GuardDuty      │    │
        │              │   - Security Hub   │    │
        │              └────────────────────┘    │
        │                                        │
        └────────────────┬───────────────────────┘
                         │
                ┌────────▼─────────┐
                │  Incident        │
                │  Response        │
                │  Automation      │
                └──────────────────┘
```

## Prerequisites

- Terraform >= 1.0
- AWS CLI configured with appropriate credentials
- Starlink terminal with static IP or DDNS
- AWS account with appropriate permissions

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/danielnovais-tech/secure-it-infra-Starlink.git
cd secure-it-infra-Starlink/terraform
```

### 2. Configure Variables

```bash
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with your configuration
```

Key variables to configure:
- `alert_email`: Email for monitoring alerts
- `incident_response_emails`: List of emails for incident response team
- `customer_gateway_ip`: Your Starlink terminal's public IP address

### 3. Initialize Terraform

```bash
terraform init
```

### 4. Review the Plan

```bash
terraform plan
```

### 5. Apply the Configuration

```bash
terraform apply
```

### 6. Configure Starlink Terminal

After deployment, retrieve VPN configuration:

```bash
terraform output vpn_endpoint
```

Configure your Starlink terminal or edge router with the VPN settings provided in the output.

## Module Descriptions

### Networking Module
Creates VPC, subnets, NAT gateways, and routing tables with high availability across multiple availability zones.

### Monitoring Module
Sets up CloudWatch dashboards, log groups, SNS topics, and metric alarms for comprehensive visibility.

### Threat Detection Module
Enables GuardDuty, Security Hub, and WAF to protect against threats and vulnerabilities.

### Policy Enforcement Module
Implements AWS Config rules, IAM policies, and compliance controls to ensure security standards.

### Incident Response Module
Provides automated response capabilities with Lambda functions and Step Functions workflows.

### VPN Management Module
Configures Site-to-Site VPN with dual tunnels, Transit Gateway, and health monitoring.

### Backup & Failover Module
Sets up AWS Backup plans, multi-region replication, and automated failover mechanisms.

## Security Considerations

1. **Encryption**: All data is encrypted at rest and in transit
2. **Least Privilege**: IAM roles follow principle of least privilege
3. **Network Isolation**: Private subnets for sensitive workloads
4. **Monitoring**: Comprehensive logging and alerting
5. **Compliance**: Meets CIS and PCI-DSS standards
6. **Incident Response**: Automated threat remediation
7. **Backup**: Multi-region backup for disaster recovery

## Cost Optimization

- Use AWS Cost Explorer to monitor spending
- Adjust log retention periods based on compliance requirements
- Review backup retention policies regularly
- Consider using AWS Savings Plans for predictable workloads

## Troubleshooting

### VPN Connection Issues
1. Verify customer gateway IP is correct
2. Check VPN tunnel status in CloudWatch dashboard
3. Review VPN logs in CloudWatch Logs
4. Ensure Starlink terminal firewall allows IPSec traffic

### Monitoring Alerts Not Received
1. Confirm SNS subscription in email
2. Check spam folder for SNS confirmation
3. Verify alert email in terraform.tfvars

### Backup Failures
1. Review AWS Backup console for errors
2. Ensure resources are tagged correctly (Backup=true)
3. Check IAM role permissions for AWS Backup

## Maintenance

### Regular Tasks
- Review security findings in Security Hub
- Update patch baselines monthly
- Test backup restore procedures quarterly
- Conduct incident response drills bi-annually
- Review and update Config rules as needed

### Updates
```bash
# Pull latest changes
git pull origin main

# Review changes
terraform plan

# Apply updates
terraform apply
```

## Support and Contributing

For issues or questions:
1. Check the troubleshooting section
2. Review AWS documentation for specific services
3. Open an issue in the repository

## License

This project is licensed under the Apache License 2.0 - see the LICENSE file for details.

## Acknowledgments

- Built for enterprise Starlink connectivity security
- Follows AWS Well-Architected Framework
- Implements security best practices from CIS and NIST

## References

- [AWS Site-to-Site VPN Documentation](https://docs.aws.amazon.com/vpn/)
- [AWS GuardDuty Best Practices](https://docs.aws.amazon.com/guardduty/)
- [AWS Backup Documentation](https://docs.aws.amazon.com/aws-backup/)
- [Starlink for Business](https://www.starlink.com/business)
