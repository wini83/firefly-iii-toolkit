## 1.3.0 (2025-12-07)

### Feat

- **infra**: add full dockerization setup with reverse proxy and health-checked backend stack

## 1.2.0 (2025-12-07)

### Feat

- **settings**: refactor middleware configuration into centralized settings layer

### Refactor

- **settings**: remove legacy config.py and migrate all env access to unified settings

## 1.1.0 (2025-12-06)

### Feat

- **api**: add version endpoint, improve health response, and align BLIK models

## 1.0.0 (2025-12-06)

### BREAKING CHANGE

- api endpoints changed

### Feat

- **api**: restructure API into clear namespaces and introduce blik_files pipeline

### Refactor

- **api**: isort ruff black mypy

## 0.4.5 (2025-12-06)

### Refactor

- **api**: migrate backend to a clean src-based project layout and update imports
- **api**: -add response model to allpy matches endpoint

## 0.4.4 (2025-12-02)

### Refactor

- **auth**: - replace os.getenv usage with shared `settings` instance  - explicitly type JWT payload to resolve Pylance update() errors  - clean up auth flow and remove debug prints
- **ui**: deleted login and upload pages

## 0.4.3 (2025-12-01)

### Refactor

- **api**: introduce typed Pydantic response models for file and upload endpoints

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

## 0.2.0 (2025-11-20)

### Feat

- **auth**: add X-Token header authentication with APIKeyHeader and env-based token validation

### Refactor

- **csv**: map additional fields: operation_amount, currencies, sender/recipient accounts

## 0.1.1 (2025-11-17)

### Fix

- **api**: import error fix

### Refactor

- **legacy-app-deleted**: legacy app deleted
- **api**: - extract upload and file endpoints into separate routers - move csv parsing and transaction processing to services/ - add centralized logging and encoding utilities - introduce config module for env settings - create clean app entrypoint with router registration - improve project structure for scalability and maintainability
- **all**: black isort ruff
