# HFT Microstructure & Deep Learning Prediction Engine

A production-grade, low-latency market microstructure engine and deep learning prediction pipeline for cryptocurrency trading analysis.

## Features

### Phase 1: High-Frequency Data Ingestion
- **WebSocket Client**: Real-time connection to Coinbase Exchange WebSocket endpoint
- **L3 Order Book**: Full Level 3 order book reconstruction with optimized data structures
- **Sequence Validation**: Automatic detection and recovery from sequence gaps
- **State Management**: In-memory order tracking by order_id, side, price, and remaining size

### Phase 2: Quantitative Microstructure Features
- **Order Flow Imbalance (OFI)**: Net order flow changes across top book levels
- **Volume Imbalance (VOI)**: Real-time bid/ask volume analysis
- **Micro-Price**: Volume-weighted fair price accounting for queue imbalance
- **Cancellation Velocity**: Detection of spoofing and liquidity withdrawal
- **Multi-Scale Analysis**: Rolling windows at 100ms, 500ms, 1s, 5s, and 10s

### Phase 3: Machine Learning Pipeline
- **LightGBM Model**: Gradient boosting for online learning
- **Feature Matrix**: Multi-scale OFI signals, micro-price velocity, cancel-to-trade ratios
- **Online Learning**: Continuous model updates with rolling retraining
- **Probability Estimation**: Expected terminal price distribution

### Phase 4: Stochastic Bridge
- **Time-Decaying Bridge**: Brownian bridge dynamics for price distribution
- **Probability Estimation**: Over/Under probability calculations
- **Market Condition Adaptation**: Volatility and momentum adjustments

### Phase 5: CLI Interface
- **Real-time Display**: High-precision predictions at target timestamps
- **Microstructure Signals**: OFI, depth imbalance, momentum vectors
- **Forecast Range**: Predicted high/low and expected close
- **Confidence Ratings**: Low/Moderate/High/Maximum confidence levels

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Setup

1. Navigate to the hft_engine directory:
```bash
cd hft_engine
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

Run the main application:
```bash
python main.py
```

### Configuration

### Basic Configuration
You can customize the following parameters in `main.py`:
- `product_id`: Trading pair (default: "BTC-USD")
- `window_duration`: Prediction window duration in seconds (default: 900 = 15 minutes)

### Advanced Configuration (L3 Data)
For L3 (Level 3) order book data, you need Coinbase Exchange API credentials:

1. **Get API Keys**:
   - Create a Coinbase Exchange account (not regular Coinbase)
   - Go to API settings in your account
   - Generate API key, secret, and passphrase
   - Set permissions to "View" for order book data

2. **Configure the System**:
   - Open `config.py`
   - Add your credentials:
     ```python
     COINBASE_API_KEY = "your_api_key"
     COINBASE_API_SECRET = "your_api_secret" 
     COINBASE_API_PASSPHRASE = "your_passphrase"
     ```
   - Set `DATA_SOURCE = "l3"`

3. **Or Use Environment Variables** (recommended for security):
   ```bash
   set COINBASE_API_KEY=your_key
   set COINBASE_API_SECRET=your_secret
   set COINBASE_API_PASSPHRASE=your_passphrase
   ```

### Data Source Options
- **L2 (Default)**: Public data, no authentication required, good for general analysis
- **L3**: Requires API credentials, more granular order tracking, better for microstructure analysis

### CLI Interface

When prompted, enter a strike price for the prediction window:
- Press Enter to use the current mid-price as the strike
- Enter a specific price to set a custom strike

The system will display:
- Time remaining in current window
- Live spot price and micro-price
- Target strike and delta/edge
- Microstructure signals (OFI, depth imbalance, momentum)
- Forecast range (predicted high/low/expected close)
- Final directional call (OVER/UNDER)
- Confidence rating

## Architecture

### Core Components

1. **order_book.py**: Limit order book management and reconstruction
2. **websocket_client.py**: Coinbase WebSocket connection and message handling
3. **microstructure_features.py**: Real-time feature calculation
4. **ml_pipeline.py**: Machine learning model and online learning
5. **stochastic_bridge.py**: Time-decaying probability estimation
6. **cli_interface.py**: User interface and display
7. **error_handler.py**: Comprehensive error handling and recovery
8. **main.py**: Application entry point

### Data Flow

1. WebSocket receives L3 order book updates
2. Order book is reconstructed with sequence validation
3. Microstructure features are calculated in real-time
4. ML model processes features for predictions
5. Stochastic bridge refines predictions with time decay
6. CLI displays results and updates continuously

## Error Handling

The system includes comprehensive error handling:
- **Automatic Reconnection**: WebSocket reconnection with exponential backoff
- **Circuit Breakers**: Component-level circuit breakers to prevent cascading failures
- **Graceful Shutdown**: Clean shutdown with model saving
- **Error Logging**: Detailed error tracking and statistics

## Model Persistence

The system automatically saves the trained model to `hft_model.pkl` on shutdown. This model will be loaded on subsequent runs to continue learning from historical data.

## Constraints

- **No Betting Odds**: Pure physics, order flow, and quantitative price data only
- **No P/L Tracking**: No ledger of winnings or losses
- **Stability**: Automatic error handling and reconnection

## Performance Considerations

- **Low Latency**: Optimized data structures (sortedcontainers) for order book management
- **Real-time Processing**: Asyncio for concurrent operations
- **Memory Efficiency**: Rolling windows with bounded queues
- **Scalability**: Component-based architecture for easy extension

## Troubleshooting

### Connection Issues
- Check internet connectivity
- Verify Coinbase API status
- Check firewall settings

### Model Performance
- Ensure sufficient historical data has accumulated
- Monitor error rates in logs
- Check feature importance for model insights

### High Memory Usage
- Reduce rolling window sizes in microstructure_features.py
- Limit feature buffer size in ml_pipeline.py

## Logging

The system logs to both file (`hft_engine.log`) and console. Log levels can be adjusted in the logging configuration.

## License

This is a quantitative trading system for educational and research purposes.

## Disclaimer

This system is for educational and research purposes only. It does not constitute financial advice. Past performance does not guarantee future results. Use at your own risk.