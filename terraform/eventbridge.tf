resource "aws_cloudwatch_event_rule" "aws_resource_changes" {
  name        = "aws-resource-create-delete"
  description = "Detect AWS resource creation and deletion events"

  event_pattern = jsonencode({
    detail-type = [
      "AWS API Call via CloudTrail"
    ]

    detail = {
      eventName = [
        {
          prefix = "Create"
        },
        {
          prefix = "Delete"
        },
        {
          prefix = "Run"
        },
        {
          prefix = "Terminate"
        }
      ]
    }
  })
}

resource "aws_cloudwatch_event_target" "lambda" {
  rule = aws_cloudwatch_event_rule.aws_resource_changes.name
  arn  = aws_lambda_function.telegram_monitor.arn
}

resource "aws_lambda_permission" "allow_eventbridge" {
  statement_id = "AllowEventBridgeInvoke"

  action = "lambda:InvokeFunction"

  function_name = aws_lambda_function.telegram_monitor.function_name

  principal = "events.amazonaws.com"

  source_arn = aws_cloudwatch_event_rule.aws_resource_changes.arn
}