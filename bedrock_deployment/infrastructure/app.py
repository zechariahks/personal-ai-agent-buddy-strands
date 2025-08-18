#!/usr/bin/env python3
"""
CDK App for Strands Personal AI Agent Bedrock Deployment
"""

import aws_cdk as cdk
from cdk_stack import StrandsPersonalAIAgentStack

app = cdk.App()

# Get environment configuration
account = app.node.try_get_context("account") or "123456789012"  # Replace with your account ID
region = app.node.try_get_context("region") or "us-east-1"

# Create the stack
StrandsPersonalAIAgentStack(
    app, 
    "StrandsPersonalAIAgentStack",
    env=cdk.Environment(account=account, region=region),
    description="Infrastructure for Strands Personal AI Agent with Bedrock AgentCore deployment",
    tags={
        "Framework": "StrandsAgents",
        "Project": "PersonalAIAgent",
        "Environment": "Production",
        "ManagedBy": "CDK"
    }
)

app.synth()