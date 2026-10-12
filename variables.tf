variable "region" {
  description = "The AWS region where your primary application resides."
  type        = string
  default     = "us-east-1"
}

variable "app_name" {
  description = "The target application prefix name (e.g., feedback-app)."
  type        = string
}

variable "target_vpc_id" {
  description = "The ID of the primary application VPC."
  type        = string
}

variable "target_subnet_id" {
  description = "The exact public subnet ID where the main Fargate service runs."
  type        = string
}

variable "target_security_group_id" {
  description = "The primary firewall security group ID to bind for network line-of-sight."
  type        = string
}

variable "target_ecs_cluster_name" {
  description = "The target execution cluster housing the Fargate system engine."
  type        = string
}

variable "ecs_service_name_string" {
  description = "The runtime orchestrator supervising the application availability state."
  type        = string
  default     = "feedback-app-service"
}