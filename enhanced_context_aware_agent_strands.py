#!/usr/bin/env python3
"""
Enhanced Context-Aware Agent using Strands-Agents SDK
Multi-agent system with specialized agents for different domains
Migrated from the original enhanced_context_aware_agent.py
"""

import os
import json
from datetime import datetime
from strands import Agent
from strands_tools import calculator
from strands.models.openai import OpenAIModel
from strands.models.anthropic import AnthropicModel
from strands.models.bedrock import BedrockModel
from weather_tool import get_weather
from bible_verse_tool import get_daily_bible_verse, get_bible_verse_for_posting
from x_posting_tool import post_to_x, get_x_account_info
from google_calendar_tool import create_calendar_event, get_calendar_events, update_calendar_event, delete_calendar_event
from basic_agent_strands import StrandsBasicAgent


class StrandsWeatherAgent:
    """Specialized weather agent using Strands-Agents SDK"""
    
    def __init__(self, parent_agent):
        self.parent = parent_agent
        self.name = "WeatherBot"
        
        # Create specialized weather agent with custom weather tool
        self.agent = Agent(
            tools=[calculator, get_weather],
            system_prompt="""You are a weather specialist agent. You have access to real-time weather data via the get_weather tool.
            Use the weather tool to get current conditions and provide detailed analysis including temperature, conditions,
            and recommendations for outdoor activities. Always use the weather tool when asked about weather conditions."""
        )
    
    def analyze_weather_impact(self, city):
        """Analyze weather and its impact on activities"""
        try:
            query = f"Analyze the weather in {city} and provide recommendations for outdoor activities. Include temperature, conditions, and suitability rating."
            
            response = self.agent(query)
            
            # Store in parent's context memory
            weather_data = {
                "city": city,
                "analysis": response,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "agent": self.name
            }
            
            if "weather_analysis" not in self.parent.context_memory:
                self.parent.context_memory["weather_analysis"] = []
            self.parent.context_memory["weather_analysis"].append(weather_data)
            
            return weather_data
            
        except Exception as e:
            return {"error": f"Weather analysis error: {str(e)}"}


class StrandsCalendarAgent:
    """Specialized calendar agent using Strands-Agents SDK with Google Calendar integration"""
    
    def __init__(self, parent_agent):
        self.parent = parent_agent
        self.name = "CalendarBot"
        
        # Create specialized calendar agent with Google Calendar tools
        self.agent = Agent(
            tools=[create_calendar_event, get_calendar_events, update_calendar_event, delete_calendar_event],
            system_prompt="""You are a calendar and scheduling specialist agent with Google Calendar integration.
            You can create, read, update, and delete calendar events using Google Calendar API.
            Help with event management, conflict detection, and schedule optimization.
            Use the Google Calendar tools to manage real calendar events instead of in-memory storage."""
        )
    
    def check_weather_conflicts(self, weather_info):
        """Check for calendar conflicts based on weather conditions using Google Calendar"""
        try:
            # Get real events from Google Calendar
            events_result = get_calendar_events(7)  # Get next 7 days of events
            
            if "No upcoming events" in events_result:
                return "📅 No calendar events to check for weather conflicts."
            
            weather_text = weather_info.get("analysis", "Weather information not available")
            
            query = f"""
            Analyze these calendar events for weather-related conflicts:
            
            Events from Google Calendar:
            {events_result}
            
            Weather Analysis:
            {weather_text}
            
            Identify any outdoor events that might be affected by weather conditions and suggest alternatives.
            """
            
            response = self.agent(query)
            
            # Store analysis in context memory
            conflict_analysis = {
                "analysis": response,
                "events_source": "Google Calendar",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "agent": self.name
            }
            
            if "calendar_conflicts" not in self.parent.context_memory:
                self.parent.context_memory["calendar_conflicts"] = []
            self.parent.context_memory["calendar_conflicts"].append(conflict_analysis)
            
            return f"📅 Calendar Conflict Analysis:\n{response}"
            
        except Exception as e:
            return f"❌ Calendar conflict analysis error: {str(e)}"
    
    def process_calendar_request(self, user_request):
        """Process calendar-related requests with Google Calendar integration"""
        try:
            request_lower = user_request.lower()
            
            # Check if it's a list/show request
            if any(word in request_lower for word in ['show', 'list', 'display', 'events', 'schedule']):
                return get_calendar_events(7)
            
            # Check if it's a create event request
            elif any(word in request_lower for word in ['create', 'schedule', 'add', 'meeting', 'appointment']):
                # Extract event details using AI
                query = f"""
                Extract event details from this request: {user_request}
                
                Provide the following information:
                - Title: [event title]
                - Start time: [YYYY-MM-DDTHH:MM:SS format]
                - End time: [YYYY-MM-DDTHH:MM:SS format]
                - Description: [optional description]
                - Location: [optional location]
                
                If specific times aren't provided, suggest reasonable defaults.
                """
                
                ai_response = self.agent(query)
                
                # For now, return AI analysis and suggest manual creation
                return f"""
🤖 AI Analysis of Calendar Request:
{ai_response}

💡 To create this event in Google Calendar, please provide:
• Event title
• Start time (YYYY-MM-DDTHH:MM:SS format)
• End time (YYYY-MM-DDTHH:MM:SS format)
• Description (optional)
• Location (optional)

Example: "Create event 'Team Meeting' from '2024-01-15T10:00:00' to '2024-01-15T11:00:00' with description 'Weekly team sync' at 'Conference Room A'"
                """.strip()
            
            # For other requests, use AI analysis
            else:
                query = f"""
                Process this calendar request and provide appropriate guidance:
                
                Request: {user_request}
                
                Available Google Calendar actions:
                - Create event (create_calendar_event)
                - List events (get_calendar_events)
                - Update event (update_calendar_event)
                - Delete event (delete_calendar_event)
                
                Provide clear guidance on how to accomplish the user's request.
                """
                
                response = self.agent(query)
                return f"📅 Calendar Assistant:\n{response}"
            
        except Exception as e:
            return f"❌ Calendar processing error: {str(e)}"


