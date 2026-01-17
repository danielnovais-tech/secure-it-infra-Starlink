# Governance Module - Mandatory tagging, compliance reporting, and policy enforcement

# Mandatory tagging policy via AWS Config
resource "aws_config_config_rule" "required_tags" {
  name = "starlink-${var.environment}-required-tags"

  source {
    owner             = "AWS"
    source_identifier = "REQUIRED_TAGS"
  }

  input_parameters = jsonencode({
    tag1Key = "Environment"
    tag2Key = "Project"
    tag3Key = "ManagedBy"
    tag4Key = "CostCenter"
  })

  scope {
    compliance_resource_types = [
      "AWS::EC2::Instance",
      "AWS::EC2::Volume",
      "AWS::RDS::DBInstance",
      "AWS::S3::Bucket",
      "AWS::Lambda::Function"
    ]
  }

  depends_on = [var.config_recorder_id]
}

# Tag value validation
resource "aws_config_config_rule" "tag_value_compliance" {
  name = "starlink-${var.environment}-tag-value-compliance"

  source {
    owner             = "AWS"
    source_identifier = "REQUIRED_TAGS"
  }

  input_parameters = jsonencode({
    tag1Key   = "Environment"
    tag1Value = "dev,staging,prod"
    tag2Key   = "Project"
    tag2Value = "Starlink-Security"
  })

  depends_on = [var.config_recorder_id]
}

# Compliance reporting - Export to S3
resource "aws_s3_bucket" "compliance_reports" {
  bucket = "starlink-${var.environment}-compliance-reports-${data.aws_caller_identity.current.account_id}"

  tags = {
    Name        = "starlink-${var.environment}-compliance-reports"
    Environment = var.environment
    Project     = "Starlink-Security"
    ManagedBy   = "Terraform"
  }
}

resource "aws_s3_bucket_versioning" "compliance_reports" {
  bucket = aws_s3_bucket.compliance_reports.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "compliance_reports" {
  bucket = aws_s3_bucket.compliance_reports.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "compliance_reports" {
  bucket = aws_s3_bucket.compliance_reports.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Lambda function to generate compliance reports
resource "aws_lambda_function" "compliance_reporter" {
  filename      = data.archive_file.compliance_reporter.output_path
  function_name = "starlink-${var.environment}-compliance-reporter"
  role          = aws_iam_role.compliance_reporter.arn
  handler       = "index.handler"
  runtime       = "python3.11"
  timeout       = 300

  source_code_hash = data.archive_file.compliance_reporter.output_base64sha256

  environment {
    variables = {
      ENVIRONMENT   = var.environment
      REPORT_BUCKET = aws_s3_bucket.compliance_reports.id
      SNS_TOPIC_ARN = aws_sns_topic.compliance_notifications.arn
    }
  }

  tags = {
    Name        = "starlink-${var.environment}-compliance-reporter"
    Environment = var.environment
    Project     = "Starlink-Security"
    ManagedBy   = "Terraform"
  }
}

data "archive_file" "compliance_reporter" {
  type        = "zip"
  output_path = "${path.module}/compliance_reporter.zip"

  source {
    content  = <<-EOF
      import json
      import boto3
      import os
      from datetime import datetime
      
      config = boto3.client('config')
      s3 = boto3.client('s3')
      sns = boto3.client('sns')
      
      def handler(event, context):
          """
          Generate compliance report from AWS Config
          """
          print("Generating compliance report")
          
          # Get compliance summary
          compliance_summary = config.describe_compliance_by_config_rule()
          
          # Get resource compliance details
          resource_compliance = {}
          for rule in compliance_summary.get('ComplianceByConfigRules', []):
              rule_name = rule['ConfigRuleName']
              compliance_type = rule.get('Compliance', {}).get('ComplianceType', 'UNKNOWN')
              resource_compliance[rule_name] = compliance_type
          
          # Generate report
          report = {
              'timestamp': datetime.utcnow().isoformat(),
              'environment': os.environ['ENVIRONMENT'],
              'compliance_summary': {
                  'total_rules': len(resource_compliance),
                  'compliant': sum(1 for v in resource_compliance.values() if v == 'COMPLIANT'),
                  'non_compliant': sum(1 for v in resource_compliance.values() if v == 'NON_COMPLIANT'),
                  'not_applicable': sum(1 for v in resource_compliance.values() if v == 'NOT_APPLICABLE')
              },
              'rules': resource_compliance
          }
          
          # Save to S3
          report_key = f"compliance-reports/{datetime.utcnow().strftime('%Y/%m/%d')}/compliance-report-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}.json"
          s3.put_object(
              Bucket=os.environ['REPORT_BUCKET'],
              Key=report_key,
              Body=json.dumps(report, indent=2),
              ContentType='application/json'
          )
          
          # Send notification
          sns.publish(
              TopicArn=os.environ['SNS_TOPIC_ARN'],
              Subject=f"Compliance Report - {os.environ['ENVIRONMENT']}",
              Message=json.dumps(report, indent=2)
          )
          
          return {
              'statusCode': 200,
              'body': json.dumps({
                  'message': 'Compliance report generated',
                  'report_key': report_key
              })
          }
    EOF
    filename = "index.py"
  }
}

resource "aws_iam_role" "compliance_reporter" {
  name = "starlink-${var.environment}-compliance-reporter-role"

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

resource "aws_iam_role_policy" "compliance_reporter" {
  name = "starlink-${var.environment}-compliance-reporter-policy"
  role = aws_iam_role.compliance_reporter.id

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
          "config:DescribeComplianceByConfigRule",
          "config:DescribeComplianceByResource",
          "config:GetComplianceDetailsByConfigRule"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "s3:PutObject",
          "s3:PutObjectAcl"
        ]
        Resource = "${aws_s3_bucket.compliance_reports.arn}/*"
      },
      {
        Effect = "Allow"
        Action = [
          "sns:Publish"
        ]
        Resource = aws_sns_topic.compliance_notifications.arn
      }
    ]
  })
}

