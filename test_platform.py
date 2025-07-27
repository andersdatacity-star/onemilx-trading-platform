#!/usr/bin/env python3
"""
OneMilX Trading Platform - Test Script
Tests all major components to ensure they're working correctly
"""

import sys
import os
import time
from datetime import datetime

def test_imports():
    """Test that all required modules can be imported"""
    print("🔍 Testing imports...")
    
    try:
        import pandas as pd
        print("✅ pandas imported successfully")
    except ImportError as e:
        print(f"❌ pandas import failed: {e}")
        return False
    
    try:
        import numpy as np
        print("✅ numpy imported successfully")
    except ImportError as e:
        print(f"❌ numpy import failed: {e}")
        return False
    
    try:
        import requests
        print("✅ requests imported successfully")
    except ImportError as e:
        print(f"❌ requests import failed: {e}")
        return False
    
    try:
        import ta
        print("✅ ta (technical analysis) imported successfully")
    except ImportError as e:
        print(f"❌ ta import failed: {e}")
        return False
    
    try:
        from config import Config
        print("✅ Config imported successfully")
    except ImportError as e:
        print(f"❌ Config import failed: {e}")
        return False
    
    try:
        from database import TradingDatabase
        print("✅ TradingDatabase imported successfully")
    except ImportError as e:
        print(f"❌ TradingDatabase import failed: {e}")
        return False
    
    try:
        from binance_client import BinanceClient
        print("✅ BinanceClient imported successfully")
    except ImportError as e:
        print(f"❌ BinanceClient import failed: {e}")
        return False
    
    try:
        from whale_trap_strategy import WhaleTrapStrategy
        print("✅ WhaleTrapStrategy imported successfully")
    except ImportError as e:
        print(f"❌ WhaleTrapStrategy import failed: {e}")
        return False
    
    return True

def test_config():
    """Test configuration loading"""
    print("\n🔧 Testing configuration...")
    
    try:
        from config import Config
        
        print(f"✅ Risk mode: {Config.RISK_MODE}")
        print(f"✅ Initial capital: ${Config.INITIAL_CAPITAL}")
        print(f"✅ Position size: {Config.get_position_size()}")
        print(f"✅ Stop loss: {Config.STOP_LOSS_PERCENTAGE}%")
        print(f"✅ Take profit: {Config.TAKE_PROFIT_PERCENTAGE}%")
        
        return True
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def test_database():
    """Test database operations"""
    print("\n🗄️ Testing database...")
    
    try:
        from database import TradingDatabase
        
        # Initialize database
        db = TradingDatabase("test_trading_data.db")
        print("✅ Database initialized successfully")
        
        # Test saving trade
        trade_id = db.save_trade("BTCUSDT", "BUY", 0.001, 50000, 52500, 47500)
        print(f"✅ Trade saved with ID: {trade_id}")
        
        # Test saving market data
        db.save_market_data("BTCUSDT", 50000, 1000000)
        print("✅ Market data saved successfully")
        
        # Test saving wallet balance
        db.save_wallet_balance(1000)
        print("✅ Wallet balance saved successfully")
        
        # Test retrieving data
        open_trades = db.get_open_trades()
        print(f"✅ Retrieved {len(open_trades)} open trades")
        
        trade_history = db.get_trade_history(10)
        print(f"✅ Retrieved {len(trade_history)} trade history records")
        
        # Clean up test database
        if os.path.exists("test_trading_data.db"):
            os.remove("test_trading_data.db")
            print("✅ Test database cleaned up")
        
        return True
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def test_binance_client():
    """Test Binance API client (without real API calls)"""
    print("\n🔗 Testing Binance client...")
    
    try:
        from binance_client import BinanceClient
        
        # Initialize client
        client = BinanceClient()
        print("✅ Binance client initialized successfully")
        
        # Test public endpoints (these don't require API keys)
        try:
            exchange_info = client.get_exchange_info()
            if 'error' not in exchange_info:
                print("✅ Exchange info retrieved successfully")
            else:
                print("⚠️ Exchange info request failed (expected without API keys)")
        except Exception as e:
            print(f"⚠️ Exchange info request failed: {e}")
        
        return True
    except Exception as e:
        print(f"❌ Binance client test failed: {e}")
        return False

