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
import uuid
from datetime import datetime
from typing import Dict, Any
from dotenv import load_dotenv

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
        # required_files = ['app.py', 'Dockerfile', 'requirements.txt']
        # for file in required_files:
        #     if os.path.exists(file):
        #         print(f"✅ {file}: Found")
        #     else:
        #         print(f"❌ {file}: Missing")
        #         return False
        
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
            
            # # Copy agent files to deployment directory
            # print("📁 Copying agent files...")
            # agent_files = [
            #     '../../enhanced_context_aware_agent_strands.py',
            #     '../../basic_agent_strands.py',
            #     '../../weather_tool.py',
            #     '../../bible_verse_tool.py',
            #     '../../x_posting_tool.py',
            #     '../../google_calendar_tool.py'
            # ]
            
            # for file in agent_files:
            #     if os.path.exists(file):
            #         subprocess.run(['cp', file, '../'], check=True)
            #         print(f"✅ Copied {file}")
            
            # Build Docker image
            print("🔨 Building Docker image...")
            image_tag = f"{repository_uri}:latest"
            
            subprocess.run([
                'docker', 'build', '--no-cache', '-t', image_tag, '.'
            ], check=True)
            print(f"✅ Built Docker image: {image_tag}")
            
            # Push image to ECR with retry logic
            print("📤 Pushing image to ECR...")
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    subprocess.run(['docker', 'push', image_tag], check=True, timeout=600)
                    print(f"✅ Pushed image to ECR: {image_tag}")
                    break
                except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
                    if attempt < max_retries - 1:
                        print(f"⚠️ Push attempt {attempt + 1} failed, retrying...")
                        time.sleep(10)  # Wait 10 seconds before retry
                    else:
                        print(f"❌ All push attempts failed. Try: docker system prune -f && docker push {image_tag}")
                        raise
            
            return image_tag
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Docker operation failed: {e}")
            return None
        except Exception as e:
            print(f"❌ Error building/pushing image: {str(e)}")
            return None
    
    def deploy_to_agentcore(self, image_uri):
        """Build a runtime payload using the AWS CLI generated skeleton"""
        print(f"\n🤖 Preparing Bedrock AgentCore runtime configuration...")

        try:
            load_dotenv()

            # Generate CLI skeleton for the create-agent-runtime operation
            print("🔧 Generating CLI skeleton from aws-cli...")
            result = subprocess.run(
                ["aws", "bedrock-agentcore-control", "create-agent-runtime", "--generate-cli-skeleton"],
                capture_output=True, text=True, check=True
            )
            skeleton = json.loads(result.stdout)

            # Fill required top-level fields
            skeleton["agentRuntimeName"] = os.getenv("AGENTCORE_RUNTIME_NAME", self.agent_name)
            skeleton["description"] = skeleton.get("description") or "Strands Personal AI Agent (FastAPI container) - generated"
            skeleton["clientToken"] = os.getenv("AGENTCORE_CLIENT_TOKEN", str(uuid.uuid4()))

            # agentRuntimeArtifact: prefer containerConfiguration if present in skeleton
            artifact = skeleton.get("agentRuntimeArtifact", {})
            container_cfg = {
                "containerUri": image_uri
            }
            if "containerConfiguration" in artifact:
                artifact["containerConfiguration"].update(container_cfg)
            else:
                skeleton["agentRuntimeArtifact"] = {"containerConfiguration": container_cfg}

            # roleArn
            skeleton["roleArn"] = os.getenv(
                "AGENTCORE_ROLE_ARN",
                f"arn:aws:iam::{self.account_id}:role/service-role/AmazonBedrockAgentCoreRuntimeDefaultServiceRole-6dppq"
            )

            # networkConfiguration
            network_mode = os.getenv("AGENTCORE_NETWORK_MODE", "PUBLIC")
            skeleton["networkConfiguration"] = {"networkMode": network_mode}           

            # protocolConfiguration
            proto = skeleton.get("protocolConfiguration", {})
            proto["serverProtocol"] = os.getenv("AGENTCORE_SERVER_PROTOCOL", "HTTP")
            skeleton["protocolConfiguration"] = proto

            # environment variables
            env_vars = {
                "PYTHONPATH": "/app",
                "PYTHONUNBUFFERED": "1",
                "PORT": "8080"
            }
            extra_env = os.getenv("AGENTCORE_ENV_VARS")
            if extra_env:
                for pair in [p for p in extra_env.split(",") if "=" in p]:
                    k, v = pair.split("=", 1)
                    env_vars[k.strip()] = v.strip()
            skeleton["environmentVariables"] = env_vars

            # Remove incomplete authorizerConfiguration
            if "authorizerConfiguration" in skeleton:
                ac = skeleton.get("authorizerConfiguration")
                remove_ac = False
                if not ac or not isinstance(ac, dict):
                    remove_ac = True
                else:
                    cja = ac.get("customJWTAuthorizer")
                    if not cja or not isinstance(cja, dict):
                        remove_ac = True
                    else:
                        disc = cja.get("discoveryUrl", "")
                        if not disc or not isinstance(disc, str) or disc.strip() == "":
                            remove_ac = True

                if remove_ac:
                    print("ℹ️ Removing incomplete authorizerConfiguration from payload.")
                    skeleton.pop("authorizerConfiguration", None)

            # Save the final payload
            with open("agentcore_config.json", "w") as f:
                json.dump(skeleton, f, indent=2)

            print("✅ agentcore_config.json created using AWS CLI skeleton.")
            return True

        except subprocess.CalledProcessError as e:
            print("❌ Failed to generate CLI skeleton. Is aws-cli v2 installed and configured?")
            print(e.stderr or str(e))
            return False
        except Exception as e:
            print(f"❌ Error preparing AgentCore configuration: {e}")
            return False
    
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
            
            # Step 4: Deploy to AgentCore (prepare configuration)
            if not self.deploy_to_agentcore(image_uri):
                return False
            
            end_time = time.time()
            duration = end_time - start_time
            
            print(f"\n🎉 Deployment Preparation Complete!")
            print("=" * 80)
            print(f"⏱️ Total time: {duration:.2f} seconds")
            print(f"🐳 Docker image: {image_uri}")
            print(f"📋 Configuration: agentcore_config.json")
            
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