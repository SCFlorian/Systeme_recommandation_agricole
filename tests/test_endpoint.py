from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

def test_predict_endpoint():
    # On envoie une requête JSON fictive à l'API
    payload = {
        "region": "Western Europe",
        "item": "Wheat",
        "avg_temp": 15.0,
        "rainfall_mm": 500.0,
        "pesticides_tonnes": 100.0
    }
    response = client.post("/predict", json=payload)
    
    # On vérifie que l'API répond 200 (OK) et renvoie une prédiction
    assert response.status_code == 200
    assert "prediction" in response.json()