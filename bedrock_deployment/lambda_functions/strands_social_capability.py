#!/usr/bin/env python3
"""
Strands Social Media Capability Lambda Function
AWS Lambda implementation of X (Twitter) posting and Bible verse sharing
"""

import json
import os
import boto3
import requests
import hashlib
import hmac
import base64
import urllib.parse
import time
import secrets
from datetime import datetime
from typing import Dict, Any

def lambda_handler(event, context):
    """
    AWS Lambda handler for Strands Social Media Capability
    """
    try:
        print(f"Received event: {json.dumps(event)}")
        
        # Extract parameters and determine action
        parameters = extract_parameters(event)
        action = determine_action(event, parameters)
        
        # Route to appropriate handler
        if action == 'post_content':
            result = handle_post_content(parameters)
        elif action == 'post_bible_verse':
            result = handle_post_bible_verse(parameters)
        elif action == 'check_status':
            result = handle_check_status(parameters)
        else:
            result = {
                'success': False,
                'error': f'Unknown action: {action}',
                'available_actions': ['post_content', 'post_bible_verse', 'check_status']
            }
        
        return {
            'statusCode': 200 if result.get('success', True) else 400,
            'body': json.dumps(result)
        }
        
    except Exception as e:
        print(f"Error in social media capability: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'success': False,
                'error': str(e),
                'message': 'Social media capability error'
            })
        }

def extract_parameters(event):
    """Extract parameters from Bedrock Agent event"""
    parameters = {}
    
    # Handle different event formats
    if 'parameters' in event:
        for param in event['parameters']:
            parameters[param['name']] = param['value']
    elif 'requestBody' in event:
        body = json.loads(event['requestBody']['content']['application/json']['properties'])
        parameters = body
    elif 'body' in event:
        body = json.loads(event['body']) if isinstance(event['body'], str) else event['body']
        parameters = body
    
    return parameters

def determine_action(event, parameters):
    """Determine the social media action to perform"""
    # Check explicit action parameter
    action = parameters.get('action', '').lower()
    if action:
        return action
    
    # Check content type
    content_type = parameters.get('type', '').lower()
    if content_type == 'bible_verse':
        return 'post_bible_verse'
    
    # Check if content is provided
    if parameters.get('content'):
        return 'post_content'
    
    # Default to status check
    return 'check_status'

def handle_post_content(parameters):
    """Handle posting custom content to X"""
    try:
        content = parameters.get('content', '').strip()
        if not content:
            return {
                'success': False,
                'error': 'Content is required for posting',
                'message': 'Please provide content to post'
            }
        
        # Check content length (X has 280 character limit)
        if len(content) > 280:
            return {
                'success': False,
                'error': 'Content too long',
                'message': f'Content is {len(content)} characters, maximum is 280'
            }
        
        # Post to X
        result = post_to_x(content)
        
        if result['success']:
            return {
                'success': True,
                'message': 'Content posted successfully to X',
                'content': content,
                'character_count': len(content),
                'post_details': result.get('details', {})
            }
        else:
            return {
                'success': False,
                'error': result.get('error', 'Unknown error'),
                'message': 'Failed to post content to X'
            }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'message': 'Failed to post custom content'
        }

def handle_post_bible_verse(parameters):
    """Handle getting and posting a Bible verse"""
    try:
        # Get Bible verse
        verse_result = get_bible_verse_for_posting()
        
        if not verse_result or "❌" in verse_result:
            return {
                'success': False,
                'error': 'Failed to fetch Bible verse',
                'message': verse_result or 'Unable to retrieve Bible verse'
            }
        
        # Format for X posting
        post_content = f'"{verse_result}" #BibleVerse #Faith #Inspiration'
        
        # Check length and truncate if necessary
        if len(post_content) > 280:
            # Truncate the verse but keep hashtags
            max_verse_length = 280 - len(' #BibleVerse #Faith #Inspiration') - 3  # 3 for quotes and space
            truncated_verse = verse_result[:max_verse_length] + "..."
            post_content = f'"{truncated_verse}" #BibleVerse #Faith #Inspiration'
        
        # Post to X
        result = post_to_x(post_content)
        
        if result['success']:
            return {
                'success': True,
                'message': 'Bible verse posted successfully to X',
                'verse': verse_result,
                'post_content': post_content,
                'character_count': len(post_content),
                'post_details': result.get('details', {})
            }
        else:
            return {
                'success': False,
                'error': result.get('error', 'Unknown error'),
                'message': 'Failed to post Bible verse to X',
                'verse': verse_result
            }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'message': 'Failed to post Bible verse'
        }

