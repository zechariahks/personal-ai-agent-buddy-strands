#!/usr/bin/env python3
"""
AWS CDK Stack for Strands Personal AI Agent Bedrock Deployment
Infrastructure as Code for deploying the agent to AWS
"""

import aws_cdk as cdk
from aws_cdk import (
    Stack,
    Duration,
    aws_lambda as _lambda,
    aws_iam as iam,
    aws_dynamodb as dynamodb,
    aws_secretsmanager as secretsmanager,
    aws_logs as logs,
    aws_cloudwatch as cloudwatch,
    CfnOutput
)
from constructs import Construct
import json

class StrandsPersonalAIAgentStack(Stack):
    """CDK Stack for Strands Personal AI Agent infrastructure"""

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # DynamoDB Tables for agent data storage
        self.create_dynamodb_tables()
        
        # Secrets Manager for API credentials
        self.create_secrets()
        
        # Lambda Layer for common dependencies
        self.create_lambda_layer()
        
        # IAM roles for Lambda functions
        self.create_iam_roles()
        
        # Lambda functions for each capability
        self.create_lambda_functions()
        
        # CloudWatch monitoring
        self.create_monitoring()
        
        # Outputs
        self.create_outputs()

    def create_dynamodb_tables(self):
        """Create DynamoDB tables for agent data storage"""
        
        # Weather analysis storage
        self.weather_table = dynamodb.Table(
            self, "StrandsWeatherAnalysisTable",
            table_name="strands-weather-analysis",
            partition_key=dynamodb.Attribute(
                name="session_id",
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="timestamp",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            encryption=dynamodb.TableEncryption.AWS_MANAGED,
            time_to_live_attribute="ttl",
            removal_policy=cdk.RemovalPolicy.DESTROY,
            tags={
                "Framework": "StrandsAgents",
                "Purpose": "WeatherAnalysis"
            }
        )
        
        # Agent conversation history
        self.conversation_table = dynamodb.Table(
            self, "StrandsConversationTable",
            table_name="strands-conversation-history",
            partition_key=dynamodb.Attribute(
                name="session_id",
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="timestamp",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            encryption=dynamodb.TableEncryption.AWS_MANAGED,
            time_to_live_attribute="ttl",
            removal_policy=cdk.RemovalPolicy.DESTROY,
            tags={
                "Framework": "StrandsAgents",
                "Purpose": "ConversationHistory"
            }
        )

    def create_secrets(self):
        """Create AWS Secrets Manager secrets for API credentials"""
        
        # X (Twitter) API credentials
        self.x_credentials_secret = secretsmanager.Secret(
            self, "StrandsXCredentials",
            secret_name="strands-agent/x-credentials",
            description="X (Twitter) API credentials for Strands Personal AI Agent",
            generate_secret_string=secretsmanager.SecretStringGenerator(
                secret_string_template=json.dumps({
                    "api_key": "",
                    "api_secret": "",
                    "access_token": "",
                    "access_token_secret": ""
                }),
                generate_string_key="placeholder",
                exclude_characters=" %+~`#$&*()|[]{}:;<>?!'/\"\\",
            )
        )
        
        # Google Calendar credentials
        self.google_credentials_secret = secretsmanager.Secret(
            self, "StrandsGoogleCredentials",
            secret_name="strands-agent/google-credentials",
            description="Google Calendar API credentials for Strands Personal AI Agent",
            generate_secret_string=secretsmanager.SecretStringGenerator(
                secret_string_template=json.dumps({
                    "token": "",
                    "refresh_token": "",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "client_id": "",
                    "client_secret": ""
                }),
                generate_string_key="placeholder",
                exclude_characters=" %+~`#$&*()|[]{}:;<>?!'/\"\\",
            )
        )
        
        # OpenWeather API key
        self.weather_api_secret = secretsmanager.Secret(
            self, "StrandsWeatherAPI",
            secret_name="strands-agent/weather-api",
            description="OpenWeatherMap API key for Strands Personal AI Agent",
            generate_secret_string=secretsmanager.SecretStringGenerator(
                secret_string_template=json.dumps({
                    "api_key": "",
                    "default_city": "New York"
                }),
                generate_string_key="placeholder",
                exclude_characters=" %+~`#$&*()|[]{}:;<>?!'/\"\\",
            )
        )

    def create_lambda_layer(self):
        """Create Lambda layer with common dependencies"""
        
        self.common_layer = _lambda.LayerVersion(
            self, "StrandsCommonLayer",
            layer_version_name="strands-agent-common",
            code=_lambda.Code.from_asset("lambda_layers/common"),
            compatible_runtimes=[_lambda.Runtime.PYTHON_3_11],
            description="Common dependencies for Strands Personal AI Agent Lambda functions",
        )

    def create_iam_roles(self):
        """Create IAM roles for Lambda functions"""
        
        # Base policy for all Lambda functions
        base_policy = iam.PolicyDocument(
            statements=[
                iam.PolicyStatement(
                    effect=iam.Effect.ALLOW,
                    actions=[
                        "logs:CreateLogGroup",
                        "logs:CreateLogStream",
                        "logs:PutLogEvents"
                    ],
                    resources=["*"]
                ),
                iam.PolicyStatement(
                    effect=iam.Effect.ALLOW,
                    actions=[
                        "dynamodb:GetItem",
                        "dynamodb:PutItem",
                        "dynamodb:UpdateItem",
                        "dynamodb:Query",
                        "dynamodb:Scan"
                    ],
                    resources=[
                        self.weather_table.table_arn,
                        self.conversation_table.table_arn
                    ]
                ),
                iam.PolicyStatement(
                    effect=iam.Effect.ALLOW,
                    actions=[
                        "secretsmanager:GetSecretValue"
                    ],
                    resources=[
                        self.x_credentials_secret.secret_arn,
                        self.google_credentials_secret.secret_arn,
                        self.weather_api_secret.secret_arn
                    ]
                )
            ]
        )
        
        # Lambda execution role
        self.lambda_role = iam.Role(
            self, "StrandsLambdaRole",
            role_name="StrandsPersonalAIAgentLambdaRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            inline_policies={
                "StrandsAgentPolicy": base_policy
            },
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "service-role/AWSLambdaBasicExecutionRole"
                )
            ]
        )

    def create_lambda_functions(self):
        """Create Lambda functions for each capability"""
        
        # Common environment variables
        common_env = {
            "WEATHER_ANALYSIS_TABLE": self.weather_table.table_name,
            "CONVERSATION_TABLE": self.conversation_table.table_name,
            "X_CREDENTIALS_SECRET_NAME": self.x_credentials_secret.secret_name,
            "GOOGLE_CALENDAR_SECRET_NAME": self.google_credentials_secret.secret_name,
            "WEATHER_API_SECRET_NAME": self.weather_api_secret.secret_name,
            "AWS_REGION": self.region
        }
        
        # Weather Capability Lambda
        self.weather_lambda = _lambda.Function(
            self, "StrandsWeatherCapability",
            function_name="strands-weather-capability",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="strands_weather_capability.lambda_handler",
            code=_lambda.Code.from_asset("lambda_functions"),
            layers=[self.common_layer],
            role=self.lambda_role,
            environment=common_env,
            timeout=Duration.seconds(30),
            memory_size=256,
            description="Strands Weather Capability - Weather analysis with impact assessment",
            log_retention=logs.RetentionDays.ONE_WEEK
        )
        
        # Calendar Capability Lambda
        self.calendar_lambda = _lambda.Function(
            self, "StrandsCalendarCapability",
            function_name="strands-calendar-capability",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="strands_calendar_capability.lambda_handler",
            code=_lambda.Code.from_asset("lambda_functions"),
            layers=[self.common_layer],
            role=self.lambda_role,
            environment=common_env,
            timeout=Duration.seconds(60),
            memory_size=512,
            description="Strands Calendar Capability - Google Calendar integration",
            log_retention=logs.RetentionDays.ONE_WEEK
        )
        
        # Social Media Capability Lambda
        self.social_lambda = _lambda.Function(
            self, "StrandsSocialCapability",
            function_name="strands-social-capability",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="strands_social_capability.lambda_handler",
            code=_lambda.Code.from_asset("lambda_functions"),
            layers=[self.common_layer],
            role=self.lambda_role,
            environment=common_env,
            timeout=Duration.minutes(5),
            memory_size=512,
            description="Strands Social Media Capability - X posting and Bible verse sharing",
            log_retention=logs.RetentionDays.ONE_WEEK
        )

    def create_monitoring(self):
        """Create CloudWatch monitoring and alarms"""
        
        # CloudWatch Dashboard
        self.dashboard = cloudwatch.Dashboard(
            self, "StrandsAgentDashboard",
            dashboard_name="strands-personal-ai-agent",
            widgets=[
                [
                    cloudwatch.GraphWidget(
                        title="Lambda Function Invocations",
                        left=[
                            self.weather_lambda.metric_invocations(),
                            self.calendar_lambda.metric_invocations(),
                            self.social_lambda.metric_invocations()
                        ],
                        width=12,
                        height=6
                    )
                ],
                [
                    cloudwatch.GraphWidget(
                        title="Lambda Function Errors",
                        left=[
                            self.weather_lambda.metric_errors(),
                            self.calendar_lambda.metric_errors(),
                            self.social_lambda.metric_errors()
                        ],
                        width=12,
                        height=6
                    )
                ],
                [
                    cloudwatch.GraphWidget(
                        title="Lambda Function Duration",
                        left=[
                            self.weather_lambda.metric_duration(),
                            self.calendar_lambda.metric_duration(),
                            self.social_lambda.metric_duration()
                        ],
                        width=12,
                        height=6
                    )
                ],
                [
                    cloudwatch.GraphWidget(
                        title="DynamoDB Operations",
                        left=[
                            self.weather_table.metric_consumed_read_capacity_units(),
                            self.weather_table.metric_consumed_write_capacity_units(),
                            self.conversation_table.metric_consumed_read_capacity_units(),
                            self.conversation_table.metric_consumed_write_capacity_units()
                        ],
                        width=12,
                        height=6
                    )
                ]
            ]
        )
        
        # Alarms for high error rates
        cloudwatch.Alarm(
            self, "WeatherLambdaErrorAlarm",
            alarm_name="strands-weather-lambda-errors",
            metric=self.weather_lambda.metric_errors(),
            threshold=5,
            evaluation_periods=2,
            alarm_description="High error rate in Weather Lambda function"
        )
        
        cloudwatch.Alarm(
            self, "CalendarLambdaErrorAlarm",
            alarm_name="strands-calendar-lambda-errors",
            metric=self.calendar_lambda.metric_errors(),
            threshold=5,
            evaluation_periods=2,
            alarm_description="High error rate in Calendar Lambda function"
        )
        
        cloudwatch.Alarm(
            self, "SocialLambdaErrorAlarm",
            alarm_name="strands-social-lambda-errors",
            metric=self.social_lambda.metric_errors(),
            threshold=5,
            evaluation_periods=2,
            alarm_description="High error rate in Social Media Lambda function"
        )

    def create_outputs(self):
        """Create CloudFormation outputs"""
        
        CfnOutput(
            self, "WeatherLambdaArn",
            value=self.weather_lambda.function_arn,
            description="ARN of the Weather Capability Lambda function",
            export_name="StrandsWeatherLambdaArn"
        )
        
        CfnOutput(
            self, "CalendarLambdaArn",
            value=self.calendar_lambda.function_arn,
            description="ARN of the Calendar Capability Lambda function",
            export_name="StrandsCalendarLambdaArn"
        )
        
        CfnOutput(
            self, "SocialLambdaArn",
            value=self.social_lambda.function_arn,
            description="ARN of the Social Media Capability Lambda function",
            export_name="StrandsSocialLambdaArn"
        )
        
        CfnOutput(
            self, "WeatherTableName",
            value=self.weather_table.table_name,
            description="Name of the Weather Analysis DynamoDB table",
            export_name="StrandsWeatherTableName"
        )
        
        CfnOutput(
            self, "ConversationTableName",
            value=self.conversation_table.table_name,
            description="Name of the Conversation History DynamoDB table",
            export_name="StrandsConversationTableName"
        )
        
        CfnOutput(
            self, "XCredentialsSecretArn",
            value=self.x_credentials_secret.secret_arn,
            description="ARN of the X API credentials secret",
            export_name="StrandsXCredentialsSecretArn"
        )
        
        CfnOutput(
            self, "GoogleCredentialsSecretArn",
            value=self.google_credentials_secret.secret_arn,
            description="ARN of the Google Calendar credentials secret",
            export_name="StrandsGoogleCredentialsSecretArn"
        )
        
        CfnOutput(
            self, "DashboardUrl",
            value=f"https://{self.region}.console.aws.amazon.com/cloudwatch/home?region={self.region}#dashboards:name={self.dashboard.dashboard_name}",
            description="URL to the CloudWatch dashboard",
            export_name="StrandsDashboardUrl"
        )