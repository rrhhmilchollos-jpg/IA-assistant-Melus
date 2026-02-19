"""
Backend API Tests for Assistant Melus - Admin, Agents, Credits Features
Tests: Admin Panel, Multi-Agent System, Credits, Admin Dashboard
"""
import pytest
import requests
import os
import uuid

# Base URL from environment
BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://motor-no-chat.preview.emergentagent.com')

# Admin credentials
ADMIN_EMAIL = "rrhh.milchollos@gmail.com"
ADMIN_PASSWORD = "19862210Des"


class TestHealthAndBase:
    """Health check and base endpoint tests"""
    
    def test_api_health(self):
        """Test API health endpoint"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "operational"
        assert data["database"] == "healthy"
        print("✓ API health check passed")
    
    def test_api_root(self):
        """Test API root returns expected info"""
        response = requests.get(f"{BASE_URL}/api/")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Assistant Melus API"
        assert data["version"] == "2.0.0"
        print("✓ API root endpoint accessible")


class TestAgentsCosts:
    """Agent costs endpoint tests - Public API"""
    
    def test_get_agent_costs(self):
        """Test getting agent costs without authentication"""
        response = requests.get(f"{BASE_URL}/api/agents/costs")
        assert response.status_code == 200
        
        data = response.json()
        assert "costs" in data
        assert "descriptions" in data
        
        # Verify expected agent costs
        costs = data["costs"]
        assert costs["orchestrator"] == 50
        assert costs["design"] == 100
        assert costs["frontend"] == 150
        assert costs["backend"] == 150
        assert costs["database"] == 100
        assert costs["deploy"] == 200
        print(f"✓ Agent costs retrieved: {costs}")


class TestAdminAuthentication:
    """Admin user authentication tests"""
    
    def test_admin_login_success(self):
        """Test admin login with valid credentials"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        
        assert response.status_code == 200, f"Admin login failed: {response.text}"
        data = response.json()
        
        # Verify response structure
        assert "user" in data
        assert "session_token" in data
        assert "message" in data
        
        # Verify admin user data
        user = data["user"]
        assert user["email"] == ADMIN_EMAIL
        assert user["is_admin"] == True, "User should be admin"
        assert user["credits"] > 0, "Admin should have credits"
        
        print(f"✓ Admin login successful: {user['name']} with {user['credits']} credits")
        return data["session_token"]
    
    def test_admin_login_invalid_password(self):
        """Test admin login with wrong password"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": "wrongpassword"
        })
        assert response.status_code == 401
        print("✓ Admin invalid password rejected")


class TestAdminDashboard:
    """Admin panel dashboard tests"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup - login as admin"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200
        self.session_token = response.json()["session_token"]
        
        self.session = requests.Session()
        self.session.headers.update({
            "X-Session-Token": self.session_token,
            "Content-Type": "application/json"
        })
    
    def test_get_admin_dashboard(self):
        """Test admin dashboard data retrieval"""
        response = self.session.get(f"{BASE_URL}/api/admin/dashboard")
        assert response.status_code == 200, f"Dashboard request failed: {response.text}"
        
        data = response.json()
        
        # Verify response structure
        assert "users" in data
        assert "revenue" in data
        assert "credits" in data
        assert "agent_usage" in data
        assert "subscriptions" in data
        assert "recent_projects" in data
        
        # Verify user stats
        assert "total" in data["users"]
        assert "active_24h" in data["users"]
        assert data["users"]["total"] >= 0
        
        # Verify revenue stats
        assert "total" in data["revenue"]
        assert "today" in data["revenue"]
        
        # Verify credits stats
        assert "total_used" in data["credits"]
        assert "total_available" in data["credits"]
        
        print(f"✓ Admin dashboard loaded: {data['users']['total']} users, ${data['revenue']['total']} revenue")
    
    def test_get_admin_users_list(self):
        """Test admin users list retrieval"""
        response = self.session.get(f"{BASE_URL}/api/admin/users?limit=10&skip=0")
        assert response.status_code == 200
        
        data = response.json()
        assert "users" in data
        assert "total" in data
        assert isinstance(data["users"], list)
        
        # Verify user structure
        if len(data["users"]) > 0:
            user = data["users"][0]
            assert "email" in user
            assert "credits" in user
            # Should not have password_hash
            assert "password_hash" not in user
        
        print(f"✓ Admin users list: {len(data['users'])} users (total: {data['total']})")
    
    def test_get_admin_system_health(self):
        """Test admin system health check"""
        response = self.session.get(f"{BASE_URL}/api/admin/system-health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "operational"
        assert "services" in data
        assert data["services"]["mongodb"] == "healthy"
        assert data["services"]["api"] == "healthy"
        assert "metrics" in data
        
        print(f"✓ System health: {data['status']}")
    
    def test_get_admin_transactions(self):
        """Test admin transactions list"""
        response = self.session.get(f"{BASE_URL}/api/admin/transactions?limit=10&skip=0")
        assert response.status_code == 200
        
        data = response.json()
        assert "transactions" in data
        assert "total" in data
        
        print(f"✓ Admin transactions: {data['total']} total")
    
    def test_get_admin_projects(self):
        """Test admin projects list"""
        response = self.session.get(f"{BASE_URL}/api/admin/projects?limit=10&skip=0")
        assert response.status_code == 200
        
        data = response.json()
        assert "projects" in data
        assert "total" in data
        
        print(f"✓ Admin projects: {data['total']} total")
    
    def test_get_revenue_chart(self):
        """Test admin revenue chart data"""
        response = self.session.get(f"{BASE_URL}/api/admin/revenue/chart?days=30")
        assert response.status_code == 200
        
        data = response.json()
        assert "data" in data
        assert "period_days" in data
        assert data["period_days"] == 30
        
        print(f"✓ Revenue chart: {len(data['data'])} data points")
    
    def test_get_credit_costs_settings(self):
        """Test admin credit costs settings retrieval"""
        response = self.session.get(f"{BASE_URL}/api/admin/settings/credit-costs")
        assert response.status_code == 200
        
        data = response.json()
        assert "costs" in data
        
        print(f"✓ Credit costs settings retrieved")


class TestAdminDashboardUnauthorized:
    """Test admin endpoints reject non-admin users"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup - register a regular user"""
        self.test_email = f"TEST_nonadmin_{uuid.uuid4().hex[:8]}@test.com"
        self.test_password = "testpass123"
        
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": self.test_email,
            "password": self.test_password,
            "name": "Non-Admin User"
        })
        assert response.status_code == 200
        data = response.json()
        self.session_token = data["session_token"]
        
        self.session = requests.Session()
        self.session.headers.update({
            "X-Session-Token": self.session_token,
            "Content-Type": "application/json"
        })
    
    def test_non_admin_cannot_access_dashboard(self):
        """Test non-admin users are rejected from admin endpoints"""
        response = self.session.get(f"{BASE_URL}/api/admin/dashboard")
        assert response.status_code == 403, "Non-admin should be rejected"
        print("✓ Non-admin user rejected from admin dashboard")
    
    def test_non_admin_cannot_access_users(self):
        """Test non-admin cannot access users list"""
        response = self.session.get(f"{BASE_URL}/api/admin/users")
        assert response.status_code == 403
        print("✓ Non-admin user rejected from admin users")


