output "guardduty_detector_id" {
  description = "GuardDuty detector ID"
  value       = aws_guardduty_detector.main.id
}

output "threat_alerts_topic_arn" {
  description = "SNS topic ARN for threat alerts"
  value       = aws_sns_topic.threat_alerts.arn
}

output "waf_web_acl_id" {
  description = "WAF Web ACL ID"
  value       = aws_wafv2_web_acl.main.id
}

output "waf_web_acl_arn" {
  description = "WAF Web ACL ARN"
  value       = aws_wafv2_web_acl.main.arn
}

output "security_hub_arn" {
  description = "Security Hub ARN"
  value       = aws_securityhub_account.main.arn
}
