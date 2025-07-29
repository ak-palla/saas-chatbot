#!/usr/bin/env python3
"""
Comprehensive test suite for Phase 1 implementation
Tests all endpoints, authentication, database operations, and core functionality
"""

import requests
import json
import sys
import time
from typing import Dict, Any

# Configuration
BASE_URL = "http://localhost:8000"
API_V1 = f"{BASE_URL}/api/v1"

class Phase1Tester:
    def __init__(self):
        self.access_token = None
        self.test_user_email = f"test_{int(time.time())}@example.com"
        self.test_user_password = "testpassword123"
        self.created_chatbot_id = None
        self.created_conversation_id = None
        
    def log(self, message: str, status: str = "INFO"):
        """Log test messages with status"""
        status_icons = {
            "INFO": "ℹ️",
            "SUCCESS": "✅",
            "ERROR": "❌",
            "WARNING": "⚠️"
        }
        print(f"{status_icons.get(status, 'ℹ️')} {message}")
    
    def make_request(self, method: str, endpoint: str, data: Dict = None, auth: bool = False) -> Dict[str, Any]:
        """Make HTTP request with optional authentication"""
        url = f"{API_V1}{endpoint}"
        headers = {"Content-Type": "application/json"}
        
        if auth and self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=headers)
            elif method.upper() == "POST":
                response = requests.post(url, json=data, headers=headers)
            elif method.upper() == "PUT":
                response = requests.put(url, json=data, headers=headers)
            elif method.upper() == "DELETE":
                response = requests.delete(url, headers=headers)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            return {
                "status_code": response.status_code,
                "data": response.json() if response.content else {},
                "success": response.status_code < 400
            }
        except requests.exceptions.ConnectionError:
            return {
                "status_code": 0,
                "data": {"error": "Connection refused - Is the server running?"},
                "success": False
            }
        except Exception as e:
            return {
                "status_code": 0,
                "data": {"error": str(e)},
                "success": False
            }
    
    def test_server_connection(self) -> bool:
        """Test if server is running and accessible"""
        self.log("Testing server connection...")
        
        response = self.make_request("GET", "/health/")
        if not response["success"]:
            self.log(f"Server connection failed: {response['data']}", "ERROR")
            return False
        
        self.log("Server is running and accessible", "SUCCESS")
        return True
    
    def test_health_endpoints(self) -> bool:
        """Test health check endpoints"""
        self.log("Testing health endpoints...")
        
        # Test basic health
        response = self.make_request("GET", "/health/")
        if not response["success"]:
            self.log(f"Basic health check failed: {response['data']}", "ERROR")
            return False
        
        self.log(f"Basic health: {response['data']['message']}", "SUCCESS")
        
        # Test database health
        response = self.make_request("GET", "/health/db")
        if response["success"]:
            self.log("Database health check passed", "SUCCESS")
        else:
            self.log(f"Database health check failed: {response['data']}", "WARNING")
        
        return True
    
    def test_user_registration(self) -> bool:
        """Test user registration"""
        self.log("Testing user registration...")
        
        user_data = {
            "email": self.test_user_email,
            "password": self.test_user_password,
            "full_name": "Test User"
        }
        
        response = self.make_request("POST", "/auth/register", user_data)
        if not response["success"]:
            self.log(f"User registration failed: {response['data']}", "ERROR")
            return False
        
        # Store access token
        self.access_token = response["data"]["access_token"]
        self.log(f"User registered successfully: {response['data']['user']['email']}", "SUCCESS")
        return True
    
    def test_user_login(self) -> bool:
        """Test user login"""
        self.log("Testing user login...")
        
        # Prepare form data for OAuth2PasswordRequestForm
        login_data = {
            "username": self.test_user_email,  # OAuth2 uses 'username' field
            "password": self.test_user_password
        }
        
        # Use form data instead of JSON for OAuth2
        url = f"{API_V1}/auth/login"
        response = requests.post(url, data=login_data)
        
        if response.status_code >= 400:
            self.log(f"User login failed: {response.json() if response.content else 'No response'}", "ERROR")
            return False
        
        data = response.json()
        self.access_token = data["access_token"]
        self.log(f"User logged in successfully: {data['user']['email']}", "SUCCESS")
        return True
    
    def test_get_current_user(self) -> bool:
        """Test getting current user info"""
        self.log("Testing get current user...")
        
        response = self.make_request("GET", "/auth/me", auth=True)
        if not response["success"]:
            self.log(f"Get current user failed: {response['data']}", "ERROR")
            return False
        
        self.log(f"Current user: {response['data']['email']}", "SUCCESS")
        return True
    
    def test_create_chatbot(self) -> bool:
        """Test creating a chatbot"""
        self.log("Testing chatbot creation...")
        
        chatbot_data = {
            "name": "Test Chatbot",
            "description": "A test chatbot for Phase 1 testing",
            "system_prompt": "You are a helpful assistant.",
            "appearance_config": {
                "color": "#007bff",
                "position": "bottom-right"
            }
        }
        
        response = self.make_request("POST", "/chatbots/", chatbot_data, auth=True)
        if not response["success"]:
            self.log(f"Chatbot creation failed: {response['data']}", "ERROR")
            return False
        
        self.created_chatbot_id = response["data"]["id"]
        self.log(f"Chatbot created: {response['data']['name']} (ID: {self.created_chatbot_id})", "SUCCESS")
        return True
    
    def test_get_chatbots(self) -> bool:
        """Test getting user's chatbots"""
        self.log("Testing get user chatbots...")
        
        response = self.make_request("GET", "/chatbots/", auth=True)
        if not response["success"]:
            self.log(f"Get chatbots failed: {response['data']}", "ERROR")
            return False
        
        chatbots = response["data"]
        self.log(f"Retrieved {len(chatbots)} chatbots", "SUCCESS")
        return True
    
    def test_get_specific_chatbot(self) -> bool:
        """Test getting a specific chatbot"""
        if not self.created_chatbot_id:
            self.log("No chatbot ID available for testing", "WARNING")
            return True
        
        self.log("Testing get specific chatbot...")
        
        response = self.make_request("GET", f"/chatbots/{self.created_chatbot_id}", auth=True)
        if not response["success"]:
            self.log(f"Get specific chatbot failed: {response['data']}", "ERROR")
            return False
        
        self.log(f"Retrieved chatbot: {response['data']['name']}", "SUCCESS")
        return True
    
    def test_update_chatbot(self) -> bool:
        """Test updating a chatbot"""
        if not self.created_chatbot_id:
            self.log("No chatbot ID available for testing", "WARNING")
            return True
        
        self.log("Testing chatbot update...")
        
        update_data = {
            "description": "Updated test chatbot description",
            "appearance_config": {
                "color": "#28a745",
                "position": "bottom-left"
            }
        }
        
        response = self.make_request("PUT", f"/chatbots/{self.created_chatbot_id}", update_data, auth=True)
        if not response["success"]:
            self.log(f"Chatbot update failed: {response['data']}", "ERROR")
            return False
        
        self.log("Chatbot updated successfully", "SUCCESS")
        return True
    
    def test_create_conversation(self) -> bool:
        """Test creating a conversation"""
        if not self.created_chatbot_id:
            self.log("No chatbot ID available for testing", "WARNING")
            return True
        
        self.log("Testing conversation creation...")
        
        conversation_data = {
            "chatbot_id": self.created_chatbot_id,
            "title": "Test Conversation",
            "session_id": f"session_{int(time.time())}"
        }
        
        response = self.make_request("POST", "/conversations/", conversation_data, auth=True)
        if not response["success"]:
            self.log(f"Conversation creation failed: {response['data']}", "ERROR")
            return False
        
        self.created_conversation_id = response["data"]["id"]
        self.log(f"Conversation created (ID: {self.created_conversation_id})", "SUCCESS")
        return True
    
    def test_get_conversations(self) -> bool:
        """Test getting conversations for a chatbot"""
        if not self.created_chatbot_id:
            self.log("No chatbot ID available for testing", "WARNING")
            return True
        
        self.log("Testing get chatbot conversations...")
        
        response = self.make_request("GET", f"/conversations/chatbot/{self.created_chatbot_id}", auth=True)
        if not response["success"]:
            self.log(f"Get conversations failed: {response['data']}", "ERROR")
            return False
        
        conversations = response["data"]
        self.log(f"Retrieved {len(conversations)} conversations", "SUCCESS")
        return True
    
    def test_authentication_protection(self) -> bool:
        """Test that protected endpoints require authentication"""
        self.log("Testing authentication protection...")
        
        # Temporarily remove token
        original_token = self.access_token
        self.access_token = None
        
        # Try to access protected endpoint without auth
        response = self.make_request("GET", "/chatbots/")
        if response["status_code"] in [401, 403]:  # Both 401 and 403 are acceptable for auth failure
            self.log(f"Protected endpoint correctly requires authentication (HTTP {response['status_code']})", "SUCCESS")
            self.access_token = original_token
            return True
        else:
            self.log(f"Protected endpoint should require authentication, got: {response['status_code']}", "ERROR")
            self.access_token = original_token
            return False
    
    def test_cleanup(self) -> bool:
        """Clean up test data"""
        self.log("Cleaning up test data...")
        
        # Delete conversation
        if self.created_conversation_id:
            response = self.make_request("DELETE", f"/conversations/{self.created_conversation_id}", auth=True)
            if response["success"]:
                self.log("Test conversation deleted", "SUCCESS")
            else:
                self.log("Failed to delete test conversation", "WARNING")
        
        # Delete chatbot
        if self.created_chatbot_id:
            response = self.make_request("DELETE", f"/chatbots/{self.created_chatbot_id}", auth=True)
            if response["success"]:
                self.log("Test chatbot deleted", "SUCCESS")
            else:
                self.log("Failed to delete test chatbot", "WARNING")
        
        return True
    
    def run_all_tests(self) -> bool:
        """Run all Phase 1 tests"""
        self.log("🧪 Starting Phase 1 Comprehensive Tests", "INFO")
        self.log("=" * 50)
        
        tests = [
            ("Server Connection", self.test_server_connection),
            ("Health Endpoints", self.test_health_endpoints),
            ("User Registration", self.test_user_registration),
            ("User Login", self.test_user_login),
            ("Get Current User", self.test_get_current_user),
            ("Create Chatbot", self.test_create_chatbot),
            ("Get Chatbots", self.test_get_chatbots),
            ("Get Specific Chatbot", self.test_get_specific_chatbot),
            ("Update Chatbot", self.test_update_chatbot),
            ("Create Conversation", self.test_create_conversation),
            ("Get Conversations", self.test_get_conversations),
            ("Authentication Protection", self.test_authentication_protection),
            ("Cleanup", self.test_cleanup),
        ]
        
        passed = 0
        failed = 0
        
        for test_name, test_func in tests:
            try:
                self.log(f"\n--- {test_name} ---")
                if test_func():
                    passed += 1
                else:
                    failed += 1
            except Exception as e:
                self.log(f"Test {test_name} crashed: {str(e)}", "ERROR")
                failed += 1
        
        # Results
        self.log("\n" + "=" * 50)
        self.log("🏁 Phase 1 Test Results:", "INFO")
        self.log(f"✅ Passed: {passed}")
        self.log(f"❌ Failed: {failed}")
        self.log(f"📊 Total: {passed + failed}")
        
        if failed == 0:
            self.log("🎉 All tests passed! Phase 1 implementation is working correctly.", "SUCCESS")
            return True
        else:
            self.log(f"⚠️ {failed} tests failed. Please check the implementation.", "ERROR")
            return False

def main():
    """Main function to run tests"""
    print("Phase 1 Implementation Tester")
    print("Make sure the FastAPI server is running on http://localhost:8000")
    print("Starting tests in 3 seconds...")
    time.sleep(3)
    
    tester = Phase1Tester()
    success = tester.run_all_tests()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()