output "backup_vault_arn" {
  description = "Backup vault ARN"
  value       = aws_backup_vault.main.arn
}

output "backup_plan_id" {
  description = "Backup plan ID"
  value       = aws_backup_plan.main.id
}

output "config_backup_bucket_id" {
  description = "Configuration backup S3 bucket ID"
  value       = aws_s3_bucket.config_backup.id
}

output "failover_state_table_name" {
  description = "DynamoDB table name for failover state"
  value       = aws_dynamodb_table.failover_state.name
}

output "failover_handler_arn" {
  description = "Failover handler Lambda ARN"
  value       = aws_lambda_function.failover_handler.arn
}

output "health_check_id" {
  description = "Route53 health check ID"
  value       = aws_route53_health_check.primary.id
}
