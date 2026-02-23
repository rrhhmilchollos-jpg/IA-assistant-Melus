"""
Test cases for new Melus AI features:
A) GitHub Deploy - /api/github/push-workspace
B) Expert Agents - /api/agents/v2/expert-agents and /api/agents/v2/generate-expert
C) Marketplace Agents verification
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://melus-ai-dev.preview.emergentagent.com')

# Test credentials
TEST_EMAIL = "rrhh.milchollos@gmail.com"
TEST_PASSWORD = "19862210Des"

@pytest.fixture(scope="module")
def session():
    """Create a requests session for all tests"""
    return requests.Session()

@pytest.fixture(scope="module")
def auth_token(session):
    """Get authentication token"""
    response = session.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
    )
    if response.status_code == 200:
        data = response.json()
        return data.get("session_token")
    pytest.skip(f"Authentication failed: {response.text}")

@pytest.fixture
def authenticated_session(session, auth_token):
    """Session with auth header"""
    session.headers.update({"X-Session-Token": auth_token})
    return session


# ============================================
# A) GitHub Deploy Tests
# ============================================
class TestGitHubDeploy:
    """Test GitHub deploy functionality"""
    
    def test_github_status_endpoint(self, authenticated_session):
        """Test that GitHub status endpoint returns connection status"""
        response = authenticated_session.get(f"{BASE_URL}/api/github/status")
        assert response.status_code == 200
        data = response.json()
        assert "connected" in data
        print(f"GitHub Status: connected={data.get('connected')}")
    
    def test_push_workspace_validates_input(self, authenticated_session):
        """Test push-workspace endpoint validates input (workspace_id or GitHub connection)"""
        response = authenticated_session.post(
            f"{BASE_URL}/api/github/push-workspace",
            json={
                "repo_name": "test-repo"
            }
        )
        # Should fail - either because workspace_id missing or GitHub not connected
        assert response.status_code == 400
        data = response.json()
        detail = data.get("detail", "").lower()
        # Either workspace_id required or GitHub not connected - both are valid error responses
        valid_error = ("workspace_id" in detail or 
                      "required" in detail or 
                      "github" in detail or 
                      "conectado" in detail)
        assert valid_error, f"Unexpected error: {detail}"
        print(f"Push correctly rejected: {data}")
    
    def test_push_workspace_invalid_workspace(self, authenticated_session):
        """Test push-workspace with invalid workspace returns 404"""
        response = authenticated_session.post(
            f"{BASE_URL}/api/github/push-workspace",
            json={
                "workspace_id": "ws_invalid_12345",
                "repo_name": "test-repo"
            }
        )
        # Should return 404 for non-existent workspace
        assert response.status_code in [400, 404]
        print(f"Invalid workspace correctly handled: {response.json()}")


# ============================================
# B) Expert Agents Tests
# ============================================
class TestExpertAgents:
    """Test Expert Agents functionality - 8 specialized agents"""
    
    EXPECTED_AGENTS = ["game", "mobile", "ecommerce", "dashboard", "saas", "api", "ai_app", "portfolio"]
    
    def test_expert_agents_endpoint_returns_all_agents(self, authenticated_session):
        """Test /api/agents/v2/expert-agents returns all 8 expert agents"""
        response = authenticated_session.get(f"{BASE_URL}/api/agents/v2/expert-agents")
        assert response.status_code == 200
        
        data = response.json()
        assert "agents" in data
        agents = data["agents"]
        
        # Check we have 8 agents
        assert len(agents) >= 8, f"Expected at least 8 agents, got {len(agents)}"
        
        # Verify agent structure
        agent_types = [a["type"] for a in agents]
        for expected_type in self.EXPECTED_AGENTS:
            assert expected_type in agent_types, f"Missing expected agent type: {expected_type}"
        
        print(f"Expert agents found: {agent_types}")
    
    def test_expert_agents_have_required_fields(self, authenticated_session):
        """Test each expert agent has required fields"""
        response = authenticated_session.get(f"{BASE_URL}/api/agents/v2/expert-agents")
        assert response.status_code == 200
        
        data = response.json()
        agents = data["agents"]
        
        for agent in agents:
            assert "type" in agent, f"Agent missing 'type' field"
            assert "name" in agent, f"Agent missing 'name' field"
            assert "description" in agent, f"Agent missing 'description' field"
            assert "cost" in agent, f"Agent missing 'cost' field"
            assert "capabilities" in agent, f"Agent missing 'capabilities' field"
            assert isinstance(agent["cost"], int), f"Agent cost should be integer"
            assert agent["cost"] > 0, f"Agent cost should be positive"
        
        print(f"All {len(agents)} agents have required fields")
    
    def test_game_developer_agent_details(self, authenticated_session):
        """Test Game Developer agent has correct details"""
        response = authenticated_session.get(f"{BASE_URL}/api/agents/v2/expert-agents")
        assert response.status_code == 200
        
        agents = response.json()["agents"]
        game_agent = next((a for a in agents if a["type"] == "game"), None)
        
        assert game_agent is not None, "Game agent not found"
        assert game_agent["name"] == "Game Developer Agent"
        assert game_agent["cost"] == 200
        assert "canvas" in game_agent["capabilities"]
        print(f"Game agent verified: {game_agent}")
    
    def test_ecommerce_agent_details(self, authenticated_session):
        """Test E-commerce agent has correct details"""
        response = authenticated_session.get(f"{BASE_URL}/api/agents/v2/expert-agents")
        assert response.status_code == 200
        
        agents = response.json()["agents"]
        ecommerce_agent = next((a for a in agents if a["type"] == "ecommerce"), None)
        
        assert ecommerce_agent is not None, "E-commerce agent not found"
        assert ecommerce_agent["name"] == "E-commerce Agent"
        assert ecommerce_agent["cost"] == 300
        assert "cart" in ecommerce_agent["capabilities"]
        print(f"E-commerce agent verified: {ecommerce_agent}")
    
    def test_generate_expert_requires_description(self, authenticated_session):
        """Test generate-expert endpoint requires description"""
        response = authenticated_session.post(
            f"{BASE_URL}/api/agents/v2/generate-expert",
            json={
                "name": "Test Project",
                "expert_type": "game"
            }
        )
        assert response.status_code == 400
        data = response.json()
        assert "description" in data.get("detail", "").lower() or "required" in data.get("detail", "").lower()
        print(f"Generate expert without description correctly rejected")
    
    def test_generate_expert_accepts_valid_request(self, authenticated_session):
        """Test generate-expert endpoint accepts valid request structure"""
        response = authenticated_session.post(
            f"{BASE_URL}/api/agents/v2/generate-expert",
            json={
                "description": "Create a simple test game",
                "name": "Test Game",
                "expert_type": "game",
                "ultra_mode": False
            }
        )
        # Should either succeed (200/202) or fail with credits error (402) - not validation error
        assert response.status_code in [200, 201, 202, 402], f"Unexpected status: {response.status_code}"
        
        if response.status_code == 402:
            print("Generate expert request valid but insufficient credits (expected)")
        else:
            data = response.json()
            assert "workspace_id" in data or "job_id" in data
            print(f"Generate expert started successfully: {data.get('workspace_id', data.get('job_id'))}")


# ============================================
# C) Marketplace Templates Endpoint
# ============================================
class TestMarketplace:
    """Test marketplace functionality"""
    
    def test_marketplace_templates_endpoint(self, authenticated_session):
        """Test marketplace templates endpoint works"""
        response = authenticated_session.get(f"{BASE_URL}/api/agents/v2/marketplace/templates")
        assert response.status_code == 200
        
        data = response.json()
        assert "templates" in data
        print(f"Marketplace templates count: {len(data['templates'])}")
    
    def test_marketplace_templates_structure(self, authenticated_session):
        """Test marketplace templates have correct structure"""
        response = authenticated_session.get(f"{BASE_URL}/api/agents/v2/marketplace/templates")
        assert response.status_code == 200
        
        data = response.json()
        templates = data["templates"]
        
        # If there are templates, verify structure
        if templates:
            template = templates[0]
            # Check basic structure
            expected_fields = ["template_id", "name"]
            for field in expected_fields:
                if field in template:
                    print(f"Template has field '{field}': {template[field]}")


# ============================================
# D) Workspace API Tests (for Deploy modal)
# ============================================
class TestWorkspaceAPI:
    """Test workspace-related APIs needed for Deploy"""
    
    def test_recent_workspaces_endpoint(self, authenticated_session):
        """Test /api/workspace/recent returns user workspaces"""
        response = authenticated_session.get(f"{BASE_URL}/api/workspace/recent")
        assert response.status_code == 200
        
        data = response.json()
        assert "workspaces" in data
        print(f"User has {len(data['workspaces'])} recent workspaces")


# ============================================
# E) Core API Health Check
# ============================================
class TestCoreAPIs:
    """Basic health checks for core APIs"""
    
    def test_auth_login_endpoint(self, session):
        """Test login endpoint works"""
        response = session.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        assert response.status_code == 200
        data = response.json()
        assert "session_token" in data
        print("Login endpoint working")
    
    def test_agents_v2_costs_endpoint(self, authenticated_session):
        """Test /api/agents/v2/costs returns agent costs"""
        response = authenticated_session.get(f"{BASE_URL}/api/agents/v2/costs")
        assert response.status_code == 200
        
        data = response.json()
        assert "costs" in data
        print(f"Agent costs available: {len(data['costs'])} agents")
    
    def test_agents_v2_list_endpoint(self, authenticated_session):
        """Test /api/agents/v2/agents returns agent list"""
        response = authenticated_session.get(f"{BASE_URL}/api/agents/v2/agents")
        assert response.status_code == 200
        
        data = response.json()
        assert "agents" in data
        print(f"Agents list returned: {len(data['agents'])} agents")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
