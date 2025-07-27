import pandas as pd
import numpy as np
import time
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import ta
from binance_client import BinanceClient
from database import TradingDatabase
from config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WhaleTrapStrategy:
    def __init__(self, risk_mode: str = "pro"):
        self.risk_mode = risk_mode
        self.binance = BinanceClient()
        self.db = TradingDatabase()
        self.position_size = Config.get_position_size()
        self.stop_loss_pct = Config.STOP_LOSS_PERCENTAGE
        self.take_profit_pct = Config.TAKE_PROFIT_PERCENTAGE
        
        # Market analysis parameters
        self.volume_spike_threshold = Config.VOLUME_SPIKE_THRESHOLD
        self.price_spike_threshold = Config.PRICE_SPIKE_THRESHOLD
        self.scan_interval = Config.SCAN_INTERVAL
        
        # Strategy state
        self.active_trades = {}
        self.market_data_cache = {}
        self.last_scan_time = {}
        
        logger.info(f"WhaleTrap Strategy initialized - Risk Mode: {risk_mode}")
    
    def get_top_coins(self) -> List[str]:
        """Get top coins based on volume and price action"""
        try:
            # Get volume leaders
            volume_leaders = self.binance.get_volume_leaders(Config.TOP_COINS_COUNT)
            
            # Get top gainers
            top_gainers = self.binance.get_top_gainers(Config.TOP_COINS_COUNT)
            
            # Combine and deduplicate
            all_symbols = set()
            for coin in volume_leaders + top_gainers:
                all_symbols.add(coin['symbol'])
            
            return list(all_symbols)[:Config.TOP_COINS_COUNT]
        
        except Exception as e:
            logger.error(f"Error getting top coins: {e}")
            return ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT', 'SOLUSDT']
    
    def get_market_data(self, symbol: str, interval: str = '1m', limit: int = 100) -> pd.DataFrame:
        """Get and process market data for analysis"""
        try:
            klines = self.binance.get_klines(symbol, interval, limit)
            
            if not klines or 'error' in klines:
                return pd.DataFrame()
            
            df = pd.DataFrame(klines, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_volume', 'trades', 'taker_buy_base',
                'taker_buy_quote', 'ignore'
            ])
            
            # Convert to numeric
            numeric_columns = ['open', 'high', 'low', 'close', 'volume']
            for col in numeric_columns:
                df[col] = pd.to_numeric(df[col])
            
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            
            return df
        
        except Exception as e:
            logger.error(f"Error getting market data for {symbol}: {e}")
            return pd.DataFrame()
    
    def calculate_technical_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate technical indicators for analysis"""
        if df.empty:
            return df
        
        try:
            # Volume indicators
            df['volume_sma'] = ta.volume.volume_sma(df['close'], df['volume'], window=20)
            df['volume_ratio'] = df['volume'] / df['volume_sma']
            
            # Price indicators
            df['price_sma'] = ta.trend.sma_indicator(df['close'], window=20)
            df['price_ema'] = ta.trend.ema_indicator(df['close'], window=12)
            df['rsi'] = ta.momentum.rsi(df['close'], window=14)
            df['macd'] = ta.trend.macd_diff(df['close'])
            df['bb_upper'], df['bb_middle'], df['bb_lower'] = ta.volatility.bollinger_bands(df['close'])
            
            # Volatility indicators
            df['atr'] = ta.volatility.average_true_range(df['high'], df['low'], df['close'])
            df['price_change'] = df['close'].pct_change()
            df['volume_change'] = df['volume'].pct_change()
            
            return df
        
        except Exception as e:
            logger.error(f"Error calculating indicators: {e}")
            return df
    
    def detect_volume_spike(self, df: pd.DataFrame) -> bool:
        """Detect unusual volume spikes"""
        if df.empty or len(df) < 20:
            return False
        
        try:
            current_volume = df['volume'].iloc[-1]
            avg_volume = df['volume'].rolling(window=20).mean().iloc[-1]
            
            volume_ratio = current_volume / avg_volume if avg_volume > 0 else 0
            
            return volume_ratio > self.volume_spike_threshold
        
        except Exception as e:
            logger.error(f"Error detecting volume spike: {e}")
            return False
    
    def detect_price_spike(self, df: pd.DataFrame) -> bool:
        """Detect unusual price movements"""
        if df.empty or len(df) < 10:
            return False
        
        try:
            # Check recent price change
            recent_change = abs(df['price_change'].iloc[-1])
            
            # Check if price is above upper Bollinger Band
            current_price = df['close'].iloc[-1]
            bb_upper = df['bb_upper'].iloc[-1]
            
            # Check RSI for overbought conditions
            current_rsi = df['rsi'].iloc[-1]
            
            return (recent_change > self.price_spike_threshold / 100 or 
                   current_price > bb_upper * 1.02 or 
                   current_rsi > 70)
        
        except Exception as e:
            logger.error(f"Error detecting price spike: {e}")
            return False
    
    def detect_whale_activity(self, symbol: str) -> Dict:
        """Detect potential whale activity patterns"""
        try:
            # Get order book
            order_book = self.binance.get_order_book(symbol, limit=100)
            
            if 'error' in order_book:
                return {'detected': False, 'confidence': 0}
            
            bids = pd.DataFrame(order_book['bids'], columns=['price', 'quantity'])
            asks = pd.DataFrame(order_book['asks'], columns=['price', 'quantity'])
            
            bids['price'] = pd.to_numeric(bids['price'])
            bids['quantity'] = pd.to_numeric(bids['quantity'])
            asks['price'] = pd.to_numeric(asks['price'])
            asks['quantity'] = pd.to_numeric(asks['quantity'])
            
            # Calculate order book imbalance
            total_bid_volume = bids['quantity'].sum()
            total_ask_volume = asks['quantity'].sum()
            
            imbalance = (total_bid_volume - total_ask_volume) / (total_bid_volume + total_ask_volume)
            
            # Check for large orders
            large_bids = bids[bids['quantity'] > bids['quantity'].quantile(0.9)]
            large_asks = asks[asks['quantity'] > asks['quantity'].quantile(0.9)]
            
            whale_confidence = 0
            
            # Strong buying pressure
            if imbalance > 0.2 and len(large_bids) > len(large_asks):
                whale_confidence += 0.4
            
            # Large order presence
            if len(large_bids) > 5 or len(large_asks) > 5:
                whale_confidence += 0.3
            
            # Price near support/resistance
            current_price = self.binance.get_ticker_price(symbol)
            if current_price:
                price_position = (current_price - bids['price'].min()) / (asks['price'].max() - bids['price'].min())
                if price_position < 0.1 or price_position > 0.9:
                    whale_confidence += 0.3
            
            return {
                'detected': whale_confidence > 0.5,
                'confidence': whale_confidence,
                'imbalance': imbalance,
                'large_orders': len(large_bids) + len(large_asks)
            }
        
        except Exception as e:
            logger.error(f"Error detecting whale activity: {e}")
            return {'detected': False, 'confidence': 0}
    
    def analyze_market_conditions(self, symbol: str) -> Dict:
        """Comprehensive market analysis"""
        try:
            # Get market data
            df = self.get_market_data(symbol, '1m', 100)
            if df.empty:
                return {'signal': 'no_data', 'confidence': 0}
            
            # Calculate indicators
            df = self.calculate_technical_indicators(df)
            
            # Check for spikes
            volume_spike = self.detect_volume_spike(df)
            price_spike = self.detect_price_spike(df)
            
            # Check whale activity
            whale_activity = self.detect_whale_activity(symbol)
            
            # Get 24hr stats
            ticker_24h = self.binance.get_24hr_ticker(symbol)
            
            # Calculate signal strength
            signal_strength = 0
            signal_type = 'neutral'
            
            # Volume analysis
            if volume_spike:
                signal_strength += 0.3
                signal_type = 'volume_spike'
            
            # Price analysis
            if price_spike:
                signal_strength += 0.3
                signal_type = 'price_spike'
            
            # Whale activity
            if whale_activity['detected']:
                signal_strength += whale_activity['confidence'] * 0.4
                signal_type = 'whale_activity'
            
            # Trend analysis
            if len(df) >= 20:
                current_price = df['close'].iloc[-1]
                sma_20 = df['price_sma'].iloc[-1]
                
                if current_price > sma_20 * 1.02:  # Strong uptrend
                    signal_strength += 0.2
                elif current_price < sma_20 * 0.98:  # Strong downtrend
                    signal_strength -= 0.2
            
            # RSI analysis
            if len(df) >= 14:
                rsi = df['rsi'].iloc[-1]
                if rsi < 30:  # Oversold
                    signal_strength += 0.1
                elif rsi > 70:  # Overbought
                    signal_strength -= 0.1
            
            return {
                'symbol': symbol,
                'signal': signal_type,
                'confidence': min(signal_strength, 1.0),
                'volume_spike': volume_spike,
                'price_spike': price_spike,
                'whale_activity': whale_activity,
                'current_price': df['close'].iloc[-1] if not df.empty else None,
                'volume_ratio': df['volume_ratio'].iloc[-1] if not df.empty else None,
                'rsi': df['rsi'].iloc[-1] if not df.empty else None,
                'timestamp': datetime.now()
            }
        
        except Exception as e:
            logger.error(f"Error analyzing market conditions for {symbol}: {e}")
            return {'signal': 'error', 'confidence': 0}
    
    def should_enter_trade(self, analysis: Dict) -> bool:
        """Determine if we should enter a trade based on analysis"""
        if analysis['signal'] == 'no_data' or analysis['signal'] == 'error':
            return False
        
        # Minimum confidence threshold
        if analysis['confidence'] < 0.6:
            return False
        
        # Check if we already have an active trade for this symbol
        if analysis['symbol'] in self.active_trades:
            return False
        
        # Check available balance
        balance = self.binance.get_balance('USDT')
        if balance < self.position_size:
            return False
        
        return True
    
    def calculate_position_size(self, symbol: str, confidence: float) -> float:
        """Calculate position size based on confidence and risk"""
        base_size = self.position_size
        
        # Adjust based on confidence
        confidence_multiplier = 0.5 + (confidence * 0.5)  # 0.5 to 1.0
        
        # Adjust based on risk mode
        risk_multiplier = 1.0 if self.risk_mode == 'pro' else 2.0
        
        position_size = base_size * confidence_multiplier * risk_multiplier
        
        # Ensure we don't exceed available balance
        balance = self.binance.get_balance('USDT')
        return min(position_size, balance * 0.95)  # Keep 5% buffer
    
    def execute_trade(self, symbol: str, analysis: Dict) -> bool:
        """Execute a trade based on analysis"""
        try:
            if not self.should_enter_trade(analysis):
                return False
            
            # Calculate position size
            position_size = self.calculate_position_size(symbol, analysis['confidence'])
            
            if position_size < 10:  # Minimum trade size
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
            stop_loss_price = current_price * (1 - self.stop_loss_pct / 100)
            take_profit_price = current_price * (1 + self.take_profit_pct / 100)
            
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
                'entry_time': datetime.now()
            }
            
            logger.info(f"Entered trade for {symbol}: {quantity} @ {current_price}")
            logger.info(f"Stop Loss: {stop_loss_price}, Take Profit: {take_profit_price}")
            
            return True
        
        except Exception as e:
            logger.error(f"Error executing trade for {symbol}: {e}")
            return False
    
    def monitor_trades(self):
        """Monitor active trades and manage exits"""
        for symbol, trade_info in list(self.active_trades.items()):
            try:
                current_price = self.binance.get_ticker_price(symbol)
                if not current_price:
                    continue
                
                entry_price = trade_info['entry_price']
                stop_loss = trade_info['stop_loss']
                take_profit = trade_info['take_profit']
                
                # Check stop loss
                if current_price <= stop_loss:
                    self.close_trade(symbol, 'stop_loss', current_price)
                
                # Check take profit
                elif current_price >= take_profit:
                    self.close_trade(symbol, 'take_profit', current_price)
                
                # Check time-based exit (optional)
                time_in_trade = datetime.now() - trade_info['entry_time']
                if time_in_trade > timedelta(hours=4):  # 4-hour max hold
                    self.close_trade(symbol, 'time_exit', current_price)
            
            except Exception as e:
                logger.error(f"Error monitoring trade for {symbol}: {e}")
    
    def close_trade(self, symbol: str, exit_reason: str, exit_price: float):
        """Close a trade and calculate PnL"""
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
                
                logger.info(f"Closed trade for {symbol}: {exit_reason}")
                logger.info(f"PnL: {pnl:.2f} USDT")
                
                # Remove from active trades
                del self.active_trades[symbol]
            
        except Exception as e:
            logger.error(f"Error closing trade for {symbol}: {e}")
    
    def scan_market(self):
        """Main market scanning function"""
        try:
            symbols = self.get_top_coins()
            
            for symbol in symbols:
                # Skip if we already have an active trade
                if symbol in self.active_trades:
                    continue
                
                # Analyze market conditions
                analysis = self.analyze_market_conditions(symbol)
                
                # Save market data
                if analysis.get('current_price'):
                    self.db.save_market_data(symbol, analysis['current_price'], 0)
                
                # Execute trade if conditions are met
                if self.should_enter_trade(analysis):
                    self.execute_trade(symbol, analysis)
                
                # Small delay to avoid rate limits
                time.sleep(0.1)
            
            # Monitor existing trades
            self.monitor_trades()
            
            # Save wallet balance
            balance = self.binance.get_balance('USDT')
            self.db.save_wallet_balance(balance)
            
        except Exception as e:
            logger.error(f"Error in market scan: {e}")
    
    def run(self):
        """Main strategy loop"""
        logger.info("Starting WhaleTrap Strategy...")
        
        while True:
            try:
                self.scan_market()
                time.sleep(self.scan_interval)
                
            except KeyboardInterrupt:
                logger.info("Strategy stopped by user")
                break
            except Exception as e:
                logger.error(f"Strategy error: {e}")
                time.sleep(60)  # Wait before retrying 