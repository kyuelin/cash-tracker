# Cash Tracker Application

A full-stack application for tracking cash purchases with React frontend and Python Flask backend.

## Repository contents

Full-stack cash tracking app with a React frontend, Flask backend, and Terraform AWS deployment.

- `ARCHITECTURE.md` — architecture overview and diagrams
- `backend/` — Flask API and JSON persistence
- `frontend/` — React UI and client-side code
- `infra/` — Terraform for AWS ECS/EFS deployment
- `deploy_aws.sh` — one-command build/push/deploy helper
- `start_app.sh` — start both services locally
- `start_backend.sh` — start the API only
- `start_frontend.sh` — start the UI only
- `docker-compose.yml` — local full-stack container setup
- `tracker.postman_collection.json` — API request collection
## Index

| Section | Link |
|---|---|
| Architecture | [Architecture](#architecture) |
| Quick Start | [Quick Start](#quick-start) |
| Docker (local testing) | [Docker (local testing)](#docker-local-testing) |
| AWS ECS deployment (Terraform + EFS) | [AWS ECS deployment (Terraform + EFS)](#aws-ecs-deployment-terraform--efs) |
| Manual Setup | [Manual Setup](#manual-setup) |
| Features | [Features](#features) |
| File Structure | [File Structure](#file-structure) |
| Deployment on Mac Mini | [Deployment on Mac Mini](#deployment-on-mac-mini) |
| Data Backup | [Data Backup](#data-backup) |
| Troubleshooting | [Troubleshooting](#troubleshooting) |
| API Endpoints | [API Endpoints](#api-endpoints) |
| License | [License](#license) |

## Architecture

See [ARCHITECTURE.md](ARCHITECTURE.md) for system design details and C4 diagrams.

## Quick Start

1. Copy all the code from the artifacts into their respective files:
   - Copy Flask app code to `backend/app.py`
   - Copy React components to `frontend/src/components/`
   - Copy App.js to `frontend/src/App.js`
   - Copy App.css to `frontend/src/App.css`
   - Copy tailwind.config.js to `frontend/tailwind.config.js`

2. Start the application:
   ```bash
   ./start_app.sh
   ```

3. Access the application:
    - Frontend: http://localhost:3000
    - Backend API: http://localhost:5001

## Docker (local testing)

Run the full stack (Flask API + React UI served by Nginx):

```bash
docker compose up --build
```

Endpoints:
- UI: http://localhost:3000
- API health: http://localhost:5001/health

Stop and clean up:

```bash
docker compose down
```

## AWS ECS deployment (Terraform + EFS)

Terraform for AWS provisioning is in `infra/terraform/` and creates:
- VPC + public subnets + internet gateway
- ECS Fargate cluster with separate frontend/backend services
- Application Load Balancer with path routing:
  - `/api/*` and `/health*` -> backend
  - all other paths -> frontend
- ECR repos for both images
- EFS mounted to backend at `/app/data` (persistent JSON storage)

### AWS authentication setup (CLI profile)

IAM Identity Center setup reference (AWS docs):
- Enable IAM Identity Center: https://docs.aws.amazon.com/singlesignon/latest/userguide/get-started-enable-identity-center.html
- Configure AWS CLI with IAM Identity Center: https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-sso.html
- Assign users/groups and permission sets to accounts: https://docs.aws.amazon.com/singlesignon/latest/userguide/assignusers.html

Install and verify AWS CLI v2:

```bash
aws --version
```

List local AWS profiles:

```bash
aws configure list-profiles
```

#### Option A: IAM Identity Center (SSO)

Configure SSO profile:

```bash
aws configure sso
```

Recommended values for this project:
- Start URL: your IAM Identity Center access portal URL (for example `https://d-xxxxxxxxxx.awsapps.com/start`)
- Network: `ipv4-only`
- SSO registration scopes: `sso:account:access`
- Region: `us-east-1`
- Output: `json`
- Profile name: `cash-tracker-sso`

Login and verify:

```bash
aws sso login --profile cash-tracker-sso
aws sts get-caller-identity --profile cash-tracker-sso
```

Set active profile for current shell:

```bash
export AWS_PROFILE=cash-tracker-sso
export AWS_REGION=us-east-1
```

#### Option B: Static IAM access keys

```bash
aws configure
aws sts get-caller-identity
```

### Common credential fix (InvalidClientTokenId)

If Terraform fails with `InvalidClientTokenId`, clear conflicting env vars and re-login:

```bash
unset AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY AWS_SESSION_TOKEN AWS_SECURITY_TOKEN AWS_DEFAULT_PROFILE
export AWS_PROFILE=cash-tracker-sso
export AWS_REGION=us-east-1
export AWS_SDK_LOAD_CONFIG=1
aws sso login --profile cash-tracker-sso
aws sts get-caller-identity
```

### Provision infrastructure

```bash
cd infra/terraform
cp terraform.tfvars.example terraform.tfvars
terraform init
terraform apply
```

### Push images to ECR

Use the `frontend_ecr_repository_url` and `backend_ecr_repository_url` Terraform outputs:

```bash
# From repo root
aws ecr get-login-password --region <region> | docker login --username AWS --password-stdin <account-id>.dkr.ecr.<region>.amazonaws.com

docker build -t <frontend-repo-url>:v1 ./frontend
docker push <frontend-repo-url>:v1

docker build -t <backend-repo-url>:v1 ./backend
docker push <backend-repo-url>:v1
```

Set `frontend_image` and `backend_image` in `infra/terraform/terraform.tfvars`, then run:

```bash
cd infra/terraform
terraform apply
```

### One-command build, push, and deploy

You can run the full flow (ensure ECR repos, build images, push to ECR, update image URIs in tfvars, and apply Terraform) with:

```bash
chmod +x deploy_aws.sh
./deploy_aws.sh --tag v1
```

Optional auto-approve mode:

```bash
./deploy_aws.sh --tag v1 --auto-approve
```

### Destroy infrastructure

Preview destroy plan:

```bash
cd infra/terraform
terraform plan -destroy
```

Destroy resources:

```bash
terraform destroy
```

Non-interactive destroy:

```bash
terraform destroy -auto-approve
```

## Manual Setup

### Backend
```bash
cd backend
source venv/bin/activate
python app.py
```

### Frontend
```bash
cd frontend
npm start
```

## Features

- ✅ Transaction entry with smart category suggestions
- ✅ Description autocomplete
- ✅ Real-time balance tracking
- ✅ Cash received tracking
- ✅ Transaction history with pagination and filtering
- ✅ Analytics with bar and pie charts
- ✅ Mobile-responsive design
- ✅ Data persistence in JSON files

## File Structure

```
cash-tracker/
├── backend/
│   ├── app.py                 # Flask application
│   ├── requirements.txt       # Python dependencies
│   ├── venv/                 # Virtual environment
│   └── data/
│       ├── transactions.json  # Transaction data
│       └── categories.json    # Categories and descriptions
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   │   ├── TransactionForm.js
│   │   │   ├── TransactionHistory.js
│   │   │   └── Analytics.js
│   │   ├── App.js
│   │   ├── App.css
│   │   └── index.js
│   ├── package.json
│   └── tailwind.config.js
├── start_app.sh              # Start both services
├── start_backend.sh          # Start backend only
└── start_frontend.sh         # Start frontend only
```

## Deployment on Mac Mini

1. **Install Prerequisites:**
   - Python 3.8+: `brew install python`
   - Node.js 14+: `brew install node`

2. **Clone and Setup:**
   ```bash
   git clone <your-repo> cash-tracker
   cd cash-tracker
   chmod +x *.sh
   ./start_app.sh
   ```

3. **Access from Mobile:**
    - Find your Mac Mini IP: `ifconfig | grep inet`
    - Access from iOS: `http://[MAC_MINI_IP]:5001`

## Data Backup

Your transaction data is stored in `backend/data/`. Regular backups are recommended:

```bash
# Backup
cp -r backend/data backend/data_backup_20250811

# Restore
cp -r backend/data_backup_YYYYMMDD backend/data
```

## Troubleshooting

### Port Already in Use
```bash
# Kill processes on port 5001
lsof -ti:5001 | xargs kill -9

# Kill processes on port 3000  
lsof -ti:3000 | xargs kill -9
```

### Python Virtual Environment Issues
```bash
cd backend
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Node Dependencies Issues
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

## API Endpoints

- `GET /api/transactions` - Get transactions with pagination
- `POST /api/transactions` - Add new transaction
- `POST /api/cash-received` - Add cash received
- `GET /api/categories` - Get categories and descriptions
- `POST /api/suggestions/category` - Get category suggestion
- `GET /api/suggestions/description` - Get description suggestions
- `GET /api/balance` - Get current balance
- `GET /api/analytics` - Get analytics data

## License

MIT License - feel free to modify and distribute.

## Maturity review

**Maturity:** Functional MVP with a working local stack and an AWS deployment path.

**What remains to make this a functional application:**
- Add stronger auth/permission handling if it is meant for multiple users.
- Expand automated tests around the API, UI, and deployment flow.
- Harden backup, monitoring, and error handling for production use.
