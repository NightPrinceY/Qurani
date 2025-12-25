#!/usr/bin/env python3
"""
Test script to verify background GIF is accessible
"""
import requests
import sys

def test_gif():
    url = "http://localhost:8080/background.gif"
    
    try:
        print(f"Testing GIF access at: {url}")
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            content_type = response.headers.get('Content-Type', '')
            content_length = len(response.content)
            
            print(f"✅ GIF is accessible!")
            print(f"   Status Code: {response.status_code}")
            print(f"   Content-Type: {content_type}")
            print(f"   Size: {content_length:,} bytes ({content_length/1024:.1f} KB)")
            
            if 'gif' in content_type.lower():
                print("   ✅ Correct MIME type")
            else:
                print(f"   ⚠️  Warning: Expected 'image/gif', got '{content_type}'")
            
            return True
        else:
            print(f"❌ Error: Status code {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Error: Cannot connect to web server")
        print("   Make sure web_server.py is running on port 8080")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_gif()
    sys.exit(0 if success else 1)

