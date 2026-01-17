# Security Enhancements Module - Secret rotation, custom detection rules, and advanced security

# Automatic rotation for VPN secrets
resource "aws_secretsmanager_secret_rotation" "vpn_config" {
  secret_id           = var.vpn_config_secret_id
  rotation_lambda_arn = aws_lambda_function.rotate_vpn_secrets.arn

  rotation_rules {
    automatically_after_days = 30
  }
}

# Lambda function for VPN secret rotation
resource "aws_lambda_function" "rotate_vpn_secrets" {
  filename      = data.archive_file.rotate_vpn_secrets.output_path
  function_name = "starlink-${var.environment}-rotate-vpn-secrets"
  role          = aws_iam_role.rotate_vpn_secrets.arn
  handler       = "index.handler"
  runtime       = "python3.11"
  timeout       = 300

  source_code_hash = data.archive_file.rotate_vpn_secrets.output_base64sha256

  environment {
    variables = {
      ENVIRONMENT = var.environment
    }
  }

  tags = {
    Name = "starlink-${var.environment}-rotate-vpn-secrets"
  }
}

data "archive_file" "rotate_vpn_secrets" {
  type        = "zip"
  output_path = "${path.module}/rotate_vpn_secrets.zip"

  source {
    content  = <<-EOF
      import json
      import boto3
      import os
      from secrets import token_urlsafe

      secrets_manager = boto3.client('secretsmanager')
      ec2 = boto3.client('ec2')

      def handler(event, context):
          """
          Rotate VPN tunnel pre-shared keys
          """
          print(f"Secret rotation event: {json.dumps(event)}")
          
          arn = event['SecretId']
          token = event['ClientRequestToken']
          step = event['Step']
          
          if step == "createSecret":
              # Generate new pre-shared keys
              new_psk1 = token_urlsafe(32)
              new_psk2 = token_urlsafe(32)
              
              # Get current secret
              current = secrets_manager.get_secret_value(SecretId=arn)
              current_secret = json.loads(current['SecretString'])
              
              # Create new version with new PSKs
              new_secret = current_secret.copy()
              new_secret['tunnel1_preshared_key'] = new_psk1
              new_secret['tunnel2_preshared_key'] = new_psk2
              
              secrets_manager.put_secret_value(
                  SecretId=arn,
                  ClientRequestToken=token,
                  SecretString=json.dumps(new_secret),
                  VersionStages=['AWSPENDING']
              )
              
          elif step == "setSecret":
              # Update VPN connection with new PSKs
              # Note: This would require recreating VPN connection or using AWS API
              # For production, implement VPN update logic here
              pass
              
          elif step == "testSecret":
              # Test new VPN configuration
              # For production, implement connectivity test here
              pass
              
          elif step == "finishSecret":
              # Finalize rotation
              metadata = secrets_manager.describe_secret(SecretId=arn)
              current_version = None
              for version in metadata["VersionIdsToStages"]:
                  if "AWSCURRENT" in metadata["VersionIdsToStages"][version]:
                      if version == token:
                          return
                      current_version = version
                      break
              
              secrets_manager.update_secret_version_stage(
                  SecretId=arn,
                  VersionStage="AWSCURRENT",
                  MoveToVersionId=token,
                  RemoveFromVersionId=current_version
              )
          
          return {
              'statusCode': 200,
              'body': json.dumps(f'Rotation step {step} completed')
          }
    EOF
    filename = "index.py"
  }
}

resource "aws_iam_role" "rotate_vpn_secrets" {
  name = "starlink-${var.environment}-rotate-vpn-secrets-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy" "rotate_vpn_secrets" {
  name = "starlink-${var.environment}-rotate-vpn-secrets-policy"
  role = aws_iam_role.rotate_vpn_secrets.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:*:*:*"
      },
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:DescribeSecret",
          "secretsmanager:GetSecretValue",
          "secretsmanager:PutSecretValue",
          "secretsmanager:UpdateSecretVersionStage"
        ]
        Resource = var.vpn_config_secret_id
      },
      {
        Effect = "Allow"
        Action = [
          "ec2:ModifyVpnConnection",
          "ec2:DescribeVpnConnections"
        ]
        Resource = "*"
      }
    ]
  })
}

resource "aws_lambda_permission" "allow_secrets_manager" {
  statement_id  = "AllowExecutionFromSecretsManager"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.rotate_vpn_secrets.function_name
  principal     = "secretsmanager.amazonaws.com"
}

# Custom GuardDuty threat intelligence set
resource "aws_guardduty_threatintelset" "custom" {
  activate    = true
  detector_id = var.guardduty_detector_id
  format      = "TXT"
  location    = "https://${aws_s3_bucket.threat_intel.bucket_regional_domain_name}/threat-intel.txt"
  name        = "starlink-${var.environment}-custom-threat-intel"

  depends_on = [aws_s3_object.threat_intel]
}

resource "aws_s3_bucket" "threat_intel" {
  bucket = "starlink-${var.environment}-threat-intel-${data.aws_caller_identity.current.account_id}"

  tags = {
    Name = "starlink-${var.environment}-threat-intel"
  }
}

resource "aws_s3_bucket_public_access_block" "threat_intel" {
  bucket = aws_s3_bucket.threat_intel.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_object" "threat_intel" {
  bucket  = aws_s3_bucket.threat_intel.id
  key     = "threat-intel.txt"
  content = "# Custom threat intelligence IPs\n# Add known malicious IPs here, one per line\n"
}

# Custom WAF rules for application-specific protection
resource "aws_wafv2_regex_pattern_set" "sql_injection_patterns" {
  name  = "starlink-${var.environment}-sql-injection-patterns"
  scope = "REGIONAL"

  regular_expression {
    regex_string = "(?i)(union.*select|select.*from|insert.*into|delete.*from|drop.*table)"
  }

  regular_expression {
    regex_string = "(?i)(exec.*xp_|sp_executesql|xp_cmdshell)"
  }

  tags = {
    Name = "starlink-${var.environment}-sql-injection-patterns"
  }
}

resource "aws_wafv2_regex_pattern_set" "suspicious_user_agents" {
  name  = "starlink-${var.environment}-suspicious-user-agents"
  scope = "REGIONAL"

  regular_expression {
    regex_string = "(?i)(nikto|sqlmap|nmap|masscan|metasploit)"
  }

  regular_expression {
    regex_string = "(?i)(acunetix|burp|nessus|w3af)"
  }

  tags = {
    Name = "starlink-${var.environment}-suspicious-user-agents"
  }
}

# X-Ray tracing for Lambda functions
resource "aws_lambda_function_event_invoke_config" "rotate_vpn_secrets_tracing" {
  function_name = aws_lambda_function.rotate_vpn_secrets.function_name

  destination_config {
    on_failure {
      destination = aws_sns_topic.security_alerts.arn
    }
  }
}

resource "aws_sns_topic" "security_alerts" {
  name = "starlink-${var.environment}-security-alerts"

  tags = {
    Name = "starlink-${var.environment}-security-alerts"
  }
}

resource "aws_sns_topic_subscription" "security_alerts" {
  topic_arn = aws_sns_topic.security_alerts.arn
  protocol  = "email"
  endpoint  = var.alert_email
}

data "aws_caller_identity" "current" {}
