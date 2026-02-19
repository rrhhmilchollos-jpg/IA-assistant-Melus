"""
Backend API Tests for Assistant Melus
Tests: Authentication (Register, Login), Conversations, Messages, Credits
"""
import pytest
import requests
import os
import uuid
import time

# Base URL from environment - using external URL for e2e testing
BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://melus-studio.preview.emergentagent.com')

# Test data
TEST_EMAIL_PREFIX = "TEST_"
TEST_PASSWORD = "testpass123"

def generate_test_email():
    """Generate unique test email"""
    return f"{TEST_EMAIL_PREFIX}user_{uuid.uuid4().hex[:8]}@test.com"


class TestHealthCheck:
    """Health check tests - run first"""
    
    def test_api_root_accessible(self):
        """Test API root endpoint is accessible"""
        response = requests.get(f"{BASE_URL}/api/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert data["message"] == "Assistant Melus API"
        print("✓ API root endpoint accessible")


class TestModels:
    """AI Models endpoint tests"""
    
    def test_get_available_models(self):
        """Test getting available AI models"""
        response = requests.get(f"{BASE_URL}/api/models")
        assert response.status_code == 200
        models = response.json()
        assert isinstance(models, list)
        assert len(models) > 0
        
        # Check model structure
        model = models[0]
        assert "model_id" in model
        assert "name" in model
        assert "provider" in model
        print(f"✓ Got {len(models)} available models")


class TestAuthentication:
    """Authentication tests - Register and Login"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test data"""
        self.test_email = generate_test_email()
        self.test_name = "Test User"
        self.test_password = TEST_PASSWORD
        
    def test_register_new_user(self):
        """Test user registration"""
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": self.test_email,
            "password": self.test_password,
            "name": self.test_name
        })
        
        assert response.status_code == 200, f"Registration failed: {response.text}"
        data = response.json()
        
        # Verify response structure
        assert "user" in data
        assert "session_token" in data
        assert "message" in data
        
        # Verify user data
        user = data["user"]
        assert user["email"] == self.test_email
        assert user["name"] == self.test_name
        assert "credits" in user
        assert user["credits"] >= 0  # Should have some free credits
        
        print(f"✓ Registered user: {self.test_email} with {user['credits']} credits")
        
    def test_register_duplicate_email(self):
        """Test registration with duplicate email fails"""
        # First registration
        email = generate_test_email()
        response1 = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": email,
            "password": self.test_password,
            "name": "First User"
        })
        assert response1.status_code == 200
        
        # Second registration with same email
        response2 = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": email,
            "password": self.test_password,
            "name": "Second User"
        })
        assert response2.status_code == 400
        assert "already registered" in response2.json()["detail"].lower()
        print("✓ Duplicate email registration rejected")
        
    def test_register_invalid_email(self):
        """Test registration with invalid email format"""
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": "invalid-email",
            "password": self.test_password,
            "name": "Test User"
        })
        assert response.status_code == 400
        print("✓ Invalid email rejected")
        
    def test_register_short_password(self):
        """Test registration with too short password"""
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": generate_test_email(),
            "password": "12345",  # Less than 6 chars
            "name": "Test User"
        })
        assert response.status_code == 400
        print("✓ Short password rejected")
    
    def test_login_success(self):
        """Test login with valid credentials"""
        # First register
        email = generate_test_email()
        reg_response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": email,
            "password": self.test_password,
            "name": "Login Test User"
        })
        assert reg_response.status_code == 200
        
        # Then login
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": email,
            "password": self.test_password
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "user" in data
        assert "session_token" in data
        assert data["user"]["email"] == email
        print(f"✓ Login successful for: {email}")
        
    def test_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "nonexistent@test.com",
            "password": "wrongpassword"
        })
        assert response.status_code == 401
        print("✓ Invalid credentials rejected")
        
    def test_login_wrong_password(self):
        """Test login with wrong password"""
        # First register
        email = generate_test_email()
        requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": email,
            "password": self.test_password,
            "name": "Test User"
        })
        
        # Login with wrong password
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": email,
            "password": "wrongpassword"
        })
        assert response.status_code == 401
        print("✓ Wrong password rejected")


class TestAuthenticatedEndpoints:
    """Tests for endpoints requiring authentication"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup - register and get session token"""
        self.test_email = generate_test_email()
        self.test_password = TEST_PASSWORD
        
        # Register user
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": self.test_email,
            "password": self.test_password,
            "name": "Auth Test User"
        })
        assert response.status_code == 200
        data = response.json()
        self.session_token = data["session_token"]
        self.user = data["user"]
        
        # Session with auth header
        self.session = requests.Session()
        self.session.headers.update({
            "X-Session-Token": self.session_token,
            "Content-Type": "application/json"
        })
        
    def test_get_current_user(self):
        """Test getting current authenticated user"""
        response = self.session.get(f"{BASE_URL}/api/auth/me")
        assert response.status_code == 200
        
        data = response.json()
        assert data["email"] == self.test_email
        print("✓ Current user retrieved successfully")
        
    def test_unauthorized_without_token(self):
        """Test endpoints require authentication"""
        response = requests.get(f"{BASE_URL}/api/auth/me")
        assert response.status_code == 401
        print("✓ Unauthorized access properly rejected")


