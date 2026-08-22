# HFT Engine Setup and Usage Guide

## Quick Start

### 1. Installation
```bash
cd hft_engine
pip install -r requirements.txt
```

### 2. Run Tests
```bash
python test_components.py
```

### 3. Start the Engine
```bash
python main.py
```

## System Overview

The HFT Microstructure & Deep Learning Prediction Engine is a complete production-grade system for analyzing cryptocurrency markets using order book data and machine learning.

### Core Components

1. **Order Book Management** (`order_book.py`)
   - Real-time L3 order book reconstruction
   - Sequence validation and automatic recovery
   - Optimized data structures using sortedcontainers

2. **WebSocket Client** (`websocket_client.py`)
   - Coinbase Exchange WebSocket connection
   - Automatic reconnection with exponential backoff
   - REST API fallback for snapshots

3. **Microstructure Features** (`microstructure_features.py`)
   - Order Flow Imbalance (OFI) calculation
   - Volume Imbalance (VOI) and depth analysis
   - Micro-price and momentum indicators
   - Multi-scale analysis (100ms to 10s windows)

4. **ML Pipeline** (`ml_pipeline.py`)
   - LightGBM model for online learning
   - Real-time feature preprocessing
   - Automatic model retraining
   - Model persistence

5. **Stochastic Bridge** (`stochastic_bridge.py`)
   - Time-decaying Brownian bridge dynamics
   - Probability estimation for price targets
   - Market condition adaptation
   - Confidence interval calculation

6. **CLI Interface** (`cli_interface.py`)
   - Real-time prediction display
   - Microstructure signal visualization
   - User interaction for strike prices
   - 15-minute prediction windows

7. **Error Handling** (`error_handler.py`)
   - Comprehensive error tracking
   - Circuit breaker pattern
   - Graceful shutdown mechanisms
   - Health monitoring

## Configuration

### Main Parameters (in `main.py`)
- `product_id`: Trading pair (default: "BTC-USD")
- `window_duration`: Prediction window in seconds (default: 900 = 15 minutes)

### Feature Windows (in `microstructure_features.py`)
- Default windows: [0.1, 0.5, 1.0, 5.0, 10.0] seconds
- Can be customized for different analysis frequencies

### ML Parameters (in `ml_pipeline.py`)
- Model: LightGBM with 100 estimators
- Learning rate: 0.05
- Retrain interval: 1000 samples
- Model path: "hft_model.pkl"

## Usage Flow

1. **Start the system**: Run `python main.py`
2. **Connection**: System connects to Coinbase WebSocket
3. **Strike Price**: Enter target strike price (or use current mid-price)
4. **Prediction Window**: System starts 15-minute prediction window
5. **Real-time Updates**: Display updates every second with:
   - Time remaining
   - Current prices (spot and micro-price)
   - Microstructure signals
   - Forecast range
   - Directional prediction (OVER/UNDER)
   - Confidence rating

## Output Interpretation

### Microstructure Signals
- **OFI Signal**: Positive (buying pressure), Negative (selling pressure), Neutral
- **Depth Imbalance**: Bid/ask volume distribution
- **Momentum**: Short-term price direction (Strong Bullish/Bearish/Neutral)

### Forecast Range
- **Predicted High/Low**: 2-standard deviation confidence interval
- **Expected Close**: Combined ML + bridge prediction
- **Directional Call**: OVER (price above strike) or UNDER (price below strike)

### Confidence Ratings
- **Maximum**: >80% confidence
- **High**: 60-80% confidence
- **Moderate**: 40-60% confidence
- **Low**: <40% confidence

## Model Training

The system uses online learning:
- Initial model starts untrained (returns NEUTRAL predictions)
- Accumulates samples during each prediction window
- Retrains automatically after 1000 samples
- Model is saved to `hft_model.pkl` on shutdown
- Model is loaded on subsequent runs

## Error Recovery

The system includes automatic error handling:
- **WebSocket Disconnection**: Automatic reconnection with exponential backoff
- **Sequence Gaps**: Automatic book synchronization via REST API
- **Component Failures**: Circuit breakers prevent cascading failures
- **Graceful Shutdown**: Clean shutdown with model saving

## Performance Considerations

### Memory Usage
- Order book: O(number of orders)
- Feature buffers: Rolling windows with bounded size
- Model: LightGBM memory footprint

### Latency
- WebSocket message processing: <1ms
- Feature calculation: <1ms
- ML inference: <10ms
- Total pipeline: <20ms per message

### Scalability
- Single product per instance
- Can run multiple instances for different products
- Asyncio for concurrent operations

## Troubleshooting

### Connection Issues
- Check internet connectivity
- Verify Coinbase API status
- Check firewall/proxy settings

### Model Performance
- Allow time for data accumulation
- Monitor feature importance
- Check prediction confidence

### System Performance
- Reduce feature window sizes if memory constrained
- Adjust display update interval
- Monitor CPU usage during peak hours

## Logs

The system logs to:
- Console: Real-time status messages
- File: `hft_engine.log` (detailed logs)

Log levels can be adjusted in `main.py`.

## Security Notes

- No API keys required (public Coinbase data)
- No account credentials needed
- No betting/gambling functionality
- Pure quantitative analysis

## Extensions

Potential enhancements:
- Add more trading pairs
- Implement portfolio management
- Add backtesting capabilities
- Create web interface
- Add database logging
- Implement alerting system

## Disclaimer

This system is for educational and research purposes only. It does not constitute financial advice. Use at your own risk.