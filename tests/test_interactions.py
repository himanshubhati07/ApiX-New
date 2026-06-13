# Tests for interaction endpoints.
import pytest
from tests.utils.factories import interaction_payload, interaction_update_payload, user_payload


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
async def test_create_interaction(client, seed_customer):
    token = await get_token(client)
    response = await client.post(
        "/api/v1/interactions",
        json=interaction_payload(seed_customer.id),
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 201
    assert response.json()["customer_id"] == seed_customer.id


@pytest.mark.asyncio
async def test_list_interactions(client, seed_customer):
    token = await get_token(client)
    await client.post(
        "/api/v1/interactions",
        json=interaction_payload(seed_customer.id),
        headers={"Authorization": f"Bearer {token}"},
    )
    response = await client.get("/api/v1/interactions", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_interaction(client, seed_customer):
    token = await get_token(client)
    created = await client.post(
        "/api/v1/interactions",
        json=interaction_payload(seed_customer.id),
        headers={"Authorization": f"Bearer {token}"},
    )
    interaction_id = created.json()["id"]
    response = await client.get(
        f"/api/v1/interactions/{interaction_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_update_interaction(client, seed_customer):
    token = await get_token(client)
    created = await client.post(
        "/api/v1/interactions",
        json=interaction_payload(seed_customer.id),
        headers={"Authorization": f"Bearer {token}"},
    )
    interaction_id = created.json()["id"]
    response = await client.patch(
        f"/api/v1/interactions/{interaction_id}",
        json=interaction_update_payload(),
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json()["subject"] == "Updated Interaction"


@pytest.mark.asyncio
async def test_delete_interaction(client, seed_customer):
    token = await get_token(client)
    created = await client.post(
        "/api/v1/interactions",
        json=interaction_payload(seed_customer.id),
        headers={"Authorization": f"Bearer {token}"},
    )
    interaction_id = created.json()["id"]
    response = await client.delete(
        f"/api/v1/interactions/{interaction_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 204
