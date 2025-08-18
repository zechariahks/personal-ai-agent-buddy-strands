# Strands Personal AI Agent - Bedrock AgentCore Deployment

This directory contains the complete deployment setup for your **Strands Personal AI Agent** using Amazon Bedrock AgentCore approach.

## 🏗️ Architecture Overview

```
Amazon Bedrock AgentCore Runtime
├── ECR Container Image
│   ├── FastAPI Server (app.py)
│   ├── Your Working Strands Agents
│   │   ├── StrandsEnhancedContextAwareAgent
│   │   ├── WeatherAgent (with real weather API)
│   │   ├── CalendarAgent (with Google Calendar)
│   │   ├── SocialAgent (with X posting)
│   │   ├── EmailAgent (contextual email)
│   │   └── DecisionAgent (cross-domain reasoning)
│   └── All Your Working Tools
│       ├── weather_tool.py (OpenWeatherMap API)
│       ├── bible_verse_tool.py (Bible API + fallbacks)
│       ├── x_posting_tool.py (X API v2 OAuth)
│       └── google_calendar_tool.py (Google Calendar API)
├── Custom HTTP Interface
│   ├── POST /invoke - Main agent interaction
│   ├── POST /weather - Weather capability
│   ├── POST /calendar - Calendar capability
│   └── POST /social - Social media capability
└── Auto-scaling & Session Isolation
```

## 📁 Files Overview

### Core Deployment Files
- **`app.py`** - FastAPI server that imports and uses your actual working agents
- **`Dockerfile`** - Multi-stage container build that copies all your agent files
- **`deploy.py`** - Complete deployment automation (ECR + AgentCore)
- **`requirements.txt`** - All dependencies for your agents and FastAPI
- **`test_agent_import.py`** - Test script to verify all imports work

### Your Working Agent Files (Copied During Build)
- **`enhanced_context_aware_agent_strands.py`** - Your main multi-agent system
- **`basic_agent_strands.py`** - Base agent class with Strands SDK
- **`weather_tool.py`** - Real weather data with OpenWeatherMap
- **`bible_verse_tool.py`** - Bible verses with multiple API fallbacks
- **`x_posting_tool.py`** - X (Twitter) posting with OAuth 1.0a
- **`google_calendar_tool.py`** - Google Calendar integration

## 🚀 Quick Deployment

### Prerequisites
1. **Docker** installed and running
2. **AWS CLI** configured with appropriate permissions
3. **Python 3.8+** with pip
4. **Your API credentials** set as environment variables

### Setup Local Environment
```bash
cd mcp/agentic-ai/personal-ai-agent-buddy-strands/bedrock_agentcore_deployment

# Install all dependencies
python setup_local_env.py

# Copy .env.example to .env and add your API keys
cp .env.example .env
# Edit .env with your actual API keys
```

### One-Command Deployment
```bash
python deploy.py --region us-east-1
```

This will:
1. ✅ Check all prerequisites
2. 🏗️ Create ECR repository
3. 📁 Copy all your working agent files
4. 🐳 Build Docker image with your agents
5. 📤 Push to ECR
6. 🤖 Generate AgentCore configuration
7. 📚 Create deployment guide

## 🧪 Local Testing

Before deploying, test your agents locally:

### 1. Quick Setup Test
```bash
# Test dependencies and imports
python test_agent_import.py
```

### 2. Start the FastAPI Server
```bash
# Start the server
python app.py

# Server will be available at http://localhost:8000
```

### 3. Test the API
```bash
# Method 1: Use the automated test script
python test_fastapi_app.py

# Method 2: Manual testing
curl http://localhost:8000/health
curl -X POST http://localhost:8000/invoke \
  -H "Content-Type: application/json" \
  -d '{"message": "What'\''s the weather in New York?", "session_id": "test-123"}'

# Method 3: Interactive API docs
# Open http://localhost:8000/docs in your browser
```

### 4. Detailed API Usage Guide
📖 **See [`API_USAGE_GUIDE.md`](API_USAGE_GUIDE.md)** for comprehensive examples including:
- How to use each endpoint in Swagger UI
- Request/response formats with examples
- Common use cases and testing scenarios
- Troubleshooting tips for local development

## 🔧 Available Endpoints

### Main Agent Interaction
- **POST `/invoke`** - Main agent interaction using your enhanced multi-agent system
  ```json
  {
    "message": "What's the weather in Tokyo and should I go hiking?",
    "session_id": "user-123",
    "context": {}
  }
  ```

### Specialized Capabilities
- **POST `/weather`** - Direct weather capability
  ```json
  {"city": "London"}
  ```

- **POST `/calendar`** - Calendar management
  ```json
  {"action": "show events"}
  ```

- **POST `/social`** - Social media actions
  ```json
  {"action": "post bible verse"}
  ```

### System Endpoints
- **GET `/health`** - Detailed health check with agent status
- **GET `/capabilities`** - List all available agent capabilities
- **GET `/status`** - Complete agent system status

## 🤖 Your Agent Capabilities

The deployed system includes all your working capabilities:

### ✅ Weather Analysis
- Real-time weather data from OpenWeatherMap
- Activity impact assessment
- Outdoor suitability scoring
- Weather-based recommendations

### ✅ Google Calendar Integration
- Create, read, update, delete events
- Conflict detection with weather
- Real Google Calendar API integration
- OAuth 2.0 authentication

### ✅ X (Twitter) Integration
- Post Bible verses automatically
- OAuth 1.0a authentication
- Character limit handling
- Error handling and retries

