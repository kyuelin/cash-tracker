#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TF_DIR="$ROOT_DIR/infra/terraform"
TFVARS_FILE="$TF_DIR/terraform.tfvars"

AUTO_APPROVE=false
IMAGE_TAG="${IMAGE_TAG:-}"
IMAGE_PLATFORM="${IMAGE_PLATFORM:-linux/amd64}"

usage() {
  cat <<'EOF'
Usage: ./deploy_aws.sh [--tag <image-tag>] [--platform <docker-platform>] [--auto-approve]

Builds frontend/backend Docker images, pushes them to ECR, updates terraform.tfvars,
and runs terraform apply.

Options:
  --tag <image-tag>   Image tag to use for both images (default: timestamp)
  --platform <value>  Docker build platform (default: linux/amd64)
  --auto-approve      Pass -auto-approve to terraform apply commands
  -h, --help          Show this help message
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --tag)
      IMAGE_TAG="${2:-}"
      if [[ -z "$IMAGE_TAG" ]]; then
        echo "Error: --tag requires a value." >&2
        exit 1
      fi
      shift 2
      ;;
    --platform)
      IMAGE_PLATFORM="${2:-}"
      if [[ -z "$IMAGE_PLATFORM" ]]; then
        echo "Error: --platform requires a value." >&2
        exit 1
      fi
      shift 2
      ;;
    --auto-approve)
      AUTO_APPROVE=true
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Error: Unknown option '$1'" >&2
      usage
      exit 1
      ;;
  esac
done

if [[ -z "$IMAGE_TAG" ]]; then
  IMAGE_TAG="$(date +%Y%m%d%H%M%S)"
fi

for cmd in terraform aws docker awk; do
  if ! command -v "$cmd" >/dev/null 2>&1; then
    echo "Error: Required command '$cmd' is not installed or not in PATH." >&2
    exit 1
  fi
done

if [[ ! -f "$TFVARS_FILE" ]]; then
  echo "Error: terraform vars file not found at $TFVARS_FILE" >&2
  echo "Create it from infra/terraform/terraform.tfvars.example first." >&2
  exit 1
fi

update_tfvar() {
  local key="$1"
  local value="$2"
  local tmp_file

  tmp_file="$(mktemp)"
  awk -v key="$key" -v value="$value" '
    BEGIN { updated = 0 }
    $0 ~ "^[[:space:]]*" key "[[:space:]]*=" {
      print key " = \"" value "\""
      updated = 1
      next
    }
    { print }
    END {
      if (!updated) {
        print key " = \"" value "\""
      }
    }
  ' "$TFVARS_FILE" > "$tmp_file"

  mv "$tmp_file" "$TFVARS_FILE"
}

terraform_apply_args=()
if [[ "$AUTO_APPROVE" == "true" ]]; then
  terraform_apply_args+=("-auto-approve")
fi

echo "==> Initializing Terraform"
pushd "$TF_DIR" >/dev/null
terraform init -input=false

echo "==> Ensuring ECR repositories exist"
if [[ "$AUTO_APPROVE" == "true" ]]; then
  terraform apply -target=aws_ecr_repository.frontend -target=aws_ecr_repository.backend "${terraform_apply_args[@]}"
else
  terraform apply -target=aws_ecr_repository.frontend -target=aws_ecr_repository.backend
fi

FRONTEND_REPO_URL="$(terraform output -raw frontend_ecr_repository_url)"
BACKEND_REPO_URL="$(terraform output -raw backend_ecr_repository_url)"
AWS_REGION="$(awk -F= '/^[[:space:]]*aws_region[[:space:]]*=/{gsub(/[ \"\t]/, "", $2); print $2; exit}' "$TFVARS_FILE")"

if [[ -z "$AWS_REGION" ]]; then
  AWS_REGION="us-east-1"
fi

REGISTRY_HOST="${FRONTEND_REPO_URL%%/*}"

echo "==> Logging in to ECR ($REGISTRY_HOST)"
aws ecr get-login-password --region "$AWS_REGION" | docker login --username AWS --password-stdin "$REGISTRY_HOST"
popd >/dev/null

echo "==> Building and pushing frontend image: ${FRONTEND_REPO_URL}:${IMAGE_TAG}"
docker build --platform "$IMAGE_PLATFORM" -t "${FRONTEND_REPO_URL}:${IMAGE_TAG}" "$ROOT_DIR/frontend"
docker push "${FRONTEND_REPO_URL}:${IMAGE_TAG}"

echo "==> Building and pushing backend image: ${BACKEND_REPO_URL}:${IMAGE_TAG}"
docker build --platform "$IMAGE_PLATFORM" -t "${BACKEND_REPO_URL}:${IMAGE_TAG}" "$ROOT_DIR/backend"
docker push "${BACKEND_REPO_URL}:${IMAGE_TAG}"

echo "==> Updating terraform.tfvars image URIs"
update_tfvar "frontend_image" "${FRONTEND_REPO_URL}:${IMAGE_TAG}"
update_tfvar "backend_image" "${BACKEND_REPO_URL}:${IMAGE_TAG}"

echo "==> Applying full Terraform stack"
pushd "$TF_DIR" >/dev/null
if [[ "$AUTO_APPROVE" == "true" ]]; then
  terraform apply "${terraform_apply_args[@]}"
else
  terraform apply
fi

if terraform output alb_dns_name >/dev/null 2>&1; then
  ALB_DNS="$(terraform output -raw alb_dns_name)"
  echo "==> Deployment complete"
  echo "App URL: http://${ALB_DNS}"
else
  echo "==> Deployment complete"
fi
popd >/dev/null
