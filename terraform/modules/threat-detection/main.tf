# Threat Detection Module - GuardDuty, Security Hub, and threat intelligence

# Enable GuardDuty for threat detection
resource "aws_guardduty_detector" "main" {
  enable = true

  datasources {
    s3_logs {
      enable = true
    }
    kubernetes {
      audit_logs {
        enable = true
      }
    }
    malware_protection {
      scan_ec2_instance_with_findings {
        ebs_volumes {
          enable = true
        }
      }
    }
  }

  tags = {
    Name = "starlink-${var.environment}-guardduty"
  }
}

# GuardDuty findings to SNS
resource "aws_cloudwatch_event_rule" "guardduty_findings" {
  name        = "starlink-${var.environment}-guardduty-findings"
  description = "Capture GuardDuty findings"

  event_pattern = jsonencode({
    source      = ["aws.guardduty"]
    detail-type = ["GuardDuty Finding"]
    detail = {
      severity = [4, 4.0, 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 4.8, 4.9, 5, 5.0, 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7, 5.8, 5.9, 6, 6.0, 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7, 6.8, 6.9, 7, 7.0, 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 7.7, 7.8, 7.9, 8, 8.0, 8.1, 8.2, 8.3, 8.4, 8.5, 8.6, 8.7, 8.8, 8.9]
    }
  })
}

resource "aws_cloudwatch_event_target" "guardduty_sns" {
  rule      = aws_cloudwatch_event_rule.guardduty_findings.name
  target_id = "SendToSNS"
  arn       = aws_sns_topic.threat_alerts.arn
}

# SNS Topic for threat alerts
resource "aws_sns_topic" "threat_alerts" {
  name = "starlink-${var.environment}-threat-alerts"

  tags = {
    Name = "starlink-${var.environment}-threat-alerts"
  }
}

resource "aws_sns_topic_policy" "threat_alerts" {
  arn = aws_sns_topic.threat_alerts.arn

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "events.amazonaws.com"
        }
        Action   = "SNS:Publish"
        Resource = aws_sns_topic.threat_alerts.arn
      }
    ]
  })
}

resource "aws_sns_topic_subscription" "threat_alert_email" {
  topic_arn = aws_sns_topic.threat_alerts.arn
  protocol  = "email"
  endpoint  = var.alert_email
}

# Enable AWS Security Hub
resource "aws_securityhub_account" "main" {}

resource "aws_securityhub_standards_subscription" "cis" {
  standards_arn = "arn:aws:securityhub:::ruleset/cis-aws-foundations-benchmark/v/1.2.0"

  depends_on = [aws_securityhub_account.main]
}

resource "aws_securityhub_standards_subscription" "pci_dss" {
  standards_arn = "arn:aws:securityhub:${data.aws_region.current.name}::standards/pci-dss/v/3.2.1"

  depends_on = [aws_securityhub_account.main]
}

# WAF Web ACL for protection
resource "aws_wafv2_web_acl" "main" {
  name  = "starlink-${var.environment}-waf"
  scope = "REGIONAL"

  default_action {
    allow {}
  }

  rule {
    name     = "RateLimitRule"
    priority = 1

    action {
      block {}
    }

    statement {
      rate_based_statement {
        limit              = 2000
        aggregate_key_type = "IP"
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "RateLimitRule"
      sampled_requests_enabled   = true
    }
  }

  rule {
    name     = "AWSManagedRulesCommonRuleSet"
    priority = 2

    override_action {
      none {}
    }

    statement {
      managed_rule_group_statement {
        name        = "AWSManagedRulesCommonRuleSet"
        vendor_name = "AWS"
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "AWSManagedRulesCommonRuleSet"
      sampled_requests_enabled   = true
    }
  }

  rule {
    name     = "AWSManagedRulesKnownBadInputsRuleSet"
    priority = 3

    override_action {
      none {}
    }

    statement {
      managed_rule_group_statement {
        name        = "AWSManagedRulesKnownBadInputsRuleSet"
        vendor_name = "AWS"
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "AWSManagedRulesKnownBadInputsRuleSet"
      sampled_requests_enabled   = true
    }
  }

  visibility_config {
    cloudwatch_metrics_enabled = true
    metric_name                = "starlink-${var.environment}-waf"
    sampled_requests_enabled   = true
  }

  tags = {
    Name = "starlink-${var.environment}-waf"
  }
}

# CloudWatch Alarms for threat detection
resource "aws_cloudwatch_metric_alarm" "guardduty_high_severity" {
  alarm_name          = "starlink-${var.environment}-guardduty-high-severity"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "GuardDutyHighSeverityFindings"
  namespace           = "Starlink/Security"
  period              = 300
  statistic           = "Sum"
  threshold           = 0
  alarm_description   = "Alert on high severity GuardDuty findings"
  alarm_actions       = [aws_sns_topic.threat_alerts.arn]
  treat_missing_data  = "notBreaching"

  tags = {
    Name = "starlink-${var.environment}-guardduty-high-severity"
  }
}

# CloudWatch Log Metric Filter for GuardDuty findings
resource "aws_cloudwatch_log_metric_filter" "guardduty_findings" {
  name           = "starlink-${var.environment}-guardduty-findings"
  log_group_name = "/aws/guardduty/${var.environment}"
  pattern        = "[severity >= 4]"

  metric_transformation {
    name      = "GuardDutyHighSeverityFindings"
    namespace = "Starlink/Security"
    value     = "1"
  }
}

resource "aws_cloudwatch_log_group" "guardduty" {
  name              = "/aws/guardduty/${var.environment}"
  retention_in_days = 90

  tags = {
    Name = "starlink-${var.environment}-guardduty-logs"
  }
}

# Network ACL rules for threat mitigation
resource "aws_network_acl" "threat_mitigation" {
  vpc_id = var.vpc_id

  ingress {
    protocol   = -1
    rule_no    = 100
    action     = "allow"
    cidr_block = "0.0.0.0/0"
    from_port  = 0
    to_port    = 0
  }

  egress {
    protocol   = -1
    rule_no    = 100
    action     = "allow"
    cidr_block = "0.0.0.0/0"
    from_port  = 0
    to_port    = 0
  }

  tags = {
    Name = "starlink-${var.environment}-threat-mitigation"
  }
}

data "aws_region" "current" {}