# SNS topic for compliance notifications
resource "aws_sns_topic" "compliance_notifications" {
  name = "starlink-${var.environment}-compliance-notifications"

  tags = {
    Name        = "starlink-${var.environment}-compliance-notifications"
    Environment = var.environment
    Project     = "Starlink-Security"
    ManagedBy   = "Terraform"
  }
}

resource "aws_sns_topic_subscription" "compliance_email" {
  count     = length(var.compliance_emails)
  topic_arn = aws_sns_topic.compliance_notifications.arn
  protocol  = "email"
  endpoint  = var.compliance_emails[count.index]
}

# EventBridge rule to trigger compliance reports weekly
resource "aws_cloudwatch_event_rule" "weekly_compliance_report" {
  name                = "starlink-${var.environment}-weekly-compliance-report"
  description         = "Trigger weekly compliance report generation"
  schedule_expression = "cron(0 8 ? * MON *)"

  tags = {
    Name        = "starlink-${var.environment}-weekly-compliance-report"
    Environment = var.environment
    Project     = "Starlink-Security"
    ManagedBy   = "Terraform"
  }
}

resource "aws_cloudwatch_event_target" "compliance_reporter" {
  rule      = aws_cloudwatch_event_rule.weekly_compliance_report.name
  target_id = "ComplianceReporter"
  arn       = aws_lambda_function.compliance_reporter.arn
}

resource "aws_lambda_permission" "allow_eventbridge" {
  statement_id  = "AllowExecutionFromEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.compliance_reporter.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.weekly_compliance_report.arn
}

# CloudWatch Log Group for compliance reporter
resource "aws_cloudwatch_log_group" "compliance_reporter" {
  name              = "/aws/lambda/${aws_lambda_function.compliance_reporter.function_name}"
  retention_in_days = 30

  tags = {
    Name        = "starlink-${var.environment}-compliance-reporter-logs"
    Environment = var.environment
    Project     = "Starlink-Security"
    ManagedBy   = "Terraform"
  }
}

data "aws_caller_identity" "current" {}
