#!/usr/bin/env python3
"""Test weather API directly"""

import requests

# Test wttr.in API
location = "San Francisco"
url = f"https://wttr.in/{location}?format=j1"

print(f"Testing weather API for: {location}")
print(f"URL: {url}")

try:
    response = requests.get(url, timeout=10)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        current = data['current_condition'][0]
        
        print("\nWeather Data:")
        print(f"- Temperature: {current['temp_C']}°C ({current['temp_F']}°F)")
        print(f"- Feels like: {current['FeelsLikeC']}°C ({current['FeelsLikeF']}°F)")
        print(f"- Condition: {current['weatherDesc'][0]['value']}")
        print(f"- Humidity: {current['humidity']}%")
        print(f"- Wind: {current['windspeedKmph']} km/h {current['winddir16Point']}")
    else:
        print(f"Error: {response.text}")
        
except Exception as e:
    print(f"Exception: {e}")