def handle_check_status(parameters):
    """Handle checking X account status"""
    try:
        # Check if X credentials are available
        credentials = get_x_credentials()
        if not all(credentials.values()):
            missing = [k for k, v in credentials.items() if not v]
            return {
                'success': False,
                'error': 'Missing X credentials',
                'message': f'Missing credentials: {", ".join(missing)}',
                'status': 'Not configured'
            }
        
        # Try to get account info
        account_info = get_x_account_info()
        
        if account_info.get('success'):
            return {
                'success': True,
                'message': 'X account connection successful',
                'account_info': account_info.get('data', {}),
                'status': 'Connected'
            }
        else:
            return {
                'success': False,
                'error': account_info.get('error', 'Unknown error'),
                'message': 'Failed to connect to X account',
                'status': 'Connection failed'
            }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'message': 'Failed to check X account status',
            'status': 'Error'
        }

def get_x_credentials():
    """Get X API credentials from environment or AWS Secrets Manager"""
    try:
        # Try AWS Secrets Manager first
        secret_name = os.environ.get('X_CREDENTIALS_SECRET_NAME')
        if secret_name:
            secrets_client = boto3.client('secretsmanager')
            response = secrets_client.get_secret_value(SecretId=secret_name)
            secret_data = json.loads(response['SecretString'])
            
            return {
                'api_key': secret_data.get('api_key'),
                'api_secret': secret_data.get('api_secret'),
                'access_token': secret_data.get('access_token'),
                'access_token_secret': secret_data.get('access_token_secret')
            }
        
        # Fallback to environment variables
        return {
            'api_key': os.environ.get('X_API_KEY'),
            'api_secret': os.environ.get('X_API_SECRET'),
            'access_token': os.environ.get('X_ACCESS_TOKEN'),
            'access_token_secret': os.environ.get('X_ACCESS_TOKEN_SECRET')
        }
        
    except Exception as e:
        print(f"Error getting X credentials: {str(e)}")
        return {
            'api_key': None,
            'api_secret': None,
            'access_token': None,
            'access_token_secret': None
        }

