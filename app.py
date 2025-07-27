from flask import Flask, render_template, jsonify, request, redirect, url_for
import threading
import time
import json
from datetime import datetime, timedelta
import pandas as pd
import plotly.graph_objs as go
import plotly.utils
from binance_client import BinanceClient
from database import TradingDatabase
from whale_trap_strategy import WhaleTrapStrategy
from config import Config

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

# Global variables
binance_client = BinanceClient()
db = TradingDatabase()
strategy = None
strategy_thread = None
strategy_running = False

@app.route('/')
def dashboard():
    """Main dashboard page"""
    return render_template('dashboard.html')

@app.route('/api/account-info')
def get_account_info():
    """Get account information"""
    try:
        balance = binance_client.get_balance('USDT')
        account_info = binance_client.get_account_info()
        
        return jsonify({
            'balance': balance,
            'total_assets': len(account_info.get('balances', [])),
            'account_type': account_info.get('accountType', 'Unknown')
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/trades')
def get_trades():
    """Get trade history"""
    try:
        trades = db.get_trade_history(100)
        return jsonify(trades.to_dict('records'))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/open-trades')
def get_open_trades():
    """Get open trades"""
    try:
        open_trades = db.get_open_trades()
        return jsonify(open_trades.to_dict('records'))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/market-data/<symbol>')
def get_market_data(symbol):
    """Get market data for a symbol"""
    try:
        # Get current price
        current_price = binance_client.get_ticker_price(symbol)
        
        # Get 24hr stats
        ticker_24h = binance_client.get_24hr_ticker(symbol)
        
        # Get historical data for chart
        klines = binance_client.get_klines(symbol, '1h', 24)
        
        chart_data = []
        if klines and 'error' not in klines:
            for kline in klines:
                chart_data.append({
                    'time': datetime.fromtimestamp(kline[0] / 1000).strftime('%Y-%m-%d %H:%M'),
                    'price': float(kline[4])
                })
        
        return jsonify({
            'symbol': symbol,
            'current_price': current_price,
            'price_change_24h': float(ticker_24h.get('priceChangePercent', 0)),
            'volume_24h': float(ticker_24h.get('volume', 0)),
            'chart_data': chart_data
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/top-coins')
def get_top_coins():
    """Get top coins for analysis"""
    try:
        volume_leaders = binance_client.get_volume_leaders(10)
        top_gainers = binance_client.get_top_gainers(10)
        
        return jsonify({
            'volume_leaders': volume_leaders,
            'top_gainers': top_gainers
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/strategy/start', methods=['POST'])
def start_strategy():
    """Start the trading strategy"""
    global strategy, strategy_thread, strategy_running
    
    try:
        if strategy_running:
            return jsonify({'error': 'Strategy already running'}), 400
        
        strategy_type = request.json.get('strategy_type', 'ultra_ai')
        
        if strategy_type == 'ultra_ai':
            from ultra_ai_strategy import UltraAIStrategy
            strategy = UltraAIStrategy()
        else:
            risk_mode = request.json.get('risk_mode', 'ultra')
            strategy = WhaleTrapStrategy(risk_mode=risk_mode)
        
        strategy_running = True
        strategy_thread = threading.Thread(target=strategy.run, daemon=True)
        strategy_thread.start()
        
        return jsonify({'message': f'{strategy_type} strategy started successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/strategy/stop', methods=['POST'])
def stop_strategy():
    """Stop the trading strategy"""
    global strategy_running
    
    try:
        strategy_running = False
        return jsonify({'message': 'Strategy stopped successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/strategy/status')
def get_strategy_status():
    """Get strategy status"""
    global strategy_running, strategy
    
    try:
        active_trades = {}
        if strategy:
            active_trades = strategy.active_trades
        
        return jsonify({
            'running': strategy_running,
            'active_trades_count': len(active_trades),
            'active_trades': active_trades
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/place-order', methods=['POST'])
def place_order():
    """Place a manual order"""
    try:
        data = request.json
        symbol = data.get('symbol')
        side = data.get('side')
        quantity = float(data.get('quantity'))
        
        if side == 'BUY':
            order = binance_client.place_market_order(symbol, 'BUY', quantity)
        else:
            order = binance_client.place_market_order(symbol, 'SELL', quantity)
        
        if 'error' in order:
            return jsonify({'error': order['error']}), 400
        
        return jsonify({'message': 'Order placed successfully', 'order': order})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/wallet-history')
def get_wallet_history():
    """Get wallet balance history"""
    try:
        history = db.get_wallet_history(7)  # Last 7 days
        return jsonify(history.to_dict('records'))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/pnl')
def get_pnl():
    """Get total PnL"""
    try:
        total_pnl = db.get_total_pnl()
        return jsonify({'total_pnl': total_pnl})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analyze/<symbol>')
def analyze_symbol(symbol):
    """Analyze a specific symbol"""
    try:
        strategy_temp = WhaleTrapStrategy()
        analysis = strategy_temp.analyze_market_conditions(symbol)
        return jsonify(analysis)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 