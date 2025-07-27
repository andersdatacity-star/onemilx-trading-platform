import time
import hmac
import hashlib
from urllib.parse import urlencode
import requests

def test_binance_testnet():
    print("Testing Binance Testnet...")
    
    # Testnet credentials (these are public test credentials)
    api_key = "your_testnet_api_key"  # You need to create this on testnet
    secret_key = "your_testnet_secret_key"
    
    # Testnet URL
    base_url = "https://testnet.binance.vision"
    
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
    
    # Make request
    url = f"{base_url}/api/v3/account"
    headers = {'X-MBX-APIKEY': api_key}
    
    try:
        response = requests.get(url, params=params, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
    except Exception as e:
        print(f"❌ Request failed: {str(e)}")

def test_public_api():
    print("\nTesting Public API (should work)...")
    
    try:
        # Test public endpoint
        response = requests.get("https://api.binance.com/api/v3/time")
        print(f"Server Time: {response.json()}")
        
        # Test account info without auth
        response = requests.get("https://api.binance.com/api/v3/exchangeInfo")
        print(f"Exchange Info Status: {response.status_code}")
        
    except Exception as e:
        print(f"❌ Public API failed: {str(e)}")

if __name__ == "__main__":
    test_public_api()
    # test_binance_testnet()  # Uncomment when you have testnet credentials 