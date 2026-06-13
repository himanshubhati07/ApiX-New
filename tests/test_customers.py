import pytest

from tests.utils.factories import user_payload, customer_payload


async def get_token(client, role="admin"):
    payload = user_payload(role=role)
    await client.post("/api/v1/auth/register", json=payload)
    login_resp = await client.post(
        "/api/v1/auth/login",
        data={"username": payload["email"], "password": payload["password"]},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    return login_resp.json()["access_token"]


@pytest.mark.asyncio
async def test_customer_crud(client):
    token = await get_token(client, role="admin")
    headers = {"Authorization": f"Bearer {token}"}

    create_resp = await client.post("/api/v1/customers", json=customer_payload(), headers=headers)
    assert create_resp.status_code == 201
    customer = create_resp.json()

    list_resp = await client.get("/api/v1/customers", headers=headers)
    assert list_resp.status_code == 200
    assert list_resp.json()["total"] >= 1

    get_resp = await client.get(f"/api/v1/customers/{customer['id']}", headers=headers)
    assert get_resp.status_code == 200

    update_resp = await client.put(
        f"/api/v1/customers/{customer['id']}",
        json={"status": "inactive"},
        headers=headers,
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["status"] == "inactive"

    activities_resp = await client.get(
        f"/api/v1/customers/{customer['id']}/activities",
        headers=headers,
    )
    assert activities_resp.status_code == 200

    audit_resp = await client.get("/api/v1/audit-logs", headers=headers)
    assert audit_resp.status_code == 200

    delete_resp = await client.delete(f"/api/v1/customers/{customer['id']}", headers=headers)
    assert delete_resp.status_code == 204
