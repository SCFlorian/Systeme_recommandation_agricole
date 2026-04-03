# Test des endpoints
from fastapi.testclient import TestClient
import pytest
import os, sys

from app import app
import pandas as pd

# Pour tester l'application FastAPI
client = TestClient(app)

# Test endpoint/health
def test_health_endpoint():
    """Vérifie que le endpoint/health renvoie bien 200 et un message OK"""
    response = client.get("/health")
    assert response.status_code == 200, "Le endpoint /health doit répondre 200"
    data = response.json()
    assert "status" in data, "Le JSON doit contenir 'status'"
    assert data["status"].lower() == "ok"

