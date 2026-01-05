from fastapi.testclient import TestClient
from main import app
import os

client = TestClient(app)

def test_health_check():
    """Verify the health check endpoint returns 200 OK."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data

def test_frontend_serving():
    """Verify that the React frontend is being served at the root."""
    # This requires the frontend to be built. 
    # If not built, main.py logs a warning but doesn't crash.
    # We'll check if we get a 200 (if built) or 404 (if not built/mounted).
    # Given we ran npm run build, we expect 200.
    
    response = client.get("/")
    # If the static mount failed (e.g. path issue), this might be 404.
    # However, for a smoke test, we want to ensure it IS served if we expect it.
    
    # Check if the dist directory actually exists to know what to expect
    react_dist_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "a2ui_integration/client/dist")
    if os.path.exists(react_dist_path):
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
    else:
        # If not built, we might get 404. 
        # But for this specific test run, we expect it to be built.
        assert response.status_code == 200

def test_dashboard_api():
    """Verify the dashboard API returns valid structure."""
    response = client.get("/api/a2ui/dashboard")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert "stats" in data["data"]

def test_chat_api():
    """Verify the chat API handles messages."""
    payload = {
        "message": "Hello Kernel",
        "session_id": "test-session"
    }
    response = client.post("/api/a2ui/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert "Kernel Placeholder" in data["response"] or "Neural link" in data["response"]

def test_email_inbox_api():
    """Verify the email inbox API."""
    response = client.get("/api/a2ui/email/inbox")
    assert response.status_code == 200
    data = response.json()
    # Depending on implementation, might be a list or dict
    # Based on previous context, it returns a UIResponse with data
    assert "data" in data
