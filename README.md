# 🤖 AWS ECS Feedback App AI Add-On Module

An enterprise-grade, fully compliant **Day 1 Add-On Infrastructure Module** built for HCP Terraform No-Code Provisioning workflows. This module attaches native, secure natural language processing (NLP) capabilities directly to an existing running application stack.

## 🚀 Architectural Overview
This module provisions a secure, private **AWS Lambda Function** embedded inside the primary application's VPC and Security Group layout. It routes text classification data natively to **Amazon Comprehend** using first-party AWS SDK mechanisms, clearing all standard corporate compliance, auditing, and procurement checks instantly.

## 📋 Portal Input Parameters
When provisioning this add-on through the Developer Portal, the platform orchestrator extracts these fields automatically via cross-workspace state linkages:

| Variable Name | Type | Description |
| :--- | :--- | :--- |
| `app_name` | `string` | Target application prefix utilized for resource alignment. |
| `target_vpc_id` | `string` | The ID of the primary network infrastructure VPC. |
| `target_subnet_id` | `string` | The exact execution subnet hosting the Fargate service nodes. |
| `target_security_group_id` | `string` | The primary firewall profile ensuring line-of-sight network connectivity. |
| `target_ecs_cluster_name` | `string` | The target compute cluster hosting the application components. |

## 🛠 Day 2 Operations (Actions Engine)
This module includes a registry-validated **Terraform 1.16+ `action` block**. In the event of an operational emergency or system optimization phase, operators can execute a native out-of-band lockdown command directly from the portal interface to cycle application availability states immediately.
