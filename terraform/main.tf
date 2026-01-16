# Main Terraform configuration for Starlink Enterprise Infrastructure Security
# This configuration integrates monitoring, threat detection, policy enforcement,
# incident response, VPN management, and backup/failover mechanisms

terraform {
  required_version = ">= 1.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "Starlink-Security"
      Environment = var.environment
      ManagedBy   = "Terraform"
    }
  }
}

# Secondary region provider for multi-region backup
provider "aws" {
  alias  = "secondary"
  region = var.secondary_region

  default_tags {
    tags = {
      Project     = "Starlink-Security"
      Environment = var.environment
      ManagedBy   = "Terraform"
      Region      = "Secondary"
    }
  }
}

# Monitoring Module
module "monitoring" {
  source = "./modules/monitoring"

  environment        = var.environment
  vpc_id             = module.networking.vpc_id
  private_subnet_ids = module.networking.private_subnet_ids
  alert_email        = var.alert_email
  retention_days     = var.log_retention_days
}

# Threat Detection Module
module "threat_detection" {
  source = "./modules/threat-detection"

  environment   = var.environment
  vpc_id        = module.networking.vpc_id
  alert_email   = var.alert_email
  log_bucket_id = module.monitoring.log_bucket_id
}

# Policy Enforcement Module
module "policy_enforcement" {
  source = "./modules/policy-enforcement"

  environment = var.environment
  vpc_id      = module.networking.vpc_id
}

# Incident Response Module
module "incident_response" {
  source = "./modules/incident-response"

  environment          = var.environment
  vpc_id               = module.networking.vpc_id
  alert_sns_topic_arn  = module.monitoring.alert_sns_topic_arn
  response_team_emails = var.incident_response_emails
}

# VPN Management Module
module "vpn_management" {
  source = "./modules/vpn-management"

  environment         = var.environment
  vpc_id              = module.networking.vpc_id
  public_subnet_ids   = module.networking.public_subnet_ids
  customer_gateway_ip = var.customer_gateway_ip
}

# Backup and Failover Module
module "backup_failover" {
  source = "./modules/backup-failover"

  environment           = var.environment
  vpc_id                = module.networking.vpc_id
  private_subnet_ids    = module.networking.private_subnet_ids
  backup_retention_days = var.backup_retention_days
  enable_multi_region   = var.enable_multi_region_backup

  providers = {
    aws.secondary = aws.secondary
  }
}

# Networking Module (supporting infrastructure)
module "networking" {
  source = "./modules/networking"

  environment        = var.environment
  vpc_cidr           = var.vpc_cidr
  availability_zones = var.availability_zones
}

# Security Enhancements Module
module "security_enhancements" {
  source = "./modules/security-enhancements"

  environment           = var.environment
  vpn_config_secret_id  = module.vpn_management.vpn_config_secret_arn
  guardduty_detector_id = module.threat_detection.guardduty_detector_id
  alert_email           = var.alert_email
}

# Governance Module
module "governance" {
  source = "./modules/governance"

  environment        = var.environment
  config_recorder_id = module.policy_enforcement.config_recorder_id
  compliance_emails  = var.compliance_emails
}

# Outputs
output "monitoring_dashboard_url" {
  description = "URL to CloudWatch monitoring dashboard"
  value       = module.monitoring.dashboard_url
}

output "vpn_endpoint" {
  description = "VPN connection endpoint"
  value       = module.vpn_management.vpn_endpoint
  sensitive   = true
}

output "incident_response_topic_arn" {
  description = "SNS topic ARN for incident response"
  value       = module.incident_response.sns_topic_arn
}

output "backup_vault_arn" {
  description = "AWS Backup vault ARN"
  value       = module.backup_failover.backup_vault_arn
}

output "compliance_reports_bucket" {
  description = "S3 bucket for compliance reports"
  value       = module.governance.compliance_reports_bucket_id
}

output "threat_intel_bucket" {
  description = "S3 bucket for custom threat intelligence"
  value       = module.security_enhancements.threat_intel_bucket_id
}
