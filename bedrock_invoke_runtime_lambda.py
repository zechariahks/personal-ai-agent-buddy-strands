import json
import boto3
import uuid
import os
import argparse
from IPython.display import Markdown, display

def lambda_handler(event, context):
    """Lambda function to wrap Bedrock AgentCore runtime calls"""
    
    # Parse request
    try:
        if 'body' in event:
            body = json.loads(event['body'])
        else:
            body =  json.loads(event)
            
        print(body)
        message = body.get('message', '')
        session_id = str(uuid.uuid4())
        
    except Exception as e:
        return {
            'statusCode': 400,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': f'Invalid request: {str(e)}'})
        }
    
    # Call Bedrock AgentCore
    try:
        agentcore_client = boto3.client('bedrock-agentcore', region_name='us-east-1')
        
        response = agentcore_client.invoke_agent_runtime(
            agentRuntimeArn=os.getenv('AGENT_RUNTIME_ARN', agent_runtime_arn),
            qualifier="DEFAULT",
            runtimeSessionId=session_id,
            payload=json.dumps({
                "message": message,
                "session_id": session_id
            })
        )
 
        # Handle response
        if "text/event-stream" in response.get("contentType", ""):
            content = []
            for line in response["response"].iter_lines(chunk_size=1):
                if line:
                    line = line.decode("utf-8")
                    if line.startswith("data: "):
                        content.append(line[6:])
            response_text = "\n".join(content)
            print("Response (Event Stream):")
            print(response_text)
        else:
            # Handle JSON response from StreamingBody
            try:
                response_body = response['response'].read()
                response_data = json.loads(response_body.decode('utf-8'))
                
                # Check if response_data is a dict with 'response' key, otherwise use the whole data
                if isinstance(response_data, dict):
                    response_text = response_data.get('response', str(response_data))
                else:
                    # If it's a string or other type, use it directly
                    response_text = str(response_data)
                    
                print("Response (JSON):")
                print(response_text)
            except json.JSONDecodeError as e:
                # If JSON parsing fails, treat as plain text
                response_text = response_body.decode('utf-8')
                print("Response (Plain Text):")
                print(response_text)
            except Exception as e:
                response_text = f"Error reading response: {e}"
                print("Error:")
                print(response_text)
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'response': response_text,
                'session_id': session_id,
                'success': True
            })
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': str(e), 'success': False})
        }

if __name__ == '__main__':

    global  agent_runtime_arn 
    parser = argparse.ArgumentParser(description='Invoke Agent Runtime')    
    
    parser.add_argument('--agent-runtime-arn', default='', help='Bedrock Agent Runtime ARN')
    parser.add_argument('--input', default='', help='Input Request payload')
    
    args = parser.parse_args()
    agent_runtime_arn = args.agent_runtime_arn
    input_payload = args.input

    agent_response = lambda_handler(input_payload, {})

    print(agent_response['body'])