def post_to_x(content):
    """Post content to X using OAuth 1.0a"""
    try:
        credentials = get_x_credentials()
        
        if not all(credentials.values()):
            return {
                'success': False,
                'error': 'Missing X API credentials'
            }
        
        # X API v2 endpoint for posting tweets
        url = "https://api.twitter.com/2/tweets"
        
        # Request payload
        payload = {
            "text": content
        }
        
        # Generate OAuth 1.0a signature
        oauth_params = generate_oauth_signature(
            url=url,
            method='POST',
            api_key=credentials['api_key'],
            api_secret=credentials['api_secret'],
            access_token=credentials['access_token'],
            access_token_secret=credentials['access_token_secret'],
            payload=payload
        )
        
        # Make the request
        headers = {
            'Authorization': oauth_params,
            'Content-Type': 'application/json'
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        if response.status_code == 201:
            tweet_data = response.json()
            return {
                'success': True,
                'message': 'Successfully posted to X',
                'details': {
                    'tweet_id': tweet_data.get('data', {}).get('id'),
                    'text': tweet_data.get('data', {}).get('text'),
                    'timestamp': datetime.now().isoformat()
                }
            }
        else:
            error_data = response.json() if response.content else {}
            return {
                'success': False,
                'error': f'X API error: {response.status_code}',
                'details': error_data
            }
        
    except Exception as e:
        return {
            'success': False,
            'error': f'Failed to post to X: {str(e)}'
        }

def generate_oauth_signature(url, method, api_key, api_secret, access_token, access_token_secret, payload=None):
    """Generate OAuth 1.0a signature for X API"""
    try:
        # OAuth parameters
        oauth_params = {
            'oauth_consumer_key': api_key,
            'oauth_token': access_token,
            'oauth_signature_method': 'HMAC-SHA1',
            'oauth_timestamp': str(int(time.time())),
            'oauth_nonce': secrets.token_urlsafe(32),
            'oauth_version': '1.0'
        }
        
        # Create parameter string
        params = oauth_params.copy()
        
        # Sort parameters
        sorted_params = sorted(params.items())
        param_string = '&'.join([f'{k}={urllib.parse.quote(str(v), safe="")}' for k, v in sorted_params])
        
        # Create signature base string
        base_string = f'{method.upper()}&{urllib.parse.quote(url, safe="")}&{urllib.parse.quote(param_string, safe="")}'
        
        # Create signing key
        signing_key = f'{urllib.parse.quote(api_secret, safe="")}&{urllib.parse.quote(access_token_secret, safe="")}'
        
        # Generate signature
        signature = base64.b64encode(
            hmac.new(
                signing_key.encode(),
                base_string.encode(),
                hashlib.sha1
            ).digest()
        ).decode()
        
        oauth_params['oauth_signature'] = signature
        
        # Create authorization header
        auth_header = 'OAuth ' + ', '.join([f'{k}="{urllib.parse.quote(str(v), safe="")}"' for k, v in sorted(oauth_params.items())])
        
        return auth_header
        
    except Exception as e:
        raise Exception(f"Failed to generate OAuth signature: {str(e)}")

def get_x_account_info():
    """Get X account information"""
    try:
        credentials = get_x_credentials()
        
        if not all(credentials.values()):
            return {
                'success': False,
                'error': 'Missing X API credentials'
            }
        
        # X API v2 endpoint for user info
        url = "https://api.twitter.com/2/users/me"
        
        # Generate OAuth 1.0a signature
        oauth_params = generate_oauth_signature(
            url=url,
            method='GET',
            api_key=credentials['api_key'],
            api_secret=credentials['api_secret'],
            access_token=credentials['access_token'],
            access_token_secret=credentials['access_token_secret']
        )
        
        headers = {
            'Authorization': oauth_params
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            user_data = response.json()
            return {
                'success': True,
                'data': {
                    'username': user_data.get('data', {}).get('username'),
                    'name': user_data.get('data', {}).get('name'),
                    'id': user_data.get('data', {}).get('id'),
                    'verified': user_data.get('data', {}).get('verified', False)
                }
            }
        else:
            return {
                'success': False,
                'error': f'X API error: {response.status_code}'
            }
        
    except Exception as e:
        return {
            'success': False,
            'error': f'Failed to get X account info: {str(e)}'
        }

def get_bible_verse_for_posting():
    """Get a Bible verse suitable for social media posting"""
    try:
        # Try multiple Bible APIs
        apis = [
            "https://bible-api.com/john+3:16",
            "https://labs.bible.org/api/?passage=random&type=json",
            "https://bible-api.com/romans+8:28"
        ]
        
        for api_url in apis:
            try:
                response = requests.get(api_url, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    
                    if 'text' in data:
                        # bible-api.com format
                        verse_text = data['text'].strip()
                        reference = data.get('reference', 'Bible')
                        return f"{verse_text} - {reference}"
                    elif isinstance(data, list) and len(data) > 0:
                        # labs.bible.org format
                        verse_data = data[0]
                        verse_text = verse_data.get('text', '').strip()
                        book = verse_data.get('bookname', '')
                        chapter = verse_data.get('chapter', '')
                        verse = verse_data.get('verse', '')
                        reference = f"{book} {chapter}:{verse}" if all([book, chapter, verse]) else "Bible"
                        return f"{verse_text} - {reference}"
                        
            except Exception as e:
                print(f"API {api_url} failed: {str(e)}")
                continue
        
        # Fallback verses if APIs fail
        fallback_verses = [
            "For God so loved the world that he gave his one and only Son, that whoever believes in him shall not perish but have eternal life. - John 3:16",
            "And we know that in all things God works for the good of those who love him, who have been called according to his purpose. - Romans 8:28",
            "Trust in the Lord with all your heart and lean not on your own understanding. - Proverbs 3:5",
            "I can do all this through him who gives me strength. - Philippians 4:13",
            "The Lord is my shepherd, I lack nothing. - Psalm 23:1"
        ]
        
        import random
        return random.choice(fallback_verses)
        
    except Exception as e:
        return f"❌ Error fetching Bible verse: {str(e)}"

# For local testing
if __name__ == "__main__":
    test_event = {
        'parameters': [
            {'name': 'action', 'value': 'post_bible_verse'}
        ],
        'sessionId': 'test-session'
    }
    
    result = lambda_handler(test_event, None)
    print(json.dumps(result, indent=2))