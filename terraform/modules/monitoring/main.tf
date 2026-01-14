# Monitoring Module - CloudWatch dashboards, metrics, and logging

# S3 bucket for log storage
resource "aws_s3_bucket" "logs" {
  bucket = "starlink-${var.environment}-logs-${data.aws_caller_identity.current.account_id}"
  
  tags = {
    Name = "starlink-${var.environment}-logs"
  }
}

resource "aws_s3_bucket_versioning" "logs" {
  bucket = aws_s3_bucket.logs.id
  
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "logs" {
  bucket = aws_s3_bucket.logs.id
  
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "logs" {
  bucket = aws_s3_bucket.logs.id
  
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_lifecycle_configuration" "logs" {
  bucket = aws_s3_bucket.logs.id
  
  rule {
    id     = "log-retention"
    status = "Enabled"
    
    transition {
      days          = 30
      storage_class = "STANDARD_IA"
    }
    
    transition {
      days          = 60
      storage_class = "GLACIER"
    }
    
    expiration {
      days = var.retention_days
    }
  }
}

# CloudWatch Log Groups for centralized logging
resource "aws_cloudwatch_log_group" "application" {
  name              = "/aws/starlink/${var.environment}/application"
  retention_in_days = var.retention_days
  
  tags = {
    Name = "starlink-${var.environment}-application-logs"
  }
}

resource "aws_cloudwatch_log_group" "security" {
  name              = "/aws/starlink/${var.environment}/security"
  retention_in_days = var.retention_days
  
  tags = {
    Name = "starlink-${var.environment}-security-logs"
  }
}

resource "aws_cloudwatch_log_group" "connectivity" {
  name              = "/aws/starlink/${var.environment}/connectivity"
  retention_in_days = var.retention_days
  
  tags = {
    Name = "starlink-${var.environment}-connectivity-logs"
  }
}

# SNS Topic for alerts
resource "aws_sns_topic" "alerts" {
  name = "starlink-${var.environment}-alerts"
  
  tags = {
    Name = "starlink-${var.environment}-alerts"
  }
}

resource "aws_sns_topic_subscription" "alert_email" {
  topic_arn = aws_sns_topic.alerts.arn
  protocol  = "email"
  endpoint  = var.alert_email
}

# CloudWatch Dashboard
resource "aws_cloudwatch_dashboard" "main" {
  dashboard_name = "starlink-${var.environment}-monitoring"
  
  dashboard_body = jsonencode({
    widgets = [
      {
        type = "metric"
        properties = {
          metrics = [
            ["AWS/VPN", "TunnelState", { stat = "Average" }],
            ["AWS/VPN", "TunnelDataIn", { stat = "Sum" }],
            ["AWS/VPN", "TunnelDataOut", { stat = "Sum" }]
          ]
          period = 300
          region = data.aws_region.current.name
          title  = "VPN Connectivity"
        }
      },
      {
        type = "metric"
        properties = {
          metrics = [
            ["AWS/CloudWatch/Logs", "IncomingLogEvents", { stat = "Sum" }],
            ["AWS/CloudWatch/Logs", "IncomingBytes", { stat = "Sum" }]
          ]
          period = 300
          region = data.aws_region.current.name
          title  = "Log Ingestion"
        }
      },
      {
        type = "log"
        properties = {
          query   = "SOURCE '${aws_cloudwatch_log_group.security.name}' | fields @timestamp, @message | sort @timestamp desc | limit 100"
          region  = data.aws_region.current.name
          title   = "Recent Security Events"
        }
      }
    ]
  })
}

# CloudWatch Metric Alarms
resource "aws_cloudwatch_metric_alarm" "high_error_rate" {
  alarm_name          = "starlink-${var.environment}-high-error-rate"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "Errors"
  namespace           = "Starlink/Application"
  period              = 300
  statistic           = "Sum"
  threshold           = 10
  alarm_description   = "Alert when error rate is high"
  alarm_actions       = [aws_sns_topic.alerts.arn]
  
  tags = {
    Name = "starlink-${var.environment}-high-error-rate"
  }
}

resource "aws_cloudwatch_metric_alarm" "connectivity_loss" {
  alarm_name          = "starlink-${var.environment}-connectivity-loss"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = 2
  metric_name         = "TunnelState"
  namespace           = "AWS/VPN"
  period              = 60
  statistic           = "Average"
  threshold           = 1
  alarm_description   = "Alert when VPN tunnel goes down"
  alarm_actions       = [aws_sns_topic.alerts.arn]
  treat_missing_data  = "breaching"
  
  tags = {
    Name = "starlink-${var.environment}-connectivity-loss"
  }
}

# CloudWatch Log Metric Filters
resource "aws_cloudwatch_log_metric_filter" "security_events" {
  name           = "starlink-${var.environment}-security-events"
  log_group_name = aws_cloudwatch_log_group.security.name
  pattern        = "[time, request_id, event_type = SecurityEvent*, ...]"
  
  metric_transformation {
    name      = "SecurityEvents"
    namespace = "Starlink/Security"
    value     = "1"
  }
}

resource "aws_cloudwatch_log_metric_filter" "failed_authentications" {
  name           = "starlink-${var.environment}-failed-auth"
  log_group_name = aws_cloudwatch_log_group.security.name
  pattern        = "[time, request_id, event_type = AuthenticationFailure*, ...]"
  
  metric_transformation {
    name      = "FailedAuthentications"
    namespace = "Starlink/Security"
    value     = "1"
  }
}

# Data sources
data "aws_caller_identity" "current" {}
data "aws_region" "current" {}
