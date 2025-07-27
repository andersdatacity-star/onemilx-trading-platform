from binance_client import BinanceClient

def test_binance_api():
    print("Testing Binance API...")
    
    # Create client
    client = BinanceClient()
    print(f"API Key: {client.api_key[:10]}...")
    print(f"Secret Key: {client.secret_key[:10]}...")
    
    # Test public API calls (no authentication needed)
    try:
        print("\nTesting public API calls...")
        
        # Test getting BTC price
        btc_price = client.get_ticker_price('BTCUSDT')
        if btc_price:
            print(f"✅ BTC Price: ${btc_price:,.2f}")
        else:
            print("❌ Failed to get BTC price")
            
        # Test getting 24hr ticker
        btc_24h = client.get_24hr_ticker('BTCUSDT')
        if 'error' not in btc_24h:
            print(f"✅ BTC 24h Change: {btc_24h.get('priceChangePercent', 'N/A')}%")
        else:
            print("❌ Failed to get 24h ticker")
            
        # Test getting exchange info
        exchange_info = client.get_exchange_info()
        if 'error' not in exchange_info:
            print(f"✅ Exchange info loaded: {len(exchange_info.get('symbols', []))} symbols")
        else:
            print("❌ Failed to get exchange info")
            
    except Exception as e:
        print(f"❌ Public API test failed: {str(e)}")
        return False
    
    # Test private API calls (authentication required)
    try:
        print("\nTesting private API calls...")
        
        # Test getting account info
        account = client.get_account_info()
        if 'error' in account:
            print(f"❌ Account info failed: {account['error']}")
        else:
            print("✅ Account info successful!")
            print(f"Account type: {account.get('accountType', 'Unknown')}")
            
            # Get USDT balance
            usdt_balance = client.get_balance('USDT')
            print(f"USDT Balance: {usdt_balance:.2f}")
            
        return True
            
    except Exception as e:
        print(f"❌ Private API test failed: {str(e)}")
        return False

if __name__ == "__main__":
    test_binance_api() 