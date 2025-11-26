#!/usr/bin/env python3
"""
Test script for main.py FastAPI endpoints
"""
import requests
import json
import time

BASE_URL = "http://localhost:8008"

def test_health():
    """Test the /health endpoint"""
    print("Testing /health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        response.raise_for_status()
        print(f"✓ Health check passed: {response.json()}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"✗ Health check failed: {e}")
        return False

def test_files():
    """Test the /files endpoint"""
    print("\nTesting /files endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/files", timeout=5)
        response.raise_for_status()
        data = response.json()
        print(f"✓ Files endpoint passed: Found {len(data.get('items', []))} items")
        return True
    except requests.exceptions.RequestException as e:
        print(f"✗ Files endpoint failed: {e}")
        return False

def test_download():
    """Test the /download endpoint with a sample request"""
    print("\nTesting /download endpoint...")
    try:
        payload = {
            "prompt": "Apple annual report 2023",
            "max_items": 5,
            "prefer_official": True
        }
        response = requests.post(
            f"{BASE_URL}/download",
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        data = response.json()
        print(f"✓ Download endpoint passed")
        print(f"  Intent: {data.get('intent', {})}")
        print(f"  Results: {len(data.get('results', []))} files downloaded")
        return True
    except requests.exceptions.RequestException as e:
        print(f"✗ Download endpoint failed: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"  Response: {e.response.text}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("Testing IR-FETCHER FastAPI Endpoints")
    print("=" * 50)
    
    # Wait a bit for server to be ready
    print("\nWaiting for server to be ready...")
    time.sleep(3)
    
    results = []
    results.append(("Health", test_health()))
    results.append(("Files", test_files()))
    results.append(("Download", test_download()))
    
    print("\n" + "=" * 50)
    print("Test Summary:")
    print("=" * 50)
    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{name}: {status}")
    
    all_passed = all(result[1] for result in results)
    exit(0 if all_passed else 1)

