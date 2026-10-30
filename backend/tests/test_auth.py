from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User


def test_signup_success(client):
    r = client.post(
        "/api/auth/signup",
        json={"name": "  Priya  ", "email": "Priya@Example.com", "password": "Demo@1234"},
    )
    assert r.status_code == 201
    body = r.json()
    assert body["access_token"]
    assert body["user"]["name"] == "Priya"
    assert body["user"]["email"] == "priya@example.com"
    assert "password" not in str(body).lower()


def test_password_is_stored_hashed(client, db_engine):
    client.post(
        "/api/auth/signup",
        json={"name": "A", "email": "hash@example.com", "password": "Test@1234"},
    )
    with Session(db_engine) as s:
        user = s.scalar(select(User).where(User.email == "hash@example.com"))
        assert user.password_hash.startswith("$2b$")
        assert "Test@1234" not in user.password_hash


def test_duplicate_email_is_rejected(client, make_user):
    make_user(email="dup@example.com")
    r = client.post(
        "/api/auth/signup",
        json={"name": "B", "email": "DUP@example.com", "password": "Test@1234"},
    )
    assert r.status_code == 409
    assert r.json()["message"] == "An account with this email already exists"


def test_short_password_is_rejected(client):
    r = client.post(
        "/api/auth/signup",
        json={"name": "A", "email": "a@example.com", "password": "short"},
    )
    assert r.status_code == 422
    assert "8 characters" in r.json()["errors"]["password"]


def test_invalid_email_and_blank_name_are_rejected(client):
    r = client.post(
        "/api/auth/signup",
        json={"name": "   ", "email": "not-an-email", "password": "Test@1234"},
    )
    assert r.status_code == 422
    errors = r.json()["errors"]
    assert "name" in errors and "email" in errors


def test_login_success_and_email_is_case_insensitive(client, make_user):
    make_user(email="case@example.com")
    r = client.post(
        "/api/auth/login", json={"email": "CASE@example.com", "password": "Test@1234"}
    )
    assert r.status_code == 200
    assert r.json()["access_token"]


def test_wrong_password_and_unknown_email_give_the_same_error(client, make_user):
    make_user(email="real@example.com")
    wrong_pw = client.post(
        "/api/auth/login", json={"email": "real@example.com", "password": "Wrong@1234"}
    )
    no_user = client.post(
        "/api/auth/login", json={"email": "nobody@example.com", "password": "Wrong@1234"}
    )
    assert wrong_pw.status_code == no_user.status_code == 401
    assert wrong_pw.json() == no_user.json() == {"message": "Invalid email or password"}


def test_me_with_valid_token(client, make_user):
    headers, user = make_user(name="Me")
    r = client.get("/api/auth/me", headers=headers)
    assert r.status_code == 200
    assert r.json()["id"] == user["id"]
    assert "password_hash" not in r.json()


def test_me_without_or_with_fake_token(client):
    assert client.get("/api/auth/me").status_code == 401
    r = client.get("/api/auth/me", headers={"Authorization": "Bearer abc.def.ghi"})
    assert r.status_code == 401