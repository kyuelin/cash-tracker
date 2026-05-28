aws_region              = "us-east-1"
project_name            = "cash-tracker"
environment             = "dev"
availability_zone_count = 2
ephemeral_environment   = true
log_retention_in_days   = 1

# Set these after pushing Docker images to ECR.
# If left empty, Terraform will still create ECR repos and services will point to :latest in those repos.
frontend_image = "093086864378.dkr.ecr.us-east-1.amazonaws.com/cash-tracker-dev-frontend:v4"
backend_image = "093086864378.dkr.ecr.us-east-1.amazonaws.com/cash-tracker-dev-backend:v4"

frontend_desired_count = 1
backend_desired_count  = 1
