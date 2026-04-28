import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.core.database import Base, get_db
from app.models.models import Tenant, User
from app.core.security import hash_password

# ── In-memory SQLite for tests ────────────────────────────────────────────────
TEST_DATABASE_URL = "sqlite:///./test.db"

engine_test = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine_test
)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="session", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine_test)
    yield
    Base.metadata.drop_all(bind=engine_test)


@pytest.fixture
def db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.rollback()
        db.close()


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture
def seed_tenant(db):
    tenant = Tenant(
        name             = "Test Corp",
        plan             = "pro",
        sites_allowed    = 10,
        storage_limit_mb = 1024,
    )
    db.add(tenant)
    db.flush()
    return tenant


@pytest.fixture
def seed_user(db, seed_tenant):
    import uuid
    user = User(
        tenant_id       = seed_tenant.id,
        email           = f"test{uuid.uuid4().hex[:8]}@example.com",
        name            = "Test User",
        hashed_password = hash_password("testpass"),
        role            = "owner",
    )
    db.add(user)
    db.commit()
    return user


@pytest.fixture
def auth_headers(client, seed_user):
    resp = client.post(
        "/api/auth/login",
        json={"email": seed_user.email, "password": "testpass"},
    )
    assert resp.status_code == 200
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
