output "vpn_connection_id" {
  description = "VPN connection ID"
  value       = aws_vpn_connection.main.id
}

output "vpn_endpoint" {
  description = "VPN endpoint configuration"
  value = {
    tunnel1_address = aws_vpn_connection.main.tunnel1_address
    tunnel2_address = aws_vpn_connection.main.tunnel2_address
  }
  sensitive = true
}

output "customer_gateway_id" {
  description = "Customer gateway ID"
  value       = aws_customer_gateway.starlink.id
}

output "vpn_gateway_id" {
  description = "VPN gateway ID"
  value       = aws_vpn_gateway.main.id
}

output "transit_gateway_id" {
  description = "Transit gateway ID"
  value       = aws_ec2_transit_gateway.main.id
}

output "vpn_config_secret_arn" {
  description = "Secrets Manager ARN for VPN configuration"
  value       = aws_secretsmanager_secret.vpn_config.arn
}
