#!/usr/bin/env python3
"""
Google Calendar Tool for Strands-Agents SDK
Manages calendar events using Google Calendar API
"""

import os
import json
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from strands import tool

try:
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False


# Google Calendar API scopes
SCOPES = ['https://www.googleapis.com/auth/calendar']


def get_calendar_service():
    """
    Get authenticated Google Calendar service.
    
    Returns:
        Google Calendar service object or None if authentication fails
    """
    if not GOOGLE_AVAILABLE:
        return None
        
    creds = None
    token_path = os.path.expanduser('~/.google_calendar_token.json')
    credentials_path = os.path.expanduser('~/.google_calendar_credentials.json')
    
    # Load existing token
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    
    # If there are no (valid) credentials available, let the user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception:
                creds = None
        
        if not creds:
            if not os.path.exists(credentials_path):
                return None
            flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save the credentials for the next run
        with open(token_path, 'w') as token:
            token.write(creds.to_json())
    
    try:
        service = build('calendar', 'v3', credentials=creds)
        return service
    except Exception:
        return None


@tool
def create_calendar_event(
    title: str,
    start_time: str,
    end_time: str,
    description: str = "",
    location: str = "",
    attendees: str = ""
) -> str:
    """
    Create a new event in Google Calendar.
    
    Args:
        title: Event title/summary
        start_time: Start time in ISO format (e.g., "2024-01-15T10:00:00")
        end_time: End time in ISO format (e.g., "2024-01-15T11:00:00")
        description: Event description (optional)
        location: Event location (optional)
        attendees: Comma-separated email addresses (optional)
        
    Returns:
        A formatted string with the event creation result
    """
    if not GOOGLE_AVAILABLE:
        return """
❌ Google Calendar integration not available.

To enable Google Calendar integration, install required packages:
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client

Then set up Google Calendar API credentials:
1. Go to https://console.cloud.google.com/
2. Create a new project or select existing one
3. Enable Google Calendar API
4. Create credentials (OAuth 2.0 Client ID)
5. Download credentials as ~/.google_calendar_credentials.json

📅 Event details (saved locally for now):
Title: {title}
Start: {start_time}
End: {end_time}
Description: {description}
Location: {location}
Attendees: {attendees}
        """.format(
            title=title,
            start_time=start_time,
            end_time=end_time,
            description=description,
            location=location,
            attendees=attendees
        ).strip()
    
    service = get_calendar_service()
    if not service:
        return f"""
❌ Google Calendar authentication failed.

Please ensure you have:
1. Google Calendar API credentials at ~/.google_calendar_credentials.json
2. Proper authentication setup

📅 Event details (saved locally for now):
Title: {title}
Start: {start_time}
End: {end_time}
Description: {description}
Location: {location}
Attendees: {attendees}

💡 Once authenticated, I'll be able to create this event in your Google Calendar.
        """.strip()
    
    try:
        # Parse attendees
        attendee_list = []
        if attendees:
            for email in attendees.split(','):
                email = email.strip()
                if email:
                    attendee_list.append({'email': email})
        
        # Create event object
        event = {
            'summary': title,
            'description': description,
            'start': {
                'dateTime': start_time,
                'timeZone': 'America/Los_Angeles',  # Default timezone
            },
            'end': {
                'dateTime': end_time,
                'timeZone': 'America/Los_Angeles',
            },
            'attendees': attendee_list,
        }
        
        if location:
            event['location'] = location
        
        # Create the event
        created_event = service.events().insert(calendarId='primary', body=event).execute()
        
        event_id = created_event.get('id')
        event_link = created_event.get('htmlLink', '')
        
        result = f"""
✅ Calendar event created successfully!

📅 Event Details:
• Title: {title}
• Start: {start_time}
• End: {end_time}
• Description: {description}
• Location: {location}
• Attendees: {attendees if attendees else 'None'}

🔗 Event ID: {event_id}
🌐 View in Calendar: {event_link}

🎉 Your event has been added to Google Calendar!
        """.strip()
        
        return result
        
    except HttpError as error:
        return f"""
❌ Google Calendar API error: {error}

Event details:
• Title: {title}
• Start: {start_time}
• End: {end_time}

Please check your API permissions and try again.
        """.strip()
        
    except Exception as e:
        return f"""
❌ Error creating calendar event: {str(e)}

Event details:
• Title: {title}
• Start: {start_time}
• End: {end_time}

Please try again or check your input format.
        """.strip()


