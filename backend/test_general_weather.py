#!/usr/bin/env python3
"""Test script for General Assistant API with weather query"""

import requests
import json

# Test the General Assistant
url = "http://localhost:8000/api/chat"

# Test weather query
test_queries = [
    "What is the weather today in San Francisco?",
    "Tell me the current temperature in Tokyo",
    "What's the latest news about AI?",
    "What day is it today?",
    "Who is the current president of the United States?"
]

headers = {
    "Content-Type": "application/json"
}

for query in test_queries:
    print(f"\n{'='*60}")
    print(f"Query: {query}")
    print(f"{'='*60}")
    
    payload = {
        "messages": [
            {
                "role": "user", 
                "content": query
            }
        ],
        "session_id": f"test_session_{query[:10]}",
        "model": "general"
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\nResponse: {data['message']}")
            if data.get('sources'):
                print(f"\nSources: {data['sources']}")
            if data.get('metadata', {}).get('features_used'):
                print(f"Features used: {data['metadata']['features_used']}")
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Error: {e}")