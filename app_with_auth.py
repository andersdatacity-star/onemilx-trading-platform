from flask import Flask, render_template, jsonify, request, redirect, url_for, session, flash
from functools import wraps
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
from user_auth import UserAuth

app = Flask(__name__)
app.secret_key = 'your-super-secret-flask-key-change-this'

# Initialize components
user_auth = UserAuth()
binance_client = BinanceClient()
db = TradingDatabase()
strategy = None
strategy_thread = None
strategy_running = False

def login_required(f):
    """Decorator to require login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.cookies.get('token') or session.get('token')
        if not token:
            return redirect(url_for('login'))
        
        user_info = user_auth.verify_token(token)
        if not user_info:
            return redirect(url_for('login'))
        
        request.user_info = user_info
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Decorator to require admin role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.cookies.get('token') or session.get('token')
        if not token:
            return redirect(url_for('login'))
        
        user_info = user_auth.verify_token(token)
        if not user_info or user_info.get('role') != 'admin':
            flash('Admin access required', 'error')
            return redirect(url_for('dashboard'))
        
        request.user_info = user_info
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    """Landing page"""
    return render_template('landing.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        result = user_auth.login_user(username, password)
        if result['success']:
            session['token'] = result['token']
            session['user'] = result['user']
            return redirect(url_for('dashboard'))
        else:
            flash(result['error'], 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Registration page"""
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        invite_code = request.form.get('invite_code')
        
        result = user_auth.register_user(username, email, password, invite_code)
        if result['success']:
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        else:
            flash(result['error'], 'error')
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    """Logout user"""
    session.clear()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard page"""
    return render_template('dashboard.html', user=session.get('user'))

@app.route('/admin')
@admin_required
def admin_panel():
    """Admin panel"""
    users = user_auth.get_all_users(request.user_info['user_id'])
    invites = user_auth.get_active_invites(request.user_info['user_id'])
    return render_template('admin.html', users=users, invites=invites)

@app.route('/api/admin/create-invite', methods=['POST'])
@admin_required
def create_invite():
    """Create new invite code"""
    expires_days = request.json.get('expires_days', 7)
    invite_code = user_auth.create_invite(request.user_info['user_id'], expires_days)
    return jsonify({"success": True, "invite_code": invite_code})

@app.route('/api/admin/users')
@admin_required
def get_users():
    """Get all users (admin only)"""
    users = user_auth.get_all_users(request.user_info['user_id'])
    return jsonify(users)

@app.route('/api/admin/invites')
@admin_required
def get_invites():
    """Get active invites (admin only)"""
    invites = user_auth.get_active_invites(request.user_info['user_id'])
    return jsonify(invites)

@app.route('/api/account-info')
@login_required
def get_account_info():
    """Get account information"""
    try:
        # Use user's API credentials if available
        user = session.get('user')
        if user.get('api_key') and user.get('api_secret'):
            client = BinanceClient(user['api_key'], user['api_secret'])
        else:
            client = binance_client
        
        balance = client.get_balance('USDT')
        account_info = client.get_account_info()
        
        return jsonify({
            'balance': balance,
            'total_assets': len(account_info.get('balances', [])),
            'account_type': account_info.get('accountType', 'Unknown')
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/trades')
@login_required
def get_trades():
    """Get trade history"""
    try:
        trades = db.get_trade_history(100)
        return jsonify(trades.to_dict('records'))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/open-trades')
@login_required
def get_open_trades():
    """Get open trades"""
    try:
        open_trades = db.get_open_trades()
        return jsonify(open_trades.to_dict('records'))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/market-data/<symbol>')
@login_required
def get_market_data(symbol):
    """Get market data for a symbol"""
    try:
        current_price = binance_client.get_ticker_price(symbol)
        ticker_24h = binance_client.get_24hr_ticker(symbol)
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
@login_required
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
@login_required
def start_strategy():
    """Start trading strategy"""
    global strategy, strategy_thread, strategy_running
    
    if strategy_running:
        return jsonify({'error': 'Strategy already running'}), 400
    
    try:
        risk_mode = request.json.get('risk_mode', 'ultra')
        strategy = WhaleTrapStrategy(risk_mode=risk_mode)
        strategy_running = True
        
        strategy_thread = threading.Thread(target=strategy.run)
        strategy_thread.daemon = True
        strategy_thread.start()
        
        return jsonify({'success': True, 'message': 'Strategy started'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/strategy/stop', methods=['POST'])
@login_required
def stop_strategy():
    """Stop trading strategy"""
    global strategy_running
    
    if not strategy_running:
        return jsonify({'error': 'Strategy not running'}), 400
    
    strategy_running = False
    return jsonify({'success': True, 'message': 'Strategy stopped'})

@app.route('/api/strategy/status')
@login_required
def get_strategy_status():
    """Get strategy status"""
    return jsonify({
        'running': strategy_running,
        'risk_mode': getattr(strategy, 'risk_mode', 'ultra') if strategy else None
    })

@app.route('/api/place-order', methods=['POST'])
@login_required
def place_order():
    """Place a trading order"""
    try:
        symbol = request.json.get('symbol')
        side = request.json.get('side')
        quantity = float(request.json.get('quantity'))
        
        result = binance_client.place_market_order(symbol, side, quantity)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/wallet-history')
@login_required
def get_wallet_history():
    """Get wallet balance history"""
    try:
        # This would typically come from your database
        # For now, return mock data
        history = [
            {'date': '2024-01-01', 'balance': 1000},
            {'date': '2024-01-02', 'balance': 1050},
            {'date': '2024-01-03', 'balance': 1100}
        ]
        return jsonify(history)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/pnl')
@login_required
def get_pnl():
    """Get profit/loss data"""
    try:
        # Mock PnL data
        pnl_data = {
            'total_pnl': 150.50,
            'daily_pnl': 25.30,
            'weekly_pnl': 125.80,
            'monthly_pnl': 450.20
        }
        return jsonify(pnl_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analyze/<symbol>')
@login_required
def analyze_symbol(symbol):
    """Analyze a specific symbol"""
    try:
        # Get technical indicators
        klines = binance_client.get_klines(symbol, '1h', 24)
        
        if 'error' in klines:
            return jsonify({'error': 'Failed to get market data'}), 500
        
        # Calculate basic indicators
        prices = [float(kline[4]) for kline in klines]
        volumes = [float(kline[5]) for kline in klines]
        
        current_price = prices[-1]
        price_change = ((current_price - prices[0]) / prices[0]) * 100
        avg_volume = sum(volumes) / len(volumes)
        current_volume = volumes[-1]
        volume_change = ((current_volume - avg_volume) / avg_volume) * 100
        
        analysis = {
            'symbol': symbol,
            'current_price': current_price,
            'price_change_24h': price_change,
            'volume_change': volume_change,
            'recommendation': 'BUY' if price_change > 0 and volume_change > 20 else 'HOLD'
        }
        
        return jsonify(analysis)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 