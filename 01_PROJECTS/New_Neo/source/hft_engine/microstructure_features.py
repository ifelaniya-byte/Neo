"""
Microstructure Feature Engine
Computes real-time order flow imbalance, volume imbalance, micro-price, and other indicators
"""
import numpy as np
from collections import deque
from datetime import datetime, timedelta
import time


class MicrostructureFeatures:
    def __init__(self, windows=[0.1, 0.5, 1.0, 5.0, 10.0]):
        self.windows = windows  # Time windows in seconds
        self.feature_history = {}
        self.last_update = None
        
        # Initialize rolling windows for each time scale
        for window in windows:
            self.feature_history[window] = {
                'ofi': deque(maxlen=1000),
                'bid_volume': deque(maxlen=1000),
                'ask_volume': deque(maxlen=1000),
                'micro_price': deque(maxlen=1000),
                'mid_price': deque(maxlen=1000),
                'spread': deque(maxlen=1000),
                'cancellations': deque(maxlen=1000),
                'executions': deque(maxlen=1000),
                'timestamps': deque(maxlen=1000)
            }
        
        # Track order flow for OFI calculation
        self.previous_bid_levels = {}
        self.previous_ask_levels = {}
        selfofi_buffer = deque(maxlen=100)
    
    def calculate_ofi(self, current_bids, current_asks, previous_bids, previous_asks, levels=5):
        """
        Calculate Order Flow Imbalance (OFI)
        OFI = sum of volume changes at best levels due to limit orders, cancels, and executions
        """
        ofi = 0.0
        
        # Process bids
        for i in range(min(levels, len(current_bids))):
            curr_price, curr_size = current_bids[i] if i < len(current_bids) else (0, 0)
            prev_price, prev_size = previous_bids[i] if i < len(previous_bids) else (0, 0)
            
            if curr_price == prev_price:
                # Volume change at same price level
                ofi += max(0, curr_size - prev_size)
            elif curr_price > prev_price:
                # New better bid
                ofi += curr_size
        
        # Process asks (negative contribution)
        for i in range(min(levels, len(current_asks))):
            curr_price, curr_size = current_asks[i] if i < len(current_asks) else (0, 0)
            prev_price, prev_size = previous_asks[i] if i < len(previous_asks) else (0, 0)
            
            if curr_price == prev_price:
                # Volume change at same price level
                ofi -= max(0, curr_size - prev_size)
            elif curr_price < prev_price:
                # New better ask
                ofi -= curr_size
        
        return ofi
    
    def calculate_voi(self, current_bids, current_asks):
        """
        Calculate Volume Imbalance (VOI)
        VOI = (bid_volume - ask_volume) / (bid_volume + ask_volume)
        """
        total_bid_volume = sum(size for _, size in current_bids)
        total_ask_volume = sum(size for _, size in current_asks)
        
        if total_bid_volume + total_ask_volume == 0:
            return 0.0
        
        return (total_bid_volume - total_ask_volume) / (total_bid_volume + total_ask_volume)
    
    def calculate_depth_ratio(self, current_bids, current_asks):
        """
        Calculate depth ratio
        Ratio of total bid volume to total ask volume
        """
        total_bid_volume = sum(size for _, size in current_bids)
        total_ask_volume = sum(size for _, size in current_asks)
        
        if total_ask_volume == 0:
            return float('inf') if total_bid_volume > 0 else 1.0
        
        return total_bid_volume / total_ask_volume
    
    def calculate_micro_price(self, current_bids, current_asks):
        """
        Calculate micro-price (volume-weighted fair price)
        Accounts for bid/ask queue imbalance
        """
        total_bid_volume = sum(size for _, size in current_bids)
        total_ask_volume = sum(size for _, size in current_asks)
        
        if total_bid_volume + total_ask_volume == 0:
            return None
        
        # Calculate volume-weighted bid and ask prices
        weighted_bid_price = sum(price * size for price, size in current_bids) / total_bid_volume if total_bid_volume > 0 else 0
        weighted_ask_price = sum(price * size for price, size in current_asks) / total_ask_volume if total_ask_volume > 0 else 0
        
        # Weight by volume imbalance
        total_volume = total_bid_volume + total_ask_volume
        bid_weight = total_bid_volume / total_volume
        ask_weight = total_ask_volume / total_volume
        
        micro_price = weighted_bid_price * bid_weight + weighted_ask_price * ask_weight
        return micro_price
    
    def calculate_realized_volatility(self, price_history, window_size=100):
        """
        Calculate realized volatility from price history
        """
        if len(price_history) < 2:
            return 0.0
        
        returns = []
        for i in range(1, min(len(price_history), window_size + 1)):
            if price_history[-i] and price_history[-i-1]:
                ret = (price_history[-i] - price_history[-i-1]) / price_history[-i-1]
                returns.append(ret)
        
        if not returns:
            return 0.0
        
        return np.std(returns) * np.sqrt(len(returns))
    
    def calculate_cancellation_velocity(self, cancellations, executions, window_seconds):
        """
        Calculate cancellation-to-trade ratio
        High values may indicate spoofing or liquidity withdrawal
        """
        if executions == 0:
            return 0.0
        
        return cancellations / executions
    
    def update_features(self, order_book, message_type, message_data):
        """
        Update all microstructure features based on order book state
        """
        current_time = time.time()
        
        # Get current book state
        current_bids, current_asks = order_book.get_depth(levels=10)
        mid_price = order_book.get_mid_price()
        spread = order_book.get_spread()
        micro_price = self.calculate_micro_price(current_bids, current_asks)
        
        # Track cancellations and executions
        cancellation = 1 if message_type == 'done' and message_data.get('reason') == 'canceled' else 0
        execution = 1 if message_type == 'match' else 0
        
        # Calculate OFI
        ofi = 0.0
        if self.previous_bid_levels and self.previous_ask_levels:
            ofi = self.calculate_ofi(current_bids, current_asks, 
                                   self.previous_bid_levels, self.previous_ask_levels)
        
        # Store previous levels
        self.previous_bid_levels = current_bids.copy()
        self.previous_ask_levels = current_asks.copy()
        
        # Calculate other features
        voi = self.calculate_voi(current_bids, current_asks)
        depth_ratio = self.calculate_depth_ratio(current_bids, current_asks)
        
        # Update rolling windows
        for window in self.windows:
            window_data = self.feature_history[window]
            
            # Add new data point
            window_data['ofi'].append(ofi)
            window_data['bid_volume'].append(sum(size for _, size in current_bids))
            window_data['ask_volume'].append(sum(size for _, size in current_asks))
            window_data['micro_price'].append(micro_price)
            window_data['mid_price'].append(mid_price)
            window_data['spread'].append(spread)
            window_data['cancellations'].append(cancellation)
            window_data['executions'].append(execution)
            window_data['timestamps'].append(current_time)
            
            # Remove old data outside window
            cutoff_time = current_time - window
            while window_data['timestamps'] and window_data['timestamps'][0] < cutoff_time:
                for key in window_data:
                    if key != 'timestamps':
                        window_data[key].popleft()
                window_data['timestamps'].popleft()
        
        self.last_update = current_time
        
        return self.get_current_features()
    
    def get_current_features(self):
        """
        Get current feature values across all time windows
        """
        features = {}
        
        for window in self.windows:
            window_data = self.feature_history[window]
            
            if not window_data['timestamps']:
                continue
            
            # Calculate window-specific features
            ofi_values = list(window_data['ofi'])
            micro_prices = [mp for mp in window_data['micro_price'] if mp is not None]
            mid_prices = [mp for mp in window_data['mid_price'] if mp is not None]
            
            window_features = {
                f'ofi_{window}s': np.mean(ofi_values) if ofi_values else 0,
                f'ofi_std_{window}s': np.std(ofi_values) if ofi_values else 0,
                f'voi_{window}s': self.calculate_voi(
                    [(p, s) for p, s in zip(window_data['mid_price'], window_data['bid_volume']) if p],
                    [(p, s) for p, s in zip(window_data['mid_price'], window_data['ask_volume']) if p]
                ),
                f'depth_ratio_{window}s': self.calculate_depth_ratio(
                    [(p, s) for p, s in zip(window_data['mid_price'], window_data['bid_volume']) if p],
                    [(p, s) for p, s in zip(window_data['mid_price'], window_data['ask_volume']) if p]
                ),
                f'micro_price_{window}s': np.mean(micro_prices) if micro_prices else 0,
                f'micro_price_velocity_{window}s': (micro_prices[-1] - micro_prices[0]) / window if len(micro_prices) > 1 else 0,
                f'spread_{window}s': np.mean(list(window_data['spread'])) if window_data['spread'] else 0,
                f'realized_volatility_{window}s': self.calculate_realized_volatility(mid_prices),
                f'cancel_to_trade_{window}s': self.calculate_cancellation_velocity(
                    sum(window_data['cancellations']),
                    sum(window_data['executions']),
                    window
                )
            }
            
            features.update(window_features)
        
        return features
    
    def get_signal_interpretation(self, features):
        """
        Interpret current microstructure signals
        """
        # Get OFI signal from multiple timeframes
        ofi_1s = features.get('ofi_1.0s', 0)
        ofi_5s = features.get('ofi_5.0s', 0)
        ofi_10s = features.get('ofi_10.0s', 0)
        
        # Combined OFI score
        ofi_score = (ofi_1s * 0.5 + ofi_5s * 0.3 + ofi_10s * 0.2)
        
        # Determine OFI direction
        if ofi_score > 0.1:
            ofi_signal = "Positive"
        elif ofi_score < -0.1:
            ofi_signal = "Negative"
        else:
            ofi_signal = "Neutral"
        
        # Get depth imbalance
        depth_ratio = features.get('depth_ratio_1.0s', 1.0)
        if depth_ratio > 1.2:
            depth_imbalance = f"{int((depth_ratio / (1 + depth_ratio)) * 100)}% Bids / {int((1 / (1 + depth_ratio)) * 100)}% Asks"
        elif depth_ratio < 0.8:
            depth_imbalance = f"{int((depth_ratio / (1 + depth_ratio)) * 100)}% Bids / {int((1 / (1 + depth_ratio)) * 100)}% Asks"
        else:
            depth_imbalance = "Balanced"
        
        # Get momentum signal
        micro_velocity = features.get('micro_price_velocity_1.0s', 0)
        if micro_velocity > 0.5:
            momentum = "Strong Bullish"
        elif micro_velocity > 0.1:
            momentum = "Moderate Bullish"
        elif micro_velocity < -0.5:
            momentum = "Strong Bearish"
        elif micro_velocity < -0.1:
            momentum = "Moderate Bearish"
        else:
            momentum = "Neutral"
        
        return {
            'ofi_signal': ofi_signal,
            'ofi_score': abs(ofi_score),
            'depth_imbalance': depth_imbalance,
            'momentum': momentum,
            'micro_price': features.get('micro_price_1.0s', 0),
            'realized_volatility': features.get('realized_volatility_1.0s', 0)
        }