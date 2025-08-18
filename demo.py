#!/usr/bin/env python3
"""
Demo script for Strands-Agents Personal AI Agent
Shows the capabilities of both basic and enhanced agents
"""

import os
import sys
from basic_agent_strands import StrandsBasicAgent
from enhanced_context_aware_agent_strands import StrandsEnhancedContextAwareAgent


def demo_basic_agent():
    """Demonstrate basic Strands agent capabilities"""
    print("🤖 Basic Strands Agent Demo")
    print("=" * 50)
    
    agent = StrandsBasicAgent("Demo-Basic")
    
    # Test calculations
    print("\n📊 Testing Calculator Tool:")
    response = agent.ask_agent("What is 15 * 23 + 100?")
    print(f"Response: {response}")
    
    # Test weather (if configured)
    print("\n🌤️ Testing Weather Analysis:")
    response = agent.ask_agent("What's the weather like in San Francisco?")
    print(f"Response: {response}")
    
    # Test general AI
    print("\n💬 Testing General AI Capabilities:")
    response = agent.ask_agent("Explain what AI agents are in simple terms")
    print(f"Response: {response}")
    
    print("\n✅ Basic agent demo completed!")


def demo_enhanced_agent():
    """Demonstrate enhanced multi-agent system capabilities"""
    print("\n🚀 Enhanced Multi-Agent System Demo")
    print("=" * 60)
    
    agent = StrandsEnhancedContextAwareAgent("Demo-Enhanced")
    
    # Test multi-agent weather analysis
    print("\n🌤️ Testing Multi-Agent Weather Analysis:")
    response = agent.process_request("What's the weather in London and should I plan outdoor activities?")
    print(f"Response: {response}")
    
    # Test social media content creation
    print("\n📱 Testing Social Media Agent:")
    response = agent.process_request("Create content about artificial intelligence")
    print(f"Response: {response}")
    
    # Test decision making
    print("\n🧠 Testing Decision Agent:")
    response = agent.process_request("Should I invest in learning AI development?")
    print(f"Response: {response}")
    
    # Test service status
    print("\n🔧 Testing Service Status:")
    response = agent.get_service_status()
    print(f"Response: {response}")
    
    print("\n✅ Enhanced multi-agent demo completed!")


def interactive_demo():
    """Interactive demo allowing user to choose agent type"""
    print("🎯 Interactive Strands-Agents Demo")
    print("=" * 50)
    
    while True:
        print("\nChoose demo type:")
        print("1. Basic Strands Agent")
        print("2. Enhanced Multi-Agent System")
        print("3. Interactive Chat (Basic)")
        print("4. Interactive Chat (Enhanced)")
        print("5. Exit")
        
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == "1":
            demo_basic_agent()
        elif choice == "2":
            demo_enhanced_agent()
        elif choice == "3":
            print("\n🎮 Starting Interactive Basic Agent...")
            agent = StrandsBasicAgent("Interactive-Basic")
            agent.chat()
        elif choice == "4":
            print("\n🎮 Starting Interactive Enhanced Agent...")
            agent = StrandsEnhancedContextAwareAgent("Interactive-Enhanced")
            agent.chat()
        elif choice == "5":
            print("👋 Thanks for trying Strands-Agents! Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please try again.")


def check_prerequisites():
    """Check if required environment variables are set"""
    print("🔍 Checking Prerequisites...")
    
    # Check for AI model provider
    has_openai = bool(os.getenv("OPENAI_API_KEY"))
    has_anthropic = bool(os.getenv("ANTHROPIC_API_KEY"))
    has_aws = bool(os.getenv("AWS_ACCESS_KEY_ID") or os.getenv("AWS_PROFILE"))
    
    if not (has_openai or has_anthropic or has_aws):
        print("⚠️ Warning: No AI model provider configured!")
        print("   Please set one of:")
        print("   - OPENAI_API_KEY for OpenAI")
        print("   - ANTHROPIC_API_KEY for Anthropic")
        print("   - AWS credentials for Amazon Bedrock")
        print()
    else:
        providers = []
        if has_openai:
            providers.append("OpenAI")
        if has_anthropic:
            providers.append("Anthropic")
        if has_aws:
            providers.append("AWS Bedrock")
        print(f"✅ AI Providers available: {', '.join(providers)}")
    
    # Check optional services
    has_weather = bool(os.getenv("WEATHER_API_KEY"))
    has_email = bool(os.getenv("GMAIL_EMAIL") and os.getenv("GMAIL_APP_PASSWORD"))
    
    print(f"🌤️ Weather API: {'✅ Configured' if has_weather else '❌ Not configured'}")
    print(f"📧 Email Service: {'✅ Configured' if has_email else '❌ Not configured'}")
    
    print("\n💡 Tip: Even without optional services, you can still use:")
    print("   - Calculator tools")
    print("   - General AI assistance")
    print("   - Multi-agent coordination")
    print("   - Context-aware responses")
    print()


def main():
    """Main demo function"""
    print("🚀 Welcome to Strands-Agents Personal AI Agent Demo!")
    print("=" * 60)
    print("This demo showcases the power of the Strands-Agents SDK")
    print("for building intelligent, multi-agent AI systems.")
    print("=" * 60)
    
    # Check prerequisites
    check_prerequisites()
    
    # Show available demo options
    print("Demo Options:")
    print("1. Quick Demo - Run automated demonstrations")
    print("2. Interactive Demo - Choose your own adventure")
    print("3. Basic Agent Only - Test basic functionality")
    print("4. Enhanced Agent Only - Test multi-agent system")
    
    choice = input("\nWhat would you like to do? (1-4): ").strip()
    
    try:
        if choice == "1":
            demo_basic_agent()
            demo_enhanced_agent()
        elif choice == "2":
            interactive_demo()
        elif choice == "3":
            demo_basic_agent()
        elif choice == "4":
            demo_enhanced_agent()
        else:
            print("❌ Invalid choice. Running interactive demo...")
            interactive_demo()
            
    except KeyboardInterrupt:
        print("\n\n👋 Demo interrupted. Goodbye!")
    except Exception as e:
        print(f"\n❌ Demo error: {str(e)}")
        print("Please check your configuration and try again.")


if __name__ == "__main__":
    main()