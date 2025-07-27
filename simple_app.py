# OneMilX Trading Platform - Simple Flask App
# Last deployment: 2024-12-19
# Auto-deployed via GitHub Actions

from flask import Flask, render_template, jsonify, request, redirect, url_for, session, flash
from functools import wraps
import threading
import time
import json
import os
from datetime import datetime, timedelta
from user_auth import UserAuth

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'your-super-secret-flask-key-change-this')

# Initialize components
user_auth = UserAuth()

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
        # Mock data for now
        return jsonify({
            'balance': 1000.00,
            'total_assets': 5,
            'account_type': 'Spot'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/trades')
@login_required
def get_trades():
    """Get trade history"""
    try:
        # Mock data for now
        trades = [
            {'symbol': 'BTCUSDT', 'side': 'BUY', 'quantity': 0.001, 'price': 50000, 'time': '2024-01-01 10:00:00'},
            {'symbol': 'ETHUSDT', 'side': 'SELL', 'quantity': 0.01, 'price': 3000, 'time': '2024-01-01 11:00:00'}
        ]
        return jsonify(trades)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/open-trades')
@login_required
def get_open_trades():
    """Get open trades"""
    try:
        # Mock data for now
        open_trades = [
            {'symbol': 'BTCUSDT', 'side': 'BUY', 'quantity': 0.001, 'price': 50000}
        ]
        return jsonify(open_trades)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/market-data/<symbol>')
@login_required
def get_market_data(symbol):
    """Get market data for a symbol"""
    try:
        # Mock data for now
        return jsonify({
            'symbol': symbol,
            'current_price': 50000.00,
            'price_change_24h': 2.5,
            'volume_24h': 1000000,
            'chart_data': []
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/top-coins')
@login_required
def get_top_coins():
    """Get top coins for analysis"""
    try:
        # Mock data for now
        return jsonify({
            'volume_leaders': [
                {'symbol': 'BTCUSDT', 'volume': 1000000, 'price': 50000},
                {'symbol': 'ETHUSDT', 'volume': 800000, 'price': 3000}
            ],
            'top_gainers': [
                {'symbol': 'BTCUSDT', 'change': 5.2, 'price': 50000},
                {'symbol': 'ETHUSDT', 'change': 3.8, 'price': 3000}
            ]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/strategy/start', methods=['POST'])
@login_required
def start_strategy():
    """Start trading strategy"""
    try:
        risk_mode = request.json.get('risk_mode', 'ultra')
        return jsonify({'success': True, 'message': f'Strategy started in {risk_mode} mode'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/strategy/stop', methods=['POST'])
@login_required
def stop_strategy():
    """Stop trading strategy"""
    try:
        return jsonify({'success': True, 'message': 'Strategy stopped'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/strategy/status')
@login_required
def get_strategy_status():
    """Get strategy status"""
    return jsonify({
        'running': False,
        'risk_mode': 'ultra'
    })

@app.route('/api/place-order', methods=['POST'])
@login_required
def place_order():
    """Place a trading order"""
    try:
        symbol = request.json.get('symbol')
        side = request.json.get('side')
        quantity = float(request.json.get('quantity'))
        
        return jsonify({
            'success': True,
            'order_id': 12345,
            'symbol': symbol,
            'side': side,
            'quantity': quantity
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/wallet-history')
@login_required
def get_wallet_history():
    """Get wallet balance history"""
    try:
        # Mock data for now
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
        # Mock data for now
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
        # Mock analysis for now
        analysis = {
            'symbol': symbol,
            'current_price': 50000.00,
            'price_change_24h': 2.5,
            'volume_change': 15.3,
            'recommendation': 'BUY'
        }
        return jsonify(analysis)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port) 