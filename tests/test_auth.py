import pytest

from tests.utils.factories import user_payload


@pytest.mark.asyncio
async def test_register_login_me(client):
    payload = user_payload(role="admin")
    resp = await client.post("/api/v1/auth/register", json=payload)
    assert resp.status_code == 201

    login_resp = await client.post(
        "/api/v1/auth/login",
        data={"username": payload["email"], "password": payload["password"]},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]

    me_resp = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_resp.status_code == 200
    assert me_resp.json()["email"] == payload["email"]

    invalid_resp = await client.get("/api/v1/auth/me", headers={"Authorization": "Bearer invalid"})
    assert invalid_resp.status_code == 401
