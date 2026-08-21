"""
CLI Interface for HFT Microstructure Prediction Engine
Real-time display of predictions and market signals
"""
import asyncio
import sys
import logging
from datetime import datetime, timedelta
import os
import time
import pytz
from websocket_client import CoinbaseWebSocketClient
from microstructure_features import MicrostructureFeatures
from ml_pipeline import MLPipeline, OnlineLearningSystem
from stochastic_bridge import PredictionEngine
from error_handler import global_error_handler, global_shutdown_handler, ErrorHandler
from risk_management import RiskManager, PerformanceTracker
from prediction_market_api import PredictionMarketAPI
import config

logger = logging.getLogger(__name__)


class CLIInterface:
    def __init__(self, product_id="BTC-USD", window_duration=900):
        self.product_id = product_id
        self.window_duration = window_duration
        self.ws_client = CoinbaseWebSocketClient(product_id)
        self.feature_engine = MicrostructureFeatures()
        self.ml_pipeline = MLPipeline(model_path="hft_model.pkl")
        self.online_learning = OnlineLearningSystem(self.ml_pipeline, window_duration)
        self.prediction_engine = PredictionEngine(self.ml_pipeline, window_duration)
        
        self.running = False
        self.current_price = None
        self.strike_price = None
        self.last_prediction = None
        self.current_features = None
        self.display_update_interval = 1.0  # Update display every second
        
        # Reset circuit breaker for message_handler
        global_error_handler.reset_circuit_breaker("message_handler")
        
        # Prediction tracking for performance analysis
        self.prediction_history = []
        self.price_history = []
        
        # Risk management
        self.risk_manager = RiskManager()
        self.performance_tracker = PerformanceTracker()
        self.current_window_start = None
        self.entry_price = None
        
        # Prediction market API
        self.prediction_api = PredictionMarketAPI()
        self.auto_target_fetch = True
        
        # Time synchronization
        self.utc = pytz.UTC
        
    def get_coinbase_window_info(self):
        """Calculate current Coinbase 15-minute window info"""
        now = datetime.now(self.utc)
        
        # Coinbase 15-minute windows start at :00, :15, :30, :45
        minute = now.minute
        window_start_minute = (minute // 15) * 15
        
        # Calculate window start and end times
        window_start = now.replace(minute=window_start_minute, second=0, microsecond=0)
        window_end = window_start + timedelta(minutes=15)
        
        # Calculate time remaining
        time_remaining = (window_end - now).total_seconds()
        elapsed = (now - window_start).total_seconds()
        
        return {
            'window_start': window_start,
            'window_end': window_end,
            'time_remaining': max(0, time_remaining),
            'elapsed': elapsed,
            'window_number': int(now.timestamp() // 900)  # Unique window ID
        }
        
    def format_time(self, seconds):
        """Format seconds into MM:SS"""
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes:02d}:{secs:02d}"
    
    def format_price(self, price):
        """Format price with appropriate precision"""
        if price is None:
            return "N/A"
        return f"${price:,.2f}"
    
    def format_percentage(self, value):
        """Format percentage with sign"""
        if value is None:
            return "N/A"
        sign = "+" if value > 0 else ""
        return f"{sign}{value:.4f}%"
    
    def clear_screen(self):
        """Clear terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def display_prediction(self, prediction):
        """Display prediction in simplified, clear format"""
        self.clear_screen()
        
        # Get Coinbase window info
        window_info = self.get_coinbase_window_info()
        
        # Key prediction data
        current_price = prediction.get('current_price', 0)
        expected_close = prediction.get('expected_close', 0)
        strike_price = prediction.get('strike_price', 0)
        direction = prediction.get('direction', 'NEUTRAL')
        confidence = prediction.get('confidence', 0)
        time_remaining = window_info['time_remaining']
        
        # Determine simple UP/DOWN call (relative to target)
        if expected_close > strike_price:
            simple_call = "UP"
            price_diff = expected_close - strike_price
            price_diff_pct = (price_diff / strike_price) * 100
        elif expected_close < strike_price:
            simple_call = "DOWN"
            price_diff = strike_price - expected_close
            price_diff_pct = (price_diff / strike_price) * 100
        else:
            simple_call = "FLAT"
            price_diff = 0
            price_diff_pct = 0
        
        # Confidence level
        if confidence > 0.7:
            conf_level = "HIGH"
        elif confidence > 0.4:
            conf_level = "MEDIUM"
        else:
            conf_level = "LOW"
        
        print("=" * 70)
        print("                    PREDICTION: " + simple_call)
        print("=" * 70)
        
        # Main prediction call - big and clear
        print(f"\n📊 CURRENT BTC PRICE:  ${current_price:,.2f}")
        print(f"🎯 COINBASE TARGET:   ${strike_price:,.2f} ← Price to beat")
        print(f"🎯 OUR PREDICTION:    ${expected_close:,.2f} ← Where we think it ends")
        print(f"📈 EXPECTED MOVE:     {simple_call} ${price_diff:,.2f} ({price_diff_pct:+.2f}%)")
        print(f"⏱️  TIME REMAINING:   {self.format_time(time_remaining)}")
        print(f"🔒 CONFIDENCE:        {conf_level} ({confidence:.1%})")
        
        # Simple interpretation
        print(f"\n💡 INTERPRETATION:")
        if simple_call == "UP":
            print(f"   Predicted close ${expected_close:,.2f} will be ABOVE target ${strike_price:,.2f}")
            print(f"   Current price: ${current_price:,.2f}")
        elif simple_call == "DOWN":
            print(f"   Predicted close ${expected_close:,.2f} will be BELOW target ${strike_price:,.2f}")
            print(f"   Current price: ${current_price:,.2f}")
        else:
            print(f"   Predicted close ${expected_close:,.2f} will be around target ${strike_price:,.2f}")
            print(f"   Current price: ${current_price:,.2f}")
        
        # Coinbase window info
        print(f"\n🕐 Coinbase Window: {window_info['window_start'].strftime('%H:%M')} - {window_info['window_end'].strftime('%H:%M')} UTC")
        
        # Recent bias
        if len(self.prediction_history) > 10:
            recent_directions = [p['prediction']['direction'] for p in self.prediction_history[-10:]]
            over_count = recent_directions.count('OVER')
            under_count = recent_directions.count('UNDER')
            bias = "UP" if over_count > under_count else "DOWN" if under_count > over_count else "NEUTRAL"
            print(f"📊 Recent Bias: {bias} ({over_count} UP / {under_count} DOWN)")
        
        # Technical details (condensed)
        print(f"\n📋 TECHNICAL DETAILS:")
        print(f"   Order Flow: {prediction.get('ofi_signal', 'Neutral')}")
        print(f"   Momentum:   {prediction.get('momentum', 'Neutral')}")
        print(f"   Depth:      {prediction.get('depth_imbalance', 'Balanced')}")
        
        # Risk assessment
        print(f"\n🎲 RISK ASSESSMENT:")
        print(f"   Optimal Entry: {config.OPTIMAL_ENTRY_TIME_REMAINING} seconds remaining")
        print(f"   Late Entry: {config.LATE_ENTRY_THRESHOLD} seconds remaining")
        print(f"   Min Confidence: {config.MIN_CONFIDENCE_TO_BET:.0%}")
        print(f"   Min Expected Move: {config.MIN_EXPECTED_MOVE_PERCENT:.2%}")
        
        if confidence < config.MIN_CONFIDENCE_TO_BET:
            print(f"   ⚠️  Current confidence ({confidence:.1%}) below minimum ({config.MIN_CONFIDENCE_TO_BET:.1%})")
        if abs(price_diff_pct) < config.MIN_EXPECTED_MOVE_PERCENT * 100:
            print(f"   ⚠️  Expected move ({price_diff_pct:.2f}%) below minimum ({config.MIN_EXPECTED_MOVE_PERCENT * 100:.2f}%)")
        
        # Timing status
        if time_remaining <= config.OPTIMAL_ENTRY_TIME_REMAINING and time_remaining >= config.LATE_ENTRY_THRESHOLD:
            timing_status = "✅ OPTIMAL ENTRY TIME"
        elif time_remaining > config.OPTIMAL_ENTRY_TIME_REMAINING:
            timing_status = "⏰ WAIT FOR OPTIMAL TIME"
        elif time_remaining < config.LATE_ENTRY_THRESHOLD:
            timing_status = "⚠️  TOO LATE - AVOID ENTRY"
        
        print(f"   Timing: {timing_status}")
        
        print("=" * 70)
        print(f"Last Update: {datetime.now(self.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC")
        print("Press Ctrl+C to stop\n")
    
    async def handle_websocket_message(self, message, order_book):
        """Handle incoming WebSocket messages"""
        try:
            msg_type = message.get('type')
            
            # Log first few messages for debugging
            if not hasattr(self, 'message_count'):
                self.message_count = 0
            self.message_count += 1
            if self.message_count <= 10:
                print(f"Received message {self.message_count}: {msg_type}")
            
            # Handle ticker messages for price updates
            if msg_type == 'ticker':
                price = message.get('price')
                if price:
                    self.current_price = float(price)
                    if self.message_count <= 10:
                        print(f"Price from ticker: ${self.current_price}")
                return  # Don't process features for ticker messages
            
            # Update features with each message (skip ticker)
            if msg_type != 'ticker':
                try:
                    features = self.feature_engine.update_features(order_book, msg_type, message)
                except Exception as e:
                    # Feature calculation might fail if order book is empty
                    if self.message_count <= 10:
                        print(f"Feature calculation skipped: {e}")
                    features = None
                
                # Get current price from order book
                mid_price = order_book.get_mid_price()
                if mid_price:
                    self.current_price = mid_price
                    if self.message_count <= 10:
                        print(f"Current price updated: ${mid_price}")
                
                # Add observation to online learning system
                if self.current_price and features:
                    try:
                        self.online_learning.add_observation(features, self.current_price)
                    except Exception as e:
                        if self.message_count <= 10:
                            print(f"Observation skipped: {e}")
                
                # Get microstructure signals
                if features:
                    try:
                        signals = self.feature_engine.get_signal_interpretation(features)
                    except Exception as e:
                        if self.message_count <= 10:
                            print(f"Signal interpretation skipped: {e}")
                        signals = {
                            'ofi_signal': 'Neutral',
                            'ofi_score': 0.0,
                            'depth_imbalance': 'Balanced',
                            'momentum': 'Neutral'
                        }
                else:
                    signals = {
                        'ofi_signal': 'Neutral',
                        'ofi_score': 0.0,
                        'depth_imbalance': 'Balanced',
                        'momentum': 'Neutral'
                    }
                
                # Update prediction if window is active
                if self.current_price and self.strike_price:
                    try:
                        prediction = self.prediction_engine.update_prediction(
                            self.current_price, features if features else {}, signals
                        )
                        if prediction:
                            self.last_prediction = prediction
                    except Exception as e:
                        if self.message_count <= 10:
                            print(f"Prediction update skipped: {e}")
        except Exception as e:
            global_error_handler.record_error("message_handler", e)
    
    async def set_strike_price(self):
        """Set strike price - use current Coinbase price for training"""
        print("🎯 AUTOMATIC TARGET SETTING")
        print("=" * 60)
        print("� Using current Coinbase price as target for training")
        print("🔄 System will use current price as the price to beat")
        print("✅ No manual input required - fully automated")
        print("=" * 60)
        
        # Get current Coinbase price
        try:
            import aiohttp
            async with aiohttp.ClientSession() as session:
                async with session.get("https://api.exchange.coinbase.com/products/BTC-USD/ticker") as response:
                    if response.status == 200:
                        data = await response.json()
                        self.current_price = float(data.get('price', 0))
                        print(f"📊 Current Coinbase spot price: ${self.current_price:,.2f}")
        except Exception as e:
            print(f"Error fetching current price: {e}")
            self.current_price = 63500.00
        
        # Use current price as target for training
        self.strike_price = self.current_price
        print(f"✅ Target set to current price: ${self.strike_price:,.2f}")
        print(f"   System will predict if price will go UP or DOWN from this level")
        print(f"   Target updates automatically as price changes")
        
        # Start automatic target updates
        asyncio.create_task(self.auto_update_target())
    
    async def auto_update_target(self):
        """Automatically update target price to current price every window"""
        while self.running:
            try:
                # Wait for window transition
                await asyncio.sleep(60)  # Check every minute
                
                # Get current window info
                window_info = self.get_coinbase_window_info()
                new_window_number = window_info['window_number']
                
                # Check if we're in a new Coinbase window
                if not hasattr(self, 'current_window_number'):
                    self.current_window_number = new_window_number
                
                if new_window_number != self.current_window_number:
                    # New window - update target to current price
                    try:
                        import aiohttp
                        async with aiohttp.ClientSession() as session:
                            async with session.get("https://api.exchange.coinbase.com/products/BTC-USD/ticker") as response:
                                if response.status == 200:
                                    data = await response.json()
                                    new_price = float(data.get('price', 0))
                                    if new_price and new_price != self.current_price:
                                        old_target = self.strike_price
                                        self.strike_price = new_price
                                        self.current_price = new_price
                                        self.current_window_number = new_window_number
                                        print(f"🔄 New window - Target updated: ${old_target:,.2f} -> ${new_price:,.2f}")
                    except Exception as e:
                        logger.error(f"Error updating target: {e}")
                
            except Exception as e:
                logger.error(f"Error in auto_update_target: {e}")
                await asyncio.sleep(60)
    
    async def run_display_loop(self):
        """Run the display update loop"""
        update_count = 0
        while self.running:
            update_count += 1
            
            # Update current price every second for accuracy
            if update_count % 1 == 0:  # Every second
                try:
                    import aiohttp
                    async with aiohttp.ClientSession() as session:
                        async with session.get("https://api.exchange.coinbase.com/products/BTC-USD/ticker", timeout=3) as response:
                            if response.status == 200:
                                data = await response.json()
                                new_price = float(data.get('price', 0))
                                if new_price and new_price != self.current_price:
                                    old_price = self.current_price
                                    self.current_price = new_price
                                    print(f"📊 Price update: ${old_price:,.2f} -> ${new_price:,.2f}")
                except Exception as e:
                    pass  # Silent fail for display updates
            
            if self.last_prediction:
                self.display_prediction(self.last_prediction)
                
                # Show current target info
                print(f"\n⚙️  Current Target: ${self.strike_price:,.2f}")
                print("   To correct: Press Ctrl+C, restart, and enter correct target")
            else:
                # Show status if no prediction yet
                if update_count % 5 == 0:  # Every 5 seconds
                    print(f"Waiting for predictions... (Update #{update_count})")
                    print(f"Current price: ${self.current_price if self.current_price else 'N/A'}")
                    print(f"Messages received: {getattr(self, 'message_count', 0)}")
                    print()
            
            await asyncio.sleep(self.display_update_interval)
    
    async def run_window_management(self):
        """Manage prediction windows synced to Coinbase 15-minute schedule"""
        poll_count = 0
        current_window_number = None
        last_price_update = 0
        
        while self.running:
            if self.current_price and not self.strike_price:
                # Wait for strike price to be set
                await asyncio.sleep(1)
                continue
            
            if self.current_price and self.strike_price:
                # Get current Coinbase window info
                window_info = self.get_coinbase_window_info()
                new_window_number = window_info['window_number']
                
                # Check if we've entered a new Coinbase window
                if current_window_number != new_window_number:
                    print(f"\n🕐 New Coinbase 15-minute window started!")
                    print(f"Window: {window_info['window_start'].strftime('%H:%M')} - {window_info['window_end'].strftime('%H:%M')} UTC")
                    print(f"Time remaining: {self.format_time(window_info['time_remaining'])}")
                    
                    # Start new prediction window
                    self.prediction_engine.start_prediction_window(
                        self.current_price, self.strike_price
                    )
                    self.online_learning.start_new_window(self.current_price)
                    
                    current_window_number = new_window_number
                
                # Update prediction engine with current time in window
                if self.prediction_engine.window_start_time:
                    # Override the prediction engine's time with Coinbase window time
                    elapsed = window_info['elapsed']
                    time_remaining = window_info['time_remaining']
                    
                    # Update the bridge's internal time tracking
                    if self.prediction_engine.stochastic_bridge:
                        self.prediction_engine.stochastic_bridge.initial_price = self.current_price
                
                # Poll REST API for current price every 0.5 seconds for maximum accuracy
                poll_count += 1
                if poll_count % 1 == 0:  # Every 0.5 seconds (double frequency)
                    try:
                        import aiohttp
                        async with aiohttp.ClientSession() as session:
                            # Get current ticker
                            async with session.get("https://api.exchange.coinbase.com/products/BTC-USD/ticker") as response:
                                if response.status == 200:
                                    data = await response.json()
                                    new_price = float(data.get('price', 0))
                                    if new_price and new_price != self.current_price:
                                        old_price = self.current_price
                                        self.current_price = new_price
                                        print(f"Price updated (Coinbase): ${old_price:,.2f} -> ${new_price:,.2f}")
                                        
                                        # Get order book snapshot
                                        async with session.get("https://api.exchange.coinbase.com/products/BTC-USD/book?level=2") as book_response:
                                            if book_response.status == 200:
                                                book_data = await book_response.json()
                                                # Update order book with REST data
                                                self.ws_client.order_book.clear()
                                                
                                                # Process bids
                                                for bid in book_data.get('bids', []):
                                                    price = float(bid[0])
                                                    size = float(bid[1])
                                                    order_id = f"bid_{price}"
                                                    self.ws_client.order_book.process_received(order_id, price, size, 'buy')
                                                
                                                # Process asks  
                                                for ask in book_data.get('asks', []):
                                                    price = float(ask[0])
                                                    size = float(ask[1])
                                                    order_id = f"ask_{price}"
                                                    self.ws_client.order_book.process_received(order_id, price, size, 'sell')
                                                
                                                print(f"Order book updated via REST: {len(book_data.get('bids', []))} bids, {len(book_data.get('asks', []))} asks")
                    except Exception as e:
                        print(f"REST polling error: {e}")
                
                # Generate prediction even if not getting real-time updates
                try:
                    # Get current features even if not being updated
                    current_price_val = self.current_price if self.current_price else 63000.0
                    
                    # Use Coinbase window timing instead of internal timing
                    elapsed = window_info['elapsed']
                    time_remaining = window_info['time_remaining']
                    
                    if not hasattr(self, 'current_features') or not self.current_features:
                        # Generate dummy features for initial prediction with all required keys
                        self.current_features = {
                            'ofi_0.1s': 0.0, 'ofi_std_0.1s': 0.0, 'voi_0.1s': 0.0, 'depth_ratio_0.1s': 1.0,
                            'micro_price_0.1s': current_price_val, 'micro_price_velocity_0.1s': 0.0, 'spread_0.1s': 1.0,
                            'realized_volatility_0.1s': 0.001, 'cancel_to_trade_0.1s': 0.0,
                            'ofi_0.5s': 0.0, 'ofi_std_0.5s': 0.0, 'voi_0.5s': 0.0, 'depth_ratio_0.5s': 1.0,
                            'micro_price_0.5s': current_price_val, 'micro_price_velocity_0.5s': 0.0, 'spread_0.5s': 1.0,
                            'realized_volatility_0.5s': 0.001, 'cancel_to_trade_0.5s': 0.0,
                            'ofi_1.0s': 0.0, 'ofi_std_1.0s': 0.0, 'voi_1.0s': 0.0, 'depth_ratio_1.0s': 1.0,
                            'micro_price_1.0s': current_price_val, 'micro_price_velocity_1.0s': 0.0, 'spread_1.0s': 1.0,
                            'realized_volatility_1.0s': 0.001, 'cancel_to_trade_1.0s': 0.0,
                            'ofi_5.0s': 0.0, 'ofi_std_5.0s': 0.0, 'voi_5.0s': 0.0, 'depth_ratio_5.0s': 1.0,
                            'micro_price_5.0s': current_price_val, 'micro_price_velocity_5.0s': 0.0, 'spread_5.0s': 1.0,
                            'realized_volatility_5.0s': 0.001, 'cancel_to_trade_5.0s': 0.0,
                            'ofi_10.0s': 0.0, 'ofi_std_10.0s': 0.0, 'voi_10.0s': 0.0, 'depth_ratio_10.0s': 1.0,
                            'micro_price_10.0s': current_price_val, 'micro_price_velocity_10.0s': 0.0, 'spread_10.0s': 1.0,
                            'realized_volatility_10.0s': 0.001, 'cancel_to_trade_10.0s': 0.0,
                            'time_remaining': time_remaining
                        }
                    else:
                        # Update time remaining on existing features
                        self.current_features['time_remaining'] = time_remaining
                    
                    # Get microstructure signals from actual order book
                    try:
                        # Update features with current order book state
                        book_features = self.feature_engine.update_features(
                            self.ws_client.order_book, 'l2update', {'type': 'l2update'}
                        )
                        signals = self.feature_engine.get_signal_interpretation(book_features)
                        
                        # Update current features with real book data
                        for key, value in book_features.items():
                            if key in self.current_features:
                                self.current_features[key] = value
                    except Exception as e:
                        # Fallback to neutral signals if feature calculation fails
                        signals = {
                            'ofi_signal': 'Neutral',
                            'ofi_score': 0.0,
                            'depth_imbalance': 'Balanced',
                            'momentum': 'Neutral'
                        }
                    
                    # Try to update prediction with fallback
                    try:
                        prediction = self.prediction_engine.update_prediction(
                            self.current_price, self.current_features, signals
                        )
                        
                        # Track predictions for analysis
                        if prediction:
                            self.prediction_history.append({
                                'timestamp': datetime.utcnow(),
                                'prediction': prediction,
                                'current_price': self.current_price,
                                'signals': signals
                            })
                            self.price_history.append(self.current_price)
                            
                            # Keep only last 100 predictions to manage memory
                            if len(self.prediction_history) > 100:
                                self.prediction_history.pop(0)
                            if len(self.price_history) > 100:
                                self.price_history.pop(0)
                    
                    except Exception as e:
                        print(f"Prediction engine error: {e}")
                        # Create a basic prediction manually
                        elapsed = (datetime.utcnow() - self.prediction_engine.window_start_time).total_seconds()
                        time_remaining = max(0, self.window_duration - elapsed)
                        
                        prediction = {
                            'elapsed_time': elapsed,
                            'time_remaining': time_remaining,
                            'current_price': self.current_price,
                            'micro_price': self.current_price,
                            'strike_price': self.strike_price,
                            'delta': 0.0,
                            'edge_pct': 0.0,
                            'direction': 'NEUTRAL',
                            'predicted_high': self.current_price * 1.001,
                            'predicted_low': self.current_price * 0.999,
                            'expected_close': self.current_price,
                            'confidence': 0.1,
                            'confidence_rating': 'Low',
                            'ofi_signal': signals.get('ofi_signal', 'Neutral'),
                            'ofi_score': signals.get('ofi_score', 0.0),
                            'depth_imbalance': signals.get('depth_imbalance', 'Balanced'),
                            'momentum': signals.get('momentum', 'Neutral')
                        }
                    
                    # Try to update prediction with fallback
                    try:
                        prediction = self.prediction_engine.update_prediction(
                            self.current_price, self.current_features, signals
                        )
                    except Exception as e:
                        print(f"Prediction engine error: {e}")
                        # Create a basic prediction manually
                        elapsed = (datetime.utcnow() - self.prediction_engine.window_start_time).total_seconds()
                        time_remaining = max(0, self.window_duration - elapsed)
                        
                        prediction = {
                            'elapsed_time': elapsed,
                            'time_remaining': time_remaining,
                            'current_price': self.current_price,
                            'micro_price': self.current_price,
                            'strike_price': self.strike_price,
                            'delta': 0.0,
                            'edge_pct': 0.0,
                            'direction': 'NEUTRAL',
                            'predicted_high': self.current_price * 1.001,
                            'predicted_low': self.current_price * 0.999,
                            'expected_close': self.current_price,
                            'confidence': 0.1,
                            'confidence_rating': 'Low',
                            'ofi_signal': 'Neutral',
                            'ofi_score': 0.0,
                            'depth_imbalance': 'Balanced',
                            'momentum': 'Neutral'
                        }
                    if prediction:
                        self.last_prediction = prediction
                except Exception as e:
                    print(f"Error generating prediction: {e}")
                
                # Check if window has ended
                elapsed = (datetime.utcnow() - self.prediction_engine.window_start_time).total_seconds()
                if elapsed >= self.window_duration:
                    # Finalize window
                    print(f"Window ended. Final price: {self.format_price(self.current_price)}")
                    self.online_learning.finalize_window(self.current_price)
                    
                    # Start new window
                    print("Starting new prediction window...")
                    self.prediction_engine.start_prediction_window(
                        self.current_price, self.strike_price
                    )
                    self.online_learning.start_new_window(self.current_price)
            
            await asyncio.sleep(1)
    
    async def start(self):
        """Start the HFT engine"""
        print("Starting HFT Microstructure Prediction Engine...")
        print(f"Product: {self.product_id}")
        print(f"Window Duration: {self.window_duration} seconds")
        print()
        
        # Register shutdown hook
        async def shutdown_hook():
            print("\nShutting down...")
            self.running = False
            await self.ws_client.stop()
            
            # Save model before exit
            if self.ml_pipeline.is_trained:
                self.ml_pipeline.save_model("hft_model.pkl")
                print("Model saved.")
        
        global_shutdown_handler.register_shutdown_hook(shutdown_hook)
        
        # Register callback
        self.ws_client.register_callback(self.handle_websocket_message)
        
        # Start WebSocket client
        self.running = True
        ws_task = asyncio.create_task(self.ws_client.start())
        
        # Wait for connection and initial price
        print("Connecting to Coinbase WebSocket...")
        await asyncio.sleep(5)
        
        # Set strike price
        await self.set_strike_price()
        
        # Start display and window management loops
        display_task = asyncio.create_task(self.run_display_loop())
        window_task = asyncio.create_task(self.run_window_management())
        
        try:
            # Wait for tasks to complete
            await asyncio.gather(ws_task, display_task, window_task)
        except KeyboardInterrupt:
            await global_shutdown_handler.shutdown()
            
            # Cancel tasks
            ws_task.cancel()
            display_task.cancel()
            window_task.cancel()
            
            print("HFT Engine stopped.")


async def main():
    """Main entry point"""
    # You can customize these parameters
    product_id = "BTC-USD"
    window_duration = 900  # 15 minutes
    
    cli = CLIInterface(product_id, window_duration)
    await cli.start()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nProgram terminated by user.")