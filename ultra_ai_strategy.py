import pandas as pd
import numpy as np
import time
import logging
import threading
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import ta
from binance_client import BinanceClient
from database import TradingDatabase
from config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UltraAIStrategy:
    def __init__(self):
        self.binance = BinanceClient()
        self.db = TradingDatabase()
        self.current_capital = Config.INITIAL_CAPITAL
        self.active_trades = {}
        self.daily_profit = 0
        self.total_trades = 0
        self.winning_trades = 0
        
        # AI Decision Making
        self.ai_confidence_threshold = 0.3  # Very low threshold for ultra-aggressive
        self.max_concurrent_trades = Config.MAX_COINS_TO_TRADE
        self.position_size = Config.BASE_POSITION_SIZE
        
        # Performance tracking
        self.start_time = datetime.now()
        self.daily_target = Config.get_target_daily_return() * self.current_capital
        
        logger.info(f"🚀 Ultra AI Strategy initialized")
        logger.info(f"Target: 1M in 6 months")
        logger.info(f"Daily target: {self.daily_target:.2f} USDT")
        logger.info(f"Max coins to trade: {self.max_concurrent_trades}")
    
    def get_all_tradeable_coins(self) -> List[str]:
        """Get all available USDT trading pairs"""
        try:
            exchange_info = self.binance.get_exchange_info()
            if 'error' in exchange_info:
                return []
            
            usdt_pairs = []
            for symbol_info in exchange_info.get('symbols', []):
                symbol = symbol_info['symbol']
                if (symbol.endswith('USDT') and 
                    symbol_info['status'] == 'TRADING' and
                    symbol_info['isSpotTradingAllowed']):
                    usdt_pairs.append(symbol)
            
            return usdt_pairs[:Config.MAX_COINS_TO_TRADE]
        
        except Exception as e:
            logger.error(f"Error getting tradeable coins: {e}")
            return ['BTCUSDT', 'ETHUSDT', 'BNBUSDT']  # Fallback
    
    def ultra_fast_analysis(self, symbol: str) -> Dict:
        """Ultra-fast market analysis for scalping"""
        try:
            # Get 1-minute klines for fast analysis
            klines = self.binance.get_klines(symbol, '1m', 10)
            
            if not klines or 'error' in klines:
                return {'signal': 'no_data', 'confidence': 0}
            
            # Convert to DataFrame
            df = pd.DataFrame(klines, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_volume', 'trades', 'taker_buy_base',
                'taker_buy_quote', 'ignore'
            ])
            
            # Convert to numeric
            for col in ['open', 'high', 'low', 'close', 'volume']:
                df[col] = pd.to_numeric(df[col])
            
            # Ultra-fast indicators
            current_price = df['close'].iloc[-1]
            prev_price = df['close'].iloc[-2]
            current_volume = df['volume'].iloc[-1]
            avg_volume = df['volume'].rolling(5).mean().iloc[-1]
            
            # Calculate ultra-fast signals
            price_change = (current_price - prev_price) / prev_price
            volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1
            
            # Ultra-aggressive signal generation
            signal_strength = 0
            signal_type = 'neutral'
            
            # Price momentum (very sensitive)
            if price_change > 0.002:  # 0.2% price increase
                signal_strength += 0.4
                signal_type = 'momentum_up'
            elif price_change < -0.002:  # 0.2% price decrease
                signal_strength -= 0.4
                signal_type = 'momentum_down'
            
            # Volume spike (very sensitive)
            if volume_ratio > 1.2:  # 20% volume increase
                signal_strength += 0.3
                signal_type = 'volume_spike'
            
            # Price acceleration
            if len(df) >= 3:
                price_accel = (df['close'].iloc[-1] - df['close'].iloc[-2]) - (df['close'].iloc[-2] - df['close'].iloc[-3])
                if price_accel > 0:
                    signal_strength += 0.2
            
            # RSI for oversold/overbought (ultra-fast)
            if len(df) >= 14:
                rsi = ta.momentum.rsi(df['close'], window=14).iloc[-1]
                if rsi < 30:  # Oversold
                    signal_strength += 0.2
                elif rsi > 70:  # Overbought
                    signal_strength -= 0.2
            
            return {
                'symbol': symbol,
                'signal': signal_type,
                'confidence': min(abs(signal_strength), 1.0),
                'direction': 'buy' if signal_strength > 0 else 'sell',
                'price_change': price_change,
                'volume_ratio': volume_ratio,
                'current_price': current_price,
                'timestamp': datetime.now()
            }
        
        except Exception as e:
            logger.error(f"Error in ultra-fast analysis for {symbol}: {e}")
            return {'signal': 'error', 'confidence': 0}
    
    def should_enter_trade(self, analysis: Dict) -> bool:
        """AI decision for trade entry"""
        if analysis['signal'] == 'no_data' or analysis['signal'] == 'error':
            return False
        
        # Ultra-aggressive: Enter on very low confidence
        if analysis['confidence'] < self.ai_confidence_threshold:
            return False
        
        # Check if we already have max trades
        if len(self.active_trades) >= self.max_concurrent_trades:
            return False
        
        # Check if we already have this symbol
        if analysis['symbol'] in self.active_trades:
            return False
        
        # Check available capital
        if self.current_capital < self.position_size:
            return False
        
        # AI decision: Enter if momentum is positive
        return analysis['direction'] == 'buy'
    
    def calculate_dynamic_position_size(self) -> float:
        """Calculate position size based on current capital and compound growth"""
        base_size = Config.BASE_POSITION_SIZE
        
        if Config.COMPOUND_MODE and Config.AUTO_ADJUST_POSITION_SIZE:
            # Increase position size with capital growth
            growth_factor = self.current_capital / Config.INITIAL_CAPITAL
            adjusted_size = base_size * min(growth_factor, 10)  # Max 10x increase
            
            # Ensure we don't exceed available capital
            return min(adjusted_size, self.current_capital * 0.1)  # Max 10% of capital per trade
        
        return base_size
    
    def execute_ultra_trade(self, symbol: str, analysis: Dict) -> bool:
        """Execute ultra-fast trade"""
        try:
            if not self.should_enter_trade(analysis):
                return False
            
            # Calculate position size
            position_size = self.calculate_dynamic_position_size()
            
            if position_size < 0.1:  # Minimum 0.1 USDT
                return False
            
            # Get current price
            current_price = self.binance.get_ticker_price(symbol)
            if not current_price:
                return False
            
            # Calculate quantity
            quantity = position_size / current_price
            
            # Round quantity to appropriate precision
            symbol_info = self.binance.get_symbol_info(symbol)
            if symbol_info:
                lot_size_filter = next((f for f in symbol_info['filters'] if f['filterType'] == 'LOT_SIZE'), None)
                if lot_size_filter:
                    step_size = float(lot_size_filter['stepSize'])
                    quantity = round(quantity / step_size) * step_size
            
            # Place market buy order
            order = self.binance.place_market_order(symbol, 'BUY', quantity)
            
            if 'error' in order:
                logger.error(f"Failed to place order for {symbol}: {order['error']}")
                return False
            
            # Calculate stop loss and take profit
            stop_loss_price = current_price * (1 - Config.STOP_LOSS_PERCENTAGE / 100)
            take_profit_price = current_price * (1 + Config.TAKE_PROFIT_PERCENTAGE / 100)
            
            # Save trade to database
            trade_id = self.db.save_trade(
                symbol=symbol,
                side='BUY',
                quantity=quantity,
                price=current_price,
                take_profit=take_profit_price,
                stop_loss=stop_loss_price
            )
            
            # Store active trade
            self.active_trades[symbol] = {
                'trade_id': trade_id,
                'order_id': order.get('orderId'),
                'entry_price': current_price,
                'quantity': quantity,
                'stop_loss': stop_loss_price,
                'take_profit': take_profit_price,
                'entry_time': datetime.now(),
                'position_size': position_size
            }
            
            # Update capital
            self.current_capital -= position_size
            
            logger.info(f"🚀 Ultra trade executed: {symbol}")
            logger.info(f"Position size: {position_size:.2f} USDT")
            logger.info(f"Entry price: {current_price}")
            logger.info(f"Active trades: {len(self.active_trades)}")
            
            return True
        
        except Exception as e:
            logger.error(f"Error executing ultra trade for {symbol}: {e}")
            return False
    
    def monitor_ultra_trades(self):
        """Monitor and manage ultra-fast trades"""
        for symbol, trade_info in list(self.active_trades.items()):
            try:
                current_price = self.binance.get_ticker_price(symbol)
                if not current_price:
                    continue
                
                entry_price = trade_info['entry_price']
                stop_loss = trade_info['stop_loss']
                take_profit = trade_info['take_profit']
                position_size = trade_info['position_size']
                
                # Check stop loss
                if current_price <= stop_loss:
                    self.close_ultra_trade(symbol, 'stop_loss', current_price, position_size)
                
                # Check take profit
                elif current_price >= take_profit:
                    self.close_ultra_trade(symbol, 'take_profit', current_price, position_size)
                
                # Time-based exit (ultra-fast: 2 minutes max)
                time_in_trade = datetime.now() - trade_info['entry_time']
                if time_in_trade > timedelta(minutes=2):
                    self.close_ultra_trade(symbol, 'time_exit', current_price, position_size)
            
            except Exception as e:
                logger.error(f"Error monitoring ultra trade for {symbol}: {e}")
    
    def close_ultra_trade(self, symbol: str, exit_reason: str, exit_price: float, position_size: float):
        """Close ultra trade and compound profits"""
        try:
            trade_info = self.active_trades[symbol]
            entry_price = trade_info['entry_price']
            quantity = trade_info['quantity']
            
            # Calculate PnL
            pnl = (exit_price - entry_price) * quantity
            
            # Place sell order
            order = self.binance.place_market_order(symbol, 'SELL', quantity)
            
            if 'error' not in order:
                # Update database
                self.db.update_trade_status(
                    trade_info['trade_id'],
                    'closed',
                    pnl
                )
                
                # Compound profits
                if Config.COMPOUND_MODE:
                    self.current_capital += position_size + pnl
                    self.daily_profit += pnl
                else:
                    self.current_capital += position_size + pnl
                
                # Update statistics
                self.total_trades += 1
                if pnl > 0:
                    self.winning_trades += 1
                
                logger.info(f"💰 Ultra trade closed: {symbol} - {exit_reason}")
                logger.info(f"PnL: {pnl:.4f} USDT")
                logger.info(f"Current capital: {self.current_capital:.2f} USDT")
                logger.info(f"Daily profit: {self.daily_profit:.2f} USDT")
                
                # Remove from active trades
                del self.active_trades[symbol]
            
        except Exception as e:
            logger.error(f"Error closing ultra trade for {symbol}: {e}")
    
    def ultra_market_scan(self):
        """Ultra-fast market scanning"""
        try:
            # Get all tradeable coins
            symbols = self.get_all_tradeable_coins()
            
            logger.info(f"🔍 Scanning {len(symbols)} coins...")
            
            # Analyze each symbol ultra-fast
            for symbol in symbols:
                # Skip if we have max trades
                if len(self.active_trades) >= self.max_concurrent_trades:
                    break
                
                # Skip if we already have this symbol
                if symbol in self.active_trades:
                    continue
                
                # Ultra-fast analysis
                analysis = self.ultra_fast_analysis(symbol)
                
                # Execute trade if conditions met
                if self.should_enter_trade(analysis):
                    self.execute_ultra_trade(symbol, analysis)
                
                # Small delay to avoid rate limits
                time.sleep(0.01)  # 10ms delay
            
            # Monitor existing trades
            self.monitor_ultra_trades()
            
            # Save wallet balance
            self.db.save_wallet_balance(self.current_capital)
            
            # Log performance
            self.log_performance()
            
        except Exception as e:
            logger.error(f"Error in ultra market scan: {e}")
    
    def log_performance(self):
        """Log current performance metrics"""
        try:
            win_rate = (self.winning_trades / self.total_trades * 100) if self.total_trades > 0 else 0
            time_running = datetime.now() - self.start_time
            
            logger.info(f"📊 Performance Update:")
            logger.info(f"   Capital: ${self.current_capital:,.2f}")
            logger.info(f"   Daily Profit: ${self.daily_profit:,.2f}")
            logger.info(f"   Active Trades: {len(self.active_trades)}")
            logger.info(f"   Total Trades: {self.total_trades}")
            logger.info(f"   Win Rate: {win_rate:.1f}%")
            logger.info(f"   Time Running: {time_running}")
            
            # Check if we're on track for 1M
            days_elapsed = time_running.days
            if days_elapsed > 0:
                current_daily_avg = self.daily_profit / days_elapsed
                target_daily = Config.get_target_daily_return() * Config.INITIAL_CAPITAL
                
                if current_daily_avg >= target_daily:
                    logger.info(f"🎯 ON TRACK for 1M goal!")
                else:
                    logger.info(f"⚠️ Need to increase performance for 1M goal")
            
        except Exception as e:
            logger.error(f"Error logging performance: {e}")
    
    def run(self):
        """Main ultra AI strategy loop"""
        logger.info("🚀 Starting Ultra AI Strategy for 1M goal...")
        logger.info(f"Initial capital: ${self.current_capital:,.2f}")
        logger.info(f"Target: $1,000,000 in 6 months")
        
        while True:
            try:
                self.ultra_market_scan()
                time.sleep(Config.SCAN_INTERVAL)
                
            except KeyboardInterrupt:
                logger.info("Ultra AI Strategy stopped by user")
                break
            except Exception as e:
                logger.error(f"Ultra AI Strategy error: {e}")
                time.sleep(10)  # Wait before retrying

def main():
    """Start the Ultra AI Strategy"""
    strategy = UltraAIStrategy()
    strategy.run()

if __name__ == "__main__":
    main() 