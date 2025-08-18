#!/usr/bin/env python3
"""
X (Twitter) Posting Tool for Strands-Agents SDK
Posts content to X using the X API v2 with OAuth 1.0a authentication
"""

import os
import requests
import json
import hmac
import hashlib
import base64
import urllib.parse
import time
import secrets
from datetime import datetime
from strands import tool


def generate_oauth_signature(method, url, params, consumer_secret, token_secret=""):
    """Generate OAuth 1.0a signature for X API"""
    # Create parameter string
    param_string = "&".join([f"{k}={urllib.parse.quote(str(v), safe='')}"
                            for k, v in sorted(params.items())])
    
    # Create signature base string
    base_string = f"{method}&{urllib.parse.quote(url, safe='')}&{urllib.parse.quote(param_string, safe='')}"
    
    # Create signing key
    signing_key = f"{urllib.parse.quote(consumer_secret, safe='')}&{urllib.parse.quote(token_secret, safe='')}"
    
    # Generate signature
    signature = base64.b64encode(
        hmac.new(signing_key.encode(), base_string.encode(), hashlib.sha1).digest()
    ).decode()
    
    return signature


@tool
def post_to_x(content: str) -> str:
    """
    Post content to X (Twitter) using X API v2 with OAuth 1.0a authentication.
    
    Args:
        content: The text content to post to X (max 280 characters)
        
    Returns:
        A formatted string with the posting result and post details
    """
    # Check for X API credentials
    api_key = os.getenv("X_API_KEY")
    api_secret = os.getenv("X_API_SECRET")
    access_token = os.getenv("X_ACCESS_TOKEN")
    access_token_secret = os.getenv("X_ACCESS_TOKEN_SECRET")
    
    if not all([api_key, api_secret, access_token, access_token_secret]):
        return f"""
❌ X (Twitter) API credentials not configured.

To enable X posting, please set these environment variables:
• X_API_KEY="your-api-key"
• X_API_SECRET="your-api-secret"
• X_ACCESS_TOKEN="your-access-token"
• X_ACCESS_TOKEN_SECRET="your-access-token-secret"

Setup Instructions:
1. Go to https://developer.twitter.com/
2. Create a new app or use existing one
3. Generate API keys and access tokens
4. Ensure your app has "Read and Write" permissions
5. Set the environment variables above

📝 Content ready to post:
{content}

💡 Once configured, I'll be able to post this content to your X account automatically.
        """.strip()
    
    # Validate content length
    if len(content) > 280:
        return f"""
❌ Content too long for X posting.

Content length: {len(content)} characters
X limit: 280 characters

📝 Content:
{content}

💡 Please shorten the content and try again.
        """.strip()
    
    try:
        # X API v2 endpoint for posting tweets
        url = "https://api.twitter.com/2/tweets"
        
        # OAuth 1.0a parameters
        oauth_params = {
            "oauth_consumer_key": api_key,
            "oauth_token": access_token,
            "oauth_signature_method": "HMAC-SHA1",
            "oauth_timestamp": str(int(time.time())),
            "oauth_nonce": secrets.token_urlsafe(32),
            "oauth_version": "1.0"
        }
        
        # Prepare the payload
        payload = {
            "text": content
        }
        
        # Generate OAuth signature
        all_params = {**oauth_params}
        oauth_params["oauth_signature"] = generate_oauth_signature(
            "POST", url, all_params, api_secret, access_token_secret
        )
        
        # Create Authorization header
        auth_header = "OAuth " + ", ".join([
            f'{k}="{urllib.parse.quote(str(v), safe="")}"'
            for k, v in sorted(oauth_params.items())
        ])
        
        headers = {
            "Authorization": auth_header,
            "Content-Type": "application/json"
        }
        
        print(f"📱 Posting to X: {content[:50]}...")
        
        # Make the API request
        response = requests.post(
            url,
            headers=headers,
            data=json.dumps(payload),
            timeout=30
        )
        
        if response.status_code == 201:
            # Success
            response_data = response.json()
            tweet_id = response_data.get("data", {}).get("id", "unknown")
            
            result = f"""
✅ Successfully posted to X!

📱 Post ID: {tweet_id}
🔗 URL: https://twitter.com/i/web/status/{tweet_id}
📝 Content: {content}
⏰ Posted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

🎉 Your post is now live on X!
            """.strip()
            
            return result
            
        elif response.status_code == 400:
            error_data = response.json()
            errors = error_data.get("errors", [])
            error_messages = [err.get("message", "Unknown error") for err in errors]
            
            return f"""
❌ X posting failed: Bad request

Errors: {', '.join(error_messages)}
Content: {content}

💡 Common issues:
• Duplicate content (same tweet posted recently)
• Content violates X policies
• Invalid characters or formatting
• Rate limit exceeded

Please modify your content and try again.
            """.strip()
            
        elif response.status_code == 401:
            return f"""
❌ X posting failed: Authentication error

Please check your X API credentials and app permissions:
• X_API_KEY - Your app's API key
• X_API_SECRET - Your app's API secret
• X_ACCESS_TOKEN - Your access token
• X_ACCESS_TOKEN_SECRET - Your access token secret

Make sure your X app has "Read and Write" permissions.

Response: {response.text}
            """.strip()
            
        elif response.status_code == 403:
            return f"""
❌ X posting failed: Forbidden

This could be due to:
• App doesn't have write permissions
• Account suspended or restricted
• Content violates X policies
• App not approved for posting

Please check your X developer account settings.

Response: {response.text}
            """.strip()
            
        elif response.status_code == 429:
            return f"""
❌ X posting failed: Rate limit exceeded

You've reached the posting rate limit. Please wait before posting again.

X rate limits:
• 300 tweets per 3-hour window
• 50 tweets per hour for some endpoints

Try again later.
            """.strip()
            
        else:
            return f"""
❌ X posting failed: HTTP {response.status_code}

Response: {response.text}
Content: {content}

Please check the X API status and try again.
            """.strip()
            
    except requests.exceptions.Timeout:
        return f"""
❌ X posting failed: Request timeout

The X API is taking too long to respond. Please try again.

Content: {content}
        """.strip()
        
    except requests.exceptions.RequestException as e:
        return f"""
❌ X posting failed: Network error

Error: {str(e)}
Content: {content}

Please check your internet connection and try again.
        """.strip()
        
    except Exception as e:
        return f"""
❌ X posting failed: Unexpected error

Error: {str(e)}
Content: {content}

Please try again or contact support if the issue persists.
        """.strip()


