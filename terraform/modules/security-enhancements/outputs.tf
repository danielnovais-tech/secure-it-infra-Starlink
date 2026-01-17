output "rotation_lambda_arn" {
  description = "VPN secret rotation Lambda ARN"
  value       = aws_lambda_function.rotate_vpn_secrets.arn
}

output "threat_intel_bucket_id" {
  description = "Threat intelligence S3 bucket ID"
  value       = aws_s3_bucket.threat_intel.id
}

output "sql_injection_pattern_set_arn" {
  description = "SQL injection regex pattern set ARN"
  value       = aws_wafv2_regex_pattern_set.sql_injection_patterns.arn
}

output "suspicious_ua_pattern_set_arn" {
  description = "Suspicious user agent regex pattern set ARN"
  value       = aws_wafv2_regex_pattern_set.suspicious_user_agents.arn
}

output "security_alerts_topic_arn" {
  description = "Security alerts SNS topic ARN"
  value       = aws_sns_topic.security_alerts.arn
}
