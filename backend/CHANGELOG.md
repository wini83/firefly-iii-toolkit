## 0.4.2 (2025-11-30)

### Fix

- **api**: CORS middleware added
- **main**: Updated main.py to import settings first and remove deprecated dotenv calls

## 0.4.1 (2025-11-29)

### Refactor

- **config**: introduce Settings class and centralized .env loading
- **project**: reorganize project structure into backend + frontend architecture

## 0.4.0 (2025-11-27)

### Feat

- **frontend**: first working prototype

### Refactor

- **frontend**: improved ui
- **frontend**: new template introduced
- **frontend**: new template (wip)
- **frontend**: WIP
- **frontend**: new "file" endpoint
- **api+frontend**: -introduction of a new frontend file endpoint

## 0.3.0 (2025-11-22)

### Feat

- **api:file**: add csv preview, match processing and selective apply flow using in-memory storage
- **auth**: add X-Token header authentication with APIKeyHeader and env-based token validation

### Fix

- **api**: version form pyproject.toml
- **api**: overall small issues fix
- **api**: correction small error
- **api**: import error fix

### Refactor

- **all**: isort black ruff mypy
- **csv**: map additional fields: operation_amount, currencies, sender/recipient accounts
- **legacy-app-deleted**: legacy app deleted
- **api**: - extract upload and file endpoints into separate routers - move csv parsing and transaction processing to services/ - add centralized logging and encoding utilities - introduce config module for env settings - create clean app entrypoint with router registration - improve project structure for scalability and maintainability
- **all**: black isort ruff
