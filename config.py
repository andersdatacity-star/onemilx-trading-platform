import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    # Binance API Configuration
    BINANCE_API_KEY = os.getenv('BINANCE_API_KEY', 'your_api_key_here')
    BINANCE_SECRET_KEY = os.getenv('BINANCE_SECRET_KEY', 'your_secret_key_here')
    
    # Ultra Trading Configuration - OneMilX Strategy (45 USD Start)
    RISK_MODE = os.getenv('RISK_MODE', 'ultra')  # 'ultra' for 1M goal
    INITIAL_CAPITAL = float(os.getenv('INITIAL_CAPITAL', '45'))  # 45 USD start
    
    # Position Sizing - Micro amounts per coin for 45 USD
    BASE_POSITION_SIZE = float(os.getenv('BASE_POSITION_SIZE', '0.1'))  # 0.1 USDT per coin
    MAX_COINS_TO_TRADE = int(os.getenv('MAX_COINS_TO_TRADE', '100'))  # Start with 100 coins
    
    # Ultra Aggressive Settings
    STOP_LOSS_PERCENTAGE = float(os.getenv('STOP_LOSS_PERCENTAGE', '0.5'))  # 0.5% stop loss
    TAKE_PROFIT_PERCENTAGE = float(os.getenv('TAKE_PROFIT_PERCENTAGE', '1.0'))  # 1% take profit
    
    # Market Configuration - Ultra Fast
    TOP_COINS_COUNT = 100  # Start with 100 coins
    SCAN_INTERVAL = 5  # 5 seconds between scans
    VOLUME_SPIKE_THRESHOLD = 1.5  # 150% volume increase
    PRICE_SPIKE_THRESHOLD = 0.5   # 0.5% price increase
    
    # Compound Reinvestment
    COMPOUND_MODE = True  # Always reinvest profits
    MIN_PROFIT_TO_REINVEST = 0.01  # Reinvest even 0.01 USDT profit
    
    # AI Control Settings
    AI_CONTROLLED = True  # AI makes all decisions
    AUTO_ADJUST_POSITION_SIZE = True  # Increase position size with profits
    
    # Database Configuration
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///trading_data.db')
    
    # Logging Configuration
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    @classmethod
    def get_position_size(cls):
        """Get position size based on current capital and compound growth"""
        base_size = cls.BASE_POSITION_SIZE
        
        # If compound mode is on, increase position size with profits
        if cls.COMPOUND_MODE and cls.AUTO_ADJUST_POSITION_SIZE:
            # This will be calculated dynamically based on current capital
            return base_size
        
        return base_size
    
    @classmethod
    def get_max_total_exposure(cls):
        """Calculate maximum total exposure across all coins"""
        return cls.MAX_COINS_TO_TRADE * cls.BASE_POSITION_SIZE
    
    @classmethod
    def get_target_daily_return(cls):
        """Target daily return for 1M in 6 months from 45 USD"""
        # To reach 1M from 45 in 6 months (180 days):
        # 45 * (1 + daily_return)^180 = 1,000,000
        # daily_return = (1,000,000/45)^(1/180) - 1
        # daily_return ≈ 0.052 or 5.2% daily
        return 0.052  # 5.2% daily target for 45 USD start 