class TestCreditsSystem:
    """Credits system tests"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup - login as admin"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200
        self.session_token = response.json()["session_token"]
        
        self.session = requests.Session()
        self.session.headers.update({
            "X-Session-Token": self.session_token,
            "Content-Type": "application/json"
        })
    
    def test_get_credit_balance(self):
        """Test getting credit balance"""
        response = self.session.get(f"{BASE_URL}/api/credits")
        assert response.status_code == 200
        
        data = response.json()
        assert "credits" in data
        assert "credits_used" in data
        assert "subscription_tier" in data
        assert data["credits"] > 0
        
        print(f"✓ Credit balance: {data['credits']} credits")
    
    def test_get_credit_packages(self):
        """Test getting available credit packages"""
        response = self.session.get(f"{BASE_URL}/api/credits/packages")
        assert response.status_code == 200
        
        packages = response.json()
        assert isinstance(packages, list)
        assert len(packages) > 0
        
        # Verify package structure
        for pkg in packages:
            assert "package_id" in pkg
            assert "name" in pkg
            assert "credits" in pkg
            assert "price" in pkg
        
        print(f"✓ Credit packages: {len(packages)} available")
    
    def test_get_subscription_plans(self):
        """Test getting subscription plans"""
        response = self.session.get(f"{BASE_URL}/api/credits/subscriptions")
        assert response.status_code == 200
        
        plans = response.json()
        assert isinstance(plans, list)
        
        # Check for expected plans
        plan_ids = [p["plan_id"] for p in plans]
        assert "free" in plan_ids or "pro" in plan_ids or "enterprise" in plan_ids
        
        print(f"✓ Subscription plans: {len(plans)} available")
    
    def test_get_credit_usage(self):
        """Test getting credit usage breakdown"""
        response = self.session.get(f"{BASE_URL}/api/credits/usage")
        assert response.status_code == 200
        
        data = response.json()
        assert "total_credits" in data
        assert "total_used" in data
        assert "usage_by_agent" in data
        
        print(f"✓ Credit usage: {data['total_used']} used of {data['total_credits']}")
    
    def test_validate_promo_code_valid(self):
        """Test validating a valid promo code"""
        response = self.session.post(f"{BASE_URL}/api/credits/validate-promo", json={
            "promo_code": "WELCOME10",
            "amount": 50.00
        })
        assert response.status_code == 200
        
        data = response.json()
        assert data["valid"] == True
        assert data["discount_percent"] == 10.0
        
        print(f"✓ Promo code validated: {data['discount_percent']}% off")
    
    def test_validate_promo_code_invalid(self):
        """Test invalid promo code rejection"""
        response = self.session.post(f"{BASE_URL}/api/credits/validate-promo", json={
            "promo_code": "INVALIDCODE",
            "amount": 50.00
        })
        assert response.status_code == 400
        print("✓ Invalid promo code rejected")


class TestAgentSystem:
    """Multi-Agent system tests"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup - login as admin (has sufficient credits)"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200
        data = response.json()
        self.session_token = data["session_token"]
        self.initial_credits = data["user"]["credits"]
        
        self.session = requests.Session()
        self.session.headers.update({
            "X-Session-Token": self.session_token,
            "Content-Type": "application/json"
        })
    
    def test_analyze_project(self):
        """Test project analysis with orchestrator agent"""
        # Skip if credits are low
        if self.initial_credits < 100:
            pytest.skip("Insufficient credits for agent test")
        
        response = self.session.post(f"{BASE_URL}/api/agents/analyze", json={
            "description": "Una aplicación de lista de tareas simple con autenticación de usuarios"
        })
        
        assert response.status_code == 200, f"Analyze failed: {response.text}"
        
        data = response.json()
        assert "analysis" in data
        assert "credits_used" in data
        assert "credits_remaining" in data
        assert data["credits_used"] == 50  # Orchestrator cost
        
        print(f"✓ Project analysis completed, used {data['credits_used']} credits")


