import uuid


def user_payload(role="admin"):
    suffix = uuid.uuid4().hex[:6]
    return {
        "name": f"User {suffix}",
        "email": f"user{suffix}@example.com",
        "password": "secret123",
        "role": role,
    }


def customer_payload(customer_type="business"):
    suffix = uuid.uuid4().hex[:6]
    return {
        "name": f"Customer {suffix}",
        "email": f"customer{suffix}@example.com",
        "phone_number": "+1-555-0001",
        "customer_type": customer_type,
        "status": "active",
    }


def address_payload():
    return {
        "line1": "123 Main St",
        "line2": "Suite 100",
        "city": "Metropolis",
        "state": "NY",
        "postal_code": "10001",
        "country": "USA",
    }


def contact_payload():
    return {
        "name": "Jane Doe",
        "email": "jane.doe@acme.com",
        "phone_number": "+1-555-2222",
        "title": "Sales Lead",
    }


def note_payload():
    return {"note": "Initial outreach completed."}
