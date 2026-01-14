# VPN Management Module - Site-to-Site VPN with Starlink connectivity

# Customer Gateway (Starlink endpoint)
resource "aws_customer_gateway" "starlink" {
  bgp_asn    = 65000
  ip_address = var.customer_gateway_ip
  type       = "ipsec.1"

  tags = {
    Name = "starlink-${var.environment}-customer-gateway"
  }
}

# Virtual Private Gateway
resource "aws_vpn_gateway" "main" {
  vpc_id = var.vpc_id

  tags = {
    Name = "starlink-${var.environment}-vpn-gateway"
  }
}

# VPN Connection
resource "aws_vpn_connection" "main" {
  vpn_gateway_id      = aws_vpn_gateway.main.id
  customer_gateway_id = aws_customer_gateway.starlink.id
  type                = "ipsec.1"
  static_routes_only  = false

  tunnel1_inside_cidr   = "169.254.10.0/30"
  tunnel2_inside_cidr   = "169.254.11.0/30"
  tunnel1_preshared_key = random_password.tunnel1_psk.result
  tunnel2_preshared_key = random_password.tunnel2_psk.result

  tunnel1_dpd_timeout_action = "restart"
  tunnel2_dpd_timeout_action = "restart"

  tunnel1_ike_versions = ["ikev2"]
  tunnel2_ike_versions = ["ikev2"]

  tunnel1_phase1_dh_group_numbers      = [14, 15, 16, 17, 18]
  tunnel2_phase1_dh_group_numbers      = [14, 15, 16, 17, 18]
  tunnel1_phase1_encryption_algorithms = ["AES256"]
  tunnel2_phase1_encryption_algorithms = ["AES256"]
  tunnel1_phase1_integrity_algorithms  = ["SHA2-256"]
  tunnel2_phase1_integrity_algorithms  = ["SHA2-256"]

  tunnel1_phase2_dh_group_numbers      = [14, 15, 16, 17, 18]
  tunnel2_phase2_dh_group_numbers      = [14, 15, 16, 17, 18]
  tunnel1_phase2_encryption_algorithms = ["AES256"]
  tunnel2_phase2_encryption_algorithms = ["AES256"]
  tunnel1_phase2_integrity_algorithms  = ["SHA2-256"]
  tunnel2_phase2_integrity_algorithms  = ["SHA2-256"]

  tags = {
    Name = "starlink-${var.environment}-vpn-connection"
  }
}

# Random passwords for VPN tunnels
resource "random_password" "tunnel1_psk" {
  length  = 32
  special = true
}

resource "random_password" "tunnel2_psk" {
  length  = 32
  special = true
}

# Store VPN configuration in Secrets Manager
resource "aws_secretsmanager_secret" "vpn_config" {
  name = "starlink-${var.environment}-vpn-config"

  tags = {
    Name = "starlink-${var.environment}-vpn-config"
  }
}

resource "aws_secretsmanager_secret_version" "vpn_config" {
  secret_id = aws_secretsmanager_secret.vpn_config.id

  secret_string = jsonencode({
    tunnel1_address       = aws_vpn_connection.main.tunnel1_address
    tunnel1_preshared_key = random_password.tunnel1_psk.result
    tunnel1_inside_cidr   = "169.254.10.0/30"
    tunnel2_address       = aws_vpn_connection.main.tunnel2_address
    tunnel2_preshared_key = random_password.tunnel2_psk.result
    tunnel2_inside_cidr   = "169.254.11.0/30"
    customer_gateway_ip   = var.customer_gateway_ip
  })
}

# VPN Gateway Route Propagation
resource "aws_vpn_gateway_route_propagation" "main" {
  count          = length(data.aws_route_tables.main.ids)
  vpn_gateway_id = aws_vpn_gateway.main.id
  route_table_id = data.aws_route_tables.main.ids[count.index]
}

data "aws_route_tables" "main" {
  vpc_id = var.vpc_id
}

# CloudWatch alarms for VPN monitoring
resource "aws_cloudwatch_metric_alarm" "tunnel1_state" {
  alarm_name          = "starlink-${var.environment}-vpn-tunnel1-down"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = 2
  metric_name         = "TunnelState"
  namespace           = "AWS/VPN"
  period              = 60
  statistic           = "Average"
  threshold           = 1
  alarm_description   = "Alert when VPN Tunnel 1 is down"
  treat_missing_data  = "breaching"

  dimensions = {
    VpnId = aws_vpn_connection.main.id
  }

  tags = {
    Name = "starlink-${var.environment}-vpn-tunnel1-alarm"
  }
}

resource "aws_cloudwatch_metric_alarm" "tunnel2_state" {
  alarm_name          = "starlink-${var.environment}-vpn-tunnel2-down"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = 2
  metric_name         = "TunnelState"
  namespace           = "AWS/VPN"
  period              = 60
  statistic           = "Average"
  threshold           = 1
  alarm_description   = "Alert when VPN Tunnel 2 is down"
  treat_missing_data  = "breaching"

  dimensions = {
    VpnId = aws_vpn_connection.main.id
  }

  tags = {
    Name = "starlink-${var.environment}-vpn-tunnel2-alarm"
  }
}

# CloudWatch Dashboard for VPN metrics
resource "aws_cloudwatch_dashboard" "vpn" {
  dashboard_name = "starlink-${var.environment}-vpn"

  dashboard_body = jsonencode({
    widgets = [
      {
        type = "metric"
        properties = {
          metrics = [
            ["AWS/VPN", "TunnelState", { stat = "Average", label = "Tunnel 1 State" }],
            ["...", { stat = "Average", label = "Tunnel 2 State" }]
          ]
          period = 60
          region = data.aws_region.current.name
          title  = "VPN Tunnel Status"
          yAxis = {
            left = {
              min = 0
              max = 1
            }
          }
        }
      },
      {
        type = "metric"
        properties = {
          metrics = [
            ["AWS/VPN", "TunnelDataIn", { stat = "Sum", label = "Data In" }],
            ["AWS/VPN", "TunnelDataOut", { stat = "Sum", label = "Data Out" }]
          ]
          period = 300
          region = data.aws_region.current.name
          title  = "VPN Data Transfer"
        }
      }
    ]
  })
}

# Transit Gateway for advanced routing (optional)
resource "aws_ec2_transit_gateway" "main" {
  description                     = "Starlink ${var.environment} Transit Gateway"
  default_route_table_association = "enable"
  default_route_table_propagation = "enable"

  tags = {
    Name = "starlink-${var.environment}-tgw"
  }
}

resource "aws_ec2_transit_gateway_vpc_attachment" "main" {
  subnet_ids         = var.public_subnet_ids
  transit_gateway_id = aws_ec2_transit_gateway.main.id
  vpc_id             = var.vpc_id

  tags = {
    Name = "starlink-${var.environment}-tgw-attachment"
  }
}

data "aws_region" "current" {}
