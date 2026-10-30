from app.core.limiter import limiter


def test_health_returns_ok(client):
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.text == "OK"


def test_unknown_route_uses_the_error_format(client):
    r = client.get("/nope")
    assert r.status_code == 404
    assert r.json() == {"message": "Not Found"}


def test_login_is_rate_limited(client):
    limiter.enabled = True
    try:
        responses = [
            client.post("/api/auth/login", json={"email": "a@example.com", "password": "x"})
            for _ in range(12)
        ]
    finally:
        limiter.enabled = False
        limiter.reset()
    assert [r.status_code for r in responses[:10]] == [401] * 10
    assert [r.status_code for r in responses[10:]] == [429, 429]
    assert "Too many attempts" in responses[-1].json()["message"]