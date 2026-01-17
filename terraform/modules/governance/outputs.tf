output "compliance_reports_bucket_id" {
  description = "Compliance reports S3 bucket ID"
  value       = aws_s3_bucket.compliance_reports.id
}

output "compliance_notifications_topic_arn" {
  description = "Compliance notifications SNS topic ARN"
  value       = aws_sns_topic.compliance_notifications.arn
}

output "compliance_reporter_lambda_arn" {
  description = "Compliance reporter Lambda ARN"
  value       = aws_lambda_function.compliance_reporter.arn
}

output "required_tags_rule_arn" {
  description = "Required tags Config rule ARN"
  value       = aws_config_config_rule.required_tags.arn
}