class StrandsEmailAgent:
    """Specialized email agent using Strands-Agents SDK"""
    
    def __init__(self, parent_agent):
        self.parent = parent_agent
        self.name = "EmailBot"
        
        # Create specialized email agent
        self.agent = Agent(
            system_prompt="""You are an email specialist agent. Help compose professional emails, 
            analyze email requests, and provide email management assistance. Focus on clear communication and proper formatting."""
        )
    
    def process_email_request(self, user_request, context_memory):
        """Process email requests with contextual awareness"""
        try:
            # Use Strands Agent to analyze email request
            context_info = ""
            if context_memory:
                recent_activities = []
                for key, value in context_memory.items():
                    if isinstance(value, list) and value:
                        recent_activities.append(f"{key}: {len(value)} items")
                    elif isinstance(value, dict) and value:
                        recent_activities.append(f"{key}: available")
                
                if recent_activities:
                    context_info = f"Recent context: {', '.join(recent_activities)}"
            
            query = f"""
            Analyze this email request and provide assistance:
            
            Request: {user_request}
            Context: {context_info}
            
            Help with:
            - Email composition
            - Subject line suggestions
            - Professional formatting
            - Recipient analysis
            
            Provide clear guidance for sending the email.
            """
            
            response = self.agent(query)
            
            # Check if user wants to actually send an email
            if self.parent.services_status.get("Email", False):
                return f"{response}\n\n💡 To send an email, use format: 'Send email to [email] with subject [subject] and message [message]'"
            else:
                return f"{response}\n\n❌ Email service not configured. Please add Gmail credentials."
            
        except Exception as e:
            return f"❌ Email processing error: {str(e)}"


class StrandsDecisionAgent:
    """Specialized decision-making agent using Strands-Agents SDK"""
    
    def __init__(self, parent_agent):
        self.parent = parent_agent
        self.name = "DecisionBot"
        
        # Create specialized decision agent
        self.agent = Agent(
            system_prompt="""You are a decision-making specialist agent. Analyze complex situations, 
            weigh pros and cons, and provide intelligent recommendations based on multiple factors. 
            Focus on practical, actionable advice."""
        )
    
    def make_weather_decision(self, weather_info, calendar_conflicts):
        """Make intelligent decisions based on weather and calendar data"""
        try:
            weather_text = weather_info.get("analysis", "No weather data")
            
            query = f"""
            Make intelligent recommendations based on this information:
            
            Weather Analysis:
            {weather_text}
            
            Calendar Conflicts:
            {calendar_conflicts}
            
            Provide:
            1. Key insights
            2. Recommended actions
            3. Alternative suggestions
            4. Risk assessment
            
            Focus on practical, actionable advice.
            """
            
            response = self.agent(query)
            
            # Store decision in context memory
            decision_record = {
                "decision": response,
                "factors": ["weather", "calendar"],
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "agent": self.name
            }
            
            if "decisions" not in self.parent.context_memory:
                self.parent.context_memory["decisions"] = []
            self.parent.context_memory["decisions"].append(decision_record)
            
            return f"🧠 Intelligent Recommendations:\n{response}"
            
        except Exception as e:
            return f"❌ Decision analysis error: {str(e)}"


