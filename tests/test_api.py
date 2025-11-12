"""
Basic API tests for AWS Solution Architect Tool
Minimalist Mode 🧭
Keep this file lean — no mocks, no placeholders, only confirmed logic.
"""

import pytest
import asyncio
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_root_endpoint():
    """Test root endpoint returns correct response"""
    response = client.get("/")
    assert response.status_code == 200
    assert "AWS Solution Architect Tool API" in response.json()["message"]

def test_health_endpoint():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_get_roles():
    """Test getting available roles"""
    response = client.get("/roles")
    assert response.status_code == 200
    roles = response.json()["roles"]
    assert isinstance(roles, list)
    assert len(roles) > 0
    assert "serverless-architecture" in roles

def test_mcp_servers_for_roles():
    """Test getting MCP servers for selected roles"""
    test_data = {
        "roles": ["serverless-architecture", "container-orchestration"],
        "architecture_inputs": {"region": "us-east-1"}
    }
    
    response = client.post("/roles/mcp-servers", json=test_data)
    assert response.status_code == 200
    
    data = response.json()
    assert "mcp_servers" in data
    assert "selected_roles" in data
    assert data["selected_roles"] == test_data["roles"]

def test_generate_architecture():
    """Test architecture generation endpoint"""
    test_data = {
        "roles": ["serverless-architecture"],
        "inputs": {
            "region": "us-east-1",
            "environment": "production",
            "project_name": "test-project",
            "description": "Test architecture"
        }
    }
    
    response = client.post("/generate", json=test_data)
    assert response.status_code == 200
    
    data = response.json()
    assert "cloudformation_template" in data
    assert "architecture_diagram" in data
    assert "cost_estimate" in data
    assert "mcp_servers_enabled" in data
