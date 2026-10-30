import os

# Set BEFORE the app is imported, so tests can never touch the real database
os.environ["DATABASE_URL"] = "sqlite://"
os.environ["JWT_SECRET"] = "test-secret-not-used-anywhere-else-0123456789abcdef"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401  (registers the tables)
from app.api.deps import get_db
from app.core.limiter import limiter
from app.db.base import Base
from app.main import app as fastapi_app

limiter.enabled = False  # tests make many logins; one test turns it back on


@pytest.fixture()
def db_engine():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(engine)
    yield engine
    engine.dispose()


@pytest.fixture()
def client(db_engine):
    Session = sessionmaker(bind=db_engine, autoflush=False)

    def override_get_db():
        db = Session()
        try:
            yield db
        finally:
            db.close()

    fastapi_app.dependency_overrides[get_db] = override_get_db
    with TestClient(fastapi_app) as c:
        yield c
    fastapi_app.dependency_overrides.clear()


@pytest.fixture()
def make_user(client):
    """Sign up a user. Returns (auth headers, user dict)."""
    counter = {"n": 0}

    def _make(name="Test User", email=None, password="Test@1234"):
        counter["n"] += 1
        email = email or f"user{counter['n']}@example.com"
        r = client.post(
            "/api/auth/signup", json={"name": name, "email": email, "password": password}
        )
        assert r.status_code == 201, r.text
        data = r.json()
        return {"Authorization": f"Bearer {data['access_token']}"}, data["user"]

    return _make


@pytest.fixture()
def add_task(client):
    def _add(headers, **body):
        body.setdefault("title", "Task")
        r = client.post("/api/tasks", json=body, headers=headers)
        assert r.status_code == 201, r.text
        return r.json()

    return _add