"""
Configuration file for HFT Engine
Coinbase Exchange API credentials for authenticated access
"""

# Coinbase Exchange API Configuration
COINBASE_API_KEY = "1e90604a-e1fd-43ce-8e08-656d0c3f83e2"
COINBASE_API_SECRET = "krJurQqdcSDUoLS1ogJit+qxq64dIjXEQzxzezoH3OLgwx1YUHpt1IM80u23zvaWhbOfRAhksmWw5sDPLsmDzQ=="
COINBASE_API_PASSPHRASE = ""  # Coinbase Exchange typically doesn't require passphrase for new API keys

# CF Benchmarks API Configuration (for accurate prediction market targets)
CF_BENCHMARKS_API_KEY = ""  # Requires license from CF Benchmarks
CF_BENCHMARKS_API_USERNAME = ""  # Username from CF Benchmarks
CF_BENCHMARKS_API_URL = "https://www.cfbenchmarks.com/api"

# API Configuration
COINBASE_API_URL = "https://api.exchange.coinbase.com"
COINBASE_WS_URL = "wss://ws-feed.exchange.coinbase.com"

# Data source configuration
DATA_SOURCE = "l3"  # Options: "l2" (default, no auth), "l3" (requires auth), "alternative"
PREDICTION_MARKET_SOURCE = "api"  # Options: "api", "manual", "coinbase_spot"
PREDICTION_MARKET_API = "coinmarketcap"  # Options: "coinmarketcap", "terminalfeed", "sintra", "sequence", "vezta", "polymarket", "kalshi"

# Prediction Market API Endpoints
SEQUENCE_API_URL = "https://api.sequencemkts.com/v1/markets"
VEZTA_API_URL = "https://docs.vezta.io/api/markets"
POLYMARKET_API_URL = "https://gamma-api.polymarket.com"
KALSHI_API_URL = "https://api.elections.kalshi.com/trade-api/v2"
COINMARKETCAP_API_URL = "https://pro-api.coinmarketcap.com/public-api/v1/simple/price"
TERMINALFEED_API_URL = "https://terminalfeed.io/api/btc-price"
SINTRA_API_URL = "https://sintra.fi/api/btcusd"

# Alternative exchange options
ALTERNATIVE_EXCHANGE = "binance"  # Options: "binance", "kraken", "bitstamp"

# Risk Management Configuration
RISK_MANAGEMENT_ENABLED = True
TOTAL_BANKROLL = 1000.0  # Total capital in USD
MAX_POSITION_SIZE_PERCENT = 0.05  # Maximum 5% of bankroll per trade
DEFAULT_POSITION_SIZE_PERCENT = 0.02  # Default 2% of bankroll per trade
STOP_LOSS_PERCENT = 0.01  # 1% stop loss
TAKE_PROFIT_PERCENT = 0.02  # 2% take profit
KELLY_CRITERION_ENABLED = False  # Kelly criterion for optimal sizing

# Confidence Thresholds
MIN_CONFIDENCE_TO_BET = 0.50  # 50% minimum confidence
HIGH_CONFIDENCE_THRESHOLD = 0.70  # 70% for increased position sizing
MAX_CONFIDENCE_THRESHOLD = 0.90  # 90% for maximum confidence

# Expected Move Thresholds
MIN_EXPECTED_MOVE_PERCENT = 0.001  # 0.1% minimum expected move
OPTIMAL_EXPECTED_MOVE_PERCENT = 0.002  # 0.2% optimal expected move

# Timing Configuration
OPTIMAL_ENTRY_TIME_REMAINING = 120  # 2 minutes remaining
LATE_ENTRY_THRESHOLD = 60  # 1 minute remaining (avoid last minute)
NO_ENTRY_THRESHOLD = 30  # 30 seconds remaining (too volatile)

# Volatility Regime Detection
VOLATILITY_WINDOW = 60  # 60 seconds for volatility calculation
HIGH_VOLATILITY_THRESHOLD = 0.002  # High volatility threshold
LOW_VOLATILITY_THRESHOLD = 0.0005  # Low volatility threshold

# Signal Alignment Requirements
SIGNAL_ALIGNMENT_REQUIRED = True  # Require all signals to align
MIN_BULLISH_SIGNALS = 2  # Minimum bullish signals for UP bets
MIN_BEARISH_SIGNALS = 2  # Minimum bearish signals for DOWN bets

# Logging configuration
LOG_LEVEL = "INFO"  # Options: "DEBUG", "INFO", "WARNING", "ERROR"