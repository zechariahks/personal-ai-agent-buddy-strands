#!/usr/bin/env python3
"""
Test script for enhanced features in Strands-Agents implementation
Tests Bible verse posting, X integration, and Google Calendar functionality
"""

import os
import sys
from datetime import datetime, timedelta

# Add the current directory to Python path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from enhanced_context_aware_agent_strands import StrandsEnhancedContextAwareAgent
from bible_verse_tool import get_daily_bible_verse, test_bible_verse_tool
from x_posting_tool import post_to_x, get_x_account_info, test_x_posting_tool
from google_calendar_tool import create_calendar_event, get_calendar_events, test_google_calendar_tool


def test_bible_verse_functionality():
    """Test Bible verse API functionality"""
    print("🔍 Testing Bible Verse Functionality")
    print("=" * 50)
    
    try:
        # Test getting a Bible verse
        print("1. Testing get_daily_bible_verse():")
        verse_result = get_daily_bible_verse()
        print(verse_result)
        print("\n" + "-" * 30 + "\n")
        
        # Test the tool's test function
        print("2. Running bible_verse_tool test:")
        test_bible_verse_tool()
        
        return True
        
    except Exception as e:
        print(f"❌ Bible verse test failed: {str(e)}")
        return False


def test_x_posting_functionality():
    """Test X (Twitter) posting functionality"""
    print("🔍 Testing X (Twitter) Posting Functionality")
    print("=" * 50)
    
    try:
        # Test X account info
        print("1. Testing get_x_account_info():")
        account_info = get_x_account_info()
        print(account_info)
        print("\n" + "-" * 30 + "\n")
        
        # Test posting (will show credentials needed if not configured)
        print("2. Testing post_to_x():")
        test_content = "Testing X integration from Strands-Agents SDK! 🤖 #AI #Testing"
        post_result = post_to_x(test_content)
        print(post_result)
        print("\n" + "-" * 30 + "\n")
        
        # Test the tool's test function
        print("3. Running x_posting_tool test:")
        test_x_posting_tool()
        
        return True
        
    except Exception as e:
        print(f"❌ X posting test failed: {str(e)}")
        return False


def test_google_calendar_functionality():
    """Test Google Calendar functionality"""
    print("🔍 Testing Google Calendar Functionality")
    print("=" * 50)
    
    try:
        # Test getting calendar events
        print("1. Testing get_calendar_events():")
        events_result = get_calendar_events(7)
        print(events_result)
        print("\n" + "-" * 30 + "\n")
        
        # Test creating a calendar event (will show setup needed if not configured)
        print("2. Testing create_calendar_event():")
        start_time = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%dT10:00:00')
        end_time = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%dT11:00:00')
        
        event_result = create_calendar_event(
            title="Test Event from Strands-Agents",
            start_time=start_time,
            end_time=end_time,
            description="This is a test event created by the enhanced AI agent",
            location="Virtual Meeting"
        )
        print(event_result)
        print("\n" + "-" * 30 + "\n")
        
        # Test the tool's test function
        print("3. Running google_calendar_tool test:")
        test_google_calendar_tool()
        
        return True
        
    except Exception as e:
        print(f"❌ Google Calendar test failed: {str(e)}")
        return False


def test_enhanced_agent_integration():
    """Test the enhanced agent with new features"""
    print("🔍 Testing Enhanced Agent Integration")
    print("=" * 50)
    
    try:
        # Initialize the enhanced agent
        print("1. Initializing Enhanced Agent:")
        agent = StrandsEnhancedContextAwareAgent("TestBuddy")
        print("✅ Enhanced agent initialized successfully")
        print("\n" + "-" * 30 + "\n")
        
        # Test Bible verse posting request
        print("2. Testing Bible verse posting request:")
        bible_response = agent.process_request("Post a Bible verse")
        print(bible_response)
        print("\n" + "-" * 30 + "\n")
        
        # Test X status check
        print("3. Testing X status check:")
        x_status_response = agent.process_request("Check X status")
        print(x_status_response)
        print("\n" + "-" * 30 + "\n")
        
        # Test Google Calendar events
        print("4. Testing Google Calendar events:")
        calendar_response = agent.process_request("Show my events")
        print(calendar_response)
        print("\n" + "-" * 30 + "\n")
        
        # Test service status
        print("5. Testing enhanced service status:")
        status_response = agent.get_service_status()
        print(status_response)
        print("\n" + "-" * 30 + "\n")
        
        # Test help message
        print("6. Testing enhanced help message:")
        help_response = agent.show_help()
        print(help_response[:500] + "..." if len(help_response) > 500 else help_response)
        
        return True
        
    except Exception as e:
        print(f"❌ Enhanced agent integration test failed: {str(e)}")
        return False


def run_all_tests():
    """Run all enhanced feature tests"""
    print("🚀 Enhanced Features Test Suite")
    print("=" * 60)
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    test_results = []
    
    # Run individual component tests
    test_results.append(("Bible Verse Functionality", test_bible_verse_functionality()))
    print("\n" + "=" * 60 + "\n")
    
    test_results.append(("X Posting Functionality", test_x_posting_functionality()))
    print("\n" + "=" * 60 + "\n")
    
    test_results.append(("Google Calendar Functionality", test_google_calendar_functionality()))
    print("\n" + "=" * 60 + "\n")
    
    test_results.append(("Enhanced Agent Integration", test_enhanced_agent_integration()))
    print("\n" + "=" * 60 + "\n")
    
    # Print test summary
    print("📊 Test Results Summary")
    print("=" * 60)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print("=" * 60)
    print(f"Tests Passed: {passed}/{total}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("🎉 All tests passed! Enhanced features are working correctly.")
    else:
        print("⚠️ Some tests failed. Check the output above for details.")
    
    print("=" * 60)
    print("💡 Setup Notes:")
    print("• For X posting: Set X_BEARER_TOKEN, X_API_KEY, X_API_SECRET, X_ACCESS_TOKEN, X_ACCESS_TOKEN_SECRET")
    print("• For Google Calendar: Set up ~/.google_calendar_credentials.json")
    print("• For Weather: Set OPENWEATHER_API_KEY")
    print("• Bible verses work without additional setup")
    print("=" * 60)
    
    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)