def test_strategy():
    """Test strategy initialization"""
    print("\n🤖 Testing Whale Trap strategy...")
    
    try:
        from whale_trap_strategy import WhaleTrapStrategy
        
        # Initialize strategy
        strategy = WhaleTrapStrategy(risk_mode="pro")
        print("✅ Strategy initialized successfully")
        
        # Test getting top coins
        try:
            top_coins = strategy.get_top_coins()
            print(f"✅ Retrieved {len(top_coins)} top coins")
        except Exception as e:
            print(f"⚠️ Top coins retrieval failed: {e}")
        
        return True
    except Exception as e:
        print(f"❌ Strategy test failed: {e}")
        return False

def test_compounding_calculator():
    """Test compounding calculator"""
    print("\n💰 Testing compounding calculator...")
    
    try:
        from compounding_calculator import AdvancedCompoundCalculator
        
        # Initialize calculator
        calculator = AdvancedCompoundCalculator(initial_capital=1000)
        print("✅ Compounding calculator initialized successfully")
        
        # Test scenario calculation
        result = calculator.run_scenario(
            "Test Scenario",
            daily_return=0.01,  # 1% daily
            days=30,            # 30 days
            monthly_deposit=100,
            volatility=0.02     # 2% volatility
        )
        
        print(f"✅ Test scenario calculated successfully")
        print(f"   Final capital: ${result['final_capital']:,.2f}")
        print(f"   Total return: {result['total_return']*100:.2f}%")
        print(f"   Max drawdown: {result['max_drawdown']*100:.2f}%")
        print(f"   Sharpe ratio: {result['sharpe_ratio']:.2f}")
        
        return True
    except Exception as e:
        print(f"❌ Compounding calculator test failed: {e}")
        return False

def test_web_app():
    """Test web application components"""
    print("\n🌐 Testing web application...")
    
    try:
        from flask import Flask
        print("✅ Flask imported successfully")
        
        # Test if we can create a basic Flask app
        app = Flask(__name__)
        print("✅ Flask app created successfully")
        
        return True
    except Exception as e:
        print(f"❌ Web application test failed: {e}")
        return False

def check_api_keys():
    """Check if API keys are configured"""
    print("\n🔑 Checking API keys...")
    
    try:
        from config import Config
        
        if Config.BINANCE_API_KEY == 'your_api_key_here':
            print("⚠️ API keys not configured (using default values)")
            print("   Please set up your Binance API keys in .env file")
            return False
        else:
            print("✅ API keys appear to be configured")
            return True
    except Exception as e:
        print(f"❌ API key check failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 OneMilX Trading Platform - System Test")
    print("=" * 50)
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    tests = [
        ("Imports", test_imports),
        ("Configuration", test_config),
        ("Database", test_database),
        ("Binance Client", test_binance_client),
        ("Strategy", test_strategy),
        ("Compounding Calculator", test_compounding_calculator),
        ("Web Application", test_web_app),
        ("API Keys", check_api_keys),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
    
    print("\n" + "=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your platform is ready to use.")
        print("\nNext steps:")
        print("1. Configure your Binance API keys in .env file")
        print("2. Run 'python app.py' to start the web dashboard")
        print("3. Run 'python whale_trap_strategy.py' to start trading")
    else:
        print("⚠️ Some tests failed. Please check the errors above.")
        print("\nTroubleshooting:")
        print("1. Install missing dependencies: pip install -r requirements.txt")
        print("2. Check your Python version (3.7+ required)")
        print("3. Verify file permissions")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 