class TestConversations:
    """Conversation CRUD tests"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup - create authenticated session"""
        self.test_email = generate_test_email()
        self.test_password = TEST_PASSWORD
        
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": self.test_email,
            "password": self.test_password,
            "name": "Conversation Test User"
        })
        assert response.status_code == 200
        data = response.json()
        self.session_token = data["session_token"]
        
        self.session = requests.Session()
        self.session.headers.update({
            "X-Session-Token": self.session_token,
            "Content-Type": "application/json"
        })
        
    def test_create_conversation(self):
        """Test creating a new conversation"""
        response = self.session.post(f"{BASE_URL}/api/conversations", json={
            "title": "TEST_New Conversation",
            "model": "gpt-4o"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "conversation_id" in data
        assert data["title"] == "TEST_New Conversation"
        assert data["model"] == "gpt-4o"
        print(f"✓ Created conversation: {data['conversation_id']}")
        
    def test_get_conversations_list(self):
        """Test getting list of conversations"""
        # Create a conversation first
        self.session.post(f"{BASE_URL}/api/conversations", json={
            "title": "TEST_List Test",
            "model": "gpt-4o"
        })
        
        response = self.session.get(f"{BASE_URL}/api/conversations")
        assert response.status_code == 200
        
        conversations = response.json()
        assert isinstance(conversations, list)
        print(f"✓ Retrieved {len(conversations)} conversations")
        
    def test_delete_conversation(self):
        """Test deleting a conversation"""
        # Create conversation
        create_response = self.session.post(f"{BASE_URL}/api/conversations", json={
            "title": "TEST_To Delete",
            "model": "gpt-4o"
        })
        conv_id = create_response.json()["conversation_id"]
        
        # Delete conversation
        delete_response = self.session.delete(f"{BASE_URL}/api/conversations/{conv_id}")
        assert delete_response.status_code == 200
        
        # Verify deleted (should not appear in list)
        list_response = self.session.get(f"{BASE_URL}/api/conversations")
        conversations = list_response.json()
        conv_ids = [c["conversation_id"] for c in conversations]
        assert conv_id not in conv_ids
        print(f"✓ Deleted conversation: {conv_id}")
        
    def test_fork_conversation(self):
        """Test forking a conversation"""
        # Create original conversation
        create_response = self.session.post(f"{BASE_URL}/api/conversations", json={
            "title": "TEST_Original",
            "model": "gpt-4o"
        })
        original_id = create_response.json()["conversation_id"]
        
        # Fork it
        fork_response = self.session.post(f"{BASE_URL}/api/conversations", json={
            "title": "TEST_Fork",
            "fork_from": original_id
        })
        assert fork_response.status_code == 200
        fork_data = fork_response.json()
        assert fork_data["forked_from"] == original_id
        print(f"✓ Forked conversation from {original_id}")


class TestMessages:
    """Message sending tests"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup - create authenticated session and conversation"""
        self.test_email = generate_test_email()
        self.test_password = TEST_PASSWORD
        
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": self.test_email,
            "password": self.test_password,
            "name": "Message Test User"
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
        
        # Create conversation
        conv_response = self.session.post(f"{BASE_URL}/api/conversations", json={
            "title": "TEST_Message Test",
            "model": "gpt-4o"
        })
        self.conversation_id = conv_response.json()["conversation_id"]
        
    def test_send_message_and_get_response(self):
        """Test sending a message and receiving AI response"""
        response = self.session.post(
            f"{BASE_URL}/api/conversations/{self.conversation_id}/messages",
            json={"content": "Hola, ¿cómo estás?"}
        )
        
        # Check if credits are sufficient or if we get 402
        if response.status_code == 402:
            print("⚠ Insufficient credits for message test - skipping")
            pytest.skip("Insufficient credits")
            
        assert response.status_code == 200, f"Message send failed: {response.text}"
        data = response.json()
        
        # Verify response structure
        assert "user_message" in data
        assert "assistant_message" in data
        assert "tokens_used" in data
        assert "credits_remaining" in data
        
        # Verify user message
        assert data["user_message"]["role"] == "user"
        assert data["user_message"]["content"] == "Hola, ¿cómo estás?"
        
        # Verify assistant message
        assert data["assistant_message"]["role"] == "assistant"
        assert len(data["assistant_message"]["content"]) > 0
        
        print(f"✓ Message sent and AI responded with {data['tokens_used']} tokens")
        
    def test_get_conversation_messages(self):
        """Test getting messages from a conversation"""
        # Send a message first
        self.session.post(
            f"{BASE_URL}/api/conversations/{self.conversation_id}/messages",
            json={"content": "Test message"}
        )
        
        # Get messages
        response = self.session.get(
            f"{BASE_URL}/api/conversations/{self.conversation_id}/messages"
        )
        assert response.status_code == 200
        messages = response.json()
        assert isinstance(messages, list)
        print(f"✓ Retrieved {len(messages)} messages")


class TestCredits:
    """Credits system tests"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup - create authenticated session"""
        self.test_email = generate_test_email()
        self.test_password = TEST_PASSWORD
        
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": self.test_email,
            "password": self.test_password,
            "name": "Credits Test User"
        })
        assert response.status_code == 200
        data = response.json()
        self.session_token = data["session_token"]
        
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
        print(f"✓ Credit balance: {data['credits']} credits")
        
    def test_get_credit_packages(self):
        """Test getting available credit packages"""
        response = self.session.get(f"{BASE_URL}/api/credits/packages")
        assert response.status_code == 200
        
        packages = response.json()
        assert isinstance(packages, list)
        assert len(packages) > 0
        
        # Check package structure
        package = packages[0]
        assert "package_id" in package
        assert "name" in package
        assert "credits" in package
        assert "price" in package
        print(f"✓ Got {len(packages)} credit packages")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