class StrandsSocialMediaAgent:
    """Specialized social media agent using Strands-Agents SDK with X (Twitter) integration"""
    
    def __init__(self, parent_agent):
        self.parent = parent_agent
        self.name = "SocialBot"
        
        # Create specialized social media agent with X posting and Bible verse tools
        self.agent = Agent(
            tools=[calculator, get_daily_bible_verse, post_to_x, get_x_account_info],
            system_prompt="""You are a social media specialist agent with X (Twitter) posting capabilities.
            You can get Bible verses, post to X, and check X account info. Help with content creation,
            trend analysis, and social media strategy. When users ask to post Bible verses, use the
            get_bible_verse tool to fetch a verse and post_to_x tool to share it."""
        )
    
    def post_bible_verse(self):
        """Get a Bible verse and post it to X"""
        try:
            # Get a Bible verse
            verse_result = get_bible_verse_for_posting()
            post_result = ""
            post_content = ""

            if "❌" in verse_result:
                return f"❌ Unable to fetch Bible verse:\n{verse_result}"
                        
            
            # Create a concise post for X (280 character limit)
            if verse_result:
                post_content = f'"{verse_result}"  #BibleVerse #Faith #Inspiration'                  
            
            # Post to X
            print("📱 Posting to X (Twitter):")
            print(post_content)
            post_result = post_to_x(post_content)

            
            return f"""
📖 Bible Verse Retrieved:
{verse_result}

📱 X Posting Result:
{post_result}
            """.strip()
            
        except Exception as e:
            return f"❌ Error posting Bible verse: {str(e)}"
    
    def analyze_trends(self):
        """Analyze current trends using web search"""
        try:
            query = "Search for current trending topics and provide a summary of what's popular right now"
            
            response = self.agent(query)
            
            # Store in context memory
            trend_analysis = {
                "analysis": response,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "agent": self.name
            }
            
            if "social_trends" not in self.parent.context_memory:
                self.parent.context_memory["social_trends"] = []
            self.parent.context_memory["social_trends"].append(trend_analysis)
            
            return f"📱 Current Trends Analysis:\n{response}"
            
        except Exception as e:
            return f"❌ Trends analysis error: {str(e)}"
    
    def generate_content(self, topic):
        """Generate social media content"""
        try:
            query = f"Create engaging social media content about: {topic}. Provide multiple options with different tones (professional, casual, inspirational)."
            
            response = self.agent(query)
            
            return f"📝 Content Suggestions:\n{response}"
            
        except Exception as e:
            return f"❌ Content generation error: {str(e)}"
    
    def check_x_status(self):
        """Check X account connection status"""
        try:
            return get_x_account_info()
        except Exception as e:
            return f"❌ Error checking X status: {str(e)}"


