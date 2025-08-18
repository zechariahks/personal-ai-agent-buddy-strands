#!/usr/bin/env python3
"""
Quick test script to verify FastAPI app functionality
"""

import requests
import json
import time
import sys
from typing import Dict, Any

def test_endpoint(url: str, method: str = "GET", data: Dict[str, Any] = None) -> bool:
    """Test a single endpoint"""
    try:
        print(f"🧪 Testing {method} {url}")
        
        if method == "GET":
            response = requests.get(url, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=10)
        else:
            print(f"❌ Unsupported method: {method}")
            return False
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Success: {json.dumps(result, indent=2)[:200]}...")
            return True
        else:
            print(f"   ❌ Error: {response.text[:200]}...")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"   ❌ Connection failed - is the server running on {url}?")
        return False
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return False

def main():
    """Run FastAPI app tests"""
    base_url = "http://localhost:8000"
    
    print("🚀 Testing Strands Personal AI Agent FastAPI App")
    print("=" * 60)
    
    # Test basic endpoints
    tests = [
        ("GET", "/", None),
        ("GET", "/health", None),
        ("GET", "/capabilities", None),
        ("GET", "/status", None),
        ("POST", "/invoke", {
            "message": "Hello, what can you do?",
            "session_id": "test-session"
        }),
        ("POST", "/weather", {
            "city": "New York"
        }),
        ("POST", "/calendar", {
            "action": "show events"
        }),
        ("POST", "/social", {
            "action": "post bible verse"
        }),
        # Test 404 error handling
        ("GET", "/nonexistent", None)
    ]
    
    passed = 0
    total = len(tests)
    
    for method, endpoint, data in tests:
        url = f"{base_url}{endpoint}"
        if test_endpoint(url, method, data):
            passed += 1
        print()
        time.sleep(0.5)  # Small delay between tests
    
    print("=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! FastAPI app is working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Check the server logs for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main())