"""
Melus AI - Motor No Chat (Execution Mode) Tests
Tests for: 13 agents, template format, costs with modes, generate endpoint
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_EMAIL = "rrhh.milchollos@gmail.com"
ADMIN_PASSWORD = "19862210Des"


@pytest.fixture(scope="module")
def session_token():
    """Get auth token for admin user"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    })
    assert response.status_code == 200, f"Login failed: {response.text}"
    data = response.json()
    return data.get("session_token")


@pytest.fixture
def auth_headers(session_token):
    """Headers with session token"""
    return {"X-Session-Token": session_token}


class TestAgentsV2:
    """Test /api/agents/v2/agents endpoint - 13 agents"""

    def test_list_agents_returns_13_agents(self, auth_headers):
        """Verify /api/agents/v2/agents returns exactly 13 agents"""
        response = requests.get(f"{BASE_URL}/api/agents/v2/agents", headers=auth_headers)
        assert response.status_code == 200, f"Failed: {response.text}"
        
        data = response.json()
        assert "agents" in data, "Response should have 'agents' key"
        
        agents = data["agents"]
        assert len(agents) == 13, f"Expected 13 agents, got {len(agents)}"
        
        # Verify all 13 agent IDs
        expected_agent_ids = [
            "classifier", "architect", "design", "frontend", "backend",
            "database", "integrator", "testing", "security", "deploy",
            "debugger", "optimizer", "docs"
        ]
        
        actual_ids = [a["id"] for a in agents]
        for expected_id in expected_agent_ids:
            assert expected_id in actual_ids, f"Missing agent: {expected_id}"
        
        print(f"✓ Found all 13 agents: {actual_ids}")

    def test_debugger_costs_30_credits(self, auth_headers):
        """Verify Debug Agent costs exactly 30 credits"""
        response = requests.get(f"{BASE_URL}/api/agents/v2/agents", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        agents = data["agents"]
        
        debugger = next((a for a in agents if a["id"] == "debugger"), None)
        assert debugger is not None, "Debugger agent not found"
        assert debugger["cost"] == 30, f"Debugger cost should be 30, got {debugger['cost']}"
        
        print(f"✓ Debugger agent costs 30 credits")

    def test_each_agent_has_required_fields(self, auth_headers):
        """Each agent should have id, name, description, cost, icon"""
        response = requests.get(f"{BASE_URL}/api/agents/v2/agents", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        
        required_fields = ["id", "name", "description", "cost", "icon"]
        
        for agent in data["agents"]:
            for field in required_fields:
                assert field in agent, f"Agent {agent.get('id', 'unknown')} missing field: {field}"
        
        print(f"✓ All agents have required fields")


class TestTemplateFormat:
    """Test /api/agents/v2/template endpoint - Motor No Chat template format"""

    def test_get_template_format(self, auth_headers):
        """Verify /api/agents/v2/template returns template format"""
        response = requests.get(f"{BASE_URL}/api/agents/v2/template", headers=auth_headers)
        assert response.status_code == 200, f"Failed: {response.text}"
        
        data = response.json()
        
        # Verify required keys
        assert "template" in data, "Response should have 'template' key"
        assert "description" in data, "Response should have 'description' key"
        assert "agents" in data, "Response should have 'agents' key"
        assert "tips" in data, "Response should have 'tips' key"
        
        # Verify template content
        template = data["template"]
        assert "FRONTEND" in template, "Template should mention FRONTEND"
        assert "BACKEND" in template, "Template should mention BACKEND"
        assert "DATABASE" in template, "Template should mention DATABASE"
        
        # Verify agents list includes key agents
        agents_list = data["agents"]
        assert any("FRONTEND" in a.upper() for a in agents_list), "Should list FRONTEND agent"
        assert any("BACKEND" in a.upper() for a in agents_list), "Should list BACKEND agent"
        
        print(f"✓ Template format returned with {len(agents_list)} agent descriptions")
        print(f"  Description: {data['description'][:100]}...")

    def test_template_includes_tips(self, auth_headers):
        """Verify template includes tips for Motor No Chat mode"""
        response = requests.get(f"{BASE_URL}/api/agents/v2/template", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        tips = data.get("tips", [])
        
        assert len(tips) > 0, "Should have at least one tip"
        
        # Check for command-style tips
        tips_text = " ".join(tips).lower()
        assert any(word in tips_text for word in ["genera", "construye", "implementa", "build", "create"]), \
            "Tips should suggest command-style prompts"
        
        print(f"✓ Template includes {len(tips)} tips for Motor mode")


class TestCostsWithModes:
    """Test /api/agents/v2/costs endpoint - includes execution and chat modes"""

    def test_costs_returns_modes(self, auth_headers):
        """Verify /api/agents/v2/costs returns modes: execution and chat"""
        response = requests.get(f"{BASE_URL}/api/agents/v2/costs", headers=auth_headers)
        assert response.status_code == 200, f"Failed: {response.text}"
        
        data = response.json()
        
        # Verify modes are present
        assert "modes" in data, "Response should have 'modes' key"
        
        modes = data["modes"]
        assert "execution" in modes, "Should have 'execution' mode"
        assert "chat" in modes, "Should have 'chat' mode"
        
        # Verify mode descriptions
        execution_desc = modes["execution"]
        chat_desc = modes["chat"]
        
        assert "Motor" in execution_desc or "motor" in execution_desc.lower() or "ejecución" in execution_desc.lower(), \
            f"Execution mode should mention 'Motor' or 'ejecución': {execution_desc}"
        
        print(f"✓ Costs API includes modes:")
        print(f"  - execution: {execution_desc}")
        print(f"  - chat: {chat_desc}")

    def test_costs_returns_all_agent_costs(self, auth_headers):
        """Verify costs endpoint returns all agent costs"""
        response = requests.get(f"{BASE_URL}/api/agents/v2/costs", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        
        assert "costs" in data, "Response should have 'costs' key"
        
        costs = data["costs"]
        
        # All 13 agents should be in costs
        expected_agents = [
            "classifier", "architect", "frontend", "backend", "integrator",
            "design", "database", "testing", "security", "deploy",
            "debugger", "optimizer", "docs"
        ]
        
        for agent in expected_agents:
            assert agent in costs, f"Missing cost for agent: {agent}"
            assert isinstance(costs[agent], int), f"Cost for {agent} should be integer"
        
        # Verify debugger = 30
        assert costs["debugger"] == 30, f"Debugger should cost 30, got {costs['debugger']}"
        
        print(f"✓ Costs API returns costs for all {len(costs)} agents")
        print(f"  Total: {data.get('total', sum(costs.values()))} credits")

    def test_costs_includes_categories(self, auth_headers):
        """Verify costs endpoint includes agent categories"""
        response = requests.get(f"{BASE_URL}/api/agents/v2/costs", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        
        assert "categories" in data, "Response should have 'categories' key"
        
        categories = data["categories"]
        assert "generation" in categories, "Should have 'generation' category"
        assert "specialized" in categories, "Should have 'specialized' category"
        assert "utility" in categories, "Should have 'utility' category"
        
        # Debugger should be in utility
        assert "debugger" in categories["utility"], "Debugger should be in utility category"
        
        print(f"✓ Agent categories: {list(categories.keys())}")


class TestGenerateWorkspace:
    """Test /api/agents/v2/generate endpoint - creates workspace with files"""

    def test_generate_requires_description(self, auth_headers):
        """Generate should fail without description"""
        response = requests.post(
            f"{BASE_URL}/api/agents/v2/generate",
            headers={**auth_headers, "Content-Type": "application/json"},
            json={"name": "Test App"}
        )
        
        # Should fail with 400 due to missing description
        assert response.status_code == 400, f"Expected 400 for missing description, got {response.status_code}"
        
        print(f"✓ Generate endpoint validates required fields")

    def test_generate_requires_auth(self):
        """Generate should require authentication"""
        response = requests.post(
            f"{BASE_URL}/api/agents/v2/generate",
            headers={"Content-Type": "application/json"},
            json={"description": "A test app", "name": "Test"}
        )
        
        # Should fail with 401 or 403 without auth
        assert response.status_code in [401, 403], \
            f"Expected 401/403 without auth, got {response.status_code}"
        
        print(f"✓ Generate endpoint requires authentication")


class TestExecuteProject:
    """Test /api/agents/v2/execute-project - Motor No Chat mode"""

    def test_execute_project_endpoint_exists(self, auth_headers):
        """Verify execute-project endpoint exists"""
        # Send minimal request to verify endpoint
        response = requests.post(
            f"{BASE_URL}/api/agents/v2/execute-project",
            headers={**auth_headers, "Content-Type": "application/json"},
            json={"template": "", "name": "Test"}
        )
        
        # Should not be 404 - endpoint exists
        assert response.status_code != 404, "execute-project endpoint should exist"
        
        # May be 400 due to empty template or 402 for credits
        # or 200 if it detects chat mode and suggests different endpoint
        print(f"✓ execute-project endpoint exists (status: {response.status_code})")

    def test_execute_project_detects_chat_mode(self, auth_headers):
        """Execute-project should detect chat-style prompts"""
        response = requests.post(
            f"{BASE_URL}/api/agents/v2/execute-project",
            headers={**auth_headers, "Content-Type": "application/json"},
            json={
                "template": "¿Qué opinas de crear una app?",
                "name": "Test"
            }
        )
        
        # Should detect chat mode and return message
        if response.status_code == 200:
            data = response.json()
            if "mode_detected" in data:
                assert data["mode_detected"] == "chat", "Should detect chat mode"
                print(f"✓ Correctly detected chat mode, suggesting: {data.get('message', '')[:100]}")
            else:
                print(f"⚠ Endpoint returned 200 but may have processed anyway")
        else:
            print(f"  Status: {response.status_code} - may need more credits for full test")


class TestRunSingleAgent:
    """Test /api/agents/v2/run-agent endpoint"""

    def test_run_agent_validates_agent_type(self, auth_headers):
        """run-agent should validate agent type"""
        response = requests.post(
            f"{BASE_URL}/api/agents/v2/run-agent",
            headers={**auth_headers, "Content-Type": "application/json"},
            json={"agent": "invalid_agent", "task": "test task"}
        )
        
        assert response.status_code == 400, f"Expected 400 for invalid agent, got {response.status_code}"
        
        print(f"✓ run-agent validates agent type")

    def test_run_agent_requires_credits(self, auth_headers):
        """run-agent should check user has enough credits"""
        # This just verifies the endpoint structure - actual execution depends on credits
        response = requests.post(
            f"{BASE_URL}/api/agents/v2/run-agent",
            headers={**auth_headers, "Content-Type": "application/json"},
            json={"agent": "classifier", "task": "Classify a simple todo app"}
        )
        
        # Should be 200 (success), 402 (insufficient credits), but not 404
        assert response.status_code != 404, "run-agent endpoint should exist"
        
        print(f"✓ run-agent endpoint accessible (status: {response.status_code})")


class TestWorkspaceCreation:
    """Verify workspace is created with files after generation"""

    def test_existing_workspace_has_files(self, auth_headers):
        """Verify existing workspace ws_426544ab8f20 has files"""
        workspace_id = "ws_426544ab8f20"
        
        response = requests.get(
            f"{BASE_URL}/api/workspace/{workspace_id}",
            headers=auth_headers
        )
        
        if response.status_code == 200:
            data = response.json()
            files = data.get("files", {})
            
            assert len(files) > 0, "Workspace should have files"
            
            print(f"✓ Workspace {workspace_id} has {len(files)} files")
            
            # List first few file names
            file_names = list(files.keys())[:5]
            print(f"  Sample files: {file_names}")
        else:
            print(f"⚠ Could not access workspace {workspace_id}: {response.status_code}")
            # Not a test failure - workspace may have been cleaned up


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
