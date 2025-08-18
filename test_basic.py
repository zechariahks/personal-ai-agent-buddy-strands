#!/usr/bin/env python3
"""
Quick test script to verify the Strands-Agents implementation works
"""

import os
from basic_agent_strands import StrandsBasicAgent

def test_basic_functionality():
    """Test basic agent functionality"""
    print("🧪 Testing Basic Strands Agent...")
    
    # Create agent
    agent = StrandsBasicAgent("TestBot")
    
    # Test calculator functionality
    print("\n📊 Testing Calculator:")
    try:
        response = agent.ask_agent("What is 15 * 23?")
        print(f"Calculator test: {response}")
    except Exception as e:
        print(f"Calculator test failed: {e}")
    
    # Test general AI
    print("\n🤖 Testing General AI:")
    try:
        response = agent.ask_agent("What are AI agents?")
        print(f"AI test: {response[:100]}...")
    except Exception as e:
        print(f"AI test failed: {e}")
    
    # Test weather (AI-powered)
    print("\n🌤️ Testing Weather Analysis:")
    try:
        response = agent.ask_agent("What's the weather like in San Francisco?")
        print(f"Weather test: {response[:100]}...")
    except Exception as e:
        print(f"Weather test failed: {e}")
    
    # Test service status
    print("\n🔧 Testing Service Status:")
    try:
        status = agent.get_service_status()
        print(f"Service status: {status[:200]}...")
    except Exception as e:
        print(f"Service status test failed: {e}")
    
    print("\n✅ Basic functionality test completed!")

if __name__ == "__main__":
    # Check if we have any AI provider configured
    has_openai = bool(os.getenv("OPENAI_API_KEY"))
    has_anthropic = bool(os.getenv("ANTHROPIC_API_KEY"))
    has_aws = bool(os.getenv("AWS_ACCESS_KEY_ID") or os.getenv("AWS_PROFILE"))
    
    if not (has_openai or has_anthropic or has_aws):
        print("⚠️ No AI model provider configured!")
        print("Please set one of: OPENAI_API_KEY, ANTHROPIC_API_KEY, or AWS credentials")
        print("For testing, you can set: export OPENAI_API_KEY='your-key-here'")
    else:
        test_basic_functionality()