class StrandsEnhancedContextAwareAgent(StrandsBasicAgent):
    """
    Enhanced context-aware agent using Strands-Agents SDK
    Multi-agent system with specialized agents for different domains
    """
    
    def __init__(self, name="Buddy"):
        super().__init__(name)
        self.context_memory = {}
        self.decision_history = []
        self.specialist_agents = {}
        self.setup_specialist_agents()
        
        # Override the basic agent with enhanced capabilities
        self.agent = self._initialize_enhanced_agent()
    
    def _initialize_enhanced_agent(self):
        """Initialize enhanced Strands Agent with multi-agent coordination"""
        try:
            # Enhanced tools - calculator, weather, Bible verse, X posting, and Google Calendar tools
            available_tools = [
                calculator,
                get_weather,
                get_daily_bible_verse,
                post_to_x,
                get_x_account_info,
                create_calendar_event,
                get_calendar_events,
                update_calendar_event,
                delete_calendar_event
            ]
            
            # Enhanced system prompt for coordination
            system_prompt = """You are an enhanced AI assistant that coordinates with specialized agents.
            You have access to calculator, weather, Bible verse, X posting, and Google Calendar tools.
            Use the get_weather tool for real-time weather data, get_bible_verse for daily inspiration,
            post_to_x for social media posting, and Google Calendar tools for event management.
            You can handle complex, multi-domain requests by leveraging weather analysis, calendar management,
            email assistance, decision-making, and social media insights.
            
            When users ask complex questions, break them down and coordinate with appropriate specialist agents.
            Provide comprehensive, contextual responses that consider multiple factors."""
            
            # Get model configuration
            model_config = self._get_model_config()
            
            agent = Agent(
                tools=available_tools,
                system_prompt=system_prompt,
                model=model_config
            )
            
            print(f"✅ Enhanced Strands Agent initialized with {len(available_tools)} tools")
            return agent
            
        except Exception as e:
            print(f"⚠️ Error initializing Enhanced Strands Agent: {str(e)}")
            return super()._initialize_strands_agent()
    
    def setup_specialist_agents(self):
        """Create specialized sub-agents using Strands-Agents SDK"""
        self.specialist_agents = {
            "weather": StrandsWeatherAgent(self),
            "calendar": StrandsCalendarAgent(self),
            "email": StrandsEmailAgent(self),
            "decision": StrandsDecisionAgent(self),
            "social": StrandsSocialMediaAgent(self)
        }
        
        print(f"🤖 Initialized {len(self.specialist_agents)} Strands specialist agents:")
        print("   • Weather Agent - Weather analysis and impact assessment")
        print("   • Calendar Agent - Schedule management and conflict detection")
        print("   • Email Agent - Contextual email composition and management")
        print("   • Decision Agent - Cross-domain reasoning and recommendations")
        print("   • Social Media Agent - Content creation and trend analysis")
    
    def process_request_enhanced(self, user_request):
        """Enhanced request processing with multi-agent coordination"""
        request_lower = user_request.lower()
        
        # Weather requests with context awareness
        if any(word in request_lower for word in ['weather', 'temperature', 'forecast', 'rain', 'sunny', 'cloudy']):
            weather_agent = self.specialist_agents["weather"]
            calendar_agent = self.specialist_agents["calendar"]
            decision_agent = self.specialist_agents["decision"]
            
            # Extract city or use default
            city = self._extract_city_from_request(user_request) or os.getenv("DEFAULT_CITY", "New York")
            
            # Get weather analysis
            weather_info = weather_agent.analyze_weather_impact(city)
            
            if weather_info and "error" not in weather_info:
                # # Check calendar conflicts
                # calendar_conflicts = calendar_agent.check_weather_conflicts(weather_info)
                
                # # Get decision recommendations
                # recommendations = decision_agent.make_weather_decision(weather_info, calendar_conflicts)
                
                # return f"{weather_info['analysis']}\n\n{calendar_conflicts}\n\n{recommendations}"
                return f"{weather_info['analysis']}\n"
            else:
                return f"❌ Unable to analyze weather for {city}. Please check your weather API configuration."
        
        # Social media and trends requests
        elif any(phrase in request_lower for phrase in [
            'trends', 'trending', 'social media', 'content', 'post', 'what\'s popular', 'bible verse'
        ]):
            social_agent = self.specialist_agents["social"]
            
            # Bible verse posting
            if any(phrase in request_lower for phrase in ['post bible verse', 'bible verse', 'daily verse', 'scripture']):
                return social_agent.post_bible_verse()
            elif any(word in request_lower for word in ['trends', 'trending', 'popular']):
                return social_agent.analyze_trends()
            elif any(word in request_lower for word in ['content', 'post', 'create']):
                # Extract topic for content creation
                topic = user_request.replace('create content about', '').replace('post about', '').strip()
                if not topic:
                    topic = "general inspiration"
                return social_agent.generate_content(topic)
            elif 'x status' in request_lower or 'twitter status' in request_lower:
                return social_agent.check_x_status()
            else:
                return social_agent.analyze_trends()
        
        # Email requests with context
        elif any(phrase in request_lower for phrase in ['send email', 'email', 'compose email']):
            email_agent = self.specialist_agents["email"]
            return email_agent.process_email_request(user_request, self.context_memory)
        
        # Calendar requests with AI assistance
        elif any(word in request_lower for word in ['calendar', 'schedule', 'meeting', 'appointment', 'event']):
            calendar_agent = self.specialist_agents["calendar"]
            return calendar_agent.process_calendar_request(user_request)
        
        # Complex decision-making requests
        elif any(phrase in request_lower for phrase in [
            'should i', 'what do you recommend', 'help me decide', 'advice', 'suggestion'
        ]):
            decision_agent = self.specialist_agents["decision"]
            
            # Use decision agent for complex recommendations
            query = f"Provide intelligent advice and recommendations for: {user_request}"
            return decision_agent.agent(query)
        
        # Daily summary with multi-agent coordination
        elif any(phrase in request_lower for phrase in ['daily summary', 'daily briefing', 'overview']):
            return self._generate_enhanced_daily_summary()
        
        # Context memory queries
        elif any(word in request_lower for word in ['remember', 'recall', 'context', 'history']):
            return self._query_enhanced_context_memory(user_request)
        
        # For all other requests, use the enhanced main agent
        else:
            return self.ask_agent(user_request)
    
    def _extract_city_from_request(self, request):
        """Extract city name from weather request"""
        import re
        
        patterns = [
            r'weather in ([a-zA-Z\s]+)',
            r'weather for ([a-zA-Z\s]+)',
            r'forecast for ([a-zA-Z\s]+)',
            r'temperature in ([a-zA-Z\s]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, request, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return None
    
    def _generate_enhanced_daily_summary(self):
        """Generate comprehensive daily summary using multiple agents"""
        try:
            summary_parts = []
            
            # Weather summary
            weather_agent = self.specialist_agents["weather"]
            city = os.getenv("DEFAULT_CITY", "New York")
            weather_info = weather_agent.analyze_weather_impact(city)
            
            if weather_info and "error" not in weather_info:
                summary_parts.append(f"🌤️ Weather Update:\n{weather_info['analysis']}")
            
            # Calendar summary
            events = self.memory.get("events", [])
            if events:
                summary_parts.append(f"📅 Today's Schedule:\n{len(events)} events planned")
            
            # Social media trends
            social_agent = self.specialist_agents["social"]
            try:
                trends = social_agent.analyze_trends()
                summary_parts.append(f"📱 Current Trends:\n{trends}")
            except:
                summary_parts.append("📱 Trends: Unable to fetch current trends")
            
            # Context memory summary
            context_summary = f"🧠 Context Memory: {len(self.context_memory)} active contexts"
            summary_parts.append(context_summary)
            
            daily_summary = f"""
🌅 Enhanced Daily Summary - {datetime.now().strftime('%A, %B %d, %Y')}
{'=' * 60}

{chr(10).join(summary_parts)}

{'=' * 60}
🚀 Powered by Strands-Agents Multi-Agent System
📊 Summary generated at: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
            """.strip()
            
            return daily_summary
            
        except Exception as e:
            return f"❌ Error generating enhanced daily summary: {str(e)}"
    
    def _query_enhanced_context_memory(self, query):
        """Query enhanced context memory with AI assistance"""
        try:
            decision_agent = self.specialist_agents["decision"]
            
            # Prepare context information
            context_info = []
            for key, value in self.context_memory.items():
                if isinstance(value, list):
                    context_info.append(f"{key}: {len(value)} items")
                elif isinstance(value, dict):
                    context_info.append(f"{key}: {value.get('timestamp', 'unknown time')}")
                else:
                    context_info.append(f"{key}: {str(value)[:100]}...")
            
            context_text = "\n".join(context_info) if context_info else "No context memory available"
            
            ai_query = f"""
            Analyze this context memory query and provide relevant information:
            
            User Query: {query}
            
            Available Context:
            {context_text}
            
            Provide a helpful summary of relevant context information.
            """
            
            response = decision_agent.agent(ai_query)
            
            return f"🧠 Enhanced Context Memory Analysis:\n{response}"
            
        except Exception as e:
            return f"❌ Error querying enhanced context memory: {str(e)}"
    
    def show_help(self):
        """Enhanced help with multi-agent capabilities"""
        help_text = f"""
🤖 Hi! I'm {self.name}, your Enhanced Strands-powered AI assistant with multi-agent capabilities!

🚀 **Multi-Agent System Features**:
   • Weather Agent - Advanced weather analysis and activity recommendations
   • Calendar Agent - Intelligent scheduling and conflict detection  
   • Email Agent - Contextual email composition and management
   • Decision Agent - Cross-domain reasoning and smart recommendations
   • Social Media Agent - Content creation and trend analysis

🧮 **Built-in Tools (via Strands-Agents SDK)**:
   • Calculator - "What's 15 * 23?" or "Calculate compound interest"
   • Weather - "What's the weather in Paris?" (enhanced with impact analysis)
   • Bible Verses - "Get a Bible verse" or "Post a Bible verse"
   • X (Twitter) - "Post to X" or "Check X status"
   • Google Calendar - "Create event", "Show events", "Update event"

🌤️ **Enhanced Weather**:
   • "What's the weather in Tokyo?" - Gets weather + activity recommendations + calendar conflicts
   • "Should I go hiking today?" - Weather analysis with decision support

📱 **Social Media & X Integration**:
   • "Post a Bible verse" - Get daily Bible verse and post to X
   • "What's trending now?" - Current trend analysis
   • "Create content about AI" - Generate engaging social media posts
   • "Check X status" - Verify X account connection
   • "Help me with social media strategy" - Professional content guidance

📝 **Google Calendar Integration**:
   • "Show my events" - View upcoming Google Calendar events
   • "Create event 'Meeting' from '2024-01-15T10:00:00' to '2024-01-15T11:00:00'" - Create real calendar events
   • "Check for conflicts in my schedule" - Intelligent conflict detection with real calendar data
   • "Update my meeting" - Modify existing calendar events

📧 **Contextual Email**:
   • "Help me write a professional email" - AI-powered email composition
   • "Send email to colleague about project update" - Context-aware messaging

🧠 **Intelligent Decision Making**:
   • "Should I reschedule my outdoor event?" - Multi-factor analysis
   • "What do you recommend for my schedule?" - Smart suggestions
   • "Help me decide between options" - Decision support

📊 **Enhanced Summaries**:
   • "Daily summary" - Comprehensive briefing with weather, calendar, trends
   • "What do you remember about our conversations?" - Context memory analysis

💬 **General AI Assistance**:
   • Ask complex questions that require multi-domain analysis
   • Get contextual responses that consider multiple factors
   • Benefit from coordinated specialist agent insights

🔧 **System Commands**:
   • "Check services" - See all agent and service status
   • "Help" - Show this enhanced help message

🚀 **Powered by Strands-Agents Multi-Agent Framework** - The future of AI assistance!

Just tell me what you need - I'll coordinate with my specialist agents to provide the best possible help!
        """.strip()
        
        return help_text
    
    def get_service_status(self):
        """Enhanced service status with multi-agent information"""
        status_report = super().get_service_status()
        
        status_report += f"\n🤖 Multi-Agent System Status:\n"
        for agent_name, agent in self.specialist_agents.items():
            status_report += f"   ✅ {agent_name.title()} Agent ({agent.name}): Active\n"
        
        status_report += f"\n🧠 Context Memory: {len(self.context_memory)} active contexts\n"
        status_report += f"📊 Decision History: {len(self.decision_history)} decisions recorded\n"
        
        return status_report
    
    def process_request(self, user_request):
        """Override to use enhanced multi-agent processing"""
        return self.process_request_enhanced(user_request)


def main():
    """Interactive demo of the enhanced Strands-powered context-aware agent"""
    print("🤖 Enhanced Context-Aware Agent - Strands-Agents Multi-Agent System")
    print("=" * 80)
    
    agent = StrandsEnhancedContextAwareAgent("Buddy")
    
    try:
        print("\n💡 Enhanced Multi-Agent Commands:")
        print("• 'What's the weather in London?' - Weather analysis with recommendations")
        print("• 'What's trending now?' - Current trend analysis")
        print("• 'Create content about technology' - Social media content generation")
        print("• 'Should I reschedule my meeting?' - Intelligent decision support")
        print("• 'Daily summary' - Comprehensive multi-agent briefing")
        print("• 'Help me decide between options' - Cross-domain reasoning")
        print("• 'Check services' - Multi-agent system status")
        print("• 'quit' - Exit the demo")
        
        print("\n🎯 Multi-Agent Interactive Mode - Enter commands or 'quit' to exit:")
        
        while True:
            try:
                user_input = input("\nYou: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("👋 Goodbye from the multi-agent team!")
                    break
                
                if not user_input:
                    continue
                
                print(f"Buddy: ", end="")
                result = agent.process_request(user_input)
                print(result)
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye from the multi-agent team!")
                break
            except EOFError:
                print("\n👋 Goodbye from the multi-agent team!")
                break
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")


if __name__ == "__main__":
    main()