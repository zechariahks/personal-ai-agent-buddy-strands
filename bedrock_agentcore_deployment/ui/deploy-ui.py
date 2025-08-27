#!/usr/bin/env python3
"""
UI Deployment Script for Strands Personal AI Agent
Deploys React UI to AWS using S3 + CloudFront or ECS
"""

import os
import sys
import json
import subprocess
import boto3
from datetime import datetime

class UIDeployer:
    """Deploy React UI for Strands Personal AI Agent"""
    
    def __init__(self, region='us-east-1', deployment_type='s3'):
        self.region = region
        self.deployment_type = deployment_type  # 's3' or 'ecs'
        
        # AWS clients
        self.account_id = boto3.client('sts').get_caller_identity()['Account']
        self.s3 = boto3.client('s3', region_name=region)
        self.cloudfront = boto3.client('cloudfront', region_name=region)
        self.ecr = boto3.client('ecr', region_name=region)
        self.ecs = boto3.client('ecs', region_name=region)
        
        print(f"🚀 Strands Agent UI Deployment")
        print(f"Type: {deployment_type.upper()}")
        print(f"Region: {region}")
        print("=" * 50)
    
    def build_react_app(self, agent_endpoint):
        """Build React application"""
        print("📦 Building React application...")
        
        try:
            # Set environment variables for build
            env = os.environ.copy()
            env['REACT_APP_AGENT_ENDPOINT'] = agent_endpoint
            
            # Install dependencies
            subprocess.run(['npm', 'install'], check=True, cwd='.')
            
            # Build the app
            subprocess.run(['npm', 'run', 'build'], check=True, cwd='.', env=env)
            
            print("✅ React app built successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Build failed: {e}")
            return False
    
    def deploy_to_s3(self, bucket_name=None):
        """Deploy to S3 + CloudFront"""
        if not bucket_name:
            bucket_name = f"strands-agent-ui-{self.account_id}"
        
        print(f"☁️ Deploying to S3: {bucket_name}")
        
        try:
            # Create S3 bucket
            try:
                if self.region == 'us-east-1':
                    self.s3.create_bucket(Bucket=bucket_name)
                else:
                    self.s3.create_bucket(
                        Bucket=bucket_name,
                        CreateBucketConfiguration={'LocationConstraint': self.region}
                    )
                print(f"✅ Created S3 bucket: {bucket_name}")
            except self.s3.exceptions.BucketAlreadyOwnedByYou:
                print(f"✅ S3 bucket already exists: {bucket_name}")
            
            # Configure bucket for static website
            self.s3.put_bucket_website(
                Bucket=bucket_name,
                WebsiteConfiguration={
                    'IndexDocument': {'Suffix': 'index.html'},
                    'ErrorDocument': {'Key': 'index.html'}
                }
            )
            
            # Upload build files
            build_dir = './build'
            for root, dirs, files in os.walk(build_dir):
                for file in files:
                    local_path = os.path.join(root, file)
                    s3_path = os.path.relpath(local_path, build_dir)
                    
                    # Determine content type
                    content_type = 'text/html'
                    if file.endswith('.js'):
                        content_type = 'application/javascript'
                    elif file.endswith('.css'):
                        content_type = 'text/css'
                    elif file.endswith('.json'):
                        content_type = 'application/json'
                    
                    self.s3.upload_file(
                        local_path,
                        bucket_name,
                        s3_path,
                        ExtraArgs={
                            'ContentType': content_type,
                            'ACL': 'public-read'
                        }
                    )
            
            website_url = f"http://{bucket_name}.s3-website-{self.region}.amazonaws.com"
            print(f"✅ UI deployed to: {website_url}")
            
            return website_url
            
        except Exception as e:
            print(f"❌ S3 deployment failed: {e}")
            return None
    
    def deploy_to_ecs(self, agent_endpoint):
        """Deploy to ECS with container"""
        print("🐳 Deploying to ECS...")
        
        try:
            # Build and push Docker image
            repository_name = 'strands-agent-ui'
            
            # Create ECR repository
            try:
                response = self.ecr.create_repository(repositoryName=repository_name)
                repository_uri = response['repository']['repositoryUri']
            except self.ecr.exceptions.RepositoryAlreadyExistsException:
                response = self.ecr.describe_repositories(repositoryNames=[repository_name])
                repository_uri = response['repositories'][0]['repositoryUri']
            
            # Docker login
            login_cmd = f"aws ecr get-login-password --region {self.region} | docker login --username AWS --password-stdin {repository_uri.split('/')[0]}"
            subprocess.run(login_cmd, shell=True, check=True)
            
            # Build and push image
            image_tag = f"{repository_uri}:latest"
            
            # Set build args
            build_args = f"--build-arg REACT_APP_AGENT_ENDPOINT={agent_endpoint}"
            
            subprocess.run([
                'docker', 'build', '-t', image_tag, build_args, '.'
            ], check=True)
            
            subprocess.run(['docker', 'push', image_tag], check=True)
            
            print(f"✅ UI image pushed: {image_tag}")
            return image_tag
            
        except Exception as e:
            print(f"❌ ECS deployment failed: {e}")
            return None
    
    def create_deployment_config(self, ui_url, agent_endpoint):
        """Create deployment configuration"""
        config = {
            "ui_deployment": {
                "type": self.deployment_type,
                "url": ui_url,
                "agent_endpoint": agent_endpoint,
                "region": self.region,
                "deployed_at": datetime.now().isoformat()
            }
        }
        
        with open('ui-deployment-config.json', 'w') as f:
            json.dump(config, f, indent=2)
        
        print("✅ Deployment config saved: ui-deployment-config.json")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Deploy Strands Agent UI')
    parser.add_argument('--agent-endpoint', required=True, help='AgentCore endpoint URL')
    parser.add_argument('--type', choices=['s3', 'ecs'], default='s3', help='Deployment type')
    parser.add_argument('--region', default='us-east-1', help='AWS region')
    parser.add_argument('--bucket', help='S3 bucket name (for S3 deployment)')
    
    args = parser.parse_args()
    
    deployer = UIDeployer(region=args.region, deployment_type=args.type)
    
    # Build React app
    if not deployer.build_react_app(args.agent_endpoint):
        sys.exit(1)
    
    # Deploy based on type
    if args.type == 's3':
        ui_url = deployer.deploy_to_s3(args.bucket)
    else:
        ui_url = deployer.deploy_to_ecs(args.agent_endpoint)
    
    if ui_url:
        deployer.create_deployment_config(ui_url, args.agent_endpoint)
        print(f"\n🎉 UI Deployment Complete!")
        print(f"🌐 Access your UI at: {ui_url}")
    else:
        print("❌ Deployment failed")
        sys.exit(1)

if __name__ == "__main__":
    main()