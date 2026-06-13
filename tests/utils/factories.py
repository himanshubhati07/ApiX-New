# Test payload factories.
from datetime import datetime
import uuid

def user_payload() -> dict:
    unique_email = f"testuser-{uuid.uuid4().hex[:8]}@example.com"
    return {"email": unique_email, "full_name": "Test User", "password": "TestPass123"}


def customer_payload(external_id: str) -> dict:
    return {
        "external_id": external_id,
        "name": "Test Customer",
        "email": "customer@example.com",
        "phone": "+1-555-1234",
        "status": "active",
        "address": "123 Test St",
        "notes": "Initial note",
    }


def customer_update_payload() -> dict:
    return {"name": "Updated Customer", "status": "inactive"}


def interaction_payload(customer_id: str) -> dict:
    return {
        "customer_id": customer_id,
        "channel": "email",
        "subject": "Test Interaction",
        "content": "Discussion details",
        "occurred_at": datetime.utcnow().isoformat(),
    }


def interaction_update_payload() -> dict:
    return {"subject": "Updated Interaction", "content": "Updated content"}
