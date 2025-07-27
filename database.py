import sqlite3
import pandas as pd
from datetime import datetime
import json

class TradingDatabase:
    def __init__(self, db_path="trading_data.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Trades table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                side TEXT NOT NULL,
                quantity REAL NOT NULL,
                price REAL NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'open',
                take_profit REAL,
                stop_loss REAL,
                pnl REAL DEFAULT 0
            )
        ''')
        
        # Market data table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS market_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                price REAL NOT NULL,
                volume REAL NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Wallet history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS wallet_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                balance REAL NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_trade(self, symbol, side, quantity, price, take_profit=None, stop_loss=None):
        """Save a new trade to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO trades (symbol, side, quantity, price, take_profit, stop_loss)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (symbol, side, quantity, price, take_profit, stop_loss))
        
        trade_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return trade_id
    
    def update_trade_status(self, trade_id, status, pnl=None):
        """Update trade status and PnL"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if pnl is not None:
            cursor.execute('''
                UPDATE trades SET status = ?, pnl = ? WHERE id = ?
            ''', (status, pnl, trade_id))
        else:
            cursor.execute('''
                UPDATE trades SET status = ? WHERE id = ?
            ''', (status, trade_id))
        
        conn.commit()
        conn.close()
    
    def save_market_data(self, symbol, price, volume):
        """Save market data point"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO market_data (symbol, price, volume)
            VALUES (?, ?, ?)
        ''', (symbol, price, volume))
        
        conn.commit()
        conn.close()
    
    def save_wallet_balance(self, balance):
        """Save wallet balance snapshot"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO wallet_history (balance)
            VALUES (?)
        ''', (balance,))
        
        conn.commit()
        conn.close()
    
    def get_open_trades(self):
        """Get all open trades"""
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql_query('''
            SELECT * FROM trades WHERE status = 'open' ORDER BY timestamp DESC
        ''', conn)
        conn.close()
        return df
    
    def get_trade_history(self, limit=100):
        """Get recent trade history"""
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql_query('''
            SELECT * FROM trades ORDER BY timestamp DESC LIMIT ?
        ''', conn, params=(limit,))
        conn.close()
        return df
    
    def get_market_data(self, symbol, hours=24):
        """Get market data for a symbol"""
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql_query('''
            SELECT * FROM market_data 
            WHERE symbol = ? AND timestamp >= datetime('now', '-{} hours')
            ORDER BY timestamp ASC
        '''.format(hours), conn, params=(symbol,))
        conn.close()
        return df
    
    def get_wallet_history(self, days=30):
        """Get wallet balance history"""
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql_query('''
            SELECT * FROM wallet_history 
            WHERE timestamp >= datetime('now', '-{} days')
            ORDER BY timestamp ASC
        '''.format(days), conn)
        conn.close()
        return df
    
    def get_total_pnl(self):
        """Calculate total PnL"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT SUM(pnl) FROM trades WHERE status = "closed"')
        total_pnl = cursor.fetchone()[0] or 0
        
        conn.close()
        return total_pnl 