from strands import Agent, tool
import requests
from typing import Dict, Optional
import os

@tool
def get_weather(city: str, country_code: Optional[str] = None) -> Dict[str, any]:
    """
    Get real-time weather information for a city using OpenWeatherMap API.
    
    Args:
        city: Name of the city to get weather for
        country_code: Optional 2-letter country code (e.g., 'US', 'GB') - optional dont use if not needed
        
    Returns:
        Dictionary containing current weather information
    """
    # You'll need to get an API key from openweathermap.org
    api_key = "89d3c1f4adc6d1c49259fa7ba18f24e7"
    
    if not api_key:
        return {
            "error": "OpenWeatherMap API key not found. Please set OPENWEATHER_API_KEY environment variable."
        }
    
    try:
        # Construct the query string
        query = city
        if country_code:
            query = f"{city},{country_code}"
        
        # Make API request
        url = f"http://api.openweathermap.org/data/2.5/weather?q={query}&appid={api_key}&units=metric"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        # Extract relevant information
        weather_info = {
            "city": data["name"],
            "country": data["sys"]["country"],
            "temperature": round(data["main"]["temp"], 1),
            "feels_like": round(data["main"]["feels_like"], 1),
            "condition": data["weather"][0]["main"],
            "description": data["weather"][0]["description"],
            "humidity": data["main"]["humidity"],
            "pressure": data["main"]["pressure"],
            "wind_speed": data.get("wind", {}).get("speed", 0),
            "wind_direction": data.get("wind", {}).get("deg", 0),
            "visibility": data.get("visibility", 0) / 1000,  # Convert to km
            "cloudiness": data["clouds"]["all"],
            "sunrise": data["sys"]["sunrise"],
            "sunset": data["sys"]["sunset"],
            "timezone": data["timezone"],
            "success": True
        }
        
        return weather_info
        
    except requests.exceptions.RequestException as e:
        return {
            "error": f"Failed to fetch weather data: {str(e)}",
            "success": False
        }
    except KeyError as e:
        return {
            "error": f"Unexpected response format: missing {str(e)}",
            "success": False
        }
    except Exception as e:
        return {
            "error": f"Unexpected error: {str(e)}",
            "success": False
        }

