# AWS Region Configuration
variable "aws_region" {
  description = "Primary AWS region for infrastructure deployment"
  type        = string
  default     = "us-west-2"

  validation {
    condition     = can(regex("^[a-z]{2}-[a-z]+-[0-9]{1}$", var.aws_region))
    error_message = "AWS region must be a valid region format (e.g., us-west-2)."
  }
}

# Environment Configuration
variable "environment" {
  description = "Environment name (e.g., dev, staging, production)"
  type        = string

  validation {
    condition     = contains(["dev", "staging", "production"], var.environment)
    error_message = "Environment must be one of: dev, staging, production."
  }
}

# Owner/Team Information
variable "owner" {
  description = "Team or individual responsible for the infrastructure"
  type        = string
  default     = "SecureIT-Team"
}

# Cost Center for Billing
variable "cost_center" {
  description = "Cost center for resource billing and tracking"
  type        = string
  default     = "Infrastructure"
}

# AWS Account ID
variable "aws_account_id" {
  description = "AWS Account ID for resource policies and validation"
  type        = string
  default     = ""

  validation {
    condition     = var.aws_account_id == "" || can(regex("^[0-9]{12}$", var.aws_account_id))
    error_message = "AWS Account ID must be a 12-digit number."
  }
}

# Enable/Disable Features
variable "enable_cross_region" {
  description = "Enable cross-region provider configuration"
  type        = bool
  default     = true
}

variable "enable_backup" {
  description = "Enable AWS Backup for resources"
  type        = bool
  default     = true
}

variable "enable_monitoring" {
  description = "Enable enhanced monitoring and logging"
  type        = bool
  default     = true
}

# Tags
variable "additional_tags" {
  description = "Additional tags to apply to all resources"
  type        = map(string)
  default     = {}
}
