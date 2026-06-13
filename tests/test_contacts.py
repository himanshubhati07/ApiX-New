import pytest

from tests.utils.factories import user_payload, customer_payload, contact_payload


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
async def test_contact_crud(client):
    token = await get_token(client, role="admin")
    headers = {"Authorization": f"Bearer {token}"}

    customer_resp = await client.post("/api/v1/customers", json=customer_payload("business"), headers=headers)
    customer_id = customer_resp.json()["id"]

    create_resp = await client.post(
        f"/api/v1/customers/{customer_id}/contacts",
        json=contact_payload(),
        headers=headers,
    )
    assert create_resp.status_code == 201
    contact_id = create_resp.json()["id"]

    list_resp = await client.get(f"/api/v1/customers/{customer_id}/contacts", headers=headers)
    assert list_resp.status_code == 200

    get_resp = await client.get(f"/api/v1/contacts/{contact_id}", headers=headers)
    assert get_resp.status_code == 200

    update_resp = await client.put(
        f"/api/v1/contacts/{contact_id}",
        json={"title": "Director"},
        headers=headers,
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["title"] == "Director"

    delete_resp = await client.delete(f"/api/v1/contacts/{contact_id}", headers=headers)
    assert delete_resp.status_code == 204
