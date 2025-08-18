#!/usr/bin/env python3
"""
Strands Calendar Capability Lambda Function
AWS Lambda implementation of Google Calendar integration
"""

import json
import os
import boto3
from datetime import datetime, timedelta
from typing import Dict, Any, List
import base64

# Google Calendar imports (will be available in Lambda layer)
try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    GOOGLE_CALENDAR_AVAILABLE = True
except ImportError:
    GOOGLE_CALENDAR_AVAILABLE = False

def lambda_handler(event, context):
    """
    AWS Lambda handler for Strands Calendar Capability
    """
    try:
        print(f"Received event: {json.dumps(event)}")
        
        if not GOOGLE_CALENDAR_AVAILABLE:
            return {
                'statusCode': 500,
                'body': json.dumps({
                    'success': False,
                    'error': 'Google Calendar integration not available',
                    'message': 'Google Calendar packages not installed in Lambda environment'
                })
            }
        
        # Extract parameters and determine action
        parameters = extract_parameters(event)
        action = determine_action(event, parameters)
        
        # Route to appropriate handler
        if action == 'list_events':
            result = handle_list_events(parameters)
        elif action == 'create_event':
            result = handle_create_event(parameters)
        elif action == 'update_event':
            result = handle_update_event(parameters)
        elif action == 'delete_event':
            result = handle_delete_event(parameters)
        else:
            result = {
                'success': False,
                'error': f'Unknown action: {action}',
                'available_actions': ['list_events', 'create_event', 'update_event', 'delete_event']
            }
        
        return {
            'statusCode': 200 if result.get('success', True) else 400,
            'body': json.dumps(result)
        }
        
    except Exception as e:
        print(f"Error in calendar capability: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'success': False,
                'error': str(e),
                'message': 'Calendar capability error'
            })
        }

def extract_parameters(event):
    """Extract parameters from Bedrock Agent event"""
    parameters = {}
    
    # Handle different event formats
    if 'parameters' in event:
        for param in event['parameters']:
            parameters[param['name']] = param['value']
    elif 'requestBody' in event:
        body = json.loads(event['requestBody']['content']['application/json']['properties'])
        parameters = body
    elif 'body' in event:
        body = json.loads(event['body']) if isinstance(event['body'], str) else event['body']
        parameters = body
    
    return parameters

def determine_action(event, parameters):
    """Determine the calendar action to perform"""
    # Check HTTP method if available
    http_method = event.get('httpMethod', '').upper()
    
    if http_method == 'GET':
        return 'list_events'
    elif http_method == 'POST':
        return 'create_event'
    elif http_method == 'PUT':
        return 'update_event'
    elif http_method == 'DELETE':
        return 'delete_event'
    
    # Check explicit action parameter
    action = parameters.get('action', '').lower()
    if action in ['list', 'get', 'show']:
        return 'list_events'
    elif action in ['create', 'add', 'schedule']:
        return 'create_event'
    elif action in ['update', 'modify', 'edit']:
        return 'update_event'
    elif action in ['delete', 'remove', 'cancel']:
        return 'delete_event'
    
    # Default to list events
    return 'list_events'

def get_calendar_service():
    """Get authenticated Google Calendar service"""
    try:
        # Get credentials from environment variables or AWS Secrets Manager
        creds = get_google_credentials()
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                raise Exception("No valid Google Calendar credentials available")
        
        service = build('calendar', 'v3', credentials=creds)
        return service
        
    except Exception as e:
        raise Exception(f"Failed to authenticate with Google Calendar: {str(e)}")

def get_google_credentials():
    """Get Google Calendar credentials from AWS Secrets Manager or environment"""
    try:
        # Try to get from AWS Secrets Manager first
        secret_name = os.environ.get('GOOGLE_CALENDAR_SECRET_NAME')
        if secret_name:
            secrets_client = boto3.client('secretsmanager')
            response = secrets_client.get_secret_value(SecretId=secret_name)
            secret_data = json.loads(response['SecretString'])
            
            creds = Credentials(
                token=secret_data.get('token'),
                refresh_token=secret_data.get('refresh_token'),
                token_uri=secret_data.get('token_uri'),
                client_id=secret_data.get('client_id'),
                client_secret=secret_data.get('client_secret'),
                scopes=['https://www.googleapis.com/auth/calendar']
            )
            return creds
        
        # Fallback to environment variables (base64 encoded)
        token_data = os.environ.get('GOOGLE_CALENDAR_TOKEN')
        if token_data:
            token_json = base64.b64decode(token_data).decode('utf-8')
            token_info = json.loads(token_json)
            
            creds = Credentials.from_authorized_user_info(token_info)
            return creds
        
        raise Exception("No Google Calendar credentials found")
        
    except Exception as e:
        raise Exception(f"Failed to load Google Calendar credentials: {str(e)}")

