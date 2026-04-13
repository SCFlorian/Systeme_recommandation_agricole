from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

def test_predict_endpoint():
    payload = {
        "region": "Western Europe",
        "item": "Wheat",
        "avg_temp": 15.0,
        "rainfall_mm": 500.0,
        "pesticides_tonnes": 100.0
    }
    response = client.post("/predict", json=payload)

    assert response.status_code == 200
    assert "prediction" in response.json()

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "OK"

def test_404_handler():
    response = client.get("/route-inconnue")
    assert response.status_code == 404
    body = response.json()
    assert body["error_code"] == 404

def test_predict_validation_error():
    payload = {
        "region": "France",
        "item": "Wheat",
        "avg_temp": "abc",
        "rainfall_mm": 500,
        "pesticides_tonnes": 100
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 422
    body = response.json()
    assert body["error_code"] == 422

def test_recommend_ok():
    payload = {
        "region": "Western Europe",
        "avg_temp": 15.5,
        "rainfall_mm": 500.0,
        "pesticides_tonnes": 100.0
    }
    response = client.post("/recommend", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert "best_crop" in body
    assert "ranking" in body
    assert len(body["ranking"]) == 10