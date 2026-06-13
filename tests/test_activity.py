# Tests for activity log endpoints.
import pytest
from tests.utils.factories import interaction_payload, user_payload


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
async def test_list_activity(client, seed_customer):
    token = await get_token(client)
    await client.post(
        "/api/v1/interactions",
        json=interaction_payload(seed_customer.id),
        headers={"Authorization": f"Bearer {token}"},
    )
    response = await client.get("/api/v1/activity", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_get_activity(client, seed_customer):
    token = await get_token(client)
    await client.post(
        "/api/v1/interactions",
        json=interaction_payload(seed_customer.id),
        headers={"Authorization": f"Bearer {token}"},
    )
    list_resp = await client.get("/api/v1/activity", headers={"Authorization": f"Bearer {token}"})
    activity_id = list_resp.json()[0]["id"]
    response = await client.get(
        f"/api/v1/activity/{activity_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json()["id"] == activity_id
