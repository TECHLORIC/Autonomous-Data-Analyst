import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock

from app.main import app
from app.db.session import get_db

async def override_get_db():
    class MockSession:
        async def execute(self, *args, **kwargs):
            return None
    yield MockSession()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(autouse=True)
def mock_init_db():
    with patch("app.main.init_db", new_callable=AsyncMock):
        yield

def test_health_check() -> None:
    with TestClient(app) as client:
        response = client.get("/health")

        assert response.status_code == 200

        data = response.json()

        assert data["status"] == "healthy"
        assert data["service"] == "Autonomous Data Analyst"

def test_readiness_check() -> None:
    with TestClient(app) as client:
        response = client.get("/health/ready")

        assert response.status_code == 200
        assert response.json()["status"] == "ready"