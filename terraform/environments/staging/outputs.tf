output "vpc_id" {
  description = "VPC ID"
  value       = module.network.vpc_id
}

output "public_subnet_ids" {
  description = "Public subnet IDs"
  value       = module.network.public_subnet_ids
}

output "private_subnet_ids" {
  description = "Private subnet IDs"
  value       = module.network.private_subnet_ids
}

output "app_security_group_id" {
  description = "Application security group ID"
  value       = module.security.app_security_group_id
}

output "db_security_group_id" {
  description = "Database security group ID"
  value       = module.security.db_security_group_id
}