class TestProjectsAPI:
    """Projects API tests"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup - login as admin"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200
        self.session_token = response.json()["session_token"]
        
        self.session = requests.Session()
        self.session.headers.update({
            "X-Session-Token": self.session_token,
            "Content-Type": "application/json"
        })
    
    def test_create_project(self):
        """Test creating a new project"""
        response = self.session.post(f"{BASE_URL}/api/projects", json={
            "name": "TEST_Project",
            "description": "A test project for automated testing"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "project_id" in data
        assert data["name"] == "TEST_Project"
        assert data["status"] == "draft"
        
        self.project_id = data["project_id"]
        print(f"✓ Project created: {data['project_id']}")
        
        # Cleanup - delete the project
        self.session.delete(f"{BASE_URL}/api/projects/{self.project_id}")
    
    def test_get_projects_list(self):
        """Test getting projects list"""
        response = self.session.get(f"{BASE_URL}/api/projects")
        assert response.status_code == 200
        
        projects = response.json()
        assert isinstance(projects, list)
        
        print(f"✓ Projects list: {len(projects)} projects")


class TestChatAPIWithCredits:
    """Chat API tests using admin with sufficient credits"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup - login as admin"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200
        data = response.json()
        self.session_token = data["session_token"]
        self.credits = data["user"]["credits"]
        
        self.session = requests.Session()
        self.session.headers.update({
            "X-Session-Token": self.session_token,
            "Content-Type": "application/json"
        })
    
    def test_create_conversation_and_chat(self):
        """Test creating conversation and sending chat message"""
        # Create conversation
        conv_response = self.session.post(f"{BASE_URL}/api/conversations", json={
            "title": "TEST_Admin Chat",
            "model": "gpt-4o"
        })
        assert conv_response.status_code == 200
        conv_data = conv_response.json()
        conv_id = conv_data["conversation_id"]
        
        # Skip chat if low credits
        if self.credits < 200:
            print("⚠ Skipping chat test due to low credits")
            pytest.skip("Insufficient credits for chat test")
        
        # Send message
        msg_response = self.session.post(
            f"{BASE_URL}/api/conversations/{conv_id}/messages",
            json={"content": "Hola, soy una prueba automatizada"}
        )
        
        assert msg_response.status_code == 200, f"Chat failed: {msg_response.text}"
        
        data = msg_response.json()
        assert "user_message" in data
        assert "assistant_message" in data
        assert data["user_message"]["role"] == "user"
        assert data["assistant_message"]["role"] == "assistant"
        
        print(f"✓ Chat message sent successfully, used {data['tokens_used']} tokens")
        
        # Cleanup
        self.session.delete(f"{BASE_URL}/api/conversations/{conv_id}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
