variable "aws_region" {
  description = "AWS region for all resources."
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Project name prefix for resources."
  type        = string
  default     = "cash-tracker"
}

variable "environment" {
  description = "Environment name."
  type        = string
  default     = "dev"
}

variable "ephemeral_environment" {
  description = "If true, enables destroy-friendly behavior for short-lived test stacks (for example ECR force delete)."
  type        = bool
  default     = false
}

variable "log_retention_in_days" {
  description = "CloudWatch log retention period in days."
  type        = number
  default     = 14
}

variable "vpc_cidr" {
  description = "VPC CIDR block."
  type        = string
  default     = "10.42.0.0/16"
}

variable "availability_zone_count" {
  description = "Number of AZs / public subnets to create."
  type        = number
  default     = 2
}

variable "frontend_image" {
  description = "Frontend image URI (ECR URI:tag). If empty, defaults to created ECR repo with :latest."
  type        = string
  default     = ""
}

variable "backend_image" {
  description = "Backend image URI (ECR URI:tag). If empty, defaults to created ECR repo with :latest."
  type        = string
  default     = ""
}

variable "frontend_cpu" {
  description = "Frontend task CPU units."
  type        = number
  default     = 256
}

variable "frontend_memory" {
  description = "Frontend task memory (MiB)."
  type        = number
  default     = 512
}

variable "backend_cpu" {
  description = "Backend task CPU units."
  type        = number
  default     = 512
}

variable "backend_memory" {
  description = "Backend task memory (MiB)."
  type        = number
  default     = 1024
}

variable "frontend_desired_count" {
  description = "Desired frontend task count."
  type        = number
  default     = 1
}

variable "backend_desired_count" {
  description = "Desired backend task count."
  type        = number
  default     = 1
}