def handle_list_events(parameters):
    """Handle listing calendar events"""
    try:
        service = get_calendar_service()
        days = int(parameters.get('days', 7))
        
        # Calculate time range
        now = datetime.utcnow()
        time_min = now.isoformat() + 'Z'
        time_max = (now + timedelta(days=days)).isoformat() + 'Z'
        
        # Get events
        events_result = service.events().list(
            calendarId='primary',
            timeMin=time_min,
            timeMax=time_max,
            maxResults=50,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        
        if not events:
            return {
                'success': True,
                'message': f'No upcoming events found in the next {days} days',
                'events': [],
                'count': 0
            }
        
        # Format events
        formatted_events = []
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            end = event['end'].get('dateTime', event['end'].get('date'))
            
            formatted_events.append({
                'id': event['id'],
                'title': event.get('summary', 'No Title'),
                'start': start,
                'end': end,
                'description': event.get('description', ''),
                'location': event.get('location', ''),
                'status': event.get('status', 'confirmed')
            })
        
        return {
            'success': True,
            'message': f'Found {len(formatted_events)} upcoming events',
            'events': formatted_events,
            'count': len(formatted_events),
            'time_range': f'{days} days'
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'message': 'Failed to list calendar events'
        }

def handle_create_event(parameters):
    """Handle creating a calendar event"""
    try:
        service = get_calendar_service()
        
        # Extract event details
        title = parameters.get('title', 'New Event')
        start_time = parameters.get('start_time')
        end_time = parameters.get('end_time')
        description = parameters.get('description', '')
        location = parameters.get('location', '')
        
        if not start_time or not end_time:
            return {
                'success': False,
                'error': 'start_time and end_time are required',
                'message': 'Please provide both start_time and end_time in ISO format'
            }
        
        # Create event object
        event = {
            'summary': title,
            'description': description,
            'start': {
                'dateTime': start_time,
                'timeZone': 'UTC',
            },
            'end': {
                'dateTime': end_time,
                'timeZone': 'UTC',
            },
        }
        
        if location:
            event['location'] = location
        
        # Create the event
        created_event = service.events().insert(
            calendarId='primary',
            body=event
        ).execute()
        
        return {
            'success': True,
            'message': f'Event "{title}" created successfully',
            'event': {
                'id': created_event['id'],
                'title': title,
                'start': start_time,
                'end': end_time,
                'description': description,
                'location': location,
                'html_link': created_event.get('htmlLink', '')
            }
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'message': 'Failed to create calendar event'
        }

def handle_update_event(parameters):
    """Handle updating a calendar event"""
    try:
        service = get_calendar_service()
        
        event_id = parameters.get('event_id')
        if not event_id:
            return {
                'success': False,
                'error': 'event_id is required for updates',
                'message': 'Please provide the event_id to update'
            }
        
        # Get existing event
        existing_event = service.events().get(
            calendarId='primary',
            eventId=event_id
        ).execute()
        
        # Update fields if provided
        if 'title' in parameters:
            existing_event['summary'] = parameters['title']
        if 'description' in parameters:
            existing_event['description'] = parameters['description']
        if 'location' in parameters:
            existing_event['location'] = parameters['location']
        if 'start_time' in parameters:
            existing_event['start']['dateTime'] = parameters['start_time']
        if 'end_time' in parameters:
            existing_event['end']['dateTime'] = parameters['end_time']
        
        # Update the event
        updated_event = service.events().update(
            calendarId='primary',
            eventId=event_id,
            body=existing_event
        ).execute()
        
        return {
            'success': True,
            'message': f'Event updated successfully',
            'event': {
                'id': updated_event['id'],
                'title': updated_event.get('summary', ''),
                'start': updated_event['start'].get('dateTime', ''),
                'end': updated_event['end'].get('dateTime', ''),
                'description': updated_event.get('description', ''),
                'location': updated_event.get('location', '')
            }
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'message': 'Failed to update calendar event'
        }

def handle_delete_event(parameters):
    """Handle deleting a calendar event"""
    try:
        service = get_calendar_service()
        
        event_id = parameters.get('event_id')
        if not event_id:
            return {
                'success': False,
                'error': 'event_id is required for deletion',
                'message': 'Please provide the event_id to delete'
            }
        
        # Delete the event
        service.events().delete(
            calendarId='primary',
            eventId=event_id
        ).execute()
        
        return {
            'success': True,
            'message': f'Event deleted successfully',
            'event_id': event_id
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'message': 'Failed to delete calendar event'
        }

# For local testing
if __name__ == "__main__":
    test_event = {
        'httpMethod': 'GET',
        'parameters': [
            {'name': 'days', 'value': '7'}
        ],
        'sessionId': 'test-session'
    }
    
    result = lambda_handler(test_event, None)
    print(json.dumps(result, indent=2))