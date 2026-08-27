output "lambda_function_name" {
  description = "Name of the Telegram monitoring Lambda"
  value       = aws_lambda_function.telegram_monitor.function_name
}

output "lambda_function_arn" {
  description = "ARN of the Telegram monitoring Lambda"
  value       = aws_lambda_function.telegram_monitor.arn
}

output "eventbridge_rule_name" {
  description = "EventBridge rule for AWS resource changes"
  value       = aws_cloudwatch_event_rule.aws_resource_changes.name
}

output "eventbridge_rule_arn" {
  description = "ARN of the EventBridge rule"
  value       = aws_cloudwatch_event_rule.aws_resource_changes.arn
}

output "lambda_iam_role_arn" {
  description = "IAM role ARN used by the Lambda"
  value       = aws_iam_role.lambda_role.arn
}

output "aws_region" {
  description = "AWS region being monitored"
  value       = "ap-south-1"
}

output "telegram_webhook_url" {
  description = "API Gateway URL used as Telegram webhook"
  value       = aws_apigatewayv2_api.telegram.api_endpoint
}