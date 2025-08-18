#!/usr/bin/env python3
"""
Strands Weather Capability Lambda Function
AWS Lambda implementation of the weather analysis capability
"""

import json
import os
import boto3
import requests
from datetime import datetime
from typing import Dict, Any

def lambda_handler(event, context):
    """
    AWS Lambda handler for Strands Weather Capability
    """
    try:
        print(f"Received event: {json.dumps(event)}")
        
        # Extract parameters from Bedrock Agent event
        parameters = extract_parameters(event)
        city = parameters.get('city', os.environ.get('DEFAULT_CITY', 'New York'))
        
        # Get weather data
        weather_data = get_weather_data(city)
        
        # Analyze impact
        impact_analysis = analyze_weather_impact(weather_data)
        
        # Generate recommendations
        recommendations = generate_recommendations(weather_data, impact_analysis)
        
        # Store in DynamoDB (optional)
        store_weather_analysis(event, weather_data, impact_analysis)
        
        # Return response for Bedrock Agent
        response = {
            'success': True,
            'weather_data': weather_data,
            'impact_analysis': impact_analysis,
            'recommendations': recommendations,
            'city': city,
            'timestamp': datetime.now().isoformat()
        }
        
        return {
            'statusCode': 200,
            'body': json.dumps(response)
        }
        
    except Exception as e:
        print(f"Error in weather capability: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'success': False,
                'error': str(e),
                'message': 'Weather capability error'
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

def get_weather_data(city):
    """Get weather data from OpenWeatherMap API"""
    api_key = os.environ.get('OPENWEATHER_API_KEY')
    
    if not api_key:
        return get_simulated_weather_data(city)
    
    try:
        url = "http://api.openweathermap.org/data/2.5/weather"
        params = {
            'q': city,
            'appid': api_key,
            'units': 'metric'
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            return {
                'city': city,
                'temperature': data['main']['temp'],
                'feels_like': data['main']['feels_like'],
                'humidity': data['main']['humidity'],
                'description': data['weather'][0]['description'],
                'wind_speed': data['wind']['speed'],
                'visibility': data.get('visibility', 10000) / 1000,
                'pressure': data['main']['pressure'],
                'rain': data.get('rain', {}).get('1h', 0),
                'clouds': data['clouds']['all'],
                'source': 'OpenWeatherMap'
            }
        else:
            raise Exception(f"Weather API returned status {response.status_code}")
            
    except Exception as e:
        print(f"Weather API error: {str(e)}")
        return get_simulated_weather_data(city)

def get_simulated_weather_data(city):
    """Provide simulated weather data when API is unavailable"""
    return {
        'city': city,
        'temperature': 22,
        'feels_like': 20,
        'humidity': 65,
        'description': 'partly cloudy',
        'wind_speed': 3.5,
        'visibility': 10,
        'pressure': 1013,
        'rain': 0,
        'clouds': 40,
        'source': 'Simulated',
        'note': 'Using simulated data - configure OPENWEATHER_API_KEY for real data'
    }

def analyze_weather_impact(weather_data):
    """Analyze weather impact on activities"""
    temp = weather_data['temperature']
    description = weather_data['description'].lower()
    wind_speed = weather_data['wind_speed']
    rain = weather_data.get('rain', 0)
    
    # Calculate outdoor suitability score
    score = 100
    issues = []
    
    # Temperature analysis
    if temp < 0:
        score -= 40
        issues.append("freezing temperatures")
    elif temp < 5:
        score -= 20
        issues.append("very cold weather")
    elif temp > 35:
        score -= 30
        issues.append("extremely hot weather")
    elif temp > 30:
        score -= 15
        issues.append("hot weather")
    
    # Weather condition analysis
    if "rain" in description or rain > 0:
        score -= 35
        issues.append("rain expected")
    
    if "snow" in description:
        score -= 40
        issues.append("snow expected")
    
    if "storm" in description or "thunder" in description:
        score -= 50
        issues.append("storm conditions")
    
    # Wind analysis
    if wind_speed > 15:
        score -= 30
        issues.append("very strong winds")
    elif wind_speed > 10:
        score -= 20
        issues.append("strong winds")
    
    # Visibility analysis
    visibility = weather_data.get('visibility', 10)
    if visibility < 1:
        score -= 30
        issues.append("poor visibility")
    elif visibility < 5:
        score -= 15
        issues.append("reduced visibility")
    
    final_score = max(0, score)
    
    return {
        'outdoor_suitability_score': final_score,
        'suitability_rating': get_suitability_rating(final_score),
        'issues': issues,
        'analysis_factors': {
            'temperature': temp,
            'conditions': description,
            'wind_speed': wind_speed,
            'visibility': visibility
        }
    }

def get_suitability_rating(score):
    """Convert numeric score to rating"""
    if score >= 80:
        return "Excellent"
    elif score >= 60:
        return "Good"
    elif score >= 40:
        return "Fair"
    elif score >= 20:
        return "Poor"
    else:
        return "Very Poor"

def generate_recommendations(weather_data, impact_analysis):
    """Generate weather-based recommendations"""
    recommendations = []
    temp = weather_data['temperature']
    issues = impact_analysis['issues']
    
    # Temperature recommendations
    if temp < 0:
        recommendations.append("🧥 Bundle up with warm layers and winter gear")
        recommendations.append("❄️ Be cautious of icy conditions")
    elif temp < 10:
        recommendations.append("🧥 Dress warmly with layers")
    elif temp > 30:
        recommendations.append("🌞 Stay hydrated and seek shade frequently")
        recommendations.append("🧴 Use sunscreen and wear light clothing")
    
    # Weather condition recommendations
    if "rain expected" in issues:
        recommendations.append("☔ Bring an umbrella or raincoat")
        recommendations.append("🚗 Allow extra travel time")
    
    if "snow expected" in issues:
        recommendations.append("❄️ Wear appropriate winter footwear")
        recommendations.append("🚗 Drive carefully and allow extra time")
    
    if "storm conditions" in issues:
        recommendations.append("⚡ Avoid outdoor activities")
        recommendations.append("🏠 Stay indoors if possible")
    
    if "strong winds" in issues or "very strong winds" in issues:
        recommendations.append("💨 Secure loose items outdoors")
        recommendations.append("🌳 Be cautious around trees")
    
    # General recommendations based on score
    score = impact_analysis['outdoor_suitability_score']
    if score >= 70:
        recommendations.append("🌤️ Great weather for outdoor activities!")
    elif score >= 40:
        recommendations.append("🤔 Consider indoor alternatives for extended outdoor time")
    else:
        recommendations.append("🏠 Strongly recommend indoor activities")
    
    return recommendations

def store_weather_analysis(event, weather_data, impact_analysis):
    """Store weather analysis in DynamoDB (optional)"""
    try:
        dynamodb = boto3.resource('dynamodb')
        table_name = os.environ.get('WEATHER_ANALYSIS_TABLE')
        
        if not table_name:
            return  # Skip if no table configured
        
        table = dynamodb.Table(table_name)
        
        table.put_item(
            Item={
                'session_id': event.get('sessionId', 'unknown'),
                'timestamp': datetime.now().isoformat(),
                'city': weather_data['city'],
                'weather_data': json.dumps(weather_data),
                'impact_analysis': json.dumps(impact_analysis),
                'ttl': int(datetime.now().timestamp()) + 86400  # 24 hours TTL
            }
        )
        
    except Exception as e:
        print(f"Error storing weather analysis: {str(e)}")
        # Don't fail the main function for storage errors

# For local testing
if __name__ == "__main__":
    test_event = {
        'parameters': [
            {'name': 'city', 'value': 'London'}
        ],
        'sessionId': 'test-session'
    }
    
    result = lambda_handler(test_event, None)
    print(json.dumps(result, indent=2))