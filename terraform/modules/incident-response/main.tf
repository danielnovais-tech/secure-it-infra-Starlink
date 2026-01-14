# Incident Response Module - Automated response and remediation

# SNS Topic for incident response
resource "aws_sns_topic" "incidents" {
  name = "starlink-${var.environment}-incidents"
  
  tags = {
    Name = "starlink-${var.environment}-incidents"
  }
}

resource "aws_sns_topic_subscription" "response_team" {
  count     = length(var.response_team_emails)
  topic_arn = aws_sns_topic.incidents.arn
  protocol  = "email"
  endpoint  = var.response_team_emails[count.index]
}

# Lambda function for automated response
resource "aws_lambda_function" "incident_responder" {
  filename      = data.archive_file.incident_responder.output_path
  function_name = "starlink-${var.environment}-incident-responder"
  role          = aws_iam_role.incident_responder.arn
  handler       = "index.handler"
  runtime       = "python3.11"
  timeout       = 300
  
  source_code_hash = data.archive_file.incident_responder.output_base64sha256
  
  environment {
    variables = {
      ENVIRONMENT         = var.environment
      SNS_TOPIC_ARN      = aws_sns_topic.incidents.arn
      ALERT_SNS_TOPIC_ARN = var.alert_sns_topic_arn
    }
  }
  
  tags = {
    Name = "starlink-${var.environment}-incident-responder"
  }
}

# Lambda source code
data "archive_file" "incident_responder" {
  type        = "zip"
  output_path = "${path.module}/incident_responder.zip"
  
  source {
    content  = <<-EOF
      import json
      import boto3
      import os
      from datetime import datetime
      
      sns = boto3.client('sns')
      ec2 = boto3.client('ec2')
      
      def handler(event, context):
          """
          Automated incident response handler
          Responds to security events and takes appropriate action
          """
          print(f"Received event: {json.dumps(event)}")
          
          # Parse the event
          detail = event.get('detail', {})
          severity = detail.get('severity', 0)
          finding_type = detail.get('type', 'Unknown')
          
          # Prepare incident report
          incident_report = {
              'timestamp': datetime.utcnow().isoformat(),
              'severity': severity,
              'type': finding_type,
              'environment': os.environ['ENVIRONMENT'],
              'details': detail
          }
          
          # Take action based on severity
          if severity >= 7:
              # High severity - isolate affected resources
              resource_id = detail.get('resource', {}).get('instanceDetails', {}).get('instanceId')
              if resource_id:
                  try:
                      # Isolate instance by modifying security group
                      response = isolate_instance(resource_id)
                      incident_report['action'] = 'Instance isolated'
                      incident_report['isolation_response'] = response
                  except Exception as e:
                      incident_report['error'] = str(e)
          
          # Send notification to incident response team
          sns.publish(
              TopicArn=os.environ['SNS_TOPIC_ARN'],
              Subject=f"Security Incident - Severity {severity}",
              Message=json.dumps(incident_report, indent=2)
          )
          
          return {
              'statusCode': 200,
              'body': json.dumps(incident_report)
          }
      
      def isolate_instance(instance_id):
          """Isolate EC2 instance by modifying security group"""
          try:
              # Create isolation security group if it doesn't exist
              isolation_sg = create_isolation_security_group()
              
              # Modify instance to use isolation security group
              response = ec2.modify_instance_attribute(
                  InstanceId=instance_id,
                  Groups=[isolation_sg]
              )
              
              return {
                  'instance_id': instance_id,
                  'isolation_sg': isolation_sg,
                  'status': 'isolated'
              }
          except Exception as e:
              raise Exception(f"Failed to isolate instance: {str(e)}")
      
      def create_isolation_security_group():
          """Create or get isolation security group"""
          sg_name = f"starlink-{os.environ['ENVIRONMENT']}-isolation"
          
          try:
              # Try to find existing security group
              response = ec2.describe_security_groups(
                  Filters=[
                      {'Name': 'group-name', 'Values': [sg_name]}
                  ]
              )
              
              if response['SecurityGroups']:
                  return response['SecurityGroups'][0]['GroupId']
              
              # Create new isolation security group (deny all)
              vpc_id = os.environ.get('VPC_ID')
              response = ec2.create_security_group(
                  GroupName=sg_name,
                  Description='Isolation security group for incident response',
                  VpcId=vpc_id
              )
              
              # Remove default egress rule
              sg_id = response['GroupId']
              ec2.revoke_security_group_egress(
                  GroupId=sg_id,
                  IpPermissions=[{
                      'IpProtocol': '-1',
                      'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
                  }]
              )
              
              return sg_id
          except Exception as e:
              raise Exception(f"Failed to create isolation security group: {str(e)}")
    EOF
    filename = "index.py"
  }
}

