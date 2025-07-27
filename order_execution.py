import requests, time, hmac, hashlib

API_KEY = "your_api_key"
SECRET_KEY = "your_secret_key"

def place_order(symbol, quantity, side="BUY"):
    timestamp = int(time.time() * 1000)
    params = f"symbol={symbol}&side={side}&type=MARKET&quantity={quantity}&timestamp={timestamp}"
    signature = hmac.new(SECRET_KEY.encode(), params.encode(), hashlib.sha256).hexdigest()

    url = f"https://api.binance.com/api/v3/order?{params}&signature={signature}"
    headers = {"X-MBX-APIKEY": API_KEY}
    return requests.post(url, headers=headers)