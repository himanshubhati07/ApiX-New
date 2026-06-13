# Server Logs [Iteration 0]

## Platform — OS + python version
- OS: linux
- Python: 3.12.3

## Database
- Client URL  : postgresql+asyncpg://myuser:mypassword@localhost:5432/gen_8a70b7d29d
- Fallback    : YES — substituted (original unreachable). DB name: gen_8a70b7d29d. Log in server_logs.md.
- Resolved URL: postgresql+asyncpg://myuser:mypassword@localhost:5432/gen_8a70b7d29d

## Test Runner — no live server needed
- pytest tests/ -v --tb=short  (tests use ASGI transport / TestClient — no HTTP server required)

## Files Generated / Modified
- /app/__init__.py — OK
- /app/database.py — OK
- /app/models.py — OK
- /app/schemas.py — OK
- /app/core/__init__.py — OK
- /app/core/security.py — OK
- /app/core/auth.py — OK
- /app/routers/__init__.py — OK
- /app/routers/auth.py — OK
- /app/routers/customers.py — OK
- /app/routers/interactions.py — OK
- /app/routers/activity.py — OK
- /app/main.py — OK
- /seed.py — OK
- /requirements.txt — OK
- /.env_422ca5fd-04e6-47e0-a569-9b11c4768453 — OK
- /.env.example — OK
- /start.sh — OK
- /start.bat — OK
- /Dockerfile — OK
- /docker-compose.yml — OK
- /Makefile — OK
- /README.md — OK
- /pytest.ini — OK
- /tests/__init__.py — OK
- /tests/conftest.py — OK
- /tests/test_auth.py — OK
- /tests/test_customers.py — OK
- /tests/test_interactions.py — OK
- /tests/test_activity.py — OK
- /tests/test_health.py — OK
- /tests/utils/__init__.py — OK
- /tests/utils/factories.py — OK

## API Test Results

| Test Function | Endpoint | Status | Expected Code | Notes |
|---|---|---:|---:|---|
| test_health | GET /health | PASSED | 200 | Health check |
| test_register | POST /api/v1/auth/register | PASSED | 201 | User registration |
| test_login_valid | POST /api/v1/auth/login | PASSED | 200 | Valid credentials |
| test_login_invalid | POST /api/v1/auth/login | PASSED | 401 | Invalid credentials |
| test_me | GET /api/v1/auth/me | PASSED | 200 | Current user |
| test_invalid_token | GET /api/v1/auth/me | PASSED | 401 | Invalid token |
| test_list_customers | GET /api/v1/customers | PASSED | 200 | List customers |
| test_get_customer | GET /api/v1/customers/{customer_id} | PASSED | 200 | Get customer |
| test_update_customer | PATCH /api/v1/customers/{customer_id} | PASSED | 200 | Update customer |
| test_delete_customer | DELETE /api/v1/customers/{customer_id} | PASSED | 204 | Delete customer |
| test_create_interaction | POST /api/v1/interactions | PASSED | 201 | Create interaction |
| test_list_interactions | GET /api/v1/interactions | PASSED | 200 | List interactions |
| test_get_interaction | GET /api/v1/interactions/{interaction_id} | PASSED | 200 | Get interaction |
| test_update_interaction | PATCH /api/v1/interactions/{interaction_id} | PASSED | 200 | Update interaction |
| test_delete_interaction | DELETE /api/v1/interactions/{interaction_id} | PASSED | 204 | Delete interaction |
| test_list_activity | GET /api/v1/activity | PASSED | 200 | List activity logs |
| test_get_activity | GET /api/v1/activity/{activity_id} | PASSED | 200 | Get activity log |

## Errors Fixed This Iteration
1. /tests/conftest.py → missing test DB creation → added automatic test DB creation and session loop scope alignment.
2. /tests/utils/factories.py + tests → duplicate email collisions → generated unique user emails per test.
3. /app/routers/customers.py + /app/routers/interactions.py → FK constraint on delete → nullified activity log references before delete.
4. /requirements.txt → missing email-validator/python-multipart → added dependencies for EmailStr and OAuth2 form data.

