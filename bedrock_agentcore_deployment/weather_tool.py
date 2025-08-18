#!/usr/bin/env python3
"""
Custom Weather Tool for Strands-Agents SDK
Uses OpenWeatherMap API to fetch real weather data
"""

import os
import requests
from strands import tool


@tool
def get_weather(city: str) -> str:
    """
    Get current weather information for a specified city using OpenWeatherMap API.
    
    Args:
        city: The name of the city to get weather for
        
    Returns:
        A formatted string with weather information including temperature, 
        conditions, humidity, and recommendations
    """
    api_key = os.getenv("WEATHER_API_KEY")
    
    if not api_key:
        return f"""
🌤️ Weather information for {city}:
❌ Weather API key not configured. 
💡 To get real weather data, please:
1. Get a free API key from https://openweathermap.org/api
2. Set environment variable: export WEATHER_API_KEY="your-key-here"

For now, here's general weather advice for {city}:
• Check local weather services for current conditions
• Always be prepared for changing weather
• Consider indoor alternatives for outdoor activities
        """.strip()
    
    try:
        # OpenWeatherMap API endpoint
        url = "http://api.openweathermap.org/data/2.5/weather"
        params = {
            "q": city,
            "appid": api_key,
            "units": "metric"  # Use Celsius
        }
        
        print(f"🌤️ Fetching weather data for {city}...")
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            # Extract weather information
            temp = data["main"]["temp"]
            feels_like = data["main"]["feels_like"]
            humidity = data["main"]["humidity"]
            description = data["weather"][0]["description"]
            wind_speed = data["wind"]["speed"]
            pressure = data["main"]["pressure"]
            
            # Get weather advice
            advice = _get_weather_advice(temp, description)
            
            # Format the response
            weather_report = f"""
🌤️ Current Weather in {city.title()}:
• Temperature: {temp}°C (feels like {feels_like}°C)
• Condition: {description.title()}
• Humidity: {humidity}%
• Wind Speed: {wind_speed} m/s
• Pressure: {pressure} hPa

{advice}

📊 Weather data provided by OpenWeatherMap
            """.strip()
            
            return weather_report
            
        elif response.status_code == 404:
            return f"❌ Sorry, I couldn't find weather data for '{city}'. Please check the city name and try again."
        elif response.status_code == 401:
            return f"❌ Weather API authentication failed. Please check your WEATHER_API_KEY."
        else:
            return f"❌ Weather service error (HTTP {response.status_code}). Please try again later."
            
    except requests.exceptions.Timeout:
        return f"❌ Weather service is taking too long to respond for {city}. Please try again."
    except requests.exceptions.RequestException as e:
        return f"❌ Network error while fetching weather for {city}: {str(e)}"
    except Exception as e:
        return f"❌ Unexpected error getting weather for {city}: {str(e)}"


def _get_weather_advice(temp: float, description: str) -> str:
    """
    Provide helpful advice based on weather conditions.
    
    Args:
        temp: Temperature in Celsius
        description: Weather description
        
    Returns:
        Formatted advice string
    """
    advice_parts = []
    
    # Temperature advice
    if temp < 0:
        advice_parts.append("🧥 It's freezing! Bundle up with warm layers and stay safe.")
    elif temp < 5:
        advice_parts.append("🧥 Very cold - wear a heavy coat and warm accessories.")
    elif temp < 10:
        advice_parts.append("🧥 Pretty cold - you'll want a warm jacket.")
    elif temp < 15:
        advice_parts.append("👕 Cool weather - a light jacket or sweater recommended.")
    elif temp < 25:
        advice_parts.append("👕 Pleasant temperature - comfortable for most activities.")
    elif temp < 30:
        advice_parts.append("☀️ Warm weather - great for outdoor activities!")
    else:
        advice_parts.append("🌡️ Very hot! Stay hydrated, seek shade, and avoid prolonged sun exposure.")
    
    # Condition-specific advice
    description_lower = description.lower()
    if "rain" in description_lower or "drizzle" in description_lower:
        advice_parts.append("☔ Don't forget an umbrella or rain jacket!")
    elif "snow" in description_lower:
        advice_parts.append("❄️ Watch out for slippery conditions and dress warmly!")
    elif "thunderstorm" in description_lower or "storm" in description_lower:
        advice_parts.append("⛈️ Thunderstorms expected - stay indoors if possible!")
    elif "fog" in description_lower or "mist" in description_lower:
        advice_parts.append("🌫️ Foggy conditions - drive carefully with reduced visibility!")
    elif "clear" in description_lower or "sunny" in description_lower:
        advice_parts.append("☀️ Clear skies - perfect weather for outdoor activities!")
    elif "cloud" in description_lower:
        advice_parts.append("☁️ Cloudy conditions - still good for most outdoor activities!")
    
    # Activity recommendations
    if temp >= 15 and temp <= 25 and "rain" not in description_lower and "storm" not in description_lower:
        advice_parts.append("🚶‍♂️ Great weather for walking, jogging, or outdoor sports!")
    elif temp < 5 or "storm" in description_lower or "rain" in description_lower:
        advice_parts.append("🏠 Consider indoor activities today.")
    
    return " ".join(advice_parts)


# Test function for development
def test_weather_tool():
    """Test the weather tool functionality"""
    print("Testing weather tool...")
    
    # Test with a known city
    result = get_weather("London")
    print("London weather:")
    print(result)
    print("\n" + "="*50 + "\n")
    
    # Test with invalid city
    result = get_weather("InvalidCityName123")
    print("Invalid city test:")
    print(result)


if __name__ == "__main__":
    test_weather_tool()