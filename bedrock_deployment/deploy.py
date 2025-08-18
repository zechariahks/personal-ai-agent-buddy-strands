#!/usr/bin/env python3
"""
Complete deployment script for Strands Personal AI Agent to AWS Bedrock AgentCore
This script orchestrates the entire deployment process
"""

import os
import sys
import json
import subprocess
import time
import boto3
from datetime import datetime
from bedrock_agent_setup import StrandsBedrockAgentDeployer

class StrandsCompleteDeployer:
    """Complete deployment orchestrator for Strands Personal AI Agent"""
    
    def __init__(self, region='us-east-1', profile=None):
        self.region = region
        self.profile = profile
        
        # Set AWS profile if specified
        if profile:
            os.environ['AWS_PROFILE'] = profile
        
        # Initialize AWS clients
        self.account_id = boto3.client('sts').get_caller_identity()['Account']
        self.deployment_info = {}
        
        print(f"🚀 Strands Personal AI Agent - Complete AWS Deployment")
        print(f"Account: {self.account_id}")
        print(f"Region: {self.region}")
        print("=" * 80)
    
    def check_prerequisites(self):
        """Check deployment prerequisites"""
        print("\n📋 Checking Prerequisites...")
        
        # Check AWS CLI
        try:
            result = subprocess.run(['aws', '--version'], capture_output=True, text=True)
            print(f"✅ AWS CLI: {result.stdout.strip()}")
        except FileNotFoundError:
            print("❌ AWS CLI not found. Please install AWS CLI.")
            return False
        
        # Check CDK
        try:
            result = subprocess.run(['cdk', '--version'], capture_output=True, text=True)
            print(f"✅ AWS CDK: {result.stdout.strip()}")
        except FileNotFoundError:
            print("❌ AWS CDK not found. Please install AWS CDK.")
            return False
        
        # Check Python dependencies
        try:
            import aws_cdk
            print(f"✅ CDK Python: {aws_cdk.__version__}")
        except ImportError:
            print("❌ CDK Python libraries not found. Run: pip install -r infrastructure/requirements.txt")
            return False
        
        # Check AWS credentials
        try:
            sts = boto3.client('sts')
            identity = sts.get_caller_identity()
            print(f"✅ AWS Credentials: {identity['Arn']}")
        except Exception as e:
            print(f"❌ AWS Credentials error: {str(e)}")
            return False
        
        print("✅ All prerequisites met!")
        return True
    
    def deploy_infrastructure(self):
        """Deploy CDK infrastructure"""
        print("\n🏗️ Deploying Infrastructure with CDK...")
        
        # Change to infrastructure directory
        os.chdir('infrastructure')
        
        try:
            # Install Python dependencies
            print("📦 Installing CDK dependencies...")
            subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], check=True)
            
            # Bootstrap CDK (if needed)
            print("🔧 Bootstrapping CDK...")
            subprocess.run(['cdk', 'bootstrap'], check=True)
            
            # Deploy the stack
            print("🚀 Deploying CDK stack...")
            result = subprocess.run(['cdk', 'deploy', '--require-approval', 'never'], 
                                  capture_output=True, text=True, check=True)
            
            print("✅ Infrastructure deployed successfully!")
            
            # Parse outputs from CDK
            self._parse_cdk_outputs()
            
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ CDK deployment failed: {e}")
            print(f"Error output: {e.stderr}")
            return False
        finally:
            # Return to parent directory
            os.chdir('..')
    
    def _parse_cdk_outputs(self):
        """Parse CDK outputs for Lambda ARNs"""
        try:
            # Get stack outputs
            cf = boto3.client('cloudformation', region_name=self.region)
            response = cf.describe_stacks(StackName='StrandsPersonalAIAgentStack')
            
            outputs = response['Stacks'][0].get('Outputs', [])
            
            for output in outputs:
                key = output['OutputKey']
                value = output['OutputValue']
                self.deployment_info[key] = value
                print(f"📋 {key}: {value}")
                
        except Exception as e:
            print(f"⚠️ Could not parse CDK outputs: {str(e)}")
    
    def deploy_bedrock_agent(self):
        """Deploy Bedrock Agent with Action Groups"""
        print("\n🤖 Deploying Bedrock Agent...")
        
        try:
            deployer = StrandsBedrockAgentDeployer(region=self.region)
            bedrock_info = deployer.deploy_complete_agent()
            
            if bedrock_info:
                self.deployment_info.update(bedrock_info)
                print("✅ Bedrock Agent deployed successfully!")
                return True
            else:
                print("❌ Bedrock Agent deployment failed!")
                return False
                
        except Exception as e:
            print(f"❌ Bedrock Agent deployment error: {str(e)}")
            return False
    
    def update_lambda_permissions(self):
        """Update Lambda function permissions for Bedrock Agent"""
        print("\n🔐 Updating Lambda permissions for Bedrock Agent...")
        
        try:
            lambda_client = boto3.client('lambda', region_name=self.region)
            
            # Lambda functions to update
            lambda_functions = [
                'strands-weather-capability',
                'strands-calendar-capability',
                'strands-social-capability'
            ]
            
            agent_id = self.deployment_info.get('agent_id')
            if not agent_id:
                print("⚠️ Agent ID not found, skipping permission updates")
                return True
            
            for function_name in lambda_functions:
                try:
                    # Add permission for Bedrock Agent to invoke Lambda
                    lambda_client.add_permission(
                        FunctionName=function_name,
                        StatementId=f'bedrock-agent-{agent_id}',
                        Action='lambda:InvokeFunction',
                        Principal='bedrock.amazonaws.com',
                        SourceArn=f'arn:aws:bedrock:{self.region}:{self.account_id}:agent/{agent_id}'
                    )
                    print(f"✅ Updated permissions for {function_name}")
                    
                except lambda_client.exceptions.ResourceConflictException:
                    print(f"✅ Permissions already exist for {function_name}")
                    
            return True
            
        except Exception as e:
            print(f"❌ Error updating Lambda permissions: {str(e)}")
            return False
    
    def configure_secrets(self):
        """Configure AWS Secrets Manager with API credentials"""
        print("\n🔐 Configuring API credentials in Secrets Manager...")
        
        secrets_client = boto3.client('secretsmanager', region_name=self.region)
        
        # X (Twitter) credentials
        x_secret_name = 'strands-agent/x-credentials'
        print(f"📝 Please configure X API credentials in secret: {x_secret_name}")
        print("   Required fields: api_key, api_secret, access_token, access_token_secret")
        
        # Google Calendar credentials
        google_secret_name = 'strands-agent/google-credentials'
        print(f"📝 Please configure Google Calendar credentials in secret: {google_secret_name}")
        print("   Required fields: token, refresh_token, token_uri, client_id, client_secret")
        
        # Weather API credentials
        weather_secret_name = 'strands-agent/weather-api'
        print(f"📝 Please configure Weather API credentials in secret: {weather_secret_name}")
        print("   Required fields: api_key, default_city")
        
        print("\n💡 You can update these secrets using the AWS Console or CLI:")
        print(f"   aws secretsmanager update-secret --secret-id {x_secret_name} --secret-string '{{...}}'")
        
        return True
    
    def test_deployment(self):
        """Test the deployed agent"""
        print("\n🧪 Testing Deployed Agent...")
        
        try:
            bedrock_agent_runtime = boto3.client('bedrock-agent-runtime', region_name=self.region)
            
            agent_id = self.deployment_info.get('agent_id')
            alias_id = self.deployment_info.get('alias_id')
            
            if not agent_id or not alias_id:
                print("⚠️ Agent ID or Alias ID not found, skipping tests")
                return True
            
            # Test weather capability
            print("🌤️ Testing Weather capability...")
            response = bedrock_agent_runtime.invoke_agent(
                agentId=agent_id,
                agentAliasId=alias_id,
                sessionId='test-session-weather',
                inputText='What is the weather in New York?'
            )
            
            # Process streaming response
            event_stream = response['completion']
            for event in event_stream:
                if 'chunk' in event:
                    chunk = event['chunk']
                    if 'bytes' in chunk:
                        print(f"✅ Weather test response: {chunk['bytes'].decode()[:100]}...")
                        break
            
            print("✅ Basic agent test completed!")
            return True
            
        except Exception as e:
            print(f"⚠️ Agent test error (this is normal if secrets aren't configured): {str(e)}")
            return True
    
    def save_deployment_info(self):
        """Save deployment information"""
        print("\n💾 Saving deployment information...")
        
        deployment_summary = {
            'deployment_time': datetime.now().isoformat(),
            'region': self.region,
            'account_id': self.account_id,
            'deployment_info': self.deployment_info
        }
        
        with open('deployment_summary.json', 'w') as f:
            json.dump(deployment_summary, f, indent=2)
        
        print("✅ Deployment information saved to deployment_summary.json")
    
    def print_next_steps(self):
        """Print next steps for the user"""
        print("\n🎉 Deployment Complete!")
        print("=" * 80)
        
        agent_id = self.deployment_info.get('agent_id')
        alias_id = self.deployment_info.get('alias_id')
        
        if agent_id and alias_id:
            print(f"🤖 Agent ID: {agent_id}")
            print(f"🏷️ Alias ID: {alias_id}")
        
        print("\n📋 Next Steps:")
        print("1. Configure API credentials in AWS Secrets Manager:")
        print("   - X (Twitter) API credentials")
        print("   - Google Calendar OAuth credentials")
        print("   - OpenWeatherMap API key")
        
        print("\n2. Test your agent using the AWS Console or SDK:")
        print("   - Go to Amazon Bedrock > Agents")
        print(f"   - Find your agent: StrandsPersonalAIAgent")
        print("   - Use the test interface to interact with your agent")
        
        print("\n3. Monitor your agent:")
        dashboard_url = self.deployment_info.get('DashboardUrl')
        if dashboard_url:
            print(f"   - CloudWatch Dashboard: {dashboard_url}")
        
        print("\n4. Update the agent as needed:")
        print("   - Modify Lambda functions in the AWS Console")
        print("   - Update Bedrock Agent configuration")
        print("   - Redeploy infrastructure with: python deploy.py")
        
        print("\n🚀 Your Strands Personal AI Agent is now running on AWS!")
    
    def deploy_all(self):
        """Execute complete deployment process"""
        start_time = time.time()
        
        try:
            # Step 1: Check prerequisites
            if not self.check_prerequisites():
                return False
            
            # Step 2: Deploy infrastructure
            if not self.deploy_infrastructure():
                return False
            
            # Step 3: Deploy Bedrock Agent
            if not self.deploy_bedrock_agent():
                return False
            
            # Step 4: Update Lambda permissions
            if not self.update_lambda_permissions():
                return False
            
            # Step 5: Configure secrets (informational)
            self.configure_secrets()
            
            # Step 6: Test deployment
            self.test_deployment()
            
            # Step 7: Save deployment info
            self.save_deployment_info()
            
            # Step 8: Print next steps
            self.print_next_steps()
            
            end_time = time.time()
            duration = end_time - start_time
            print(f"\n⏱️ Total deployment time: {duration:.2f} seconds")
            
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
    
    parser = argparse.ArgumentParser(description='Deploy Strands Personal AI Agent to AWS Bedrock AgentCore')
    parser.add_argument('--region', default='us-east-1', help='AWS region for deployment')
    parser.add_argument('--profile', help='AWS profile to use')
    
    args = parser.parse_args()
    
    # Create and run deployer
    deployer = StrandsCompleteDeployer(region=args.region, profile=args.profile)
    success = deployer.deploy_all()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()