#!/usr/bin/env python3
"""
Amazon Bedrock AgentCore Deployment Script for Strands-Agents
Deploy the Enhanced Personal AI Agent to AWS Bedrock AgentCore
"""

import boto3
import json
import os
import time
from datetime import datetime
from typing import Dict, Any, List

class StrandsBedrockAgentDeployer:
    """Deploy Strands-Agents to Amazon Bedrock AgentCore"""
    
    def __init__(self, region='us-east-1'):
        self.region = region
        self.bedrock_agent = boto3.client('bedrock-agent', region_name=region)
        self.iam = boto3.client('iam', region_name=region)
        self.lambda_client = boto3.client('lambda', region_name=region)
        self.account_id = boto3.client('sts').get_caller_identity()['Account']
        
        # Agent configuration
        self.agent_name = 'StrandsPersonalAIAgent'
        self.agent_description = '''Enhanced Personal AI Agent built with Strands-Agents SDK.
        
        Multi-agent system with specialized capabilities:
        - Weather analysis and impact assessment
        - Google Calendar integration and event management
        - X (Twitter) posting with Bible verse sharing
        - Intelligent decision making and recommendations
        - Cross-domain contextual reasoning
        
        Built using Strands-Agents framework for modular, scalable AI assistance.'''
        
        self.foundation_model = 'anthropic.claude-3-sonnet-20240229-v1:0'
        
    def create_agent_role(self) -> str:
        """Create IAM role for Bedrock Agent"""
        role_name = f'{self.agent_name}Role'
        
        trust_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {
                        "Service": "bedrock.amazonaws.com"
                    },
                    "Action": "sts:AssumeRole"
                }
            ]
        }
        
        permissions_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": [
                        "bedrock:InvokeModel",
                        "bedrock:InvokeAgent"
                    ],
                    "Resource": "*"
                },
                {
                    "Effect": "Allow",
                    "Action": [
                        "lambda:InvokeFunction"
                    ],
                    "Resource": [
                        f"arn:aws:lambda:{self.region}:{self.account_id}:function:strands-*"
                    ]
                },
                {
                    "Effect": "Allow",
                    "Action": [
                        "logs:CreateLogGroup",
                        "logs:CreateLogStream",
                        "logs:PutLogEvents"
                    ],
                    "Resource": "*"
                }
            ]
        }
        
        try:
            # Create role
            self.iam.create_role(
                RoleName=role_name,
                AssumeRolePolicyDocument=json.dumps(trust_policy),
                Description=f'IAM role for {self.agent_name} Bedrock Agent'
            )
            
            # Attach inline policy
            self.iam.put_role_policy(
                RoleName=role_name,
                PolicyName=f'{role_name}Policy',
                PolicyDocument=json.dumps(permissions_policy)
            )
            
            role_arn = f'arn:aws:iam::{self.account_id}:role/{role_name}'
            print(f"✅ Created IAM role: {role_arn}")
            
            # Wait for role to be available
            time.sleep(10)
            
            return role_arn
            
        except self.iam.exceptions.EntityAlreadyExistsException:
            role_arn = f'arn:aws:iam::{self.account_id}:role/{role_name}'
            print(f"✅ Using existing IAM role: {role_arn}")
            return role_arn
    
    def create_bedrock_agent(self, role_arn: str) -> str:
        """Create the main Bedrock Agent"""
        
        instruction = """You are an enhanced personal AI assistant built with Strands-Agents SDK patterns.

Core Capabilities:
- Weather analysis with activity impact assessment
- Google Calendar integration for event management
- X (Twitter) posting with Bible verse sharing
- Intelligent decision making across multiple domains
- Contextual reasoning and recommendations

Behavioral Guidelines:
1. Use appropriate action groups for specific tasks
2. Provide comprehensive, contextual responses
3. Consider multiple factors when making recommendations
4. Maintain conversation context and learning
5. Handle errors gracefully with helpful guidance

Available Action Groups:
- WeatherCapability: Weather analysis and recommendations
- CalendarCapability: Google Calendar event management
- SocialCapability: X posting and content creation
- BibleVerseCapability: Daily inspiration and verse sharing

Always route requests to the most appropriate capability and provide intelligent, actionable responses."""

        try:
            response = self.bedrock_agent.create_agent(
                agentName=self.agent_name,
                description=self.agent_description,
                foundationModel=self.foundation_model,
                instruction=instruction,
                idleSessionTTLInSeconds=1800,  # 30 minutes
                agentResourceRoleArn=role_arn,
                tags={
                    'Framework': 'StrandsAgents',
                    'Environment': 'Production',
                    'Application': 'PersonalAIAgent',
                    'Version': '2.0',
                    'Architecture': 'MultiAgent'
                }
            )
            
            agent_id = response['agent']['agentId']
            print(f"✅ Created Bedrock Agent: {agent_id}")
            return agent_id
            
        except Exception as e:
            print(f"❌ Error creating Bedrock Agent: {str(e)}")
            raise
    
    def create_action_groups(self, agent_id: str) -> Dict[str, str]:
        """Create Action Groups for each Strands capability"""
        action_groups = {}
        
        # Weather Capability Action Group
        weather_schema = {
            "openapi": "3.0.0",
            "info": {
                "title": "Strands Weather Capability API",
                "version": "2.0.0",
                "description": "Weather analysis with activity impact assessment"
            },
            "paths": {
                "/weather": {
                    "post": {
                        "description": "Get weather information with impact analysis",
                        "operationId": "getWeatherWithImpact",
                        "requestBody": {
                            "required": True,
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "city": {
                                                "type": "string",
                                                "description": "City name for weather information"
                                            }
                                        },
                                        "required": ["city"]
                                    }
                                }
                            }
                        },
                        "responses": {
                            "200": {
                                "description": "Weather information with impact analysis",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "type": "object",
                                            "properties": {
                                                "success": {"type": "boolean"},
                                                "weather_data": {"type": "object"},
                                                "impact_analysis": {"type": "object"},
                                                "recommendations": {"type": "array"}
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
        
        weather_action_group = self.bedrock_agent.create_agent_action_group(
            agentId=agent_id,
            agentVersion='DRAFT',
            actionGroupName='WeatherCapability',
            description='Weather analysis with activity impact assessment - Strands SDK pattern',
            actionGroupExecutor={
                'lambda': f'arn:aws:lambda:{self.region}:{self.account_id}:function:strands-weather-capability'
            },
            apiSchema={
                'payload': json.dumps(weather_schema)
            }
        )
        action_groups['weather'] = weather_action_group['actionGroup']['actionGroupId']
        
        # Calendar Capability Action Group
        calendar_schema = {
            "openapi": "3.0.0",
            "info": {
                "title": "Strands Calendar Capability API",
                "version": "2.0.0",
                "description": "Google Calendar integration with intelligent scheduling"
            },
            "paths": {
                "/calendar/events": {
                    "get": {
                        "description": "List upcoming calendar events",
                        "operationId": "listCalendarEvents",
                        "parameters": [
                            {
                                "name": "days",
                                "in": "query",
                                "schema": {"type": "integer", "default": 7},
                                "description": "Number of days to look ahead"
                            }
                        ],
                        "responses": {"200": {"description": "List of events"}}
                    },
                    "post": {
                        "description": "Create calendar event",
                        "operationId": "createCalendarEvent",
                        "requestBody": {
                            "required": True,
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "title": {"type": "string"},
                                            "start_time": {"type": "string"},
                                            "end_time": {"type": "string"},
                                            "description": {"type": "string"},
                                            "location": {"type": "string"}
                                        },
                                        "required": ["title", "start_time", "end_time"]
                                    }
                                }
                            }
                        },
                        "responses": {"200": {"description": "Event created"}}
                    }
                }
            }
        }
        
        calendar_action_group = self.bedrock_agent.create_agent_action_group(
            agentId=agent_id,
            agentVersion='DRAFT',
            actionGroupName='CalendarCapability',
            description='Google Calendar integration with intelligent scheduling',
            actionGroupExecutor={
                'lambda': f'arn:aws:lambda:{self.region}:{self.account_id}:function:strands-calendar-capability'
            },
            apiSchema={
                'payload': json.dumps(calendar_schema)
            }
        )
        action_groups['calendar'] = calendar_action_group['actionGroup']['actionGroupId']
        
        # Social Media Capability Action Group
        social_schema = {
            "openapi": "3.0.0",
            "info": {
                "title": "Strands Social Media Capability API",
                "version": "2.0.0",
                "description": "X (Twitter) posting and social media management"
            },
            "paths": {
                "/social/post": {
                    "post": {
                        "description": "Post content to X (Twitter)",
                        "operationId": "postToX",
                        "requestBody": {
                            "required": True,
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "content": {"type": "string"},
                                            "type": {"type": "string", "enum": ["bible_verse", "custom"]}
                                        },
                                        "required": ["content"]
                                    }
                                }
                            }
                        },
                        "responses": {"200": {"description": "Content posted"}}
                    }
                },
                "/social/bible-verse": {
                    "post": {
                        "description": "Get and post daily Bible verse",
                        "operationId": "postBibleVerse",
                        "responses": {"200": {"description": "Bible verse posted"}}
                    }
                },
                "/social/status": {
                    "get": {
                        "description": "Check X account status",
                        "operationId": "checkXStatus",
                        "responses": {"200": {"description": "Account status"}}
                    }
                }
            }
        }
        
        social_action_group = self.bedrock_agent.create_agent_action_group(
            agentId=agent_id,
            agentVersion='DRAFT',
            actionGroupName='SocialCapability',
            description='X (Twitter) posting and social media management',
            actionGroupExecutor={
                'lambda': f'arn:aws:lambda:{self.region}:{self.account_id}:function:strands-social-capability'
            },
            apiSchema={
                'payload': json.dumps(social_schema)
            }
        )
        action_groups['social'] = social_action_group['actionGroup']['actionGroupId']
        
        print("✅ Created Action Groups:")
        for name, group_id in action_groups.items():
            print(f"   - {name.title()}Capability: {group_id}")
        
        return action_groups
    
    def prepare_and_create_alias(self, agent_id: str) -> str:
        """Prepare agent and create production alias"""
        try:
            # Prepare the agent
            print("⏳ Preparing Bedrock Agent...")
            self.bedrock_agent.prepare_agent(agentId=agent_id)
            
            # Wait for preparation to complete
            max_wait_time = 300  # 5 minutes
            wait_time = 0
            
            while wait_time < max_wait_time:
                agent_status = self.bedrock_agent.get_agent(agentId=agent_id)
                status = agent_status['agent']['agentStatus']
                
                if status == 'PREPARED':
                    print("✅ Agent prepared successfully")
                    break
                elif status == 'FAILED':
                    print("❌ Agent preparation failed")
                    return None
                else:
                    print(f"⏳ Agent status: {status}")
                    time.sleep(10)
                    wait_time += 10
            
            if wait_time >= max_wait_time:
                print("❌ Agent preparation timed out")
                return None
            
            # Create production alias
            alias_response = self.bedrock_agent.create_agent_alias(
                agentId=agent_id,
                aliasName='Production',
                description='Production alias for Strands Personal AI Agent',
                tags={
                    'Environment': 'Production',
                    'Framework': 'StrandsAgents'
                }
            )
            
            alias_id = alias_response['agentAlias']['agentAliasId']
            print(f"✅ Created production alias: {alias_id}")
            
            return alias_id
            
        except Exception as e:
            print(f"❌ Error preparing agent or creating alias: {str(e)}")
            return None
    
    def deploy_complete_agent(self) -> Dict[str, str]:
        """Deploy the complete Strands agent to Bedrock AgentCore"""
        print("🚀 Deploying Strands Personal AI Agent to Amazon Bedrock AgentCore...")
        print("=" * 80)
        
        try:
            # Step 1: Create IAM role
            print("\n📋 Step 1: Creating IAM role...")
            role_arn = self.create_agent_role()
            
            # Step 2: Create Bedrock Agent
            print("\n🤖 Step 2: Creating Bedrock Agent...")
            agent_id = self.create_bedrock_agent(role_arn)
            
            # Step 3: Create Action Groups
            print("\n⚙️ Step 3: Creating Action Groups...")
            action_groups = self.create_action_groups(agent_id)
            
            # Step 4: Prepare and create alias
            print("\n🔧 Step 4: Preparing agent and creating alias...")
            alias_id = self.prepare_and_create_alias(agent_id)
            
            if not alias_id:
                print("❌ Failed to create production alias")
                return None
            
            # Deployment summary
            deployment_info = {
                'agent_id': agent_id,
                'alias_id': alias_id,
                'role_arn': role_arn,
                'action_groups': action_groups,
                'region': self.region,
                'foundation_model': self.foundation_model
            }
            
            print("\n🎉 Strands Agent Deployment Complete!")
            print("=" * 80)
            print(f"Agent ID: {agent_id}")
            print(f"Alias ID: {alias_id}")
            print(f"Region: {self.region}")
            print(f"Foundation Model: {self.foundation_model}")
            print(f"Action Groups: {len(action_groups)} capabilities")
            print("\n📝 Next Steps:")
            print("1. Deploy Lambda functions for each capability")
            print("2. Test agent functionality")
            print("3. Configure monitoring and logging")
            
            return deployment_info
            
        except Exception as e:
            print(f"❌ Deployment failed: {str(e)}")
            raise

def main():
    """Main deployment function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Deploy Strands Personal AI Agent to Bedrock AgentCore')
    parser.add_argument('--region', default='us-east-1', help='AWS region for deployment')
    parser.add_argument('--profile', help='AWS profile to use')
    
    args = parser.parse_args()
    
    # Set AWS profile if specified
    if args.profile:
        os.environ['AWS_PROFILE'] = args.profile
    
    # Deploy agent
    deployer = StrandsBedrockAgentDeployer(region=args.region)
    deployment_info = deployer.deploy_complete_agent()
    
    if deployment_info:
        # Save deployment info
        with open('bedrock_deployment_info.json', 'w') as f:
            json.dump(deployment_info, f, indent=2)
        
        print(f"\n💾 Deployment info saved to: bedrock_deployment_info.json")
    
    return deployment_info

if __name__ == "__main__":
    main()