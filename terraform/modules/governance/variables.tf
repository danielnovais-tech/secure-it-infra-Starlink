variable "environment" {
  description = "Environment name"
  type        = string
}

variable "config_recorder_id" {
  description = "AWS Config recorder ID"
  type        = string
}

variable "compliance_emails" {
  description = "List of email addresses for compliance notifications"
  type        = list(string)
}
