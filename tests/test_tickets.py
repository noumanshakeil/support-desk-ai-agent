import pytest

@pytest.mark.asyncio
async def test_health(client):
    r = await client.get("/health"); assert r.status_code == 200

@pytest.mark.asyncio
async def test_create_ticket(client):
    r = await client.post("/api/tickets", json={"subject": "Cannot login", "body": "MFA loop on web app"})
    assert r.status_code == 200
    body = r.json()
    assert body["priority"] in {"urgent", "high", "medium", "low"}
    assert body["reply_draft"]
