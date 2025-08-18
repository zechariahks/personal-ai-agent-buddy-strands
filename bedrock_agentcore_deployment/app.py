#!/usr/bin/env python3
"""
Strands Personal AI Agent - Bedrock AgentCore Custom Agent Implementation
Option B: Custom Agent using FastAPI server for full control
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, Any, Optional
import os
import json
from datetime import datetime

# Import our existing Strands agents and tools (copied into container)
from enhanced_context_aware_agent_strands import StrandsEnhancedContextAwareAgent

class AgentRequest(BaseModel):
    """Request model for agent interactions"""
    message: str
    session_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None

class AgentResponse(BaseModel):
    """Response model for agent interactions"""
    response: str
    session_id: str
    timestamp: str
    success: bool
    metadata: Optional[Dict[str, Any]] = None

# Initialize FastAPI app
app = FastAPI(
    title="Strands Personal AI Agent",
    description="Enhanced Personal AI Agent built with Strands-Agents SDK for Bedrock AgentCore",
    version="2.0.0"
)

# Initialize the Strands agent
strands_agent = None

@app.on_event("startup")
async def startup_event():
    """Initialize the Strands agent on startup"""
    global strands_agent
    try:
        strands_agent = StrandsEnhancedContextAwareAgent("Buddy")
        print("✅ Strands Personal AI Agent initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize Strands agent: {str(e)}")
        raise

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Strands Personal AI Agent",
        "version": "2.0.0",
        "framework": "Strands-Agents SDK",
        "deployment": "Bedrock AgentCore Custom Agent"
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    try:
        # Check if agent is initialized
        if strands_agent is None:
            raise HTTPException(status_code=503, detail="Agent not initialized")
        
        # Check agent services
        service_status = strands_agent.get_service_status()
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "agent_status": "ready",
            "services": service_status,
            "specialist_agents": len(strands_agent.specialist_agents)
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Health check failed: {str(e)}")

@app.post("/invoke", response_model=AgentResponse)
async def invoke_agent(request: AgentRequest):
    """Main agent invocation endpoint"""
    try:
        if strands_agent is None:
            raise HTTPException(status_code=503, detail="Agent not initialized")
        
        # Generate session ID if not provided
        session_id = request.session_id or f"session-{int(datetime.now().timestamp())}"
        
        # Process the request using our enhanced Strands agent
        response = strands_agent.process_request(request.message)
        
        return AgentResponse(
            response=response,
            session_id=session_id,
            timestamp=datetime.now().isoformat(),
            success=True,
            metadata={
                "agent_type": "StrandsEnhancedContextAwareAgent",
                "capabilities": ["weather", "calendar", "social", "email", "decision"],
                "context_memory_size": len(strands_agent.context_memory)
            }
        )
        
    except Exception as e:
        return AgentResponse(
            response=f"❌ Error processing request: {str(e)}",
            session_id=request.session_id or "error-session",
            timestamp=datetime.now().isoformat(),
            success=False,
            metadata={"error": str(e)}
        )

@app.post("/weather")
async def weather_capability(request: Dict[str, Any]):
    """Weather capability endpoint"""
    try:
        if strands_agent is None:
            raise HTTPException(status_code=503, detail="Agent not initialized")
        
        city = request.get("city", "New York")
        weather_query = f"What's the weather in {city}?"
        
        response = strands_agent.process_request(weather_query)
        
        return {
            "success": True,
            "response": response,
            "capability": "weather",
            "city": city,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Weather capability error: {str(e)}")

@app.post("/calendar")
async def calendar_capability(request: Dict[str, Any]):
    """Calendar capability endpoint"""
    try:
        if strands_agent is None:
            raise HTTPException(status_code=503, detail="Agent not initialized")
        
        action = request.get("action", "show events")
        calendar_query = f"Calendar: {action}"
        
        response = strands_agent.process_request(calendar_query)
        
        return {
            "success": True,
            "response": response,
            "capability": "calendar",
            "action": action,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Calendar capability error: {str(e)}")

@app.post("/social")
async def social_capability(request: Dict[str, Any]):
    """Social media capability endpoint"""
    try:
        if strands_agent is None:
            raise HTTPException(status_code=503, detail="Agent not initialized")
        
        action = request.get("action", "post bible verse")
        social_query = f"Social media: {action}"
        
        response = strands_agent.process_request(social_query)
        
        return {
            "success": True,
            "response": response,
            "capability": "social",
            "action": action,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Social capability error: {str(e)}")

@app.get("/capabilities")
async def list_capabilities():
    """List available agent capabilities"""
    if strands_agent is None:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    return {
        "capabilities": [
            {
                "name": "weather",
                "description": "Weather analysis with activity impact assessment",
                "endpoints": ["/weather"],
                "agent": "WeatherAgent"
            },
            {
                "name": "calendar",
                "description": "Google Calendar integration and event management",
                "endpoints": ["/calendar"],
                "agent": "CalendarAgent"
            },
            {
                "name": "social",
                "description": "X (Twitter) posting and social media management",
                "endpoints": ["/social"],
                "agent": "SocialMediaAgent"
            },
            {
                "name": "email",
                "description": "Contextual email composition and management",
                "endpoints": ["/invoke"],
                "agent": "EmailAgent"
            },
            {
                "name": "decision",
                "description": "Cross-domain reasoning and recommendations",
                "endpoints": ["/invoke"],
                "agent": "DecisionAgent"
            }
        ],
        "specialist_agents": len(strands_agent.specialist_agents) if strands_agent else 0,
        "framework": "Strands-Agents SDK"
    }

@app.get("/status")
async def agent_status():
    """Get detailed agent status"""
    if strands_agent is None:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    return {
        "agent_name": strands_agent.name,
        "agent_type": "StrandsEnhancedContextAwareAgent",
        "framework": "Strands-Agents SDK",
        "deployment": "Bedrock AgentCore Custom Agent",
        "services": strands_agent.get_service_status(),
        "specialist_agents": {
            name: agent.name for name, agent in strands_agent.specialist_agents.items()
        },
        "context_memory": len(strands_agent.context_memory),
        "decision_history": len(strands_agent.decision_history),
        "timestamp": datetime.now().isoformat()
    }

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return JSONResponse(
        status_code=404,
        content={
            "error": "Endpoint not found",
            "message": "This endpoint is not available on the Strands Personal AI Agent",
            "available_endpoints": ["/", "/health", "/invoke", "/weather", "/calendar", "/social", "/capabilities", "/status"],
            "requested_path": str(request.url.path)
        }
    )

@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An error occurred while processing your request",
            "timestamp": datetime.now().isoformat()
        }
    )

if __name__ == "__main__":
    import uvicorn
    
    # Get port from environment or default to 8000
    port = int(os.getenv("PORT", 8000))
    
    print(f"🚀 Starting Strands Personal AI Agent on port {port}")
    print("📋 Available endpoints:")
    print("   • GET  /          - Health check")
    print("   • GET  /health    - Detailed health check")
    print("   • POST /invoke    - Main agent interaction")
    print("   • POST /weather   - Weather capability")
    print("   • POST /calendar  - Calendar capability")
    print("   • POST /social    - Social media capability")
    print("   • GET  /capabilities - List all capabilities")
    print("   • GET  /status    - Agent status")
    
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=port,
        log_level="info",
        access_log=True
    )