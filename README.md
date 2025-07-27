# 🚀 OneMilX Trading Platform

[![Deploy to Heroku](https://github.com/andersdatacity-star/onemilx-trading-platform/workflows/Deploy%20to%20Heroku/badge.svg)](https://github.com/andersdatacity-star/onemilx-trading-platform/actions)

## 🌟 **OneMilX Ultra AI Strategy - 1 Million in 6 Months**

En avanceret cryptocurrency trading platform med Whale Trap strategi, real-time market analysis og professionelt web dashboard.

## 🌟 Features

### 🤖 Trading Strategy
- **Whale Trap Strategy**: Avanceret algoritme der detekterer whale aktivitet og volume spikes
- **Real-time Market Analysis**: Tekniske indikatorer, volume analysis og price action
- **Risk Management**: Automatisk stop-loss og take-profit ordrer
- **Multiple Risk Modes**: Pro (konservativ) og Ultra (aggressiv)

### 📊 Web Dashboard
- **Real-time Monitoring**: Live tracking af trades og portfolio
- **Interactive Charts**: Wallet balance historik og market data
- **Strategy Control**: Start/stop strategi med forskellige risk modes
- **Market Analysis**: Symbol-specifik analysis og top coins tracking

### 💰 Compounding Calculator
- **Multiple Scenarios**: Conservative, Moderate, Aggressive, Ultra
- **Risk Metrics**: Sharpe ratio, max drawdown, volatility analysis
- **Visualization**: Charts og grafer for bedre forståelse
- **Export Functionality**: JSON export af alle resultater

### 🔧 Technical Features
- **Binance API Integration**: Sikker og pålidelig trading
- **SQLite Database**: Lokal data storage for trades og market data
- **Error Handling**: Robust error handling og logging
- **Modular Architecture**: Let at udvide og tilpasse

## 🚀 Installation

### 1. Clone Repository
```bash
git clone <repository-url>
cd OneMilX_Trading_Platform
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure API Keys
Opret en `.env` fil i projektets rod mappe:

```env
# Binance API Configuration
BINANCE_API_KEY=your_api_key_here
BINANCE_SECRET_KEY=your_secret_key_here

# Trading Configuration
RISK_MODE=pro
INITIAL_CAPITAL=1000
MAX_POSITION_SIZE=15
STOP_LOSS_PERCENTAGE=2.0
TAKE_PROFIT_PERCENTAGE=5.0

# Database Configuration
DATABASE_URL=sqlite:///trading_data.db

# Logging Configuration
LOG_LEVEL=INFO
```

### 4. Get Binance API Keys
1. Gå til [Binance](https://www.binance.com)
2. Opret en konto eller log ind
3. Gå til API Management
4. Opret en ny API key med trading permissions
5. Kopier API key og Secret key til din `.env` fil

## 📖 Brug

### Start Web Dashboard
```bash
python app.py
```
Åbn din browser og gå til `http://localhost:5000`

### Kør Whale Trap Strategy
```bash
python whale_trap_strategy.py
```

### Kør Compounding Calculator
```bash
python compounding_calculator.py
```

## 🎯 Whale Trap Strategy

### Hvordan det virker:
1. **Market Scanning**: Scanner top 20 coins baseret på volume og price action
2. **Volume Analysis**: Detekterer uventede volume spikes (200%+ over gennemsnit)
3. **Price Analysis**: Identificerer price spikes og Bollinger Band breakouts
4. **Whale Detection**: Analyserer order book for whale aktivitet
5. **Signal Generation**: Kombinerer alle faktorer for at generere trading signals
6. **Risk Management**: Automatisk position sizing og stop-loss/take-profit

### Tekniske Indikatorer:
- **Volume SMA**: 20-period volume moving average
- **Price SMA/EMA**: 20-period simple og exponential moving averages
- **RSI**: 14-period Relative Strength Index
- **MACD**: Moving Average Convergence Divergence
- **Bollinger Bands**: Volatility bands
- **ATR**: Average True Range

## 📊 Dashboard Features

### Account Overview
- Real-time USDT balance
- Total PnL tracking
- Active trades count
- Strategy status

### Strategy Control
- Start/stop strategi
- Risk mode selection (Pro/Ultra)
- Real-time status monitoring

### Market Analysis
- Symbol-specifik analysis
- Top volume leaders
- Top gainers tracking
- Technical indicator display

### Trade Management
- Active trades overview
- Trade history
- PnL tracking
- Manual order placement

## 💡 Compounding Calculator

### Scenarios:
- **Conservative**: 0.5% daglig return, 2% volatilitet
- **Moderate**: 1.0% daglig return, 3% volatilitet  
- **Aggressive**: 1.5% daglig return, 4% volatilitet
- **Ultra**: 2.0% daglig return, 5% volatilitet

### Metrics:
- **Final Capital**: Slutkapital efter perioden
- **Total Return**: Total procentvis return
- **Max Drawdown**: Maksimale tab fra peak
- **Sharpe Ratio**: Risk-adjusted return

## ⚠️ Risk Disclaimer

**VIGTIGT**: Dette er et trading værktøj til uddannelsesformål. Cryptocurrency trading indebærer betydelig risiko:

- Du kan miste hele din investering
- Tidligere resultater garanterer ikke fremtidige resultater
- Test altid på testnet først
- Start med små beløb
- Følg altid proper risk management

## 🔧 Konfiguration

### Risk Modes:
- **Pro Mode**: Konservativ position sizing (15 USDT max)
- **Ultra Mode**: Aggressiv position sizing (30 USDT max)

### Trading Parameters:
- **Stop Loss**: 2% standard (konfigurerbar)
- **Take Profit**: 5% standard (konfigurerbar)
- **Scan Interval**: 30 sekunder (konfigurerbar)
- **Volume Spike Threshold**: 200% (konfigurerbar)

## 📁 Projektstruktur

```
OneMilX_Trading_Platform/
├── app.py                      # Flask web application
├── config.py                   # Configuration management
├── binance_client.py          # Binance API integration
├── whale_trap_strategy.py     # Main trading strategy
├── database.py                # Database operations
├── compounding_calculator.py  # Advanced compounding analysis
├── requirements.txt           # Python dependencies
├── templates/
│   └── dashboard.html         # Web dashboard template
├── README.md                  # This file
└── .env                       # Environment variables (create this)
```

## 🛠️ Udvidelse

### Tilføj nye strategier:
1. Opret en ny strategi klasse
2. Implementer `run()` metoden
3. Tilføj til web dashboard

### Tilføj nye indikatorer:
1. Modificer `calculate_technical_indicators()` i `whale_trap_strategy.py`
2. Tilføj signal logik i `analyze_market_conditions()`

### Tilføj nye exchanges:
1. Opret en ny exchange client klasse
2. Implementer standard API metoder
3. Opdater `whale_trap_strategy.py` til at bruge den nye client

## 🐛 Troubleshooting

### Common Issues:

**API Error 401**: Ugyldige API nøgler
- Tjek at dine API nøgler er korrekte
- Sørg for at API nøglerne har trading permissions

**Database Error**: SQLite problemer
- Sørg for at mappen har write permissions
- Tjek at SQLite er installeret

**Strategy not starting**: Threading problemer
- Genstart Flask applikationen
- Tjek logs for error messages

**No trades executing**: Market conditions
- Strategien er designet til at være selektiv
- Tjek at market conditions opfylder kriterierne
- Juster thresholds i `config.py` hvis nødvendigt

## 📞 Support

For support eller spørgsmål:
- Opret en issue på GitHub
- Tjek logs for error messages
- Verificer API nøgler og konfiguration

## 📄 License

Dette projekt er til uddannelsesformål. Brug på egen risiko.

---

**Husk**: Start altid med små beløb og test grundigt før du bruger større kapital! 🎯 