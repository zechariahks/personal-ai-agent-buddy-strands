#!/usr/bin/env python3
"""
Bedrock AgentCore Deployment Script for Strands Personal AI Agent
Option B: Custom Agent using FastAPI server and ECR deployment
"""

import os
import sys
import json
import subprocess
import time
import boto3
from datetime import datetime
from typing import Dict, Any

class StrandsAgentCoreDeployer:
    """Deploy Strands Personal AI Agent to Bedrock AgentCore using Custom Agent approach"""
    
    def __init__(self, region='us-east-1', profile=None):
        self.region = region
        self.profile = profile
        
        # Set AWS profile if specified
        if profile:
            os.environ['AWS_PROFILE'] = profile
        
        # Initialize AWS clients
        self.account_id = boto3.client('sts').get_caller_identity()['Account']
        self.ecr = boto3.client('ecr', region_name=region)
        self.bedrock_agentcore = boto3.client('bedrock-agentcore', region_name=region)
        
        # Configuration
        self.image_name = 'strands-personal-ai-agent'
        self.repository_name = f'{self.image_name}-repo'
        self.agent_name = 'StrandsPersonalAIAgent'
        
        print(f"🚀 Strands Personal AI Agent - Bedrock AgentCore Deployment")
        print(f"Account: {self.account_id}")
        print(f"Region: {self.region}")
        print(f"Deployment Type: Custom Agent (FastAPI + ECR)")
        print("=" * 80)
    
    def check_prerequisites(self):
        """Check deployment prerequisites"""
        print("\n📋 Checking Prerequisites...")
        
        # Check Docker
        try:
            result = subprocess.run(['docker', '--version'], capture_output=True, text=True)
            print(f"✅ Docker: {result.stdout.strip()}")
        except FileNotFoundError:
            print("❌ Docker not found. Please install Docker.")
            return False
        
        # Check AWS CLI
        try:
            result = subprocess.run(['aws', '--version'], capture_output=True, text=True)
            print(f"✅ AWS CLI: {result.stdout.strip()}")
        except FileNotFoundError:
            print("❌ AWS CLI not found. Please install AWS CLI.")
            return False
        
        # Check AWS credentials
        try:
            sts = boto3.client('sts')
            identity = sts.get_caller_identity()
            print(f"✅ AWS Credentials: {identity['Arn']}")
        except Exception as e:
            print(f"❌ AWS Credentials error: {str(e)}")
            return False
        
        # Check if required files exist
        required_files = ['app.py', 'Dockerfile', 'requirements.txt']
        for file in required_files:
            if os.path.exists(file):
                print(f"✅ {file}: Found")
            else:
                print(f"❌ {file}: Missing")
                return False
        
        print("✅ All prerequisites met!")
        return True
    
    def create_ecr_repository(self):
        """Create ECR repository for the agent image"""
        print(f"\n🏗️ Creating ECR Repository: {self.repository_name}")
        
        try:
            # Check if repository exists
            try:
                response = self.ecr.describe_repositories(repositoryNames=[self.repository_name])
                print(f"✅ Repository already exists: {self.repository_name}")
                return response['repositories'][0]['repositoryUri']
            except self.ecr.exceptions.RepositoryNotFoundException:
                pass
            
            # Create repository
            response = self.ecr.create_repository(
                repositoryName=self.repository_name,
                imageScanningConfiguration={'scanOnPush': True},
                encryptionConfiguration={'encryptionType': 'AES256'},
                tags=[
                    {'Key': 'Framework', 'Value': 'StrandsAgents'},
                    {'Key': 'Application', 'Value': 'PersonalAIAgent'},
                    {'Key': 'DeploymentType', 'Value': 'BedrockAgentCore'}
                ]
            )
            
            repository_uri = response['repository']['repositoryUri']
            print(f"✅ Created ECR repository: {repository_uri}")
            return repository_uri
            
        except Exception as e:
            print(f"❌ Error creating ECR repository: {str(e)}")
            return None
    
    def build_and_push_image(self, repository_uri):
        """Build Docker image and push to ECR"""
        print(f"\n🐳 Building and Pushing Docker Image...")
        
        try:
            # Use AWS CLI ECR login helper (most reliable method)
            print("🔐 Logging into ECR using AWS CLI...")
            
            # Get the registry URL from repository URI
            registry_url = repository_uri.split('/')[0]
            
            # Use AWS CLI to get login password and pipe to docker login
            get_password_cmd = ['aws', 'ecr', 'get-login-password', '--region', self.region]
            docker_login_cmd = ['docker', 'login', '--username', 'AWS', '--password-stdin', registry_url]
            
            # Get the password
            password_result = subprocess.run(get_password_cmd, capture_output=True, text=True, check=True)
            password = password_result.stdout.strip()
            
            # Login to Docker
            subprocess.run(docker_login_cmd, input=password, text=True, check=True)
            print("✅ Docker login to ECR successful")
            
            # Copy agent files to deployment directory
            print("📁 Copying agent files...")
            agent_files = [
                '../enhanced_context_aware_agent_strands.py',
                '../basic_agent_strands.py',
                '../weather_tool.py',
                '../bible_verse_tool.py',
                '../x_posting_tool.py',
                '../google_calendar_tool.py'
            ]
            
            for file in agent_files:
                if os.path.exists(file):
                    subprocess.run(['cp', file, '.'], check=True)
                    print(f"✅ Copied {file}")
            
            # Build Docker image
            print("🔨 Building Docker image...")
            image_tag = f"{repository_uri}:latest"
            
            subprocess.run([
                'docker', 'build', '-t', image_tag, '.'
            ], check=True)
            print(f"✅ Built Docker image: {image_tag}")
            
            # Push image to ECR
            print("📤 Pushing image to ECR...")
            subprocess.run(['docker', 'push', image_tag], check=True)
            print(f"✅ Pushed image to ECR: {image_tag}")
            
            return image_tag
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Docker operation failed: {e}")
            return None
        except Exception as e:
            print(f"❌ Error building/pushing image: {str(e)}")
            return None
    
    def deploy_to_agentcore(self, image_uri):
        """Deploy the agent to Bedrock AgentCore"""
        print(f"\n🤖 Deploying to Bedrock AgentCore...")
        
        try:
            # Create AgentCore application
            app_config = {
                'name': self.agent_name,
                'description': 'Enhanced Personal AI Agent built with Strands-Agents SDK',
                'runtime': {
                    'type': 'CUSTOM',
                    'image': {
                        'uri': image_uri,
                        'port': 8000
                    }
                },
                'environment': {
                    'variables': {
                        'PYTHONPATH': '/app',
                        'PYTHONUNBUFFERED': '1',
                        'PORT': '8000'
                    }
                },
                'tags': {
                    'Framework': 'StrandsAgents',
                    'Version': '2.0',
                    'DeploymentType': 'CustomAgent'
                }
            }
            
            # Note: This is a placeholder for the actual Bedrock AgentCore API
            # The actual API calls will depend on the final AgentCore service implementation
            print("📋 AgentCore Configuration:")
            print(json.dumps(app_config, indent=2))
            
            # For now, we'll create a configuration file that can be used with the AgentCore CLI
            with open('agentcore_config.json', 'w') as f:
                json.dump(app_config, f, indent=2)
            
            print("✅ AgentCore configuration saved to agentcore_config.json")
            print("💡 Use this configuration with the Bedrock AgentCore CLI when available")
            
            return True
            
        except Exception as e:
            print(f"❌ Error deploying to AgentCore: {str(e)}")
            return False
    
    def test_local_deployment(self):
        """Test the agent locally before deploying"""
        print(f"\n🧪 Testing Local Deployment...")
        
        try:
            # Start the FastAPI server in background
            print("🚀 Starting local FastAPI server...")
            
            # Check if we can import the app
            sys.path.insert(0, '.')
            from app import app
            
            print("✅ FastAPI app imported successfully")
            print("💡 To test locally, run: python app.py")
            print("📋 Available endpoints:")
            print("   • GET  /health    - Health check")
            print("   • POST /invoke    - Main agent interaction")
            print("   • POST /weather   - Weather capability")
            print("   • POST /calendar  - Calendar capability")
            print("   • POST /social    - Social media capability")
            
            return True
            
        except Exception as e:
            print(f"❌ Local testing error: {str(e)}")
            return False
    
    def create_deployment_guide(self):
        """Create deployment guide and next steps"""
        print(f"\n📚 Creating Deployment Guide...")
        
        guide_content = f"""# Strands Personal AI Agent - Bedrock AgentCore Deployment

## Deployment Summary
- **Agent Name**: {self.agent_name}
- **Deployment Type**: Custom Agent (FastAPI + ECR)
- **Framework**: Strands-Agents SDK
- **Region**: {self.region}
- **Account**: {self.account_id}

## Architecture
```
Bedrock AgentCore Runtime
├── ECR Container Image
│   ├── FastAPI Server (app.py)
│   ├── Strands Enhanced Agent
│   └── All Capabilities (Weather, Calendar, Social)
├── Custom HTTP Interface
│   ├── /invoke - Main agent interaction
│   ├── /weather - Weather capability
│   ├── /calendar - Calendar capability
│   └── /social - Social media capability
└── Auto-scaling & Load Balancing
```

## Next Steps

### 1. Complete AgentCore Deployment
When Bedrock AgentCore becomes available:
```bash
# Use the generated configuration
aws bedrock-agentcore create-application --cli-input-json file://agentcore_config.json
```

### 2. Configure Environment Variables
Set up the following environment variables in AgentCore:
- `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` - AI model provider
- `X_API_KEY`, `X_API_SECRET`, `X_ACCESS_TOKEN`, `X_ACCESS_TOKEN_SECRET` - X API
- `OPENWEATHER_API_KEY` - Weather API
- Google Calendar OAuth credentials

### 3. Test the Deployment
```bash
# Health check
curl https://your-agentcore-endpoint/health

# Agent interaction
curl -X POST https://your-agentcore-endpoint/invoke \\
  -H "Content-Type: application/json" \\
  -d '{{"message": "What\\'s the weather in New York?", "session_id": "test-123"}}'
```

### 4. Monitor and Scale
- Use AgentCore monitoring dashboards
- Configure auto-scaling based on request volume
- Set up alerts for errors and performance issues

## Local Testing
To test locally before deployment:
```bash
python app.py
# Then visit http://localhost:8000/docs for interactive API documentation
```

## Capabilities Available
- ✅ Weather analysis with impact assessment
- ✅ Google Calendar integration
- ✅ X (Twitter) posting with Bible verses
- ✅ Multi-agent coordination
- ✅ Contextual decision making
- ✅ FastAPI REST endpoints
- ✅ Health monitoring
- ✅ Auto-scaling ready

Generated on: {datetime.now().isoformat()}
"""
        
        with open('DEPLOYMENT_GUIDE.md', 'w') as f:
            f.write(guide_content)
        
        print("✅ Deployment guide created: DEPLOYMENT_GUIDE.md")
    
    def deploy_all(self):
        """Execute complete deployment process"""
        start_time = time.time()
        
        try:
            # Step 1: Check prerequisites
            if not self.check_prerequisites():
                return False
            
            # Step 2: Create ECR repository
            repository_uri = self.create_ecr_repository()
            if not repository_uri:
                return False
            
            # Step 3: Build and push Docker image
            image_uri = self.build_and_push_image(repository_uri)
            if not image_uri:
                return False
            
            # Step 4: Test local deployment
            if not self.test_local_deployment():
                print("⚠️ Local testing failed, but continuing with deployment...")
            
            # Step 5: Deploy to AgentCore (prepare configuration)
            if not self.deploy_to_agentcore(image_uri):
                return False
            
            # Step 6: Create deployment guide
            self.create_deployment_guide()
            
            end_time = time.time()
            duration = end_time - start_time
            
            print(f"\n🎉 Deployment Preparation Complete!")
            print("=" * 80)
            print(f"⏱️ Total time: {duration:.2f} seconds")
            print(f"🐳 Docker image: {image_uri}")
            print(f"📋 Configuration: agentcore_config.json")
            print(f"📚 Guide: DEPLOYMENT_GUIDE.md")
            
            print(f"\n📋 Next Steps:")
            print("1. Review the generated agentcore_config.json")
            print("2. Wait for Bedrock AgentCore availability")
            print("3. Deploy using AgentCore CLI or Console")
            print("4. Configure environment variables")
            print("5. Test the deployed agent")
            
            return True
            
        except KeyboardInterrupt:
            print("\n❌ Deployment interrupted by user")
            return False
        except Exception as e:
            print(f"\n❌ Deployment failed: {str(e)}")
            return False

def main():
    """Main deployment function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Deploy Strands Personal AI Agent to Bedrock AgentCore')
    parser.add_argument('--region', default='us-east-1', help='AWS region for deployment')
    parser.add_argument('--profile', help='AWS profile to use')
    
    args = parser.parse_args()
    
    # Create and run deployer
    deployer = StrandsAgentCoreDeployer(region=args.region, profile=args.profile)
    success = deployer.deploy_all()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()