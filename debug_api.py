import time
import hmac
import hashlib
import os
from urllib.parse import urlencode
import requests

def debug_binance_api():
    print("Debugging Binance API...")
    
    # Your API credentials (use environment variables instead)
    api_key = os.getenv('BINANCE_API_KEY', 'your_api_key_here')
    secret_key = os.getenv('BINANCE_SECRET_KEY', 'your_secret_key_here')
    
    # Test parameters
    params = {}
    params['timestamp'] = int(time.time() * 1000)
    
    # Generate signature
    query_string = urlencode(params)
    signature = hmac.new(
        secret_key.encode('utf-8'),
        query_string.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    params['signature'] = signature
    
    print(f"Timestamp: {params['timestamp']}")
    print(f"Query string: {query_string}")
    print(f"Signature: {signature}")
    
    # Make request
    url = "https://api.binance.com/api/v3/account"
    headers = {'X-MBX-APIKEY': api_key}
    
    try:
        response = requests.get(url, params=params, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ API call successful!")
        else:
            print(f"❌ API call failed with status {response.status_code}")
            
    except Exception as e:
        print(f"❌ Request failed: {str(e)}")

if __name__ == "__main__":
    debug_binance_api() 