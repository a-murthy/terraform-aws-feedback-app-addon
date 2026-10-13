terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
    tfe = {
      source  = "hashicorp/tfe"
      version = "~> 0.50.0"
    }
    time = {
      source  = "hashicorp/time"
      version = "~> 0.9.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# ==============================================================================
# REFERENCE-REPLICATED WORKSPACE DISCOVERY MATRIX
# ==============================================================================
locals {
  resolved_app_name = var.developer_portal_application != null ? var.developer_portal_application : var.target_app_name
}

# 1. DYNAMIC DISCOVERY: Pinpoints the active application workspace
data "tfe_workspace" "core_ws" {
  organization = var.hcp_organization
  
  # Follows your flawless reference app mapping pattern exactly
  name = var.developer_portal_application != null ? var.developer_portal_application : var.target_app_name
}

# 2. STATE LOOKUP: Automatically grabs structural parameters from your application workspace
data "tfe_outputs" "core" {
  organization = var.hcp_organization
  workspace    = data.tfe_workspace.core_ws.name
}

# ==============================================================================
# AUTOMATED BUSINESS LOGIC COMPILATION
# ==============================================================================
data "archive_file" "lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/index.py"
  output_path = "${path.module}/lambda_function.zip"
}

# ==============================================================================
# IMMUTABLE SANDBOX ENVIRONMENT ROLE LOOKUP (Bypasses Service Principals)
# ==============================================================================
# Uses the standard admin-approved execution role pre-built inside your sandbox
data "aws_iam_role" "sandbox_lambda_role" {
  name = "LabRole" 
}

# ==============================================================================
# COMPUTE ENGINE (Runs in Native Space for Internet Access to Amazon Comprehend)
# ==============================================================================
resource "aws_lambda_function" "ai_sentiment_processor" {
  filename         = data.archive_file.lambda_zip.output_path
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256
  function_name    = "${local.resolved_app_name}-ai-engine"
  handler          = "index.handler"
  runtime          = "python3.11"
  
  # Points directly to the pre-existing admin role inside your sandbox account
  role             = data.aws_iam_role.sandbox_lambda_role.arn
}

resource "aws_lambda_function_url" "ai_endpoint" {
  function_name      = aws_lambda_function.ai_sentiment_processor.function_name
  authorization_type = "NONE"

  cors {
    allow_origins     = ["*"]
    allow_methods     = ["POST"]
    allow_headers     = ["content-type"]
    max_age           = 86400
  }
}

# ==============================================================================
# AUTOMATED DYNAMIC BACK-INJECTION (Matches Reference App Pattern)
# ==============================================================================
resource "tfe_variable" "inject_ai_url" {
  key          = "ai_endpoint_url"
  value        = aws_lambda_function_url.ai_endpoint.function_url
  category     = "terraform"
  workspace_id = data.tfe_workspace.core_ws.id
  description  = "Injected dynamically for application: ${local.resolved_app_name}."
}

resource "tfe_variable" "inject_ai_toggle" {
  key          = "ai_enabled"
  value        = "true"
  category     = "terraform"
  workspace_id = data.tfe_workspace.core_ws.id
  description  = "Activated dynamically for application: ${local.resolved_app_name}."
}

resource "tfe_workspace_run" "trigger_app_deploy" {
  workspace_id = data.tfe_workspace.core_ws.id
  depends_on   = [tfe_variable.inject_ai_url, tfe_variable.inject_ai_toggle]

  apply {
    manual_confirm = false
  }
}

# ==============================================================================
# VALID DAY 2 OPERATIONS ENGINE (Valid HCL Resource Block)
# ==============================================================================
resource "aws_lambda_invocation" "platform_maintenance_lockdown" {
  count         = var.maintenance_mode == "true" ? 1 : 0
  function_name = aws_lambda_function.ai_sentiment_processor.function_name

  input = jsonencode({
    event                 = "manual_emergency_lockout"
    target_cluster_string = data.tfe_outputs.core.values.ecs_cluster_name
    target_service_string = data.tfe_outputs.core.values.ecs_service_name
    execution_state       = "active"
    maintenance_mode      = "true"
  })
}
