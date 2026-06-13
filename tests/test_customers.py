# Tests for customer endpoints (no create).
import pytest
from tests.utils.factories import customer_update_payload, user_payload


async def get_token(client):
    payload = user_payload()
    await client.post("/api/v1/auth/register", json=payload)
    login = await client.post(
        "/api/v1/auth/login",
        data={"username": payload["email"], "password": payload["password"]},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    return login.json()["access_token"]


@pytest.mark.asyncio
async def test_list_customers(client, seed_customer):
    token = await get_token(client)
    response = await client.get("/api/v1/customers", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_get_customer(client, seed_customer):
    token = await get_token(client)
    response = await client.get(
        f"/api/v1/customers/{seed_customer.id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json()["id"] == seed_customer.id


@pytest.mark.asyncio
async def test_update_customer(client, seed_customer):
    token = await get_token(client)
    response = await client.patch(
        f"/api/v1/customers/{seed_customer.id}",
        json=customer_update_payload(),
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Customer"


@pytest.mark.asyncio
async def test_delete_customer(client, seed_customer):
    token = await get_token(client)
    response = await client.delete(
        f"/api/v1/customers/{seed_customer.id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 204
