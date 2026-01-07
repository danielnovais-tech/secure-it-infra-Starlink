# Secure IT Infrastructure - Starlink

Repository dedicated to security solutions for managed enterprise infrastructures supporting Starlink.

## Overview

This repository contains the foundational Terraform configuration for deploying and managing secure enterprise infrastructure for Starlink connectivity. It provides a comprehensive, production-ready setup with best practices for AWS infrastructure management.

## Features

- **Multi-Provider Setup**: Comprehensive provider configuration including AWS, Random, Null, Time, and TLS
- **Multi-Region Support**: Primary and secondary region configuration for disaster recovery
- **Remote State Management**: S3 backend with DynamoDB state locking
- **Default Tagging**: Automatic resource tagging for cost allocation and compliance
- **Environment Separation**: Support for dev, staging, and production environments
- **Security Best Practices**: Encrypted state, least privilege, and secure defaults

## Prerequisites

- [Terraform](https://www.terraform.io/downloads.html) >= 1.5.0
- AWS CLI configured with appropriate credentials
- An AWS account with necessary permissions

## Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/danielnovais-tech/secure-it-infra-Starlink.git
   cd secure-it-infra-Starlink
   ```

2. **Configure variables**
   ```bash
   cp terraform.tfvars.example terraform.tfvars
   # Edit terraform.tfvars with your specific values
   ```

3. **Initialize Terraform**
   ```bash
   terraform init
   ```

4. **Review the plan**
   ```bash
   terraform plan
   ```

5. **Apply the configuration**
   ```bash
   terraform apply
   ```

## Project Structure

```
.
├── backend.tf              # Remote state backend configuration
├── main.tf                 # Main infrastructure resources and data sources
├── outputs.tf              # Output values for the infrastructure
├── providers.tf            # Provider configurations
├── variables.tf            # Input variable definitions
├── versions.tf             # Terraform and provider version constraints
├── terraform.tfvars.example # Example variable values
└── README.md              # This file
```

## Configuration

### Required Variables

- `environment`: Environment name (dev, staging, or production)

### Optional Variables

- `aws_region`: AWS region for deployment (default: us-west-2)
- `owner`: Team or individual responsible for the infrastructure
- `cost_center`: Cost center for billing and tracking
- `enable_cross_region`: Enable cross-region configuration
- `enable_backup`: Enable AWS Backup for resources
- `enable_monitoring`: Enable enhanced monitoring

See [variables.tf](variables.tf) for all available configuration options.

## Remote State Setup

To enable remote state management with S3 and DynamoDB:

1. Follow the instructions in [backend.tf](backend.tf) to create the required AWS resources
2. Uncomment the backend configuration block
3. Run `terraform init -migrate-state`

## Provider Configuration

This project configures the following Terraform providers:

- **AWS Provider** (v5.x): Primary cloud infrastructure provider
  - Primary region provider for main resources
  - Secondary us-east-1 provider for CloudFront and global services
- **Random Provider** (v3.6.x): For generating unique identifiers
- **Null Provider** (v3.2.x): For provisioners and local execution
- **Time Provider** (v0.11.x): For time-based resources
- **TLS Provider** (v4.0.x): For certificate generation

## Default Tags

All AWS resources are automatically tagged with:

- `Project`: secure-it-infra-Starlink
- `ManagedBy`: Terraform
- `Environment`: Selected environment (dev/staging/production)
- `Owner`: Team or individual owner
- `CostCenter`: Cost center for billing

Additional custom tags can be added via the `additional_tags` variable.

## Security Considerations

- Store sensitive variables in AWS Secrets Manager or environment variables
- Use IAM roles with least privilege principles
- Enable MFA for AWS accounts
- Regularly rotate access credentials
- Enable AWS CloudTrail for audit logging
- Use encrypted S3 buckets for state storage
- Implement state locking to prevent concurrent modifications

## Contributing

1. Create a feature branch
2. Make your changes
3. Run `terraform fmt` to format code
4. Run `terraform validate` to validate configuration
5. Submit a pull request

## License

See [LICENSE](LICENSE) for details.

## Support

For issues and questions, please open an issue in the GitHub repository.
