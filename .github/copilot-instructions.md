# Copilot instructions for `cash-tracker`

## Build, test, and lint commands

### Backend (Flask API)
- Install deps: `cd backend && pip install -r requirements.txt`
- Run API: `cd backend && python app.py` (binds `0.0.0.0:5001`)

### Frontend (active app in `frontend/`)
- Install deps: `cd frontend && npm install`
- Dev server: `cd frontend && npm start`
- Production build: `cd frontend && npm run build`
- Test suite: `cd frontend && npm test -- --watch=false`
- Single test (if you add tests): `cd frontend && npm test -- --watch=false --runTestsByPath src/<test-file>.test.js`

### Infrastructure (Terraform for ECS + EFS)
- Terraform init/apply: `cd infra/terraform && terraform init && terraform apply`
- Terraform format: `cd infra/terraform && terraform fmt -recursive`

## High-level architecture

- The backend is a single-file Flask API in `backend/app.py` with file-based persistence (JSON), not a database.
- API endpoints under `/api/*` read and write two JSON files:
  - transactions: `backend/transactions.json`
  - categories/descriptions: `backend/data/categories.json`
- Core backend flow:
  - `load_data()` normalizes transaction records and limits transaction fields
  - write operations (`/api/transactions`, `/api/cash-received`) persist immediately to JSON files
  - analytics and balance endpoints compute aggregates from in-memory loaded JSON each request
- The frontend (`frontend/src/`) is a tabbed SPA:
  - `TransactionForm` creates purchases/cash-received entries and triggers balance refresh
  - `TransactionHistory` handles query-string filtering, sorting, and pagination against `/api/transactions`
  - `Analytics` renders category aggregates from `/api/analytics` via Recharts

## Key repository conventions

- Treat `frontend/` as the active UI used by root start scripts and deployment scripts.
- The backend is the source of truth for API field names; prefer `transaction_date`, `description`, `category`, and numeric `amount` in payloads and responses.
- Date filtering and month balance logic rely on `YYYY-MM` string prefix matching in transaction dates.
- Persistence is synchronous file I/O in request handlers; changes to write paths or schema should keep backward compatibility with existing JSON structure (`transactions` and `cash_received` arrays).
- Styling follows Tailwind utility classes plus shared utility classes in `frontend/src/App.css`; keep new UI consistent with this pattern.
- AWS deployment convention in this repo is ALB path routing (`/api/*` to backend, other paths to frontend) with backend data persisted via EFS mounted at `/app/data`.
