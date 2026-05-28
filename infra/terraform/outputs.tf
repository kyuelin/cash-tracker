output "alb_dns_name" {
  description = "Application URL base."
  value       = aws_lb.main.dns_name
}

output "frontend_ecr_repository_url" {
  description = "ECR repository URL for frontend image."
  value       = aws_ecr_repository.frontend.repository_url
}

output "backend_ecr_repository_url" {
  description = "ECR repository URL for backend image."
  value       = aws_ecr_repository.backend.repository_url
}

output "ecs_cluster_name" {
  description = "ECS cluster name."
  value       = aws_ecs_cluster.main.name
}

output "backend_efs_file_system_id" {
  description = "EFS filesystem backing backend data directory."
  value       = aws_efs_file_system.backend_data.id
}
