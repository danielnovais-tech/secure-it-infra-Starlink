# Backup and Failover Module - AWS Backup, multi-region replication, and failover

# AWS Backup Vault
resource "aws_backup_vault" "main" {
  name = "starlink-${var.environment}-backup-vault"

  tags = {
    Name = "starlink-${var.environment}-backup-vault"
  }
}

# AWS Backup Plan
resource "aws_backup_plan" "main" {
  name = "starlink-${var.environment}-backup-plan"

  rule {
    rule_name         = "daily_backup"
    target_vault_name = aws_backup_vault.main.name
    schedule          = "cron(0 2 * * ? *)"

    lifecycle {
      delete_after = var.backup_retention_days
    }

    recovery_point_tags = {
      Environment = var.environment
      BackupType  = "Daily"
    }
  }

  rule {
    rule_name         = "weekly_backup"
    target_vault_name = aws_backup_vault.main.name
    schedule          = "cron(0 3 ? * 1 *)"

    lifecycle {
      cold_storage_after = 30
      delete_after       = 90
    }

    recovery_point_tags = {
      Environment = var.environment
      BackupType  = "Weekly"
    }
  }

  advanced_backup_setting {
    backup_options = {
      WindowsVSS = "enabled"
    }
    resource_type = "EC2"
  }

  tags = {
    Name = "starlink-${var.environment}-backup-plan"
  }
}

# IAM role for AWS Backup
resource "aws_iam_role" "backup" {
  name = "starlink-${var.environment}-backup-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "backup.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "backup" {
  role       = aws_iam_role.backup.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSBackupServiceRolePolicyForBackup"
}

resource "aws_iam_role_policy_attachment" "backup_restore" {
  role       = aws_iam_role.backup.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSBackupServiceRolePolicyForRestores"
}

# Backup Selection
resource "aws_backup_selection" "main" {
  name         = "starlink-${var.environment}-backup-selection"
  plan_id      = aws_backup_plan.main.id
  iam_role_arn = aws_iam_role.backup.arn

  selection_tag {
    type  = "STRINGEQUALS"
    key   = "Backup"
    value = "true"
  }

  selection_tag {
    type  = "STRINGEQUALS"
    key   = "Environment"
    value = var.environment
  }
}

# Multi-region backup replication
resource "aws_backup_vault" "secondary" {
  count    = var.enable_multi_region ? 1 : 0
  provider = aws.secondary
  name     = "starlink-${var.environment}-backup-vault-secondary"

  tags = {
    Name = "starlink-${var.environment}-backup-vault-secondary"
  }
}

# S3 bucket for configuration backups
resource "aws_s3_bucket" "config_backup" {
  bucket = "starlink-${var.environment}-config-backup-${data.aws_caller_identity.current.account_id}"

  tags = {
    Name = "starlink-${var.environment}-config-backup"
  }
}

resource "aws_s3_bucket_versioning" "config_backup" {
  bucket = aws_s3_bucket.config_backup.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_replication_configuration" "config_backup" {
  count = var.enable_multi_region ? 1 : 0

  role   = aws_iam_role.replication[0].arn
  bucket = aws_s3_bucket.config_backup.id

  rule {
    id     = "replicate-all"
    status = "Enabled"

    destination {
      bucket        = aws_s3_bucket.config_backup_secondary[0].arn
      storage_class = "STANDARD_IA"
    }
  }

  depends_on = [aws_s3_bucket_versioning.config_backup]
}

resource "aws_s3_bucket" "config_backup_secondary" {
  count    = var.enable_multi_region ? 1 : 0
  provider = aws.secondary
  bucket   = "starlink-${var.environment}-config-backup-secondary-${data.aws_caller_identity.current.account_id}"

  tags = {
    Name = "starlink-${var.environment}-config-backup-secondary"
  }
}

resource "aws_s3_bucket_versioning" "config_backup_secondary" {
  count    = var.enable_multi_region ? 1 : 0
  provider = aws.secondary
  bucket   = aws_s3_bucket.config_backup_secondary[0].id

  versioning_configuration {
    status = "Enabled"
  }
}

# IAM role for S3 replication
resource "aws_iam_role" "replication" {
  count = var.enable_multi_region ? 1 : 0
  name  = "starlink-${var.environment}-s3-replication-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "s3.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy" "replication" {
  count = var.enable_multi_region ? 1 : 0
  name  = "starlink-${var.environment}-s3-replication-policy"
  role  = aws_iam_role.replication[0].id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetReplicationConfiguration",
          "s3:ListBucket"
        ]
        Resource = aws_s3_bucket.config_backup.arn
      },
      {
        Effect = "Allow"
        Action = [
          "s3:GetObjectVersionForReplication",
          "s3:GetObjectVersionAcl"
        ]
        Resource = "${aws_s3_bucket.config_backup.arn}/*"
      },
      {
        Effect = "Allow"
        Action = [
          "s3:ReplicateObject",
          "s3:ReplicateDelete"
        ]
        Resource = "${aws_s3_bucket.config_backup_secondary[0].arn}/*"
      }
    ]
  })
}

