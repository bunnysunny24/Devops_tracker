import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_healthz_endpoint():
    response = client.get("/healthz")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data

def test_ready_endpoint():
    response = client.get("/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready"
    assert data["traffic_enabled"] is True

def test_prometheus_metrics_endpoint():
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "text/plain" in response.headers.get("content-type", "")
    assert "http_requests_total" in response.text
    assert "app_deployment_info" in response.text

def test_get_items():
    response = client.get("/api/items")
    assert response.status_code == 200
    items = response.json()
    assert isinstance(items, list)
    assert len(items) >= 1

def test_create_and_delete_item():
    new_item = {
        "title": "Automated Testing Microservice",
        "description": "Integration test payload",
        "status": "pending"
    }
    create_res = client.post("/api/items", json=new_item)
    assert create_res.status_code == 201
    created = create_res.json()
    assert created["title"] == new_item["title"]
    assert "id" in created
    
    item_id = created["id"]
    # Verify retrieval
    get_res = client.get(f"/api/items/{item_id}")
    assert get_res.status_code == 200
    assert get_res.json()["id"] == item_id

    # Verify deletion
    del_res = client.delete(f"/api/items/{item_id}")
    assert del_res.status_code == 200
    assert del_res.json()["deleted"] is True

def test_stats_endpoint():
    response = client.get("/api/stats")
    assert response.status_code == 200
    stats = response.json()
    assert "cpu_percent" in stats
    assert "memory_used_mb" in stats

def test_simulate_error():
    response = client.get("/api/simulate/error?code=500")
    assert response.status_code == 500
    assert "detail" in response.json()
