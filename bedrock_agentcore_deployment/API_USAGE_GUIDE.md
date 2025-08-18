# Strands Personal AI Agent - API Usage Guide

This guide shows you how to use the FastAPI endpoints both in the Swagger UI (`/docs`) and with curl commands.

## Available Endpoints

### 1. Health Check Endpoints

#### GET `/` - Basic Health Check
**Swagger UI**: Just click "Try it out" → "Execute"

**curl**:
```bash
curl http://localhost:8000/
```

#### GET `/health` - Detailed Health Check
**Swagger UI**: Just click "Try it out" → "Execute"

**curl**:
```bash
curl http://localhost:8000/health
```

### 2. Main Agent Interaction

#### POST `/invoke` - Main Agent Endpoint
This is the primary endpoint for interacting with your AI agent.

**Swagger UI Input**:
```json
{
  "message": "What's the weather like in New York?",
  "session_id": "my-session-123",
  "context": {
    "user_preference": "detailed analysis"
  }
}
```

**curl**:
```bash
curl -X POST http://localhost:8000/invoke \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What'\''s the weather like in New York?",
    "session_id": "my-session-123",
    "context": {
      "user_preference": "detailed analysis"
    }
  }'
```

**Example Messages to Try**:
- `"What's the weather in San Francisco?"`
- `"Show me my calendar events"`
- `"Post a Bible verse to X"`
- `"Help me decide what to do today"`
- `"Send an email to my team about the meeting"`

### 3. Specialized Capability Endpoints

#### POST `/weather` - Weather Information
**Swagger UI Input**:
```json
{
  "city": "Los Angeles"
}
```

**curl**:
```bash
curl -X POST http://localhost:8000/weather \
  -H "Content-Type: application/json" \
  -d '{"city": "Los Angeles"}'
```

#### POST `/calendar` - Calendar Management
**Swagger UI Input**:
```json
{
  "action": "show today's events"
}
```

**curl**:
```bash
curl -X POST http://localhost:8000/calendar \
  -H "Content-Type: application/json" \
  -d '{"action": "show today'\''s events"}'
```

**Calendar Actions to Try**:
- `"show today's events"`
- `"show this week's schedule"`
- `"create a meeting"`
- `"find free time"`

#### POST `/social` - Social Media Actions
**Swagger UI Input**:
```json
{
  "action": "post bible verse"
}
```

**curl**:
```bash
curl -X POST http://localhost:8000/social \
  -H "Content-Type: application/json" \
  -d '{"action": "post bible verse"}'
```

**Social Actions to Try**:
- `"post bible verse"`
- `"post inspirational quote"`
- `"share weather update"`

### 4. Information Endpoints

#### GET `/capabilities` - List All Capabilities
**Swagger UI**: Just click "Try it out" → "Execute"

**curl**:
```bash
curl http://localhost:8000/capabilities
```

#### GET `/status` - Agent Status
**Swagger UI**: Just click "Try it out" → "Execute"

**curl**:
```bash
curl http://localhost:8000/status
```

## Using Swagger UI (http://localhost:8000/docs)

1. **Navigate to**: `http://localhost:8000/docs`
2. **Find the endpoint** you want to test
3. **Click "Try it out"** button
4. **Fill in the request body** with JSON (see examples above)
5. **Click "Execute"** to send the request
6. **View the response** in the "Response body" section

## Common Request Examples

### Weather Query
```json
{
  "message": "What's the weather in Miami and should I go to the beach?",
  "session_id": "weather-session"
}
```

### Calendar Management
```json
{
  "message": "Show me my meetings for tomorrow and suggest the best time for a 1-hour focus session",
  "session_id": "calendar-session"
}
```

### Social Media Posting
```json
{
  "message": "Post an inspiring Bible verse about perseverance to X",
  "session_id": "social-session"
}
```

### Decision Making
```json
{
  "message": "I have a free afternoon. Based on the weather and my calendar, what should I do?",
  "session_id": "decision-session",
  "context": {
    "location": "San Francisco",
    "interests": ["hiking", "reading", "coding"]
  }
}
```

## Response Format

All endpoints return JSON responses. The main `/invoke` endpoint returns:

```json
{
  "response": "Detailed agent response here...",
  "session_id": "your-session-id",
  "timestamp": "2024-01-15T10:30:00",
  "success": true,
  "metadata": {
    "agent_type": "StrandsEnhancedContextAwareAgent",
    "capabilities": ["weather", "calendar", "social", "email", "decision"],
    "context_memory_size": 5
  }
}
```

## Error Handling

If something goes wrong, you'll get an error response:

```json
{
  "response": "❌ Error processing request: [error details]",
  "session_id": "error-session",
  "timestamp": "2024-01-15T10:30:00",
  "success": false,
  "metadata": {
    "error": "Detailed error message"
  }
}
```

## Tips for Testing

1. **Start Simple**: Try the health check endpoints first
2. **Use Session IDs**: They help track conversations
3. **Check Logs**: Watch the terminal for detailed logs
4. **Try Different Messages**: The agent can handle various requests
5. **Use Context**: Add context for more personalized responses

## Environment Variables Required

Make sure these are set in your `.env` file:
- `OPENAI_API_KEY`
- `WEATHER_API_KEY`
- `X_API_KEY`, `X_API_SECRET`, `X_ACCESS_TOKEN`, `X_ACCESS_TOKEN_SECRET`
- `GOOGLE_CALENDAR_CREDENTIALS_PATH` (optional)

## Troubleshooting

### Agent Not Initialized Error
If you get "Agent not initialized" errors:
1. Check your API keys in `.env`
2. Restart the server: `python app.py`
3. Check the startup logs for errors

### Import Errors
If you get import errors:
1. Run: `python setup_local_env.py`
2. Make sure you're in the right directory
3. Check that all dependencies are installed

### API Key Errors
If tools fail:
1. Verify your API keys are correct
2. Check API quotas/limits
3. Test individual tools first