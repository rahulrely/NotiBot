resource "aws_apigatewayv2_api" "telegram" {
  name          = "aws-telegram-monitor-api"
  protocol_type = "HTTP"
}

resource "aws_apigatewayv2_stage" "telegram" {
  api_id = aws_apigatewayv2_api.telegram.id

  name = "$default"

  auto_deploy = true
}

resource "aws_apigatewayv2_integration" "lambda" {
  api_id = aws_apigatewayv2_api.telegram.id

  integration_type = "AWS_PROXY"

  integration_uri = aws_lambda_function.telegram_monitor.invoke_arn

  payload_format_version = "2.0"
}

resource "aws_apigatewayv2_route" "telegram" {
  api_id = aws_apigatewayv2_api.telegram.id

  route_key = "POST /"

  target = "integrations/${aws_apigatewayv2_integration.lambda.id}"
}

resource "aws_lambda_permission" "allow_api_gateway" {
  statement_id = "AllowAPIGatewayInvoke"

  action = "lambda:InvokeFunction"

  function_name = aws_lambda_function.telegram_monitor.function_name

  principal = "apigateway.amazonaws.com"

  source_arn = "${aws_apigatewayv2_api.telegram.execution_arn}/*/*"
}