# Route53 Health Checks for failover
resource "aws_route53_health_check" "primary" {
  ip_address        = data.aws_eip.nat_primary.public_ip
  port              = 443
  type              = "HTTPS"
  resource_path     = "/health"
  failure_threshold = 3
  request_interval  = 30

  tags = {
    Name = "starlink-${var.environment}-primary-health-check"
  }
}

# DynamoDB for state management
resource "aws_dynamodb_table" "failover_state" {
  name         = "starlink-${var.environment}-failover-state"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "resource_id"

  attribute {
    name = "resource_id"
    type = "S"
  }

  point_in_time_recovery {
    enabled = true
  }

  server_side_encryption {
    enabled = true
  }

  tags = {
    Name = "starlink-${var.environment}-failover-state"
  }
}

# Lambda for automated failover
resource "aws_lambda_function" "failover_handler" {
  filename      = data.archive_file.failover_handler.output_path
  function_name = "starlink-${var.environment}-failover-handler"
  role          = aws_iam_role.failover_handler.arn
  handler       = "index.handler"
  runtime       = "python3.11"
  timeout       = 300

  source_code_hash = data.archive_file.failover_handler.output_base64sha256

  environment {
    variables = {
      ENVIRONMENT = var.environment
      STATE_TABLE = aws_dynamodb_table.failover_state.name
    }
  }

  tags = {
    Name = "starlink-${var.environment}-failover-handler"
  }
}

data "archive_file" "failover_handler" {
  type        = "zip"
  output_path = "${path.module}/failover_handler.zip"

  source {
    content  = <<-EOF
      import json
      import boto3
      import os
      
      dynamodb = boto3.resource('dynamodb')
      route53 = boto3.client('route53')
      
      def handler(event, context):
          """Handle failover events"""
          print(f"Failover event: {json.dumps(event)}")
          
          table = dynamodb.Table(os.environ['STATE_TABLE'])
          
          # Update failover state
          response = table.put_item(
              Item={
                  'resource_id': 'primary',
                  'status': 'failed',
                  'timestamp': context.aws_request_id
              }
          )
          
          # Trigger failover procedures
          # This would include DNS updates, route table changes, etc.
          
          return {
              'statusCode': 200,
              'body': json.dumps('Failover initiated')
          }
    EOF
    filename = "index.py"
  }
}

resource "aws_iam_role" "failover_handler" {
  name = "starlink-${var.environment}-failover-handler-role"

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

resource "aws_iam_role_policy" "failover_handler" {
  name = "starlink-${var.environment}-failover-handler-policy"
  role = aws_iam_role.failover_handler.id

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
          "dynamodb:PutItem",
          "dynamodb:GetItem"
        ]
        Resource = aws_dynamodb_table.failover_state.arn
      },
      {
        Effect = "Allow"
        Action = [
          "route53:ChangeResourceRecordSets"
        ]
        Resource = "*"
      }
    ]
  })
}

# Data sources
data "aws_caller_identity" "current" {}

data "aws_eip" "nat_primary" {
  tags = {
    Name = "starlink-${var.environment}-nat-eip-1"
  }
}

# Provider configuration for secondary region
terraform {
  required_providers {
    aws = {
      source                = "hashicorp/aws"
      version               = "~> 5.0"
      configuration_aliases = [aws.secondary]
    }
  }
}
