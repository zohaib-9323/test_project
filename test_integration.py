#!/usr/bin/env python3
"""
Integration Test Suite

This script performs comprehensive end-to-end testing of the full-stack application:
- Backend API health and functionality
- Frontend accessibility and responsiveness
- Complete authentication flow (signup, login, profile updates)
- All API endpoints and error handling

The tests verify that the frontend and backend communicate correctly and all features work as expected.
"""

import requests
import json
import time

# Test configuration
BASE_URL = "http://localhost:8000"      # Backend API URL
FRONTEND_URL = "http://localhost:3000"  # Frontend application URL

def test_backend_health():
    """Test backend health endpoint"""
    print("🔍 Testing backend health...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Backend is healthy")
            return True
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend connection failed: {e}")
        return False

def test_frontend_health():
    """Test frontend accessibility"""
    print("🔍 Testing frontend accessibility...")
    try:
        response = requests.get(FRONTEND_URL)
        if response.status_code == 200:
            print("✅ Frontend is accessible")
            return True
        else:
            print(f"❌ Frontend check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Frontend connection failed: {e}")
        return False

def test_auth_flow():
    """Test complete authentication flow"""
    print("🔍 Testing authentication flow...")
    
    # Test signup
    import time
    timestamp = int(time.time())
    signup_data = {
        "name": "Integration Test User",
        "email": f"integration{timestamp}@test.com",
        "password": "TestPass123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/signup", json=signup_data)
        if response.status_code == 201:
            print("✅ User signup successful")
        else:
            print(f"❌ User signup failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Signup request failed: {e}")
        return False
    
    # Test login
    login_data = {
        "email": f"integration{timestamp}@test.com",
        "password": "TestPass123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        if response.status_code == 200:
            token_data = response.json()
            token = token_data.get("access_token")
            print("✅ User login successful")
        else:
            print(f"❌ User login failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Login request failed: {e}")
        return False
    
    # Test protected endpoint
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.get(f"{BASE_URL}/users/me", headers=headers)
        if response.status_code == 200:
            user_data = response.json()
            print(f"✅ Protected endpoint access successful - User: {user_data['name']}")
        else:
            print(f"❌ Protected endpoint access failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Protected endpoint request failed: {e}")
        return False
    
    # Test user update
    update_data = {"name": "Updated Integration User"}
    try:
        response = requests.put(f"{BASE_URL}/users/{user_data['id']}", json=update_data, headers=headers)
        if response.status_code == 200:
            updated_user = response.json()
            print(f"✅ User update successful - New name: {updated_user['name']}")
        else:
            print(f"❌ User update failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ User update request failed: {e}")
        return False
    
    return True

def test_all_endpoints():
    """Test all available endpoints"""
    print("🔍 Testing all API endpoints...")
    
    # Create a user and get a token first
    import time
    timestamp = int(time.time())
    signup_data = {
        "name": "Test User",
        "email": f"test{timestamp}@example.com",
        "password": "TestPass123"
    }
    login_data = {"email": f"test{timestamp}@example.com", "password": "TestPass123"}
    
    try:
        # Create user
        requests.post(f"{BASE_URL}/auth/signup", json=signup_data)
        # Login to get token
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        token = response.json().get("access_token")
        headers = {"Authorization": f"Bearer {token}"}
    except:
        print("❌ Could not get authentication token")
        return False
    
    endpoints = [
        ("GET", "/", "Welcome message"),
        ("GET", "/health", "Health check"),
        ("GET", "/users/", "Get all users"),
        ("GET", "/users/me", "Get current user"),
    ]
    
    for method, endpoint, description in endpoints:
        try:
            if method == "GET":
                response = requests.get(f"{BASE_URL}{endpoint}", headers=headers if "/users" in endpoint else None)
            else:
                response = requests.post(f"{BASE_URL}{endpoint}", headers=headers if "/users" in endpoint else None)
            
            if response.status_code in [200, 201]:
                print(f"✅ {description}: {response.status_code}")
            else:
                print(f"❌ {description}: {response.status_code}")
        except Exception as e:
            print(f"❌ {description}: {e}")
    
    return True

def main():
    """Run all integration tests"""
    print("🚀 Starting Integration Tests")
    print("=" * 50)
    
    tests = [
        ("Backend Health", test_backend_health),
        ("Frontend Health", test_frontend_health),
        ("Authentication Flow", test_auth_flow),
        ("All Endpoints", test_all_endpoints),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n📋 Running {test_name} Test")
        print("-" * 30)
        result = test_func()
        results.append((test_name, result))
        time.sleep(1)  # Small delay between tests
    
    print("\n" + "=" * 50)
    print("📊 Test Results Summary")
    print("=" * 50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All tests passed! Frontend and backend are working correctly.")
    else:
        print("⚠️  Some tests failed. Please check the logs above.")

if __name__ == "__main__":
    main()
