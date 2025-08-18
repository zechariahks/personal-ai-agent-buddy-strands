#!/usr/bin/env python3
"""
Basic Intelligent Agent Implementation using Strands-Agents SDK
Migrated from the original basic_agent.py to use Strands-Agents framework
"""

import os
import smtplib
import requests
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from strands import Agent
from strands_tools import calculator
from strands.models.openai import OpenAIModel
from strands.models.anthropic import AnthropicModel
from strands.models.bedrock import BedrockModel
from weather_tool import get_weather


class StrandsBasicAgent:
    """
    Basic intelligent AI agent using Strands-Agents SDK
    Provides weather, email, calendar, and chat capabilities with built-in tools
    """
    
    def __init__(self, name="Buddy"):
        """Initialize the agent with Strands-Agents SDK"""
        self.name = name
        self.memory = {}  # Store reminders, events, etc.
        self.services_status = {}
        
        print(f"🤖 Hello! I'm {self.name}, your Strands-powered AI assistant.")
        print("I can help with weather, emails, calendar events, calculations, and answer questions!")
        
        # Check which services are available
        self._check_services()
        
        # Initialize Strands Agent with built-in tools
        self.agent = self._initialize_strands_agent()
    
    def _initialize_strands_agent(self):
        """Initialize the Strands Agent with appropriate tools and configuration"""
        try:
            # Available tools
            available_tools = []
            
            # Add calculator tool (always available)
            available_tools.append(calculator)
            
            # Add custom weather tool
            available_tools.append(get_weather)
            
            # Configure model based on available credentials
            model_config = self._get_model_config()
            
            # Create Strands Agent with correct configuration
            agent = Agent(
                tools=available_tools,
                system_prompt="You are a helpful AI assistant with access to calculator and weather tools. Use the tools when appropriate to provide accurate information.",
                model=model_config
            )
            
            print(f"✅ Strands Agent initialized with {len(available_tools)} tools")
            return agent
            
        except Exception as e:
            print(f"⚠️ Error initializing Strands Agent: {str(e)}")
            print("Falling back to basic configuration...")
            return Agent()
    
    def _get_model_config(self):
        """
        Return a Strands model instance expected by Agent (not a dict).
        Uses the Strands model wrappers imported at top of this file.
        """
        openai_key = os.getenv("OPENAI_API_KEY")
        anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        bedrock_model_env = os.getenv("BEDROCK_MODEL")  # explicit Bedrock model id (recommended)

        # OpenAI provider
        if openai_key:
            model_id = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
            print(f"🔧 Instantiating OpenAIModel (id={model_id})")
            try:
                return OpenAIModel(model_id=model_id, client_config={"api_key": openai_key})
            except Exception as e:
                raise RuntimeError(f"Failed to create OpenAIModel: {e}") from e

        # Anthropic provider
        if anthropic_key:
            model_id = os.getenv("ANTHROPIC_MODEL", "claude-3-sonnet-20240229")
            print(f"🔧 Instantiating AnthropicModel (id={model_id})")
            try:
                return AnthropicModel(model_id=model_id, client_config={"api_key": anthropic_key})
            except Exception as e:
                raise RuntimeError(f"Failed to create AnthropicModel: {e}") from e

        # Amazon Bedrock provider (explicit model id required)
        if bedrock_model_env:
            print(f"🔧 Instantiating BedrockModel (id={bedrock_model_env})")
            try:
                # BedrockModel likely picks up AWS credentials from env / IAM role
                return BedrockModel(model=bedrock_model_env)
            except Exception as e:
                raise RuntimeError(f"Failed to create BedrockModel: {e}") from e

        # No provider configured
        raise RuntimeError(
            "No LLM provider configured. Set OPENAI_API_KEY or ANTHROPIC_API_KEY, "
            "or set BEDROCK_MODEL to a valid Amazon Bedrock model identifier."
        )
    
    def _check_services(self):
        """Check which external services are properly configured"""
        self.services_status = {
            "AI": (os.getenv("OPENAI_API_KEY") is not None or 
                   os.getenv("ANTHROPIC_API_KEY") is not None or
                   os.getenv("AWS_ACCESS_KEY_ID") is not None),
            "Weather": os.getenv("WEATHER_API_KEY") is not None,
            "Email": (os.getenv("GMAIL_EMAIL") is not None and 
                     os.getenv("GMAIL_APP_PASSWORD") is not None)
        }
        
        print("\n🔧 Service Status:")
        for service, available in self.services_status.items():
            status = "✅ Ready" if available else "❌ Not configured"
            print(f"   {service}: {status}")
        print()
    
    def ask_agent(self, question):
        """Use Strands Agent to process questions and requests"""
        try:
            print(f"🤔 Processing with Strands Agent: {question}")
            
            # Use Strands Agent to process the request
            response = self.agent(question)
            
            # Handle AgentResult object - extract the text content
            if hasattr(response, 'content'):
                return response.content
            elif hasattr(response, 'text'):
                return response.text
            else:
                return str(response)
            
        except Exception as e:
            return f"❌ Strands Agent error: {str(e)}"
    
    def create_reminder(self, message, recipient="yourself"):
        """Create and store reminders in memory"""
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
            
            reminder = {
                "message": message,
                "recipient": recipient,
                "created": timestamp,
                "id": f"reminder_{len(self.memory.get('reminders', []))}"
            }
            
            if "reminders" not in self.memory:
                self.memory["reminders"] = []
            self.memory["reminders"].append(reminder)
            
            return f"📝 Reminder created: '{message}' for {recipient}"
            
        except Exception as e:
            return f"❌ Reminder error: {str(e)}"
    
    def list_reminders(self):
        """Show all stored reminders"""
        if "reminders" not in self.memory or not self.memory["reminders"]:
            return "📝 No reminders found."
        
        reminder_list = "📝 Your reminders:\n"
        for i, reminder in enumerate(self.memory["reminders"], 1):
            reminder_list += f"{i}. {reminder['message']} (created: {reminder['created']})\n"
        
        return reminder_list
    
    def create_calendar_event(self, title, date, time, description=""):
        """Create and store calendar events in memory"""
        try:
            event = {
                "title": title,
                "date": date,
                "time": time,
                "description": description,
                "created": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "id": f"event_{len(self.memory.get('events', []))}"
            }
            
            if "events" not in self.memory:
                self.memory["events"] = []
            self.memory["events"].append(event)
            
            return f"📅 Calendar event created: '{title}' on {date} at {time}"
            
        except Exception as e:
            return f"❌ Calendar error: {str(e)}"
    
    def list_events(self):
        """Show all stored events"""
        if "events" not in self.memory or not self.memory["events"]:
            return "📅 No events scheduled."
        
        event_list = "📅 Your upcoming events:\n"
        for event in self.memory["events"]:
            event_list += f"• {event['title']} - {event['date']} at {event['time']}\n"
            if event['description']:
                event_list += f"  Description: {event['description']}\n"
        
        return event_list
    
    def send_email(self, to_email, subject, message):
        """Send real emails using Gmail SMTP"""
        if not self.services_status.get("Email", False):
            return "❌ Email service not configured. Please add Gmail credentials to environment variables."
        
        try:
            gmail_email = os.getenv("GMAIL_EMAIL")
            gmail_password = os.getenv("GMAIL_APP_PASSWORD")
            
            msg = MIMEMultipart()
            msg['From'] = gmail_email
            msg['To'] = to_email
            msg['Subject'] = subject
            
            body = f"""
Hello!

Your Strands-powered AI assistant ({self.name}) sent you this message:

{message}

---
Sent by your Personal AI Assistant (Strands-Agents SDK)
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            """.strip()
            
            msg.attach(MIMEText(body, 'plain'))
            
            print(f"📧 Sending email to {to_email}...")
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(gmail_email, gmail_password)
            
            text = msg.as_string()
            server.sendmail(gmail_email, to_email, text)
            server.quit()
            
            self._store_sent_email(to_email, subject, message)
            
            return f"✅ Email sent successfully to {to_email}!"
            
        except smtplib.SMTPAuthenticationError:
            return "❌ Email authentication failed. Check your Gmail credentials and app password."
        except smtplib.SMTPException as e:
            return f"❌ Email sending failed: {str(e)}"
        except Exception as e:
            return f"❌ Unexpected email error: {str(e)}"
    
    def _store_sent_email(self, to_email, subject, message):
        """Store sent email information in memory"""
        email_record = {
            "to": to_email,
            "subject": subject,
            "message": message,
            "sent_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        if "sent_emails" not in self.memory:
            self.memory["sent_emails"] = []
        self.memory["sent_emails"].append(email_record)
    
    def show_help(self):
        """Show what the agent can do"""
        help_text = f"""
🤖 Hi! I'm {self.name}, your Strands-powered AI assistant. Here's what I can help you with:

🧮 **Built-in Tools (via Strands-Agents SDK)**:
   • Calculator - "What's 15 * 23?" or "Calculate the square root of 144"
   • Weather - "What's the weather in Paris?" (OpenWeatherMap API integration)

📝 **Reminders**: 
   • "Remind me to call mom tomorrow"
   • "Create a reminder to buy groceries"
   • "Show my reminders"

📅 **Calendar**: 
   • "Schedule a meeting tomorrow at 2 PM"
   • "Create event: Team lunch on Friday at noon"
   • "Show my events"

📧 **Email**: 
   • "Send email to friend@example.com with subject 'Hello' and message 'How are you?'"
   • (Requires Gmail configuration)

💬 **General Questions**: 
   • Ask me anything! I'm powered by advanced AI models through Strands-Agents SDK.

🔧 **System**: 
   • "Check services" - See which features are available
   • "Help" - Show this message

🚀 **Powered by Strands-Agents SDK** - Advanced multi-agent AI framework!

Just tell me what you need in natural language - I'll understand!
        """.strip()
        
        return help_text
    
    def get_service_status(self):
        """Return detailed service status information"""
        status_report = "🔧 Strands-Agents Service Status Report:\n\n"
        
        for service, available in self.services_status.items():
            if available:
                status_report += f"✅ {service}: Ready and configured\n"
            else:
                status_report += f"❌ {service}: Not configured\n"
                
                if service == "AI":
                    status_report += "   → Add OPENAI_API_KEY, ANTHROPIC_API_KEY, or AWS credentials\n"
                elif service == "Weather":
                    status_report += "   → Add WEATHER_API_KEY for enhanced weather features\n"
                elif service == "Email":
                    status_report += "   → Add GMAIL_EMAIL and GMAIL_APP_PASSWORD\n"
        
        status_report += f"\n🚀 Strands-Agents SDK Status: ✅ Active\n"
        status_report += f"🔧 Available Tools: {len(self.agent.tools) if hasattr(self.agent, 'tools') else 'Unknown'}\n"
        
        return status_report
    
    def process_request(self, user_request):
        """Main request processing logic with Strands-Agents integration"""
        request_lower = user_request.lower()
        
        # Help requests
        if any(word in request_lower for word in ['help', 'what can you do', 'commands']):
            return self.show_help()
        
        # Service status requests
        elif any(word in request_lower for word in ['check services', 'service status', 'status']):
            return self.get_service_status()
        
        # Reminder requests
        elif any(word in request_lower for word in ['remind', 'reminder', 'remember']):
            if 'show' in request_lower or 'list' in request_lower:
                return self.list_reminders()
            else:
                message = self._extract_reminder_message(user_request)
                return self.create_reminder(message)
        
        # Calendar requests
        elif any(word in request_lower for word in ['calendar', 'schedule', 'meeting', 'appointment', 'event']):
            if 'show' in request_lower or 'list' in request_lower:
                return self.list_events()
            else:
                title, date, time = self._extract_event_details(user_request)
                return self.create_calendar_event(title, date, time)
        
        # Email requests
        elif any(word in request_lower for word in ['email', 'send', 'mail']):
            if self.services_status.get("Email", False):
                # Extract email details
                import re
                match = re.search(r'to (.+?) with subject (.+?) and message (.+)', user_request, re.IGNORECASE)
                if match:
                    to_email = match.group(1).strip()
                    subject = match.group(2).strip()
                    message = match.group(3).strip()
                    
                    return self.send_email(to_email, subject, message)
                else:
                    return "📧 Please provide the email in the format: 'Send email to [email] with subject [subject] and message [message]'."
            else:
                return "📧 Email service not configured. Please add Gmail credentials to environment variables."
        
        # For all other requests, use Strands Agent
        else:
            return self.ask_agent(user_request)
    
    def _extract_reminder_message(self, text):
        """Extract the reminder message from user input"""
        message = text.lower()
        for phrase in ['remind me to', 'reminder to', 'remember to', 'remind me', 'create a reminder']:
            message = message.replace(phrase, '')
        
        return message.strip().capitalize()
    
    def _extract_event_details(self, text):
        """Extract event details from user input (simplified)"""
        title = "Meeting"  # Default title
        date = "Tomorrow"  # Default date
        time = "10:00 AM"  # Default time
        
        # Look for time patterns
        words = text.split()
        for i, word in enumerate(words):
            if any(time_word in word.lower() for time_word in ['am', 'pm', ':']):
                if i > 0:
                    time = f"{words[i-1]} {word}"
                else:
                    time = word
                break
        
        # Look for date patterns
        for word in words:
            if word.lower() in ['today', 'tomorrow', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']:
                date = word.title()
                break
        
        return title, date, time
    
    def sanitize_input(self, user_input):
        """Clean and validate user input for security"""
        dangerous_chars = ['<', '>', '&', '"', "'", '`']
        cleaned_input = user_input
        
        for char in dangerous_chars:
            cleaned_input = cleaned_input.replace(char, '')
        
        if len(cleaned_input) > 1000:
            cleaned_input = cleaned_input[:1000] + "..."
        
        return cleaned_input.strip()
    
    def is_safe_request(self, user_request):
        """Check if the user request is safe to process"""
        harmful_patterns = [
            'delete', 'remove', 'destroy', 'hack', 'exploit',
            'password', 'secret', 'private', 'confidential'
        ]
        
        request_lower = user_request.lower()
        for pattern in harmful_patterns:
            if pattern in request_lower:
                return False, f"Request contains potentially harmful content: '{pattern}'"
        
        return True, "Request is safe"
    
    def chat(self):
        """Enhanced chat interface with Strands-Agents integration"""
        print(f"\n💬 Chat with {self.name} (Strands-powered) - type 'quit' to exit")
        print("=" * 60)
        print("Try asking about weather, calculations, reminders, emails, or general questions!")
        print("Type 'help' to see all available commands.")
        print("🚀 Powered by Strands-Agents SDK")
        print("=" * 60)
        
        conversation_count = 0
        
        while True:
            try:
                user_input = input(f"\n[{conversation_count + 1}] You: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'bye', 'goodbye']:
                    print(f"\n{self.name}: Goodbye! It was great chatting with you! 👋")
                    print(f"We had {conversation_count} conversations. Come back anytime!")
                    break
                
                if not user_input:
                    print(f"{self.name}: I didn't catch that. Could you please say something?")
                    continue
                
                clean_input = self.sanitize_input(user_input)
                
                is_safe, safety_message = self.is_safe_request(clean_input)
                if not is_safe:
                    print(f"{self.name}: ⚠️  {safety_message}")
                    continue
                
                print(f"{self.name}: ", end="", flush=True)
                response = self.process_request(clean_input)
                print(response)
                
                conversation_count += 1
                
                if conversation_count % 5 == 0:
                    print(f"\n💡 Tip: I'm powered by Strands-Agents SDK! Type 'help' to see everything I can do!")
                
            except KeyboardInterrupt:
                print(f"\n\n{self.name}: Interrupted! Goodbye! 👋")
                break
            except Exception as e:
                print(f"\n{self.name}: ❌ Sorry, something went wrong: {str(e)}")
                print("Let's try again!")
    
    def start_agent(self):
        """Start the agent with a welcome message"""
        print("🚀 Starting your Strands-powered Intelligent AI Assistant...")
        print("=" * 70)
        print(f"Agent Name: {self.name}")
        print(f"Framework: Strands-Agents SDK")
        print(f"Status: Ready to help!")
        print("=" * 70)
        
        self._check_services()
        self.chat()


def main():
    """Main function to create and start the Strands-powered intelligent agent"""
    print("🤖 Intelligent AI Agent - Strands-Agents SDK Version")
    print("=" * 60)
    
    # Create your Strands-powered agent
    agent = StrandsBasicAgent("Buddy")
    
    # Start the agent
    agent.start_agent()


if __name__ == "__main__":
    main()