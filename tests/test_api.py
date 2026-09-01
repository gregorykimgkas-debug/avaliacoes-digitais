import os
from pathlib import Path
import sys

os.environ["DATABASE_URL"] = "sqlite:///:memory:"
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from fastapi.testclient import TestClient  # noqa: E402

from backend.app import app  # noqa: E402


def test_health_and_dashboard():
    with TestClient(app) as client:
        health = client.get("/api/health")
        assert health.status_code == 200
        assert health.json()["status"] == "ok"

        dashboard = client.get("/api/dashboard")
        assert dashboard.status_code == 200
        body = dashboard.json()
        assert body["summary"]["responses"] == 12
        assert 0 <= body["summary"]["approval_rate"] <= 100


def test_filter_and_protected_write():
    with TestClient(app) as client:
        filtered = client.get("/api/dashboard?assessment=MO_BOLAS")
        assert filtered.status_code == 200
        assert filtered.json()["summary"]["responses"] == 3

        denied = client.post(
            "/api/submissions",
            json={
                "assessment_code": "MO_BOLAS",
                "participant_code": "ALU-999",
                "client": "Cliente Teste",
                "instructor": "Instrutor Teste",
                "score": 90,
            },
        )
        assert denied.status_code == 401

