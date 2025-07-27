import requests
import time
import hmac
import hashlib
import json
from urllib.parse import urlencode
from typing import Dict, List, Optional
import logging
from config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BinanceClient:
    def __init__(self, api_key: str = None, secret_key: str = None):
        self.api_key = api_key or Config.BINANCE_API_KEY
        self.secret_key = secret_key or Config.BINANCE_SECRET_KEY
        self.base_url = "https://api.binance.com"
        self.testnet = False  # Set to True for testing
        
        if self.testnet:
            self.base_url = "https://testnet.binance.vision"
    
    def _generate_signature(self, params: str) -> str:
        """Generate HMAC SHA256 signature"""
        return hmac.new(
            self.secret_key.encode('utf-8'),
            params.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
    
    def _make_request(self, method: str, endpoint: str, params: Dict = None, signed: bool = False) -> Dict:
        """Make HTTP request to Binance API"""
        url = f"{self.base_url}{endpoint}"
        headers = {}
        
        if self.api_key:
            headers['X-MBX-APIKEY'] = self.api_key
        
        if signed and params:
            params['timestamp'] = int(time.time() * 1000)
            query_string = urlencode(params)
            signature = self._generate_signature(query_string)
            params['signature'] = signature
        
        try:
            if method == 'GET':
                response = requests.get(url, params=params, headers=headers)
            elif method == 'POST':
                response = requests.post(url, params=params, headers=headers)
            elif method == 'DELETE':
                response = requests.delete(url, params=params, headers=headers)
            
            response.raise_for_status()
            return response.json()
        
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            return {"error": str(e)}
    
    def get_account_info(self) -> Dict:
        """Get account information"""
        return self._make_request('GET', '/api/v3/account', signed=True)
    
    def get_balance(self, asset: str = 'USDT') -> float:
        """Get balance for specific asset"""
        account = self.get_account_info()
        if 'error' in account:
            return 0.0
        
        for balance in account.get('balances', []):
            if balance['asset'] == asset:
                return float(balance['free'])
        return 0.0
    
    def get_ticker_price(self, symbol: str) -> Optional[float]:
        """Get current price for a symbol"""
        params = {'symbol': symbol}
        response = self._make_request('GET', '/api/v3/ticker/price', params)
        
        if 'error' not in response:
            return float(response['price'])
        return None
    
    def get_24hr_ticker(self, symbol: str) -> Dict:
        """Get 24hr ticker statistics"""
        params = {'symbol': symbol}
        return self._make_request('GET', '/api/v3/ticker/24hr', params)
    
    def get_klines(self, symbol: str, interval: str = '1m', limit: int = 100) -> List:
        """Get candlestick data"""
        params = {
            'symbol': symbol,
            'interval': interval,
            'limit': limit
        }
        return self._make_request('GET', '/api/v3/klines', params)
    
    def get_order_book(self, symbol: str, limit: int = 100) -> Dict:
        """Get order book for a symbol"""
        params = {'symbol': symbol, 'limit': limit}
        return self._make_request('GET', '/api/v3/depth', params)
    
    def place_market_order(self, symbol: str, side: str, quantity: float) -> Dict:
        """Place a market order"""
        params = {
            'symbol': symbol,
            'side': side.upper(),
            'type': 'MARKET',
            'quantity': quantity
        }
        return self._make_request('POST', '/api/v3/order', params, signed=True)
    
    def place_limit_order(self, symbol: str, side: str, quantity: float, price: float) -> Dict:
        """Place a limit order"""
        params = {
            'symbol': symbol,
            'side': side.upper(),
            'type': 'LIMIT',
            'timeInForce': 'GTC',
            'quantity': quantity,
            'price': price
        }
        return self._make_request('POST', '/api/v3/order', params, signed=True)
    
    def place_stop_loss_order(self, symbol: str, side: str, quantity: float, stop_price: float) -> Dict:
        """Place a stop loss order"""
        params = {
            'symbol': symbol,
            'side': side.upper(),
            'type': 'STOP_MARKET',
            'quantity': quantity,
            'stopPrice': stop_price
        }
        return self._make_request('POST', '/api/v3/order', params, signed=True)
    
    def place_take_profit_order(self, symbol: str, side: str, quantity: float, stop_price: float) -> Dict:
        """Place a take profit order"""
        params = {
            'symbol': symbol,
            'side': side.upper(),
            'type': 'TAKE_PROFIT_MARKET',
            'quantity': quantity,
            'stopPrice': stop_price
        }
        return self._make_request('POST', '/api/v3/order', params, signed=True)
    
    def cancel_order(self, symbol: str, order_id: int) -> Dict:
        """Cancel an order"""
        params = {
            'symbol': symbol,
            'orderId': order_id
        }
        return self._make_request('DELETE', '/api/v3/order', params, signed=True)
    
    def get_open_orders(self, symbol: str = None) -> List:
        """Get open orders"""
        params = {}
        if symbol:
            params['symbol'] = symbol
        return self._make_request('GET', '/api/v3/openOrders', params, signed=True)
    
    def get_order_status(self, symbol: str, order_id: int) -> Dict:
        """Get order status"""
        params = {
            'symbol': symbol,
            'orderId': order_id
        }
        return self._make_request('GET', '/api/v3/order', params, signed=True)
    
    def get_trade_history(self, symbol: str, limit: int = 100) -> List:
        """Get trade history"""
        params = {
            'symbol': symbol,
            'limit': limit
        }
        return self._make_request('GET', '/api/v3/myTrades', params, signed=True)
    
    def get_exchange_info(self) -> Dict:
        """Get exchange information"""
        return self._make_request('GET', '/api/v3/exchangeInfo')
    
    def get_symbol_info(self, symbol: str) -> Optional[Dict]:
        """Get symbol information"""
        exchange_info = self.get_exchange_info()
        if 'error' in exchange_info:
            return None
        
        for symbol_info in exchange_info.get('symbols', []):
            if symbol_info['symbol'] == symbol:
                return symbol_info
        return None
    
    def get_top_gainers(self, limit: int = 20) -> List[Dict]:
        """Get top gaining symbols in last 24h"""
        response = self._make_request('GET', '/api/v3/ticker/24hr')
        if 'error' in response:
            return []
        
        # Filter USDT pairs and sort by price change
        usdt_pairs = [
            ticker for ticker in response 
            if ticker['symbol'].endswith('USDT') and float(ticker['priceChangePercent']) > 0
        ]
        
        # Sort by price change percentage
        sorted_pairs = sorted(usdt_pairs, key=lambda x: float(x['priceChangePercent']), reverse=True)
        return sorted_pairs[:limit]
    
    def get_volume_leaders(self, limit: int = 20) -> List[Dict]:
        """Get symbols with highest volume in last 24h"""
        response = self._make_request('GET', '/api/v3/ticker/24hr')
        if 'error' in response:
            return []
        
        # Filter USDT pairs and sort by volume
        usdt_pairs = [
            ticker for ticker in response 
            if ticker['symbol'].endswith('USDT')
        ]
        
        # Sort by volume
        sorted_pairs = sorted(usdt_pairs, key=lambda x: float(x['volume']), reverse=True)
        return sorted_pairs[:limit] 