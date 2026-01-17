output "log_bucket_id" {
  description = "S3 bucket ID for logs"
  value       = aws_s3_bucket.logs.id
}

output "log_bucket_arn" {
  description = "S3 bucket ARN for logs"
  value       = aws_s3_bucket.logs.arn
}

output "alert_sns_topic_arn" {
  description = "SNS topic ARN for alerts"
  value       = aws_sns_topic.alerts.arn
}

output "dashboard_url" {
  description = "CloudWatch dashboard URL"
  value       = "https://console.aws.amazon.com/cloudwatch/home?region=${data.aws_region.current.name}#dashboards:name=${aws_cloudwatch_dashboard.main.dashboard_name}"
}

output "application_log_group_name" {
  description = "Application log group name"
  value       = aws_cloudwatch_log_group.application.name
}

output "security_log_group_name" {
  description = "Security log group name"
  value       = aws_cloudwatch_log_group.security.name
}

output "connectivity_log_group_name" {
  description = "Connectivity log group name"
  value       = aws_cloudwatch_log_group.connectivity.name
}
