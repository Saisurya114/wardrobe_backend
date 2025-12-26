#!/usr/bin/env python3
"""
Simple script to test the /api/extract-cloth endpoint
"""
import requests
import sys
import os

API_URL = "http://localhost:8000/api/extract-cloth"

def test_api(image_path: str):
    """Test the extract-cloth API endpoint"""
    
    if not os.path.exists(image_path):
        print(f"❌ Error: Image file not found: {image_path}")
        return False
    
    print(f"📤 Uploading image: {image_path}")
    
    try:
        with open(image_path, 'rb') as f:
            files = {'file': (os.path.basename(image_path), f, 'image/jpeg')}
            response = requests.post(API_URL, files=files)
        
        if response.status_code == 200:
            # Save the output
            output_path = f"test_output_{os.path.basename(image_path)}.png"
            with open(output_path, 'wb') as f:
                f.write(response.content)
            print(f"✅ Success! Output saved to: {output_path}")
            print(f"   Response size: {len(response.content)} bytes")
            return True
        else:
            print(f"❌ Error: Status code {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to server.")
        print("   Make sure the server is running: uvicorn app.main:app --reload")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_api.py <image_path>")
        print("\nExample:")
        print("  python test_api.py images/raw/test.jpg")
        sys.exit(1)
    
    image_path = sys.argv[1]
    success = test_api(image_path)
    sys.exit(0 if success else 1)

