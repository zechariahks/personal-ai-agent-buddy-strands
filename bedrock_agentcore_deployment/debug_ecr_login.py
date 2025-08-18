#!/usr/bin/env python3
"""
Debug script for ECR login issues
Helps troubleshoot Docker and ECR authentication problems
"""

import subprocess
import boto3
import base64
import sys

def check_aws_credentials():
    """Check AWS credentials and permissions"""
    print("🔐 Checking AWS Credentials...")
    try:
        sts = boto3.client('sts')
        identity = sts.get_caller_identity()
        print(f"✅ AWS Identity: {identity['Arn']}")
        print(f"✅ Account ID: {identity['Account']}")
        return True
    except Exception as e:
        print(f"❌ AWS Credentials error: {str(e)}")
        return False

def check_ecr_permissions():
    """Check ECR permissions"""
    print("\n🏗️ Checking ECR Permissions...")
    try:
        ecr = boto3.client('ecr', region_name='us-east-1')
        
        # Try to list repositories
        repos = ecr.describe_repositories()
        print(f"✅ ECR Access: Can list {len(repos['repositories'])} repositories")
        
        # Try to get authorization token
        auth = ecr.get_authorization_token()
        print("✅ ECR Authorization: Can get login token")
        return True
        
    except Exception as e:
        print(f"❌ ECR Permissions error: {str(e)}")
        return False

def test_docker():
    """Test Docker installation and functionality"""
    print("\n🐳 Testing Docker...")
    try:
        # Check Docker version
        result = subprocess.run(['docker', '--version'], capture_output=True, text=True, check=True)
        print(f"✅ Docker Version: {result.stdout.strip()}")
        
        # Check if Docker daemon is running
        result = subprocess.run(['docker', 'info'], capture_output=True, text=True, check=True)
        print("✅ Docker Daemon: Running")
        return True
        
    except FileNotFoundError:
        print("❌ Docker not found. Please install Docker.")
        return False
    except subprocess.CalledProcessError as e:
        print(f"❌ Docker error: {e}")
        print("💡 Make sure Docker daemon is running")
        return False

def test_ecr_login():
    """Test ECR login process"""
    print("\n🔑 Testing ECR Login Process...")
    try:
        region = 'us-east-1'
        
        # Get ECR authorization
        ecr = boto3.client('ecr', region_name=region)
        auth_response = ecr.get_authorization_token()
        
        token_b64 = auth_response['authorizationData'][0]['authorizationToken']
        endpoint = auth_response['authorizationData'][0]['proxyEndpoint']
        
        print(f"✅ ECR Endpoint: {endpoint}")
        
        # Decode token
        token_decoded = base64.b64decode(token_b64).decode('utf-8')
        username, password = token_decoded.split(':', 1)
        print(f"✅ Token decoded successfully (username: {username})")
        
        # Test AWS CLI ECR login
        print("\n🔧 Testing AWS CLI ECR login...")
        registry_url = endpoint.replace('https://', '')
        
        # Method 1: AWS CLI get-login-password
        try:
            get_password_cmd = ['aws', 'ecr', 'get-login-password', '--region', region]
            password_result = subprocess.run(get_password_cmd, capture_output=True, text=True, check=True)
            print("✅ AWS CLI get-login-password: Success")
            
            # Test Docker login
            docker_login_cmd = ['docker', 'login', '--username', 'AWS', '--password-stdin', registry_url]
            subprocess.run(docker_login_cmd, input=password_result.stdout.strip(), text=True, check=True)
            print("✅ Docker login to ECR: Success")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ ECR login failed: {e}")
            
            # Try alternative method
            print("\n🔄 Trying alternative login method...")
            try:
                subprocess.run([
                    'docker', 'login', '--username', username, '--password-stdin', registry_url
                ], input=password, text=True, check=True)
                print("✅ Alternative Docker login: Success")
                return True
            except subprocess.CalledProcessError as e2:
                print(f"❌ Alternative login also failed: {e2}")
                return False
                
    except Exception as e:
        print(f"❌ ECR login test error: {str(e)}")
        return False

def main():
    """Run all diagnostic tests"""
    print("🔍 ECR Login Diagnostic Tool")
    print("=" * 50)
    
    all_passed = True
    
    # Test AWS credentials
    if not check_aws_credentials():
        all_passed = False
    
    # Test ECR permissions
    if not check_ecr_permissions():
        all_passed = False
    
    # Test Docker
    if not test_docker():
        all_passed = False
    
    # Test ECR login
    if not test_ecr_login():
        all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 All tests passed! ECR login should work.")
        print("\n💡 You can now run: python deploy.py --region us-east-1")
    else:
        print("❌ Some tests failed. Please fix the issues above.")
        print("\n🔧 Common solutions:")
        print("• Make sure Docker is installed and running")
        print("• Check AWS credentials: aws configure list")
        print("• Verify ECR permissions in IAM")
        print("• Try: aws ecr get-login-password --region us-east-1")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)