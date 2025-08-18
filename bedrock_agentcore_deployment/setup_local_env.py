#!/usr/bin/env python3
"""
Setup script for local development environment
Installs all required dependencies for testing the Strands Personal AI Agent locally
"""

import subprocess
import sys
import os

def install_requirements():
    """Install requirements from requirements.txt"""
    print("📦 Installing Python dependencies...")
    
    try:
        # Check if requirements.txt exists
        if not os.path.exists('requirements.txt'):
            print("❌ requirements.txt not found!")
            return False
        
        # Install requirements
        subprocess.run([
            sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'
        ], check=True)
        
        print("✅ All dependencies installed successfully!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        print("\n💡 Try installing manually:")
        print("pip install -r requirements.txt")
        return False

def check_python_version():
    """Check Python version compatibility"""
    print("🐍 Checking Python version...")
    
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - Compatible")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} - Requires Python 3.8+")
        return False

def test_core_imports():
    """Test if core dependencies can be imported"""
    print("\n🧪 Testing core imports...")
    
    imports_to_test = [
        ('fastapi', 'FastAPI'),
        ('uvicorn', 'Uvicorn'),
        ('pydantic', 'Pydantic'),
        ('requests', 'Requests'),
        ('boto3', 'AWS SDK'),
    ]
    
    all_passed = True
    
    for module, name in imports_to_test:
        try:
            __import__(module)
            print(f"✅ {name}: Available")
        except ImportError:
            print(f"❌ {name}: Missing")
            all_passed = False
    
    return all_passed

def test_strands_sdk():
    """Test Strands-Agents SDK availability"""
    print("\n🤖 Testing Strands-Agents SDK...")
    
    try:
        from strands import Agent
        from strands_tools import calculator
        print("✅ Strands-Agents SDK: Available")
        return True
    except ImportError as e:
        print(f"❌ Strands-Agents SDK: Missing ({e})")
        print("\n💡 Install Strands-Agents SDK:")
        print("pip install strands-agents strands-agents-tools")
        return False

def create_test_environment():
    """Create a simple test environment file"""
    print("\n📝 Creating test environment file...")
    
    env_content = """# Test Environment Variables for Strands Personal AI Agent
# Copy this to .env and fill in your actual API keys

# AI Model Provider (choose one)
OPENAI_API_KEY=your-openai-api-key-here
# ANTHROPIC_API_KEY=your-anthropic-api-key-here
# BEDROCK_MODEL=anthropic.claude-3-sonnet-20240229-v1:0

# Weather API
WEATHER_API_KEY=your-openweathermap-api-key-here

# X (Twitter) API
X_API_KEY=your-x-api-key-here
X_API_SECRET=your-x-api-secret-here
X_ACCESS_TOKEN=your-x-access-token-here
X_ACCESS_TOKEN_SECRET=your-x-access-token-secret-here

# Optional: Gmail for email functionality
GMAIL_EMAIL=your-gmail-address@gmail.com
GMAIL_APP_PASSWORD=your-gmail-app-password-here

# Optional: Default settings
DEFAULT_CITY=New York
STRANDS_DEBUG=true
"""
    
    try:
        with open('.env.example', 'w') as f:
            f.write(env_content)
        print("✅ Created .env.example file")
        print("💡 Copy .env.example to .env and add your API keys")
        return True
    except Exception as e:
        print(f"❌ Failed to create .env.example: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 Strands Personal AI Agent - Local Environment Setup")
    print("=" * 60)
    
    # Check Python version
    if not check_python_version():
        print("\n❌ Setup failed: Incompatible Python version")
        return False
    
    # Install requirements
    if not install_requirements():
        print("\n❌ Setup failed: Could not install dependencies")
        return False
    
    # Test imports
    if not test_core_imports():
        print("\n⚠️ Some dependencies are missing, but continuing...")
    
    # Test Strands SDK
    if not test_strands_sdk():
        print("\n⚠️ Strands-Agents SDK not available, but continuing...")
    
    # Create test environment
    create_test_environment()
    
    print("\n🎉 Local environment setup complete!")
    print("=" * 60)
    print("📋 Next steps:")
    print("1. Copy .env.example to .env and add your API keys")
    print("2. Run: python test_agent_import.py")
    print("3. Run: python app.py")
    print("4. Visit: http://localhost:8000/docs")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)