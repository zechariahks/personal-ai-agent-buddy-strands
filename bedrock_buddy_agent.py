from bedrock_agentcore import BedrockAgentCoreApp
from strands import Agent

from pydantic import BaseModel
from typing import Dict, Any, Optional
import os
import json
from datetime import datetime, timezone

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

app = BedrockAgentCoreApp()

agent = StrandsEnhancedContextAwareAgent("Buddy")
print("✅ Strands Personal AI Agent initialized successfully")
print(f"🔧 Agent has {len(agent.specialist_agents)} specialist agents")


@app.entrypoint
def strands_agent_bedrock(payload):
    """
    Invoke the agent with a payload
    """
    user_input = payload.get("message")
    print("User input:", user_input)
    response = agent.process_request(user_input)
    return response

if __name__ == "__main__":
    app.run()