@tool
def get_x_account_info() -> str:
    """
    Get information about the connected X account using OAuth 1.0a.
    
    Returns:
        Account information and posting status
    """
    api_key = os.getenv("X_API_KEY")
    api_secret = os.getenv("X_API_SECRET")
    access_token = os.getenv("X_ACCESS_TOKEN")
    access_token_secret = os.getenv("X_ACCESS_TOKEN_SECRET")
    
    if not all([api_key, api_secret, access_token, access_token_secret]):
        return """
❌ X API credentials not configured.

To check account info, please set these environment variables:
• X_API_KEY="your-api-key"
• X_API_SECRET="your-api-secret"
• X_ACCESS_TOKEN="your-access-token"
• X_ACCESS_TOKEN_SECRET="your-access-token-secret"
        """.strip()
    
    try:
        # X API v2 endpoint for user info
        url = "https://api.twitter.com/2/users/me"
        
        # OAuth 1.0a parameters
        oauth_params = {
            "oauth_consumer_key": api_key,
            "oauth_token": access_token,
            "oauth_signature_method": "HMAC-SHA1",
            "oauth_timestamp": str(int(time.time())),
            "oauth_nonce": secrets.token_urlsafe(32),
            "oauth_version": "1.0"
        }
        
        # Generate OAuth signature
        oauth_params["oauth_signature"] = generate_oauth_signature(
            "GET", url, oauth_params, api_secret, access_token_secret
        )
        
        # Create Authorization header
        auth_header = "OAuth " + ", ".join([
            f'{k}="{urllib.parse.quote(str(v), safe="")}"'
            for k, v in sorted(oauth_params.items())
        ])
        
        headers = {
            "Authorization": auth_header
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            user_data = data.get("data", {})
            
            return f"""
✅ X Account Connected

👤 Username: @{user_data.get('username', 'unknown')}
📝 Name: {user_data.get('name', 'unknown')}
🆔 User ID: {user_data.get('id', 'unknown')}

🔗 Profile: https://twitter.com/{user_data.get('username', '')}

✅ Ready to post content to X!
            """.strip()
            
        else:
            return f"""
❌ Unable to fetch X account info

HTTP Status: {response.status_code}
Response: {response.text}

Please check your X API credentials and app permissions.
            """.strip()
            
    except Exception as e:
        return f"""
❌ Error fetching X account info: {str(e)}

Please check your X API configuration.
        """.strip()


# Test function for development
def test_x_posting_tool():
    """Test the X posting tool functionality"""
    print("Testing X posting tool...")
    
    # Test account info
    print("1. Testing account info:")
    result = get_x_account_info()
    print(result)
    print("\n" + "="*50 + "\n")
    
    # Test posting (with a test message)
    print("2. Testing post creation:")
    test_content = "Testing X integration from Strands-Agents SDK! 🤖 #AI #Automation"
    result = post_to_x(test_content)
    print(result)


if __name__ == "__main__":
    test_x_posting_tool()