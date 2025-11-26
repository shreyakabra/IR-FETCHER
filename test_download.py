#!/usr/bin/env python3
"""
Diagnostic script to test download functionality
"""
import requests
import json
import sys

BASE_URL = "http://localhost:8008"

def test_download_detailed():
    """Test download with detailed output"""
    print("=" * 60)
    print("Testing Download Functionality")
    print("=" * 60)
    
    payload = {
        "prompt": "Apple annual report 2023",
        "max_items": 2,
        "prefer_official": True
    }
    
    print(f"\n1. Sending request to {BASE_URL}/download")
    print(f"   Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/download",
            json=payload,
            timeout=60
        )
        
        print(f"\n2. Response Status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"   Error: {response.text}")
            return False
        
        data = response.json()
        
        print(f"\n3. Intent Parsed:")
        intent = data.get('intent', {})
        print(f"   Company: {intent.get('company')}")
        print(f"   Doc Type: {intent.get('doc_type')}")
        print(f"   Years: {intent.get('years')}")
        
        results = data.get('results', [])
        print(f"\n4. Download Results: {len(results)} files downloaded")
        
        if len(results) == 0:
            print("\n   ⚠️  WARNING: No files were downloaded!")
            print("   Possible reasons:")
            print("   - No files found by search")
            print("   - Files found but download failed")
            print("   - Check server logs for detailed error messages")
        else:
            for i, result in enumerate(results, 1):
                print(f"\n   File {i}:")
                print(f"     - Company: {result.get('company')}")
                print(f"     - Doc Type: {result.get('doc_type')}")
                print(f"     - Year: {result.get('year')}")
                print(f"     - Filename: {result.get('filename')}")
                print(f"     - File Path: {result.get('file_path')}")
                print(f"     - Source: {result.get('source')}")
                print(f"     - URL: {result.get('url')}")
        
        return len(results) > 0
        
    except requests.exceptions.RequestException as e:
        print(f"\n✗ Request failed: {e}")
        return False
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_download_detailed()
    sys.exit(0 if success else 1)

