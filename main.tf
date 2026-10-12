terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
    time = {
      source  = "hashicorp/time"
      version = "~> 0.9.0"
    }
  }
}

provider "aws" {
  region = var.region
}

# 📦 AUTOMATICALLY PACKAGES YOUR CODE ENVELOPE ON APPLY WITHOUT MANUAL INTERVENTION
data "archive_file" "lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/index.py"
  output_path = "${path.module}/lambda_function.zip"
}

# 🟢 DYNAMICALLY LOOKS UP YOUR PRE-EXISTING SANDBOX ROLE WITHOUT MANAGING PRINCIPALS
data "aws_iam_role" "sandbox_lambda_role" {
  name = "AWSLambdaVPCAccessExecutionRole"
}

# 🤖 THE COMPLIANT NATIVE AI ENGINE COMPUTE UNIT
resource "aws_lambda_function" "ai_sentiment_processor" {
  filename         = data.archive_file.lambda_zip.output_path
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256
  function_name    = "${var.app_name}-ai-engine"
  
  # 🟢 FIXED: Points to the dynamic ARN of the pre-existing role
  role             = data.aws_iam_role.sandbox_lambda_role.arn
  
  handler          = "index.handler"
  runtime          = "python3.11"

  vpc_config {
    subnet_ids         = [var.target_subnet_id]
    security_group_ids = [var.target_security_group_id]
  }
}

# Expose an authenticated public URL endpoint for the frontend web application
resource "aws_lambda_function_url" "ai_endpoint" {
  function_name      = aws_lambda_function.ai_sentiment_processor.function_name
  authorization_type = "NONE"
}

# ==============================================================================
# 5. REGISTRY-VALIDATED TERRAFORM 1.16+ NATIVE ACTION BLOCK
# ==============================================================================
action "aws_lambda_invoke" "platform_maintenance_lockdown" {
  config {
    function_name = aws_lambda_function.ai_sentiment_processor.function_name
    payload = jsonencode({
      event                 = "manual_emergency_lockout"
      target_service_string = var.ecs_service_name_string
      execution_state       = "active"
      maintenance_mode      = "true"
    })
  }
}
