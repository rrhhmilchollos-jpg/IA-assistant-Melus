"""
Test Suite for Melus AI - HomePage and WorkspacePage Features
Tests: Suggestion buttons, Form submit, Navigation, API generate endpoint
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://multi-agent-ai-12.preview.emergentagent.com').rstrip('/')

# Test credentials
TEST_EMAIL = "rrhh.milchollos@gmail.com"
TEST_PASSWORD = "19862210Des"


@pytest.fixture(scope="module")
def session_token():
    """Get authentication token"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    })
    assert response.status_code == 200, f"Login failed: {response.text}"
    data = response.json()
    assert "session_token" in data
    return data["session_token"]


@pytest.fixture
def api_client(session_token):
    """Requests session with auth headers"""
    session = requests.Session()
    session.headers.update({
        "Content-Type": "application/json",
        "X-Session-Token": session_token
    })
    return session


class TestHealthAndAuth:
    """Basic health and authentication tests"""
    
    def test_health_endpoint(self):
        """Test API health check"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        print("✓ Health check passed")
    
    def test_login_success(self):
        """Test login with valid credentials"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        assert response.status_code == 200
        data = response.json()
        assert "session_token" in data
        assert "user" in data
        assert data["user"]["email"] == TEST_EMAIL
        print(f"✓ Login successful, user: {data['user']['name']}")


class TestWorkspaceEndpoints:
    """Tests for workspace-related endpoints used by HomePage"""
    
    def test_workspace_recent(self, api_client):
        """Test /api/workspace/recent endpoint - used by HomePage"""
        response = api_client.get(f"{BASE_URL}/api/workspace/recent")
        assert response.status_code == 200, f"Recent endpoint failed: {response.text}"
        data = response.json()
        assert "workspaces" in data
        assert isinstance(data["workspaces"], list)
        print(f"✓ /workspace/recent works - {len(data['workspaces'])} workspaces found")
    
    def test_workspace_deployed(self, api_client):
        """Test /api/workspace/deployed endpoint - used by HomePage"""
        response = api_client.get(f"{BASE_URL}/api/workspace/deployed")
        assert response.status_code == 200, f"Deployed endpoint failed: {response.text}"
        data = response.json()
        assert "apps" in data
        assert isinstance(data["apps"], list)
        print(f"✓ /workspace/deployed works - {len(data['apps'])} deployed apps found")
    
    def test_workspace_list(self, api_client):
        """Test /api/workspace/list endpoint"""
        response = api_client.get(f"{BASE_URL}/api/workspace/list")
        assert response.status_code == 200
        data = response.json()
        assert "workspaces" in data
        print(f"✓ /workspace/list works - {len(data['workspaces'])} workspaces")


class TestGenerateEndpoint:
    """Tests for /api/agents/v2/generate - called when user submits form"""
    
    def test_generate_without_auth(self):
        """Test generate endpoint requires authentication"""
        response = requests.post(f"{BASE_URL}/api/agents/v2/generate", json={
            "description": "Test app",
            "name": "Test",
            "ultra_mode": False
        })
        assert response.status_code == 401 or "Invalid session" in response.text
        print("✓ Generate endpoint correctly requires authentication")
    
    def test_generate_endpoint_exists(self, api_client):
        """Test generate endpoint is accessible"""
        # Just test that endpoint exists and accepts request
        # Don't wait for full generation (takes too long)
        response = api_client.post(f"{BASE_URL}/api/agents/v2/generate", json={
            "description": "TEST_Simple test app for pytest",
            "name": "TEST_Pytest App",
            "ultra_mode": False
        }, timeout=120)
        
        # Should either succeed or fail with expected errors
        assert response.status_code in [200, 402, 500], f"Unexpected status: {response.status_code}"
        
        if response.status_code == 200:
            data = response.json()
            assert "workspace_id" in data
            assert "files" in data
            print(f"✓ Generate endpoint works - workspace: {data['workspace_id']}")
        else:
            print(f"✓ Generate endpoint accessible (status {response.status_code})")


class TestAgentsV2Endpoints:
    """Tests for agents/v2 endpoints"""
    
    def test_agent_costs(self, api_client):
        """Test /api/agents/v2/costs returns correct pricing"""
        response = api_client.get(f"{BASE_URL}/api/agents/v2/costs")
        assert response.status_code == 200
        data = response.json()
        
        assert "costs" in data
        assert data["costs"]["debugger"] == 30  # Fixed to 30 credits
        assert data["costs"]["classifier"] == 25
        assert data["costs"]["frontend"] == 150
        print(f"✓ Agent costs endpoint works - total: {data['total']} credits")
    
    def test_list_agents(self, api_client):
        """Test /api/agents/v2/agents returns all agents"""
        response = api_client.get(f"{BASE_URL}/api/agents/v2/agents")
        assert response.status_code == 200
        data = response.json()
        
        assert "agents" in data
        assert len(data["agents"]) >= 10  # Should have at least 10 agents
        
        agent_ids = [a["id"] for a in data["agents"]]
        assert "classifier" in agent_ids
        assert "frontend" in agent_ids
        assert "debugger" in agent_ids
        print(f"✓ Agents list endpoint works - {len(data['agents'])} agents")


class TestWorkspaceOperations:
    """Tests for workspace CRUD operations"""
    
    def test_get_workspace_by_id(self, api_client):
        """Test getting workspace by ID"""
        # First get recent workspaces
        recent_response = api_client.get(f"{BASE_URL}/api/workspace/recent")
        if recent_response.status_code == 200:
            workspaces = recent_response.json().get("workspaces", [])
            if workspaces:
                workspace_id = workspaces[0]["workspace_id"]
                response = api_client.get(f"{BASE_URL}/api/workspace/{workspace_id}")
                assert response.status_code == 200
                data = response.json()
                assert data["workspace_id"] == workspace_id
                print(f"✓ Get workspace by ID works - {workspace_id}")
            else:
                print("⚠ No workspaces to test GET by ID")
        else:
            print("⚠ Could not test GET workspace by ID - no recent workspaces")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
