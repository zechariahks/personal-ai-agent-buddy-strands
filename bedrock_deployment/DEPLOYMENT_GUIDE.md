# 🚀 Strands Personal AI Agent - AWS Bedrock AgentCore Deployment Guide

This guide walks you through deploying your enhanced Personal AI Agent to Amazon Bedrock AgentCore using the Strands-Agents framework.

## 📋 Prerequisites

### 1. AWS Account Setup
- AWS account with appropriate permissions
- AWS CLI installed and configured
- AWS CDK installed (`npm install -g aws-cdk`)

### 2. Required Permissions
Your AWS user/role needs permissions for:
- Amazon Bedrock (Agent creation and management)
- AWS Lambda (Function creation and management)
- Amazon DynamoDB (Table creation and management)
- AWS Secrets Manager (Secret creation and management)
- AWS IAM (Role and policy management)
- AWS CloudFormation (Stack management)

### 3. API Credentials (Required for full functionality)
- **X (Twitter) API**: Developer account with API keys
- **Google Calendar API**: OAuth 2.0 credentials
- **OpenWeatherMap API**: Free API key (optional)

## 🏗️ Deployment Architecture

The deployment creates:

```
AWS Bedrock AgentCore
├── Bedrock Agent (StrandsPersonalAIAgent)
│   ├── WeatherCapability Action Group
│   ├── CalendarCapability Action Group
│   └── SocialCapability Action Group
├── Lambda Functions
│   ├── strands-weather-capability
│   ├── strands-calendar-capability
│   └── strands-social-capability
├── DynamoDB Tables
│   ├── strands-weather-analysis
│   └── strands-conversation-history
├── Secrets Manager
│   ├── strands-agent/x-credentials
│   ├── strands-agent/google-credentials
│   └── strands-agent/weather-api
└── CloudWatch Monitoring
    ├── Dashboard
    └── Alarms
```

## 🚀 Quick Deployment

### Option 1: Automated Deployment (Recommended)

```bash
# Clone or navigate to the deployment directory
cd bedrock_deployment

# Run the complete deployment script
python deploy.py --region us-east-1

# Or with a specific AWS profile
python deploy.py --region us-east-1 --profile my-aws-profile
```

The automated script will:
1. ✅ Check prerequisites
2. 🏗️ Deploy infrastructure with CDK
3. 🤖 Create Bedrock Agent with Action Groups
4. 🔐 Set up Lambda permissions
5. 📊 Configure monitoring
6. 🧪 Run basic tests

### Option 2: Manual Step-by-Step Deployment

#### Step 1: Deploy Infrastructure
```bash
cd infrastructure
pip install -r requirements.txt
cdk bootstrap
cdk deploy --require-approval never
```

#### Step 2: Deploy Bedrock Agent
```bash
cd ..
python bedrock_agent_setup.py --region us-east-1
```

