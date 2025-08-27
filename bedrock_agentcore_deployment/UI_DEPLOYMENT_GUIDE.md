# Strands Agent UI Deployment Guide

This guide shows you how to deploy a web UI on top of your Bedrock AgentCore deployed agents.

## Architecture Overview

```
User Browser
    ↓
React UI (S3 + CloudFront OR ECS)
    ↓
Amazon Bedrock AgentCore Runtime
    ↓
Your Strands Agents (FastAPI + ECR)
```

## Prerequisites

1. **Node.js 18+** installed
2. **AWS CLI** configured
3. **Docker** (for ECS deployment)
4. **Your AgentCore endpoint** URL

## Quick Start

### 1. Navigate to UI Directory
```bash
cd ui/
```

### 2. Install Dependencies
```bash
npm install
```

### 3. Test Locally
```bash
# Set your agent endpoint
export REACT_APP_AGENT_ENDPOINT="https://your-agentcore-endpoint"

# Start development server
npm start
```

Visit `http://localhost:3000` to test the UI locally.

## Deployment Options

### Option A: S3 + CloudFront (Recommended)

**Pros**: Cost-effective, fast global delivery, easy to manage
**Cons**: Static hosting only

```bash
# Deploy to S3
python deploy-ui.py --agent-endpoint "https://your-agentcore-endpoint" --type s3

# Optional: specify custom bucket name
python deploy-ui.py --agent-endpoint "https://your-agentcore-endpoint" --type s3 --bucket my-custom-bucket
```

### Option B: ECS Container

**Pros**: More control, can handle server-side logic
**Cons**: Higher cost, more complex

```bash
# Deploy to ECS
python deploy-ui.py --agent-endpoint "https://your-agentcore-endpoint" --type ecs
```

## UI Features

### 🎯 Main Chat Interface
- Real-time conversation with your agents
- Session management
- Message history
- Typing indicators
- Markdown support for agent responses

### 📊 Agent Status Panel
- Real-time agent health monitoring
- Specialist agent status
- Context memory tracking
- Service availability

### 🚀 Capability Testing
- Direct capability testing
- Quick action buttons
- Weather queries
- Calendar operations
- Social media actions

### 🔧 Configuration
- Dynamic endpoint configuration
- Connection status
- Error handling

## Environment Variables

Set these for your deployment:

```bash
# Required
REACT_APP_AGENT_ENDPOINT=https://your-agentcore-endpoint

# Optional
REACT_APP_APP_NAME="My AI Agent"
REACT_APP_THEME_COLOR="#667eea"
```

## Customization

### 1. Branding
Edit `src/App.js` to change:
- App title and description
- Color scheme
- Logo/icons

### 2. Quick Actions
Modify `src/components/ChatInterface.js`:
```javascript
const quickActions = [
  "Your custom action 1",
  "Your custom action 2",
  // Add more...
];
```

### 3. Capabilities
Update `src/components/CapabilityPanel.js` to add new capability tests.

## Security Considerations

### 1. CORS Configuration
Ensure your AgentCore endpoint allows requests from your UI domain:

```python
# In your FastAPI app
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-ui-domain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 2. Authentication (Optional)
For production, consider adding authentication:

```javascript
// Add to src/App.js
const [authToken, setAuthToken] = useState(null);

// Include in API calls
axios.defaults.headers.common['Authorization'] = `Bearer ${authToken}`;
```

## Monitoring & Analytics

### 1. CloudWatch Integration
The UI automatically logs errors and performance metrics.

### 2. User Analytics
Add Google Analytics or similar:

```html
<!-- In public/index.html -->
<script async src="https://www.googletagmanager.com/gtag/js?id=GA_MEASUREMENT_ID"></script>
```

## Troubleshooting

### Common Issues

1. **CORS Errors**
   - Check AgentCore CORS configuration
   - Verify endpoint URL is correct

2. **Build Failures**
   - Ensure Node.js 18+ is installed
   - Clear npm cache: `npm cache clean --force`

3. **Deployment Errors**
   - Check AWS credentials
   - Verify IAM permissions for S3/ECS

### Debug Mode
```bash
# Enable debug logging
export REACT_APP_DEBUG=true
npm start
```

## Production Checklist

- [ ] Set production agent endpoint
- [ ] Configure CORS properly
- [ ] Enable HTTPS
- [ ] Set up monitoring
- [ ] Test all capabilities
- [ ] Configure error tracking
- [ ] Set up backup/recovery

## Cost Optimization

### S3 Deployment
- Use CloudFront for caching
- Enable gzip compression
- Set appropriate cache headers

### ECS Deployment
- Use Fargate Spot instances
- Configure auto-scaling
- Monitor resource usage

## Next Steps

1. **Custom Themes**: Create multiple UI themes
2. **Mobile App**: Convert to React Native
3. **Voice Interface**: Add speech recognition
4. **Multi-language**: Internationalization support
5. **Advanced Analytics**: Custom dashboards

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review AWS CloudWatch logs
3. Test individual components
4. Verify agent endpoint connectivity

---

Your Strands AI Agent UI is now ready for production use! 🎉