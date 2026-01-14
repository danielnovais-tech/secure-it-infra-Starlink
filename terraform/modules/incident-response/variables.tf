variable "environment" {
  description = "Environment name"
  type        = string
}

variable "alert_sns_topic_arn" {
  description = "SNS topic ARN for alerts from monitoring module"
  type        = string
}

variable "response_team_emails" {
  description = "List of email addresses for incident response team"
  type        = list(string)
}