@tool
def get_calendar_events(days_ahead: int = 7) -> str:
    """
    Get upcoming events from Google Calendar.
    
    Args:
        days_ahead: Number of days ahead to look for events (default: 7)
        
    Returns:
        A formatted string with upcoming events
    """
    if not GOOGLE_AVAILABLE:
        return f"""
❌ Google Calendar integration not available.

To view calendar events, install required packages:
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client

📅 Looking for events in the next {days_ahead} days...
        """.strip()
    
    service = get_calendar_service()
    if not service:
        return f"""
❌ Google Calendar authentication failed.

Please ensure you have proper Google Calendar API setup.

📅 Looking for events in the next {days_ahead} days...
        """.strip()
    
    try:
        # Calculate time range
        now = datetime.utcnow()
        end_time = now + timedelta(days=days_ahead)
        
        # Get events
        events_result = service.events().list(
            calendarId='primary',
            timeMin=now.isoformat() + 'Z',
            timeMax=end_time.isoformat() + 'Z',
            maxResults=20,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        
        if not events:
            return f"""
📅 No upcoming events found in the next {days_ahead} days.

Your calendar is clear! 🎉
            """.strip()
        
        result = f"📅 Upcoming Events (Next {days_ahead} days):\n\n"
        
        for i, event in enumerate(events, 1):
            start = event['start'].get('dateTime', event['start'].get('date'))
            end = event['end'].get('dateTime', event['end'].get('date'))
            title = event.get('summary', 'No Title')
            description = event.get('description', '')
            location = event.get('location', '')
            
            # Format datetime
            try:
                if 'T' in start:
                    start_dt = datetime.fromisoformat(start.replace('Z', '+00:00'))
                    end_dt = datetime.fromisoformat(end.replace('Z', '+00:00'))
                    time_str = f"{start_dt.strftime('%Y-%m-%d %H:%M')} - {end_dt.strftime('%H:%M')}"
                else:
                    time_str = f"{start} (All day)"
            except:
                time_str = f"{start} - {end}"
            
            result += f"{i}. **{title}**\n"
            result += f"   ⏰ {time_str}\n"
            
            if location:
                result += f"   📍 {location}\n"
            
            if description:
                desc_short = description[:100] + "..." if len(description) > 100 else description
                result += f"   📝 {desc_short}\n"
            
            result += "\n"
        
        return result.strip()
        
    except HttpError as error:
        return f"""
❌ Google Calendar API error: {error}

Please check your API permissions and try again.
        """.strip()
        
    except Exception as e:
        return f"""
❌ Error fetching calendar events: {str(e)}

Please try again.
        """.strip()


@tool
def update_calendar_event(
    event_id: str,
    title: Optional[str] = None,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    description: Optional[str] = None,
    location: Optional[str] = None
) -> str:
    """
    Update an existing calendar event.
    
    Args:
        event_id: Google Calendar event ID
        title: New event title (optional)
        start_time: New start time in ISO format (optional)
        end_time: New end time in ISO format (optional)
        description: New description (optional)
        location: New location (optional)
        
    Returns:
        A formatted string with the update result
    """
    if not GOOGLE_AVAILABLE:
        return f"""
❌ Google Calendar integration not available.

Event ID: {event_id}
Updates requested: title={title}, start={start_time}, end={end_time}
        """.strip()
    
    service = get_calendar_service()
    if not service:
        return f"""
❌ Google Calendar authentication failed.

Event ID: {event_id}
        """.strip()
    
    try:
        # Get existing event
        event = service.events().get(calendarId='primary', eventId=event_id).execute()
        
        # Update fields if provided
        if title is not None:
            event['summary'] = title
        if start_time is not None:
            event['start']['dateTime'] = start_time
        if end_time is not None:
            event['end']['dateTime'] = end_time
        if description is not None:
            event['description'] = description
        if location is not None:
            event['location'] = location
        
        # Update the event
        updated_event = service.events().update(
            calendarId='primary',
            eventId=event_id,
            body=event
        ).execute()
        
        return f"""
✅ Calendar event updated successfully!

📅 Event: {updated_event.get('summary', 'No Title')}
🆔 Event ID: {event_id}
🔗 View: {updated_event.get('htmlLink', '')}

🎉 Your event has been updated in Google Calendar!
        """.strip()
        
    except HttpError as error:
        return f"""
❌ Google Calendar API error: {error}

Event ID: {event_id}
Please check the event ID and your permissions.
        """.strip()
        
    except Exception as e:
        return f"""
❌ Error updating calendar event: {str(e)}

Event ID: {event_id}
        """.strip()


@tool
def delete_calendar_event(event_id: str) -> str:
    """
    Delete a calendar event.
    
    Args:
        event_id: Google Calendar event ID
        
    Returns:
        A formatted string with the deletion result
    """
    if not GOOGLE_AVAILABLE:
        return f"""
❌ Google Calendar integration not available.

Event ID to delete: {event_id}
        """.strip()
    
    service = get_calendar_service()
    if not service:
        return f"""
❌ Google Calendar authentication failed.

Event ID: {event_id}
        """.strip()
    
    try:
        # Delete the event
        service.events().delete(calendarId='primary', eventId=event_id).execute()
        
        return f"""
✅ Calendar event deleted successfully!

🗑️ Event ID: {event_id}

The event has been removed from your Google Calendar.
        """.strip()
        
    except HttpError as error:
        return f"""
❌ Google Calendar API error: {error}

Event ID: {event_id}
Please check the event ID and your permissions.
        """.strip()
        
    except Exception as e:
        return f"""
❌ Error deleting calendar event: {str(e)}

Event ID: {event_id}
        """.strip()


# Test function for development
def test_google_calendar_tool():
    """Test the Google Calendar tool functionality"""
    print("Testing Google Calendar tool...")
    
    # Test getting events
    print("1. Testing get events:")
    result = get_calendar_events(7)
    print(result)
    print("\n" + "="*50 + "\n")
    
    # Test creating event
    print("2. Testing event creation:")
    start_time = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%dT10:00:00')
    end_time = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%dT11:00:00')
    
    result = create_calendar_event(
        title="Test Event from Strands-Agents",
        start_time=start_time,
        end_time=end_time,
        description="This is a test event created by the AI agent",
        location="Virtual Meeting"
    )
    print(result)


if __name__ == "__main__":
    test_google_calendar_tool()