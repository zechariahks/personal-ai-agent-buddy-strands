# 🚀 Complete Setup Guide for Enhanced Personal AI Agent

This guide provides step-by-step instructions for setting up all the enhanced features including X (Twitter) posting, Google Calendar integration, and Bible verse functionality.

## 📋 Prerequisites

- Python 3.8 or higher
- pip package manager
- Internet connection
- Developer accounts for X and Google (optional but recommended)

## 🔧 Installation

### 1. Install Dependencies

```bash
# Navigate to the project directory
cd personal-ai-agent-buddy-strands

# Install all required packages
pip install -r requirements.txt
```

### 2. Install Google Calendar Dependencies

If you encounter issues with Google Calendar integration, install the packages manually:

```bash
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

## 🐦 X (Twitter) API Setup

### Step 1: Create X Developer Account

1. Go to [Twitter Developer Portal](https://developer.twitter.com/)
2. Sign in with your Twitter account
3. Apply for a developer account (if you don't have one)
4. Wait for approval (usually instant for basic access)

### Step 2: Create a New App

1. In the Developer Portal, click "Create App"
2. Fill in the app details:
   - **App Name**: "Personal AI Agent" (or your preferred name)
   - **Description**: "AI agent for personal automation and social media posting"
   - **Website URL**: `https://example.com` (can be placeholder)
   - **Use Case**: Select "Making a bot"

### Step 3: Configure App Permissions

1. Go to your app's settings
2. Click on "App permissions"
3. Change from "Read" to "Read and Write"
4. Save changes

### Step 4: Generate API Keys

1. Go to "Keys and Tokens" tab
2. Generate/Regenerate:
   - **API Key** (Consumer Key)
   - **API Secret** (Consumer Secret)
   - **Access Token**
   - **Access Token Secret**

### Step 5: Set Environment Variables

```bash
# Add these to your environment or .env file
export X_API_KEY="your-api-key-here"
export X_API_SECRET="your-api-secret-here"
export X_ACCESS_TOKEN="your-access-token-here"
export X_ACCESS_TOKEN_SECRET="your-access-token-secret-here"
```

### Troubleshooting X API Issues

**401 Unauthorized Error:**
- Verify all 4 credentials are set correctly
- Ensure your app has "Read and Write" permissions
- Check that your access tokens are generated AFTER setting write permissions
- Regenerate access tokens if permissions were changed

**403 Forbidden Error:**
- Your app might need approval for posting
- Check if your Twitter account is in good standing
- Verify your app complies with Twitter's developer policy

## 📅 Google Calendar API Setup

### Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Name it "Personal AI Agent" or similar

### Step 2: Enable Google Calendar API

1. In the Cloud Console, go to "APIs & Services" > "Library"
2. Search for "Google Calendar API"
3. Click on it and press "Enable"

### Step 3: Create OAuth 2.0 Credentials

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth client ID"
3. If prompted, configure the OAuth consent screen:
   - Choose "External" user type
   - Fill in required fields (app name, user support email, developer email)
   - Add your email to test users
4. For Application type, choose "Desktop application"
5. Name it "Personal AI Agent Desktop"
6. Click "Create"

### Step 4: Download Credentials

1. Click the download button next to your OAuth client
2. Save the file as `~/.google_calendar_credentials.json` in your home directory
3. The file should look like this:

```json
{
  "installed": {
    "client_id": "your-client-id.googleusercontent.com",
    "project_id": "your-project-id",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_secret": "your-client-secret",
    "redirect_uris": ["http://localhost"]
  }
}
```

### Step 5: First-Time Authentication

1. Run the agent for the first time
2. When you use a calendar feature, it will open a browser window
3. Sign in to your Google account
4. Grant permissions to the app
5. The authentication token will be saved automatically

### File Locations

- **Credentials**: `~/.google_calendar_credentials.json`
- **Token**: `~/.google_calendar_token.json` (auto-generated)

### Troubleshooting Google Calendar Issues

**"Google Calendar integration not available" Error:**
- Install required packages: `pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client`
- Verify credentials file exists at `~/.google_calendar_credentials.json`

