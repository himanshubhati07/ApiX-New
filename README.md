# change api test (CMS API)

## Overview
This project delivers a production-ready Customer Management System (CMS) REST API. The **Create Customer** API has been removed because customer records are created through external/manual onboarding.

## Key Changes
- **Removed:** `POST /api/v1/customers` (Create Customer) and all related examples/tests.
- **Updated:** Audit and activity history now only capture actions still supported (customer update/delete, interaction CRUD, login).
- **RBAC:** Not enabled. JWT-based authentication is required for all endpoints.

## Change Log
### Removed APIs
- `POST /api/v1/customers`

### Modified APIs
- `GET /api/v1/customers` remains for retrieval only (no creation).
- Activity history excludes customer creation events.

### Impact on Integrations
- Integrations must use external onboarding systems to create customer records.
- CMS consumers should remove any dependencies on `POST /api/v1/customers`.

### Migration Considerations
- Ensure customer data is provisioned before calling CMS endpoints.
- Replace customer creation flows with external onboarding workflows.

## Architecture
- **Auth**: JWT (HS256, 30 min expiry)
- **Database**: PostgreSQL (asyncpg)
- **Pagination**: offset/limit (default limit=20)
- **CORS**: enabled for all origins

## Database Schema (Summary)
- **User**: authentication users
- **Customer**: externally created customers; no API creation
- **Interaction**: customer communications
- **ActivityLog**: audit trail for supported actions only

## API Endpoints
### Auth
- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `GET /api/v1/auth/me`

### Customers (Creation Removed)
- `GET /api/v1/customers`
- `GET /api/v1/customers/{customer_id}`
- `PATCH /api/v1/customers/{customer_id}`
- `DELETE /api/v1/customers/{customer_id}`

### Interactions
- `POST /api/v1/interactions`
- `GET /api/v1/interactions`
- `GET /api/v1/interactions/{interaction_id}`
- `PATCH /api/v1/interactions/{interaction_id}`
- `DELETE /api/v1/interactions/{interaction_id}`

### Activity History
- `GET /api/v1/activity`
- `GET /api/v1/activity/{activity_id}`

## Request/Response Examples
### Update Customer (PATCH /api/v1/customers/{customer_id})
**Request**
```json
{
  "name": "Acme Corp Updated",
  "status": "active",
  "notes": "Updated billing contact"
}
```
**Response**
```json
{
  "id": "uuid",
  "external_id": "EXT-1001",
  "name": "Acme Corp Updated",
  "email": "info@acme.com",
  "phone": "+1-555-1000",
  "status": "active",
  "address": null,
  "notes": "Updated billing contact",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-02T00:00:00Z"
}
```

### Create Interaction (POST /api/v1/interactions)
**Request**
```json
{
  "customer_id": "uuid",
  "channel": "email",
  "subject": "Quarterly review",
  "content": "Discussed Q3 performance",
  "occurred_at": "2024-01-02T10:00:00Z"
}
```
**Response**
```json
{
  "id": "uuid",
  "customer_id": "uuid",
  "channel": "email",
  "subject": "Quarterly review",
  "content": "Discussed Q3 performance",
  "occurred_at": "2024-01-02T10:00:00Z",
  "created_at": "2024-01-02T10:00:00Z",
  "updated_at": "2024-01-02T10:00:00Z"
}
```

## Validation Rules
- `User.password` min length 8
- `Customer.external_id` length 3-64
- `Customer.status` in {active, inactive, suspended}
- `Interaction.channel` in {email, phone, meeting, chat}

## Error Handling
- `400/422` validation errors for invalid input
- `401` invalid/expired token
- `403` inactive user
- `404` resource not found
- `409` conflicts (duplicate email)

## Sample Test Cases
- Register user → 201
- Login user → 200
- Get current user → 200
- List customers → 200
- Update customer → 200
- Delete customer → 204
- Create interaction → 201
- List interactions → 200
- List activity logs → 200

## Swagger/OpenAPI
- Swagger UI: `/docs`
- OpenAPI JSON: `/openapi.json`

## Setup
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env_422ca5fd-04e6-47e0-a569-9b11c4768453 .env_422ca5fd-04e6-47e0-a569-9b11c4768453
python seed.py
PORT=47375 bash ./start.sh
```

## Testing
```bash
pytest tests/ -v --tb=short
```

## Project Tree
```
app/
  core/
  routers/
  database.py
  models.py
  schemas.py
  main.py
seed.py
start.sh
start.bat
requirements.txt
```