# IAM role for Lambda
resource "aws_iam_role" "incident_responder" {
  name = "starlink-${var.environment}-incident-responder-role"
  
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

resource "aws_iam_role_policy" "incident_responder" {
  name = "starlink-${var.environment}-incident-responder-policy"
  role = aws_iam_role.incident_responder.id
  
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
          "sns:Publish"
        ]
        Resource = [
          aws_sns_topic.incidents.arn,
          var.alert_sns_topic_arn
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "ec2:DescribeSecurityGroups",
          "ec2:CreateSecurityGroup",
          "ec2:ModifyInstanceAttribute",
          "ec2:RevokeSecurityGroupEgress"
        ]
        Resource = "*"
      }
    ]
  })
}

# EventBridge rule to trigger incident response
resource "aws_cloudwatch_event_rule" "security_incidents" {
  name        = "starlink-${var.environment}-security-incidents"
  description = "Trigger incident response on security events"
  
  event_pattern = jsonencode({
    source      = ["aws.guardduty", "aws.securityhub"]
    detail-type = ["GuardDuty Finding", "Security Hub Findings - Imported"]
  })
}

resource "aws_cloudwatch_event_target" "incident_responder" {
  rule      = aws_cloudwatch_event_rule.security_incidents.name
  target_id = "IncidentResponder"
  arn       = aws_lambda_function.incident_responder.arn
}

resource "aws_lambda_permission" "allow_eventbridge" {
  statement_id  = "AllowExecutionFromEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.incident_responder.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.security_incidents.arn
}

# CloudWatch Log Group for Lambda
resource "aws_cloudwatch_log_group" "incident_responder" {
  name              = "/aws/lambda/${aws_lambda_function.incident_responder.function_name}"
  retention_in_days = 30
  
  tags = {
    Name = "starlink-${var.environment}-incident-responder-logs"
  }
}

# Step Functions for incident workflow
resource "aws_sfn_state_machine" "incident_workflow" {
  name     = "starlink-${var.environment}-incident-workflow"
  role_arn = aws_iam_role.step_functions.arn
  
  definition = jsonencode({
    Comment = "Incident response workflow"
    StartAt = "DetectIncident"
    States = {
      DetectIncident = {
        Type = "Task"
        Resource = aws_lambda_function.incident_responder.arn
        Next = "NotifyTeam"
      }
      NotifyTeam = {
        Type = "Task"
        Resource = "arn:aws:states:::sns:publish"
        Parameters = {
          TopicArn = aws_sns_topic.incidents.arn
          Message  = "Security incident detected and response initiated"
        }
        End = true
      }
    }
  })
  
  tags = {
    Name = "starlink-${var.environment}-incident-workflow"
  }
}

resource "aws_iam_role" "step_functions" {
  name = "starlink-${var.environment}-step-functions-role"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "states.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy" "step_functions" {
  name = "starlink-${var.environment}-step-functions-policy"
  role = aws_iam_role.step_functions.id
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "lambda:InvokeFunction"
        ]
        Resource = aws_lambda_function.incident_responder.arn
      },
      {
        Effect = "Allow"
        Action = [
          "sns:Publish"
        ]
        Resource = aws_sns_topic.incidents.arn
      }
    ]
  })
}