**Authentication Errors:**
- Delete `~/.google_calendar_token.json` and re-authenticate
- Check that your Google Cloud project has Calendar API enabled
- Verify your OAuth consent screen is configured

## 📖 Bible Verse API

No setup required! The Bible verse functionality works out of the box with:
- Free Bible API services
- Fallback to curated verses if APIs are unavailable
- Multiple translation support

## 🌤️ Weather API (Optional)

For enhanced weather features:

```bash
# Get a free API key from OpenWeatherMap
export OPENWEATHER_API_KEY="your-openweathermap-key"
export DEFAULT_CITY="Your City"
```

1. Go to [OpenWeatherMap](https://openweathermap.org/api)
2. Sign up for a free account
3. Get your API key from the dashboard

## 🧪 Testing Your Setup

### Test X Integration

```bash
cd personal-ai-agent-buddy-strands
python3 -c "
from x_posting_tool import get_x_account_info
print(get_x_account_info())
"
```

### Test Google Calendar

```bash
python3 -c "
from google_calendar_tool import get_calendar_events
print(get_calendar_events(7))
"
```

### Test Bible Verses

```bash
python3 -c "
from bible_verse_tool import get_daily_bible_verse
print(get_daily_bible_verse())
"
```

### Test Complete System

```bash
python3 enhanced_context_aware_agent_strands.py
```

Then try these commands:
- "Check X status"
- "Show my events"
- "Post a Bible verse"

## 🔐 Environment Variables Summary

Create a `.env` file or set these environment variables:

```bash
# AI Model Provider (choose one)
OPENAI_API_KEY="sk-your-openai-key"
# OR
ANTHROPIC_API_KEY="your-anthropic-key"
# OR configure AWS credentials for Bedrock

# X (Twitter) Integration
X_API_KEY="your-api-key"
X_API_SECRET="your-api-secret"
X_ACCESS_TOKEN="your-access-token"
X_ACCESS_TOKEN_SECRET="your-access-token-secret"

# Weather (Optional)
OPENWEATHER_API_KEY="your-openweathermap-key"
DEFAULT_CITY="Your City"

# Email (Optional)
GMAIL_EMAIL="your-email@gmail.com"
GMAIL_APP_PASSWORD="your-app-password"
```

## 📁 File Structure After Setup

```
personal-ai-agent-buddy-strands/
├── enhanced_context_aware_agent_strands.py
├── bible_verse_tool.py
├── x_posting_tool.py
├── google_calendar_tool.py
├── requirements.txt
└── ~/.google_calendar_credentials.json (in home directory)
└── ~/.google_calendar_token.json (auto-generated)
```

## 🎯 Usage Examples

### Post a Bible Verse to X

```
You: Post a Bible verse
Agent: [Fetches verse, formats for X, posts automatically]
```

### Check Calendar Events

```
You: Show my events
Agent: [Displays upcoming Google Calendar events]
```

### Create Calendar Event

```
You: Create event "Team Meeting" from "2024-01-15T10:00:00" to "2024-01-15T11:00:00"
Agent: [Creates event in Google Calendar]
```

## 🆘 Common Issues and Solutions

### Issue: "Module not found" errors
**Solution**: Run `pip install -r requirements.txt`

### Issue: X posting returns 401 error
**Solution**: 
1. Verify all 4 X API credentials are set
2. Ensure app has "Read and Write" permissions
3. Regenerate access tokens after changing permissions

### Issue: Google Calendar not working
**Solution**:
1. Install Google packages: `pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client`
2. Verify credentials file exists at `~/.google_calendar_credentials.json`
3. Delete token file and re-authenticate if needed

### Issue: Bible verses not loading
**Solution**: Check internet connection (uses free APIs, no setup required)

## 🎉 You're All Set!

Once everything is configured, you'll have a fully functional AI agent with:
- ✅ X (Twitter) posting capabilities
- ✅ Google Calendar integration
- ✅ Daily Bible verse sharing
- ✅ Multi-agent coordination
- ✅ Weather analysis
- ✅ Intelligent decision making

Enjoy your enhanced Personal AI Agent! 🚀