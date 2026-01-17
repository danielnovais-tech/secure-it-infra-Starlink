variable "environment" {
  description = "Environment name"
  type        = string
}

variable "vpc_id" {
  description = "VPC ID"
  type        = string
}

variable "private_subnet_ids" {
  description = "List of private subnet IDs"
  type        = list(string)
}

variable "alert_email" {
  description = "Email address for alerts"
  type        = string
}

variable "retention_days" {
  description = "Log retention in days"
  type        = number
  default     = 90
}
