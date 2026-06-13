# Customer Management System (CMS) API

## Overview
Production-ready FastAPI backend for customer management with JWT authentication, role-based access control, audit trail, customer notes, activities, contact persons, and multi-address management.

## Features
- Customer CRUD (Individual & Business)
- Address management (multiple per customer)
- Contact persons for business customers
- Notes and activity history
- Search, filtering, pagination, sorting
- JWT authentication
- RBAC (admin, manager, user)
- Audit trail for all customer changes

## Authentication
Use `/api/v1/auth/register` to create a user, then `/api/v1/auth/login` for a JWT.

**Roles**:
- `admin`: full access
- `manager`: manage customers, addresses, contacts, notes
- `user`: read and add notes

## Database Schema (High-Level)

### users
- id (PK)
- name
- email (unique)
- hashed_password
- role (admin | manager | user)
- created_at

### customers
- id (PK)
- customer_id (unique business ID)
- name
- email (unique)
- phone_number
- customer_type (individual | business)
- status (active | inactive | prospect)
- created_at

### addresses
- id (PK)
- customer_id (FK)
- line1, line2, city, state, postal_code, country
- created_at

### contact_people
- id (PK)
- customer_id (FK)
- name, email, phone_number, title
- created_at

### customer_notes
- id (PK)
- customer_id (FK)
- note
- created_at

### customer_activities
- id (PK)
- customer_id (FK)
- action
- details
- created_at

### audit_logs
- id (PK)
- actor_id (FK users)
- entity_type
- entity_id
- action
- change_summary
- created_at

## Validation Rules
- Email: valid format and unique for customers/users
- Password: min 6 chars
- Name: min 2 chars
- Address fields: required
- Contact persons allowed only for business customers

## API Endpoints

### Auth
- POST `/api/v1/auth/register`
- POST `/api/v1/auth/login`
- GET `/api/v1/auth/me`

### Customers
- POST `/api/v1/customers`
- GET `/api/v1/customers` (filters: name, status, type, start_date, end_date, sort_by, sort_order, page, page_size)
- GET `/api/v1/customers/{customer_id}`
- PUT `/api/v1/customers/{customer_id}`
- DELETE `/api/v1/customers/{customer_id}`

### Addresses
- POST `/api/v1/customers/{customer_id}/addresses`
- GET `/api/v1/customers/{customer_id}/addresses`
- GET `/api/v1/addresses/{address_id}`
- PUT `/api/v1/addresses/{address_id}`
- DELETE `/api/v1/addresses/{address_id}`

### Contact Persons (business only)
- POST `/api/v1/customers/{customer_id}/contacts`
- GET `/api/v1/customers/{customer_id}/contacts`
- GET `/api/v1/contacts/{contact_id}`
- PUT `/api/v1/contacts/{contact_id}`
- DELETE `/api/v1/contacts/{contact_id}`

### Notes
- POST `/api/v1/customers/{customer_id}/notes`
- GET `/api/v1/customers/{customer_id}/notes`
- GET `/api/v1/notes/{note_id}`
- PUT `/api/v1/notes/{note_id}`
- DELETE `/api/v1/notes/{note_id}`

### Activities
- GET `/api/v1/customers/{customer_id}/activities`

### Audit Logs
- GET `/api/v1/audit-logs`

## Request/Response Examples

### Register
```json
POST /api/v1/auth/register
{
  "name": "Admin User",
  "email": "admin@example.com",
  "password": "secret123",
  "role": "admin"
}
```

### Login
```json
POST /api/v1/auth/login
username=admin@example.com&password=secret123
```

### Create Customer
```json
POST /api/v1/customers
Authorization: Bearer <token>
{
  "name": "Acme Corp",
  "email": "info@acme.com",
  "phone_number": "+1-555-0101",
  "customer_type": "business",
  "status": "active"
}
```

### Customer Response
```json
{
  "id": "uuid",
  "customer_id": "CUST-1a2b3c4d",
  "name": "Acme Corp",
  "email": "info@acme.com",
  "phone_number": "+1-555-0101",
  "customer_type": "business",
  "status": "active",
  "created_at": "2024-01-01T00:00:00Z",
  "addresses": [],
  "contacts": [],
  "notes": []
}
```

## Error Handling
- 401 Unauthorized for invalid token
- 403 Forbidden for RBAC violations
- 404 Not Found for missing resources
- 409 Conflict for duplicates

## Swagger/OpenAPI
Available at `/docs` after running the server.

## Sample Test Cases
- Register, login, and access `/me`
- Create customer (admin/manager) and verify list/get
- Add address and verify retrieval
- Add contact for business customer (reject for individual)
- Add note and view activity history
- Verify audit logs recorded

## Running
```bash
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 43917
```