### ✅ Multi-Agent Coordination
- Weather + Calendar conflict analysis
- Cross-domain decision making
- Context memory across interactions
- Specialist agent coordination

### ✅ Bible Verse Service
- Multiple API sources with fallbacks
- Daily verse selection
- Social media formatting
- Inspirational content delivery

## 🔐 Environment Variables

Set these in your AgentCore deployment:

### Required for AI Models
```bash
OPENAI_API_KEY=your-openai-key
# OR
ANTHROPIC_API_KEY=your-anthropic-key
# OR
BEDROCK_MODEL=anthropic.claude-3-sonnet-20240229-v1:0
```

### Required for Weather
```bash
WEATHER_API_KEY=your-openweathermap-key
```

### Required for X (Twitter)
```bash
X_API_KEY=your-x-api-key
X_API_SECRET=your-x-api-secret
X_ACCESS_TOKEN=your-x-access-token
X_ACCESS_TOKEN_SECRET=your-x-access-token-secret
```

### Optional for Google Calendar
```bash
# Google Calendar OAuth credentials will be handled via file-based auth
# Place credentials at ~/.google_calendar_credentials.json
```

## 📊 Monitoring & Scaling

### Health Monitoring
The `/health` endpoint provides comprehensive status:
- Agent initialization status
- Service availability (Weather, X, Calendar)
- Specialist agent count
- Memory usage
- Error states

### Auto-scaling
AgentCore automatically scales based on:
- Request volume
- Response time
- Error rates
- Resource utilization

### Logging
All agent interactions are logged with:
- Session IDs for tracking
- Capability usage metrics
- Error details and stack traces
- Performance timing

## 🔄 Updates & Maintenance

### Updating Your Agents
1. Modify your agent files in the parent directory
2. Run deployment again:
   ```bash
   python deploy.py --region us-east-1
   ```
3. AgentCore will automatically deploy the new version

### Adding New Capabilities
1. Create new tool files following the Strands SDK pattern
2. Add to your enhanced agent's specialist agents
3. Update the Dockerfile to copy new files
4. Redeploy

## 🎯 Testing Your Deployed Agent

### Basic Health Check
```bash
curl https://your-agentcore-endpoint/health
```

### Weather Capability
```bash
curl -X POST https://your-agentcore-endpoint/weather \
  -H "Content-Type: application/json" \
  -d '{"city": "San Francisco"}'
```

### Multi-Agent Interaction
```bash
curl -X POST https://your-agentcore-endpoint/invoke \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What'\''s the weather in New York and do I have any outdoor events that might be affected?",
    "session_id": "user-123"
  }'
```

### Social Media Posting
```bash
curl -X POST https://your-agentcore-endpoint/social \
  -H "Content-Type: application/json" \
  -d '{"action": "post bible verse"}'
```

## 🚨 Troubleshooting

### ECR Login Issues
If you encounter ECR login errors like "400 Bad Request":

1. **Run the diagnostic tool**:
   ```bash
   python debug_ecr_login.py
   ```

2. **Manual ECR login test**:
   ```bash
   aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 600627345285.dkr.ecr.us-east-1.amazonaws.com
   ```

3. **Check Docker daemon**:
   ```bash
   docker info
   ```

4. **Verify AWS credentials**:
   ```bash
   aws sts get-caller-identity
   aws ecr describe-repositories
   ```

### Common Issues

1. **Import Errors**
   - Run `python test_agent_import.py` to verify all imports
   - Check that all agent files are copied correctly

2. **API Key Issues**
   - Verify environment variables are set in AgentCore
   - Check API key validity and permissions

3. **Docker Build Failures**
   - Ensure all parent directory files exist
   - Check Dockerfile COPY commands
   - Make sure Docker daemon is running

4. **Agent Initialization Errors**
   - Check logs for specific error messages
   - Verify model provider credentials

5. **ECR Authentication Failures**
   - Run `python debug_ecr_login.py` for detailed diagnostics
   - Check IAM permissions for ECR operations
   - Ensure AWS CLI is properly configured

### Debug Mode
Set environment variable for detailed logging:
```bash
export STRANDS_DEBUG=true
```

### Quick Fixes

**ECR Login 400 Error**:
```bash
# Method 1: Use AWS CLI helper
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin YOUR_ECR_REGISTRY

# Method 2: Check Docker is running
sudo systemctl start docker  # Linux
# or restart Docker Desktop on Mac/Windows

# Method 3: Clear Docker credentials
docker logout YOUR_ECR_REGISTRY
```

**Permission Denied**:
```bash
# Add user to docker group (Linux)
sudo usermod -aG docker $USER
# Then logout and login again
```

## 📈 Performance Optimization

### Response Time
- Weather API calls: ~200-500ms
- Calendar operations: ~300-800ms
- X posting: ~500-1000ms
- Multi-agent coordination: ~1-3s

### Scaling Recommendations
- **Light usage** (< 100 requests/day): Default settings
- **Medium usage** (< 1000 requests/day): Enable caching
- **Heavy usage** (> 1000 requests/day): Multiple regions

## 🎉 Success!

Your complete Strands Personal AI Agent system is now ready for enterprise deployment on Amazon Bedrock AgentCore! 

The deployment preserves all your working functionality while adding:
- ✅ Enterprise-grade scaling
- ✅ Built-in security and compliance
- ✅ Automatic load balancing
- ✅ Session isolation
- ✅ Comprehensive monitoring
- ✅ Global availability

**Next Steps**: Run the deployment and start using your AI agent at scale! 🚀