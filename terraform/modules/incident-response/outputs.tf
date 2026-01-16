output "sns_topic_arn" {
  description = "Incident response SNS topic ARN"
  value       = aws_sns_topic.incidents.arn
}

output "lambda_function_arn" {
  description = "Incident responder Lambda function ARN"
  value       = aws_lambda_function.incident_responder.arn
}

output "workflow_arn" {
  description = "Step Functions workflow ARN"
  value       = aws_sfn_state_machine.incident_workflow.arn
}
