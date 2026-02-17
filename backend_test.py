#!/usr/bin/env python3
"""
Comprehensive Backend API Tests for Assistant Melus
Tests all endpoints according to the review request
"""

import requests
import json
import uuid
from datetime import datetime, timezone
import sys
import os
from pymongo import MongoClient
import asyncio
import traceback

# Configuration
BASE_URL = "https://melus-preview.preview.emergentagent.com/api"
MONGO_URL = "mongodb://localhost:27017"
DB_NAME = "test_database"

class BackendTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.session_token = None
        self.test_user_id = None
        self.conversation_id = None
        self.mongo_client = None
        self.db = None
        
    def setup_mongo_connection(self):
        """Setup MongoDB connection for manual session creation"""
        try:
            self.mongo_client = MongoClient(MONGO_URL)
            self.db = self.mongo_client[DB_NAME]
            print("✓ MongoDB connection established")
            return True
        except Exception as e:
            print(f"❌ MongoDB connection failed: {e}")
            return False
    
    def create_test_user_and_session(self):
        """Manually create a test user and session in MongoDB"""
        try:
            # Generate test user data
            user_id = f"user_{uuid.uuid4().hex[:12]}"
            session_token = f"session_{uuid.uuid4().hex[:16]}"
            current_time = datetime.now(timezone.utc)
            
            # Create test user
            test_user = {
                "user_id": user_id,
                "email": "testuser@example.com",
                "name": "Test User",
                "picture": "https://example.com/avatar.jpg",
                "credits": 10000,  # Free credits
                "credits_used": 0,
                "created_at": current_time,
                "updated_at": current_time
            }
            
            # Insert user
            self.db.users.insert_one(test_user)
            
            # Create session
            test_session = {
                "session_id": f"sess_{uuid.uuid4().hex[:12]}",
                "user_id": user_id,
                "session_token": session_token,
                "expires_at": current_time.replace(hour=23, minute=59, second=59),
                "created_at": current_time
            }
            
            # Insert session
            self.db.user_sessions.insert_one(test_session)
            
            # Store for testing
            self.test_user_id = user_id
            self.session_token = session_token
            
            print(f"✓ Test user created: {user_id}")
            print(f"✓ Test session created: {session_token}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to create test user/session: {e}")
            traceback.print_exc()
            return False
    
    def cleanup_test_data(self):
        """Clean up test data from MongoDB"""
        try:
            if self.test_user_id:
                # Delete test user
                self.db.users.delete_one({"user_id": self.test_user_id})
                
                # Delete user sessions
                self.db.user_sessions.delete_many({"user_id": self.test_user_id})
                
                # Delete conversations and messages
                conversations = self.db.conversations.find({"user_id": self.test_user_id})
                for conv in conversations:
                    conv_id = conv["conversation_id"]
                    self.db.messages.delete_many({"conversation_id": conv_id})
                
                self.db.conversations.delete_many({"user_id": self.test_user_id})
                
                print(f"✓ Cleaned up test data for user: {self.test_user_id}")
        except Exception as e:
            print(f"⚠️ Warning: Failed to cleanup test data: {e}")
    
    def make_request(self, method, endpoint, data=None, headers=None, require_auth=True):
        """Make HTTP request with optional authentication"""
        url = f"{self.base_url}{endpoint}"
        
        # Setup headers
        request_headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        if require_auth and self.session_token:
            request_headers["Authorization"] = f"Bearer {self.session_token}"
            
        if headers:
            request_headers.update(headers)
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=request_headers, timeout=30)
            elif method.upper() == "POST":
                response = requests.post(url, headers=request_headers, json=data, timeout=30)
            elif method.upper() == "DELETE":
                response = requests.delete(url, headers=request_headers, timeout=30)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            return response
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed for {method} {endpoint}: {e}")
            return None
    
    def test_basic_health_check(self):
        """Test 1: Basic Health Check - GET /api/"""
        print("\n=== TEST 1: Basic Health Check ===")
        
        response = self.make_request("GET", "/", require_auth=False)
        
        if response is None:
            return False
            
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"✓ Health check passed: {data}")
                return True
            except json.JSONDecodeError:
                print(f"❌ Health check returned invalid JSON: {response.text}")
                return False
        else:
            print(f"❌ Health check failed: {response.status_code} - {response.text}")
            return False
    
    def test_credit_packages(self):
        """Test 2: Credit Packages (No Auth Required) - GET /api/credits/packages"""
        print("\n=== TEST 2: Credit Packages ===")
        
        response = self.make_request("GET", "/credits/packages", require_auth=False)
        
        if response is None:
            return False
            
        if response.status_code == 200:
            try:
                packages = response.json()
                print(f"✓ Credit packages retrieved: {len(packages)} packages")
                for package in packages:
                    print(f"  - {package.get('name', 'Unknown')}: {package.get('credits', 0)} credits for ${package.get('price', 0)}")
                return True
            except json.JSONDecodeError:
                print(f"❌ Credit packages returned invalid JSON: {response.text}")
                return False
        else:
            print(f"❌ Credit packages failed: {response.status_code} - {response.text}")
            return False
    
    def test_auth_me(self):
        """Test 3: Authentication - GET /api/auth/me"""
        print("\n=== TEST 3: Authentication Test ===")
        
        if not self.session_token:
            print("❌ No session token available for auth test")
            return False
        
        response = self.make_request("GET", "/auth/me", require_auth=True)
        
        if response is None:
            return False
            
        if response.status_code == 200:
            try:
                user_data = response.json()
                print(f"✓ Authentication successful: {user_data.get('name', 'Unknown User')}")
                print(f"  - Email: {user_data.get('email', 'N/A')}")
                print(f"  - Credits: {user_data.get('credits', 0)}")
                return True
            except json.JSONDecodeError:
                print(f"❌ Auth response invalid JSON: {response.text}")
                return False
        else:
            print(f"❌ Authentication failed: {response.status_code} - {response.text}")
            return False
    
    def test_get_credits(self):
        """Test 4: Get User Credits - GET /api/credits"""
        print("\n=== TEST 4: Get User Credits ===")
        
        response = self.make_request("GET", "/credits", require_auth=True)
        
        if response is None:
            return False
            
        if response.status_code == 200:
            try:
                credits_data = response.json()
                print(f"✓ Credits retrieved:")
                print(f"  - Available: {credits_data.get('credits', 0)}")
                print(f"  - Used: {credits_data.get('credits_used', 0)}")
                return True
            except json.JSONDecodeError:
                print(f"❌ Credits response invalid JSON: {response.text}")
                return False
        else:
            print(f"❌ Get credits failed: {response.status_code} - {response.text}")
            return False
    
    def test_create_conversation(self):
        """Test 5: Create New Conversation - POST /api/conversations"""
        print("\n=== TEST 5: Create Conversation ===")
        
        conversation_data = {
            "title": "Test Conversation"
        }
        
        response = self.make_request("POST", "/conversations", data=conversation_data, require_auth=True)
        
        if response is None:
            return False
            
        if response.status_code == 200:
            try:
                conv_data = response.json()
                self.conversation_id = conv_data.get("conversation_id")
                print(f"✓ Conversation created: {conv_data.get('title', 'Unknown')}")
                print(f"  - ID: {self.conversation_id}")
                return True
            except json.JSONDecodeError:
                print(f"❌ Create conversation response invalid JSON: {response.text}")
                return False
        else:
            print(f"❌ Create conversation failed: {response.status_code} - {response.text}")
            return False
    
    def test_get_conversations(self):
        """Test 6: List All Conversations - GET /api/conversations"""
        print("\n=== TEST 6: List Conversations ===")
        
        response = self.make_request("GET", "/conversations", require_auth=True)
        
        if response is None:
            return False
            
        if response.status_code == 200:
            try:
                conversations = response.json()
                print(f"✓ Conversations retrieved: {len(conversations)} conversations")
                for conv in conversations:
                    print(f"  - {conv.get('title', 'Unknown')}: {conv.get('message_count', 0)} messages")
                return True
            except json.JSONDecodeError:
                print(f"❌ List conversations response invalid JSON: {response.text}")
                return False
        else:
            print(f"❌ List conversations failed: {response.status_code} - {response.text}")
            return False
    
    def test_send_message(self):
        """Test 7: Send Message (OpenAI Integration) - POST /api/conversations/{id}/messages"""
        print("\n=== TEST 7: Send Message (OpenAI Integration) ===")
        
        if not self.conversation_id:
            print("❌ No conversation ID available for message test")
            return False
        
        message_data = {
            "content": "Hola, ¿cómo estás? Por favor responde brevemente."
        }
        
        response = self.make_request("POST", f"/conversations/{self.conversation_id}/messages", 
                                   data=message_data, require_auth=True)
        
        if response is None:
            return False
            
        if response.status_code == 200:
            try:
                msg_response = response.json()
                print(f"✓ Message sent and AI response received")
                print(f"  - User message: {msg_response.get('user_message', {}).get('content', 'N/A')[:50]}...")
                print(f"  - AI response: {msg_response.get('assistant_message', {}).get('content', 'N/A')[:100]}...")
                print(f"  - Tokens used: {msg_response.get('tokens_used', 0)}")
                print(f"  - Credits remaining: {msg_response.get('credits_remaining', 0)}")
                return True
            except json.JSONDecodeError:
                print(f"❌ Send message response invalid JSON: {response.text}")
                return False
        else:
            print(f"❌ Send message failed: {response.status_code} - {response.text}")
            return False
    
    def test_get_messages(self):
        """Test 8: Get Messages - GET /api/conversations/{id}/messages"""
        print("\n=== TEST 8: Get Messages ===")
        
        if not self.conversation_id:
            print("❌ No conversation ID available for get messages test")
            return False
        
        response = self.make_request("GET", f"/conversations/{self.conversation_id}/messages", require_auth=True)
        
        if response is None:
            return False
            
        if response.status_code == 200:
            try:
                messages = response.json()
                print(f"✓ Messages retrieved: {len(messages)} messages")
                for msg in messages:
                    role = msg.get('role', 'unknown')
                    content = msg.get('content', 'N/A')[:50]
                    print(f"  - {role}: {content}...")
                return True
            except json.JSONDecodeError:
                print(f"❌ Get messages response invalid JSON: {response.text}")
                return False
        else:
            print(f"❌ Get messages failed: {response.status_code} - {response.text}")
            return False
    
    def test_delete_conversation(self):
        """Test 9: Delete Conversation - DELETE /api/conversations/{id}"""
        print("\n=== TEST 9: Delete Conversation ===")
        
        if not self.conversation_id:
            print("❌ No conversation ID available for delete test")
            return False
        
        response = self.make_request("DELETE", f"/conversations/{self.conversation_id}", require_auth=True)
        
        if response is None:
            return False
            
        if response.status_code == 200:
            try:
                delete_response = response.json()
                print(f"✓ Conversation deleted: {delete_response.get('message', 'Success')}")
                self.conversation_id = None  # Reset for cleanup
                return True
            except json.JSONDecodeError:
                print(f"❌ Delete conversation response invalid JSON: {response.text}")
                return False
        else:
            print(f"❌ Delete conversation failed: {response.status_code} - {response.text}")
            return False
    
    def run_all_tests(self):
        """Run comprehensive backend API tests"""
        print("=" * 60)
        print("ASSISTANT MELUS BACKEND API COMPREHENSIVE TESTS")
        print("=" * 60)
        
        # Setup
        if not self.setup_mongo_connection():
            print("❌ Cannot proceed without MongoDB connection")
            return False
        
        if not self.create_test_user_and_session():
            print("❌ Cannot proceed without test user/session")
            return False
        
        test_results = []
        
        try:
            # Run tests
            test_results.append(("Basic Health Check", self.test_basic_health_check()))
            test_results.append(("Credit Packages", self.test_credit_packages()))
            test_results.append(("Authentication", self.test_auth_me()))
            test_results.append(("Get Credits", self.test_get_credits()))
            test_results.append(("Create Conversation", self.test_create_conversation()))
            test_results.append(("List Conversations", self.test_get_conversations()))
            test_results.append(("Send Message (OpenAI)", self.test_send_message()))
            test_results.append(("Get Messages", self.test_get_messages()))
            test_results.append(("Delete Conversation", self.test_delete_conversation()))
            
        finally:
            # Cleanup
            self.cleanup_test_data()
            if self.mongo_client:
                self.mongo_client.close()
        
        # Results summary
        print("\n" + "=" * 60)
        print("TEST RESULTS SUMMARY")
        print("=" * 60)
        
        passed = 0
        failed = 0
        
        for test_name, result in test_results:
            status = "✓ PASS" if result else "❌ FAIL"
            print(f"{test_name:.<40} {status}")
            if result:
                passed += 1
            else:
                failed += 1
        
        print(f"\nTotal Tests: {len(test_results)}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(f"Success Rate: {(passed/len(test_results)*100):.1f}%")
        
        return failed == 0


def main():
    """Main function to run backend tests"""
    tester = BackendTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 All backend tests PASSED!")
        return 0
    else:
        print("\n💥 Some backend tests FAILED!")
        return 1


if __name__ == "__main__":
    sys.exit(main())