# Cash Tracker Architecture

## Purpose
This document describes the current architecture of the Cash Tracker system for local development and AWS deployment.

## Scope
- Frontend SPA in React served by Nginx
- Backend API in Flask (Gunicorn in containers)
- File-based persistence using JSON data files
- AWS runtime on ECS Fargate with ALB path routing and EFS-backed backend storage

## C4 Model

### Level 1: System Context
```mermaid
C4Context
title Cash Tracker - System Context
Person(user, "End User", "Tracks purchases, cash received, and balance")
System(cashTracker, "Cash Tracker", "Web app for cash transaction tracking and analytics")
System_Ext(aws, "AWS", "Cloud runtime platform")
System_Ext(localFiles, "JSON Data Files", "Transactions and category metadata")

Rel(user, cashTracker, "Uses via browser", "HTTPS")
Rel(cashTracker, aws, "Runs on", "ECS Fargate + ALB + EFS")
Rel(cashTracker, localFiles, "Reads/Writes", "JSON")
```

### Level 2: Container Diagram
```mermaid
C4Container
title Cash Tracker - Container View
Person(user, "End User")
System_Boundary(c1, "Cash Tracker") {
  Container(frontend, "Frontend Container", "React + Nginx", "Serves SPA and static assets")
  Container(backend, "Backend Container", "Flask + Gunicorn", "Implements /api endpoints and business logic")
  ContainerDb(efs, "Backend Data Store", "Amazon EFS", "Persistent files mounted at /app/data")
}
System_Ext(alb, "Application Load Balancer", "Routes /api/* and /health* to backend; all else to frontend")
System_Ext(ecr, "Amazon ECR", "Stores versioned container images")
System_Ext(cw, "CloudWatch Logs", "Centralized container logs")

Rel(user, alb, "Accesses app", "HTTP")
Rel(alb, frontend, "Forwards /", "HTTP:80")
Rel(alb, backend, "Forwards /api/* and /health*", "HTTP:5001")
Rel(frontend, backend, "Calls APIs through ALB path routing", "HTTP /api/*")
Rel(backend, efs, "Reads/Writes transaction files", "NFS")
Rel(frontend, cw, "Writes logs", "awslogs")
Rel(backend, cw, "Writes logs", "awslogs")
Rel(ecr, frontend, "Provides image", "Pull")
Rel(ecr, backend, "Provides image", "Pull")
```

### Level 3: Backend Component Diagram
```mermaid
C4Component
title Cash Tracker - Backend Components (backend/app.py)
Container_Boundary(api, "Flask API Container") {
  Component(routes, "API Routes", "Flask route handlers", "Handles /api/transactions, /api/cash-received, /api/balance, /api/analytics, etc")
  Component(normalizer, "Transaction Normalizer", "Helper functions", "Normalizes date fields and response schema")
  Component(balanceEngine, "Balance + Analytics Engine", "In-process logic", "Computes monthly and total balances and category analytics")
  Component(persistence, "JSON Persistence", "File I/O", "Loads and saves transactions/categories synchronously")
}
ContainerDb(files, "Data Files", "JSON on EFS", "transactions.json, categories.json")

Rel(routes, normalizer, "Normalizes payloads and records")
Rel(routes, balanceEngine, "Requests computed balances/analytics")
Rel(routes, persistence, "Reads/Writes domain data")
Rel(persistence, files, "File read/write")
Rel(balanceEngine, persistence, "Uses loaded transactions")
```

## Deployment View (AWS)
- Network: one VPC, public subnets, internet gateway
- Compute: one ECS cluster with two Fargate services
- Entry: internet-facing ALB on HTTP/80
- Routing:
  - /api/* and /health* to backend target group (port 5001)
  - all other paths to frontend target group (port 80)
- Storage: backend mounts EFS at /app/data for persistent JSON files
- Registry: ECR repositories for frontend and backend images
- Logging: CloudWatch log groups for both services

## Runtime Flows
1. User opens / in browser.
2. ALB forwards request to frontend container.
3. Frontend calls /api/*.
4. ALB routes API call to backend container.
5. Backend reads/writes JSON data in EFS and returns response.

## Key Decisions
- File persistence over database for simplicity and low setup overhead
- ALB path-based routing to keep frontend/backend independently deployable
- EFS for persistence across backend task restarts/redeployments
- Immutable image tags in ECR for predictable ECS rollouts

## Risks and Constraints
- Synchronous file I/O can limit throughput under higher concurrency
- No transactional guarantees typical of RDBMS systems
- Single backend code file increases maintenance risk as complexity grows
- Public subnet design is simple but not hardened for production-grade security

## Code and Infra References
- Backend API: [backend/app.py](backend/app.py)
- Frontend app: [frontend/src/App.js](frontend/src/App.js)
- Frontend nginx config: [frontend/nginx.conf](frontend/nginx.conf)
- Terraform infra: [infra/terraform/main.tf](infra/terraform/main.tf)
- Deployment script: [deploy_aws.sh](deploy_aws.sh)