#### Step 3: Configure API Credentials
See the [API Configuration](#-api-configuration) section below.

## 🔐 API Configuration

After deployment, configure your API credentials in AWS Secrets Manager:

### X (Twitter) API Configuration

1. Go to AWS Secrets Manager console
2. Find secret: `strands-agent/x-credentials`
3. Update with your X API credentials:

```json
{
  "api_key": "your-x-api-key",
  "api_secret": "your-x-api-secret",
  "access_token": "your-x-access-token",
  "access_token_secret": "your-x-access-token-secret"
}
```

### Google Calendar API Configuration

1. Find secret: `strands-agent/google-credentials`
2. Update with your Google OAuth credentials:

```json
{
  "token": "your-oauth-token",
  "refresh_token": "your-refresh-token",
  "token_uri": "https://oauth2.googleapis.com/token",
  "client_id": "your-client-id.googleusercontent.com",
  "client_secret": "your-client-secret"
}
```

### Weather API Configuration

1. Find secret: `strands-agent/weather-api`
2. Update with your OpenWeatherMap API key:

```json
{
  "api_key": "your-openweathermap-api-key",
  "default_city": "New York"
}
```

## 🧪 Testing Your Deployment

### 1. AWS Console Testing

1. Go to Amazon Bedrock > Agents
2. Find your agent: `StrandsPersonalAIAgent`
3. Click "Test" to open the test interface
4. Try these test queries:

```
"What's the weather in London?"
"Show my calendar events"
"Post a Bible verse to X"
"Help me decide what to do today"
```

### 2. SDK Testing

```python
import boto3

bedrock_agent_runtime = boto3.client('bedrock-agent-runtime', region_name='us-east-1')

response = bedrock_agent_runtime.invoke_agent(
    agentId='YOUR_AGENT_ID',
    agentAliasId='YOUR_ALIAS_ID',
    sessionId='test-session',
    inputText='What is the weather in New York?'
)

# Process streaming response
for event in response['completion']:
    if 'chunk' in event:
        chunk = event['chunk']
        if 'bytes' in chunk:
            print(chunk['bytes'].decode())
```

### 3. CLI Testing

```bash
aws bedrock-agent-runtime invoke-agent \
  --agent-id YOUR_AGENT_ID \
  --agent-alias-id YOUR_ALIAS_ID \
  --session-id test-session \
  --input-text "What's the weather today?" \
  response.json
```

## 📊 Monitoring and Observability

### CloudWatch Dashboard
Access your monitoring dashboard:
- Go to CloudWatch > Dashboards
- Find: `strands-personal-ai-agent`
- Monitor Lambda invocations, errors, and duration

### Key Metrics to Watch
- **Lambda Invocations**: Number of capability executions
- **Lambda Errors**: Failed capability executions
- **Lambda Duration**: Response times
- **DynamoDB Operations**: Data storage activity

### Alarms
Pre-configured alarms will notify you of:
- High error rates in Lambda functions
- Unusual activity patterns
- Performance degradation

## 🔧 Customization and Updates

### Updating Lambda Functions

1. **Via AWS Console**:
   - Go to Lambda > Functions
   - Select function (e.g., `strands-weather-capability`)
   - Edit code inline or upload new deployment package

2. **Via CDK**:
   - Modify code in `lambda_functions/`
   - Run `cdk deploy` to update

### Updating Bedrock Agent

1. **Via AWS Console**:
   - Go to Bedrock > Agents
   - Select your agent
   - Modify instructions, action groups, or knowledge bases
   - Create new version and update alias

2. **Via Script**:
   - Modify `bedrock_agent_setup.py`
   - Run the script to update configuration

### Adding New Capabilities

1. Create new Lambda function in `lambda_functions/`
2. Add to CDK stack in `infrastructure/cdk_stack.py`
3. Create new Action Group in `bedrock_agent_setup.py`
4. Deploy updates

## 🚨 Troubleshooting

### Common Issues

#### 1. "Agent not found" Error
- Verify agent ID and alias ID are correct
- Check region matches your deployment
- Ensure agent is in PREPARED state

#### 2. Lambda Permission Errors
- Run: `python deploy.py` to fix permissions
- Manually add Bedrock invoke permissions to Lambda

#### 3. API Credential Issues
- Verify secrets are properly formatted JSON
- Check API keys are valid and have correct permissions
- Test credentials independently

#### 4. High Lambda Costs
- Review timeout settings (reduce if possible)
- Optimize memory allocation
- Implement caching for external API calls

### Debug Commands

```bash
# Check agent status
aws bedrock-agent get-agent --agent-id YOUR_AGENT_ID

# Check Lambda function
aws lambda get-function --function-name strands-weather-capability

# Check secrets
aws secretsmanager describe-secret --secret-id strands-agent/x-credentials

# View CloudWatch logs
aws logs describe-log-groups --log-group-name-prefix /aws/lambda/strands-
```

## 💰 Cost Optimization

### Expected Monthly Costs (Estimated)
- **Bedrock Agent**: $0.002 per 1K requests
- **Lambda**: $0.20 per 1M requests + compute time
- **DynamoDB**: $1.25 per million writes (on-demand)
- **Secrets Manager**: $0.40 per secret per month

### Cost Reduction Tips
1. **Optimize Lambda**:
   - Right-size memory allocation
   - Reduce timeout values
   - Implement connection pooling

2. **DynamoDB**:
   - Use TTL for automatic cleanup
   - Consider provisioned capacity for predictable workloads

3. **Monitoring**:
   - Set up billing alerts
   - Use AWS Cost Explorer to track usage

## 🔄 Backup and Recovery

### Backup Strategy
- **Agent Configuration**: Export via AWS CLI
- **Lambda Code**: Store in version control
- **DynamoDB Data**: Enable point-in-time recovery
- **Secrets**: Document (securely) for recovery

### Recovery Procedures
1. **Agent Recovery**: Redeploy using `bedrock_agent_setup.py`
2. **Infrastructure Recovery**: Redeploy using CDK
3. **Data Recovery**: Use DynamoDB point-in-time recovery

## 📚 Additional Resources

- [Amazon Bedrock Agents Documentation](https://docs.aws.amazon.com/bedrock/latest/userguide/agents.html)
- [AWS Lambda Best Practices](https://docs.aws.amazon.com/lambda/latest/dg/best-practices.html)
- [Strands-Agents SDK Documentation](https://strandsagents.com/)
- [AWS CDK Documentation](https://docs.aws.amazon.com/cdk/)

## 🆘 Support

### Getting Help
1. **AWS Support**: For AWS service issues
2. **Strands Community**: For framework-specific questions
3. **GitHub Issues**: For deployment script problems

### Useful Commands
```bash
# Get deployment info
cat deployment_summary.json

# View all resources
aws resourcegroupstaggingapi get-resources --tag-filters Key=Framework,Values=StrandsAgents

# Clean up deployment
cdk destroy
aws bedrock-agent delete-agent --agent-id YOUR_AGENT_ID
```

---

🎉 **Congratulations!** Your Strands Personal AI Agent is now running on AWS Bedrock AgentCore with enterprise-scale capabilities!

For questions or issues, refer to the troubleshooting section or contact support.