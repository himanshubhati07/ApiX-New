COMMIT_MESSAGE: add customer management system api with auth and tests
## Features Added
- Customer CRUD with search, filtering, pagination, and sorting
- Address, contact person, note, and activity management
- JWT authentication with RBAC (admin/manager/user)
- Audit log tracking for customer-related changes
- Swagger/OpenAPI-ready documentation and examples
- Pytest suite for auth and core entities

## Files Modified
- /home/prajval/new_fast_api_backend_v2/fast_api_generator_backend/outputs/dbf2ee37-0d53-416c-8916-7748075b87f8/README.md — production-ready API documentation
- /home/prajval/new_fast_api_backend_v2/fast_api_generator_backend/outputs/dbf2ee37-0d53-416c-8916-7748075b87f8/requirements.txt — runtime and test dependencies
- /home/prajval/new_fast_api_backend_v2/fast_api_generator_backend/outputs/dbf2ee37-0d53-416c-8916-7748075b87f8/.gitignore — ignore tooling and env artifacts

## Files Added
- /home/prajval/new_fast_api_backend_v2/fast_api_generator_backend/outputs/dbf2ee37-0d53-416c-8916-7748075b87f8/.env_dbf2ee37-0d53-416c-8916-7748075b87f8 — environment configuration
- /home/prajval/new_fast_api_backend_v2/fast_api_generator_backend/outputs/dbf2ee37-0d53-416c-8916-7748075b87f8/app/* — FastAPI app modules, models, schemas, and routers
- /home/prajval/new_fast_api_backend_v2/fast_api_generator_backend/outputs/dbf2ee37-0d53-416c-8916-7748075b87f8/tests/* — pytest suite and factories
- /home/prajval/new_fast_api_backend_v2/fast_api_generator_backend/outputs/dbf2ee37-0d53-416c-8916-7748075b87f8/pytest.ini — pytest configuration
- /home/prajval/new_fast_api_backend_v2/fast_api_generator_backend/outputs/dbf2ee37-0d53-416c-8916-7748075b87f8/server_logs.md — test and server run logs

## Secrets Extracted
- DATABASE_URL -> written to .env_dbf2ee37-0d53-416c-8916-7748075b87f8
- JWT_SECRET -> written to .env_dbf2ee37-0d53-416c-8916-7748075b87f8

## DB URLs Resolved
- none -> postgresql+asyncpg://myuser:mypassword@localhost:5432/gen_018f64c429

## Test Results Summary
5 PASSED, 0 FAILED, 0 SKIPPED
