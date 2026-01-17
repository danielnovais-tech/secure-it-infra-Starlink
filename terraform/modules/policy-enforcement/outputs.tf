output "config_recorder_id" {
  description = "AWS Config recorder ID"
  value       = aws_config_configuration_recorder.main.id
}

output "config_bucket_id" {
  description = "Config S3 bucket ID"
  value       = aws_s3_bucket.config.id
}

output "default_security_group_id" {
  description = "Default deny security group ID"
  value       = aws_security_group.default_deny.id
}

output "patch_baseline_id" {
  description = "SSM patch baseline ID"
  value       = aws_ssm_patch_baseline.main.id
}
