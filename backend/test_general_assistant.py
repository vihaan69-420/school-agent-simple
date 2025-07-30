#!/usr/bin/env python3
"""Test script for General Assistant API"""

import requests
import json

# Test the General Assistant
url = "http://localhost:8000/api/chat"

# Test query
test_query = "What is the weather today in San Francisco?"

payload = {
    "messages": [
        {
            "role": "user", 
            "content": test_query
        }
    ],
    "session_id": "test_session",
    "model": "general"
}

headers = {
    "Content-Type": "application/json"
}

print(f"Testing General Assistant with query: {test_query}")
print(f"Payload: {json.dumps(payload, indent=2)}")

try:
    response = requests.post(url, json=payload, headers=headers)
    print(f"\nStatus Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"Error: {e}")