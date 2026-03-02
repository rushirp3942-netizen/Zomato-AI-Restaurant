import requests
import json
import time
import subprocess
import os

def test_api():
    print("Starting API Integration Test...")
    
    # Base URL
    url = "http://127.0.0.1:8000"
    
    # 1. Test Health Check
    print("\n1. Testing /health endpoint...")
    try:
        response = requests.get(f"{url}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Health check failed: {e}")
        return

    # 2. Test Recommendation
    print("\n2. Testing /recommend endpoint...")
    payload = {
        "query": "I am looking for a high-rated Chinese restaurant in Bangalore under 1000 rupees."
    }
    
    try:
        start_time = time.time()
        response = requests.post(f"{url}/recommend", json=payload)
        end_time = time.time()
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"AI Recommendation received in {end_time - start_time:.2f} seconds.")
            print("-" * 30)
            try:
                print(data['recommendation'])
            except UnicodeEncodeError:
                print(data['recommendation'].encode('utf-8').decode('ascii', 'ignore'))
            print("-" * 30)
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Recommendation test failed: {e}")

if __name__ == "__main__":
    test_api()
