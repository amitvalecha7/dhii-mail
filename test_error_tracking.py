import pytest
from fastapi.testclient import TestClient
from fastapi import APIRouter
from main import app
from error_handler import ErrorCategory

client = TestClient(app, raise_server_exceptions=False)

# Create a test router to trigger exceptions
router_for_testing = APIRouter()

@router_for_testing.get("/test/error/validation")
def trigger_validation_error():
    # ValueError is mapped to ValidationError by ErrorHandler
    raise ValueError("Invalid input provided")

@router_for_testing.get("/test/error/unknown")
def trigger_unknown_error():
    # RuntimeError is not specially handled, so it becomes UNKNOWN/INTERNAL
    raise RuntimeError("Unexpected system failure")

@router_for_testing.get("/test/error/auth")
def trigger_auth_error():
    # Simulating an auth error that might be raised by libraries
    raise Exception("Authentication failed for user")

# Include the test router in the application
app.include_router(router_for_testing)

def test_validation_error_handling():
    """Test that ValueError is converted to 400 Bad Request"""
    response = client.get("/test/error/validation")
    print(f"Validation Error Response: {response.status_code} - {response.json()}")
    assert response.status_code == 400
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == "VALIDATION_ERROR"
    assert data["error"]["message"] == "Invalid input provided"
    assert data["error"]["category"] == "validation"

def test_unknown_error_handling():
    """Test that RuntimeError is converted to 500 Internal Server Error"""
    response = client.get("/test/error/unknown")
    print(f"Unknown Error Response: {response.status_code} - {response.text}")
    assert response.status_code == 500
    data = response.json()
    assert "error" in data
    # ErrorHandler maps unknown exceptions to ValidationError by default if they are ValueError/TypeError
    # But RuntimeError is not ValueError/TypeError.
    # Let's check ErrorHandler.handle_error logic again.
    # It says:
    # elif isinstance(error, (ValueError, TypeError)): ... ValidationError
    # elif "auth" ...
    # else: return AppError(message=str(error), category=ErrorCategory.UNKNOWN, severity=ErrorSeverity.HIGH, original_error=error)
    
    # So it should be UNKNOWN category.
    # In main.py global handler:
    # status_code = 500 (default)
    # if category == ...
    
    assert data["error"]["category"] == "unknown"
    assert "Unexpected system failure" in data["error"]["message"]

def test_auth_error_handling():
    """Test that auth-like string in exception is converted to 401/403"""
    response = client.get("/test/error/auth")
    # ErrorHandler maps "auth" in string to AuthenticationError
    # main.py maps AuthenticationError to 401
    assert response.status_code == 401
    data = response.json()
    assert "error" in data
    assert data["error"]["category"] == "authentication"
