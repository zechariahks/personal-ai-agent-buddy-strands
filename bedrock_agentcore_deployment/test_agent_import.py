#!/usr/bin/env python3
"""
Test script to verify that all agent imports work correctly
for Bedrock AgentCore deployment
"""

import sys
import os

def check_dependencies():
    """Check if required dependencies are installed"""
    print("📦 Checking Dependencies...")
    
    missing_deps = []
    
    # Check core dependencies
    deps_to_check = [
        ('fastapi', 'FastAPI'),
        ('uvicorn', 'Uvicorn'),
        ('pydantic', 'Pydantic'),
        ('strands', 'Strands-Agents SDK'),
        ('strands_tools', 'Strands Tools'),
        ('requests', 'Requests'),
        ('boto3', 'AWS SDK')
    ]
    
    for module, name in deps_to_check:
        try:
            __import__(module)
            print(f"✅ {name}: Available")
        except ImportError:
            print(f"❌ {name}: Missing")
            missing_deps.append(module)
    
    if missing_deps:
        print(f"\n⚠️ Missing dependencies: {', '.join(missing_deps)}")
        print("💡 Run this command to install dependencies:")
        print("python setup_local_env.py")
        print("# OR manually:")
        print("pip install -r requirements.txt")
        return False
    
    return True

def test_agent_imports():
    """Test importing all the agent components"""
    print("🧪 Testing Agent Imports for Bedrock AgentCore Deployment")
    print("=" * 60)
    
    try:
        # Test basic imports
        print("📦 Testing basic imports...")
        from enhanced_context_aware_agent_strands import StrandsEnhancedContextAwareAgent
        print("✅ StrandsEnhancedContextAwareAgent imported successfully")
        
        from basic_agent_strands import StrandsBasicAgent
        print("✅ StrandsBasicAgent imported successfully")
        
        # Test tool imports
        print("\n🔧 Testing tool imports...")
        from weather_tool import get_weather
        print("✅ Weather tool imported successfully")
        
        from bible_verse_tool import get_daily_bible_verse, get_bible_verse_for_posting
        print("✅ Bible verse tool imported successfully")
        
        from x_posting_tool import post_to_x, get_x_account_info
        print("✅ X posting tool imported successfully")
        
        from google_calendar_tool import create_calendar_event, get_calendar_events
        print("✅ Google Calendar tool imported successfully")
        
        # Test agent initialization
        print("\n🤖 Testing agent initialization...")
        agent = StrandsEnhancedContextAwareAgent("TestAgent")
        print("✅ Enhanced agent initialized successfully")
        
        # Test agent capabilities
        print("\n⚡ Testing agent capabilities...")
        capabilities = len(agent.specialist_agents)
        print(f"✅ Agent has {capabilities} specialist agents")
        
        # Test service status
        status = agent.get_service_status()
        print("✅ Service status retrieved successfully")
        
        print("\n🎉 All imports and initialization tests passed!")
        print("✅ Ready for Bedrock AgentCore deployment")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ Initialization error: {str(e)}")
        return False

def test_fastapi_app():

    """Test FastAPI app initialization"""
    print("\n🌐 Testing FastAPI App...")
    try:
        # Add current directory to path for imports
        sys.path.insert(0, '.')
        
        from app import app, strands_agent
        print("✅ FastAPI app imported successfully")
        
        # Test app configuration
        print(f"✅ App title: {app.title}")
        print(f"✅ App version: {app.version}")
        
        return True
        
    except Exception as e:
        print(f"❌ FastAPI app error: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Strands Personal AI Agent - Deployment Test Suite")
    print("=" * 60)
    
    # Check dependencies first
    if not check_dependencies():
        print("\n❌ DEPENDENCY CHECK FAILED!")
        print("💡 Install dependencies first:")
        print("python setup_local_env.py")
        sys.exit(1)
    
    # Copy agent files to current directory (simulate deployment)
    import shutil
    agent_files = [
        '../enhanced_context_aware_agent_strands.py',
        '../basic_agent_strands.py',
        '../weather_tool.py',
        '../bible_verse_tool.py',
        '../x_posting_tool.py',
        '../google_calendar_tool.py'
    ]
    
    print("\n📁 Copying agent files for testing...")
    for file in agent_files:
        if os.path.exists(file):
            shutil.copy2(file, '.')
            print(f"✅ Copied {os.path.basename(file)}")
    
    # Run tests
    import_success = test_agent_imports()
    app_success = test_fastapi_app()
    
    if import_success and app_success:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ Bedrock AgentCore deployment is ready")
        sys.exit(0)
    else:
        print("\n❌ SOME TESTS FAILED!")
        print("💡 Try running: python setup_local_env.py")
        sys.exit(1)