# Variables for Starlink Enterprise Infrastructure Security

variable "aws_region" {
  description = "AWS region for resource deployment"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "prod"
  
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be dev, staging, or prod."
  }
}

variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "availability_zones" {
  description = "List of availability zones for high availability"
  type        = list(string)
  default     = ["us-east-1a", "us-east-1b", "us-east-1c"]
}

variable "alert_email" {
  description = "Email address for monitoring alerts"
  type        = string
}

variable "incident_response_emails" {
  description = "List of email addresses for incident response team"
  type        = list(string)
}

variable "customer_gateway_ip" {
  description = "Customer gateway IP for VPN connection"
  type        = string
}

variable "log_retention_days" {
  description = "Number of days to retain logs"
  type        = number
  default     = 90
}

variable "backup_retention_days" {
  description = "Number of days to retain backups"
  type        = number
  default     = 30
}

variable "enable_multi_region_backup" {
  description = "Enable multi-region backup replication"
  type        = bool
  default     = true
}
