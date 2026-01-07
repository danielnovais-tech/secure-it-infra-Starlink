# Provider Configuration Outputs
output "aws_region" {
  description = "The AWS region where resources are deployed"
  value       = var.aws_region
}

output "environment" {
  description = "The environment name"
  value       = var.environment
}

output "aws_account_id" {
  description = "The AWS Account ID being used"
  value       = data.aws_caller_identity.current.account_id
}

output "aws_caller_arn" {
  description = "The ARN of the AWS caller identity"
  value       = data.aws_caller_identity.current.arn
}

output "provider_configuration" {
  description = "Summary of provider configuration"
  value = {
    primary_region     = var.aws_region
    cross_region       = var.enable_cross_region ? "us-east-1" : "disabled"
    environment        = var.environment
    backup_enabled     = var.enable_backup
    monitoring_enabled = var.enable_monitoring
  }
}

output "default_tags" {
  description = "Default tags applied to all resources"
  value = {
    Project     = "secure-it-infra-Starlink"
    ManagedBy   = "Terraform"
    Environment = var.environment
    Owner       = var.owner
    CostCenter  = var.cost_center
  }
}
