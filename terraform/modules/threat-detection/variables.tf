variable "environment" {
  description = "Environment name"
  type        = string
}

variable "vpc_id" {
  description = "VPC ID"
  type        = string
}

variable "alert_email" {
  description = "Email address for threat alerts"
  type        = string
}

variable "log_bucket_id" {
  description = "S3 bucket ID for logs"
  type        = string
}
