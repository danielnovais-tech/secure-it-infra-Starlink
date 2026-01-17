variable "environment" {
  description = "Environment name"
  type        = string
}

variable "vpn_config_secret_id" {
  description = "ARN of VPN configuration secret"
  type        = string
}

variable "guardduty_detector_id" {
  description = "GuardDuty detector ID"
  type        = string
}

variable "alert_email" {
  description = "Email address for security alerts"
  type        = string
}
