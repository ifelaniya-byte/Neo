"""
Time-Decaying Stochastic Bridge Probability Estimator
Calculates expected terminal price distribution using Brownian bridge dynamics
"""
import numpy as np
from scipy.stats import norm
from datetime import datetime, timedelta
import math


class StochasticBridge:
    def __init__(self, initial_price, window_duration=900):  # 15 minutes in seconds
        self.initial_price = initial_price
        self.window_duration = window_duration
        self.current_price = initial_price
        self.volatility = 0.0
        self.drift = 0.0
        self.price_history = []
        self.update_count = 0
        
    def update_parameters(self, current_price, volatility_estimate, drift_estimate=0.0):
        """
        Update bridge parameters with new market data
        """
        self.current_price = current_price
        self.volatility = max(volatility_estimate, 0.0001)  # Ensure minimum volatility
        self.drift = drift_estimate
        self.price_history.append(current_price)
        self.update_count += 1
        
    def get_time_decay_factor(self, elapsed_time):
        """
        Calculate time decay factor for bridge process
        As time approaches end of window, uncertainty decreases
        """
        if elapsed_time >= self.window_duration:
            return 0.0
        
        remaining_time = self.window_duration - elapsed_time
        return remaining_time / self.window_duration
    
    def calculate_terminal_variance(self, elapsed_time):
        """
        Calculate variance of terminal price distribution
        Based on Brownian bridge: Var(T) = sigma^2 * t * (T - t) / T
        """
        if elapsed_time >= self.window_duration:
            return 0.0
        
        T = self.window_duration
        t = elapsed_time
        
        # Brownian bridge variance
        terminal_variance = (self.volatility ** 2) * t * (T - t) / T
        
        return terminal_variance
    
    def calculate_expected_terminal_price(self, elapsed_time):
        """
        Calculate expected terminal price using bridge dynamics
        E[S_T] = S_0 + drift * T + (S_t - S_0 - drift * t) * (T - t) / t
        """
        if elapsed_time <= 0:
            return self.initial_price + self.drift * self.window_duration
        
        if elapsed_time >= self.window_duration:
            return self.current_price
        
        T = self.window_duration
        t = elapsed_time
        S_0 = self.initial_price
        S_t = self.current_price
        
        # Bridge expectation
        bridge_term = (S_t - S_0 - self.drift * t) * (T - t) / t
        expected_terminal = S_0 + self.drift * T + bridge_term
        
        return expected_terminal
    
    def calculate_price_distribution(self, elapsed_time, confidence_levels=[0.68, 0.95]):
        """
        Calculate price distribution at terminal time
        Returns expected price, variance, and confidence intervals
        """
        expected_price = self.calculate_expected_terminal_price(elapsed_time)
        variance = self.calculate_terminal_variance(elapsed_time)
        std_dev = math.sqrt(variance)
        
        # Calculate confidence intervals
        confidence_intervals = {}
        for level in confidence_levels:
            z_score = norm.ppf(0.5 + level / 2)
            lower_bound = expected_price - z_score * std_dev
            upper_bound = expected_price + z_score * std_dev
            confidence_intervals[level] = (lower_bound, upper_bound)
        
        return {
            'expected_price': expected_price,
            'variance': variance,
            'std_dev': std_dev,
            'confidence_intervals': confidence_intervals
        }
    
    def calculate_probability_above_strike(self, strike_price, elapsed_time):
        """
        Calculate probability that terminal price will be above strike
        """
        distribution = self.calculate_price_distribution(elapsed_time)
        expected_price = distribution['expected_price']
        std_dev = distribution['std_dev']
        
        if std_dev == 0:
            return 1.0 if expected_price > strike_price else 0.0
        
        z_score = (strike_price - expected_price) / std_dev
        probability = 1 - norm.cdf(z_score)
        
        return probability
    
    def calculate_probability_below_strike(self, strike_price, elapsed_time):
        """
        Calculate probability that terminal price will be below strike
        """
        return 1 - self.calculate_probability_above_strike(strike_price, elapsed_time)
    
    def generate_forecast_range(self, elapsed_time, current_price):
        """
        Generate forecast range for display
        """
        distribution = self.calculate_price_distribution(elapsed_time)
        
        expected_price = distribution['expected_price']
        std_dev = distribution['std_dev']
        
        # Calculate forecast range
        predicted_high = expected_price + 2 * std_dev
        predicted_low = expected_price - 2 * std_dev
        expected_close = expected_price
        
        return {
            'predicted_high': predicted_high,
            'predicted_low': predicted_low,
            'expected_close': expected_close,
            'current_price': current_price,
            'expected_change': expected_close - current_price,
            'expected_change_pct': (expected_close - current_price) / current_price * 100
        }
    
    def generate_forecast(self, elapsed_time, current_price):
        """
        Alias for generate_forecast_range for compatibility
        """
        return self.generate_forecast_range(elapsed_time, current_price)
    
    def get_delta_edge(self, strike_price, elapsed_time, current_price):
        """
        Calculate delta/edge for a given strike price
        """
        expected_price = self.calculate_expected_terminal_price(elapsed_time)
        variance = self.calculate_terminal_variance(elapsed_time)
        std_dev = math.sqrt(variance)
        
        delta = expected_price - strike_price
        edge_pct = (delta / current_price) * 100 if current_price > 0 else 0
        
        # Determine direction
        if delta > 0:
            direction = "OVER"
        elif delta < 0:
            direction = "UNDER"
        else:
            direction = "NEUTRAL"
        
        return {
            'delta': delta,
            'edge_pct': edge_pct,
            'direction': direction,
            'expected_price': expected_price,
            'strike_price': strike_price
        }
    
    def update_with_market_conditions(self, current_price, volatility_estimate, 
                                       microstructure_signals, elapsed_time):
        """
        Update bridge parameters based on market conditions
        """
        # Adjust volatility based on microstructure signals
        adjusted_volatility = volatility_estimate
        
        # Increase volatility if strong signals detected
        signal_strength = abs(microstructure_signals.get('ofi_score', 0))
        if signal_strength > 0.3:  # Lower threshold for more sensitivity
            adjusted_volatility *= 1.5  # Stronger adjustment
        
        # Adjust drift based on momentum
        momentum = microstructure_signals.get('momentum', 'Neutral')
        if 'Bullish' in momentum:
            drift_adjustment = 0.0005  # Stronger upward drift
        elif 'Bearish' in momentum:
            drift_adjustment = -0.0005  # Stronger downward drift
        else:
            drift_adjustment = 0.0
        
        self.update_parameters(current_price, adjusted_volatility, drift_adjustment)


class PredictionEngine:
    """
    Combines ML predictions with stochastic bridge for final forecasts
    """
    def __init__(self, ml_pipeline, window_duration=900):
        self.ml_pipeline = ml_pipeline
        self.stochastic_bridge = None
        self.window_duration = window_duration
        self.window_start_time = None
        self.strike_price = None
        
    def start_prediction_window(self, initial_price, strike_price):
        """
        Start a new prediction window
        """
        self.window_start_time = datetime.utcnow()
        self.strike_price = strike_price
        self.stochastic_bridge = StochasticBridge(initial_price, self.window_duration)
        print(f"Prediction window started. Strike: ${strike_price}, Initial: ${initial_price}")
        
    def update_prediction(self, current_price, features, microstructure_signals):
        """
        Update prediction with new data
        """
        if not self.stochastic_bridge:
            # Initialize bridge if not exists
            if self.window_start_time:
                self.stochastic_bridge = StochasticBridge(current_price, self.window_duration)
            else:
                return None
        
        # Calculate elapsed time
        elapsed = (datetime.utcnow() - self.window_start_time).total_seconds()
        elapsed = min(elapsed, self.window_duration)
        
        # Get volatility from features
        volatility = features.get('realized_volatility_1.0s', 0.001)
        
        # Update stochastic bridge
        self.stochastic_bridge.update_with_market_conditions(
            current_price, volatility, microstructure_signals, elapsed
        )
        
        # Get ML prediction
        time_remaining = self.window_duration - elapsed
        ml_prediction = self.ml_pipeline.predict(features, time_remaining)
        
        # Combine ML and bridge predictions
        bridge_forecast = self.stochastic_bridge.generate_forecast_range(elapsed, current_price)
        bridge_delta = self.stochastic_bridge.get_delta_edge(
            self.strike_price, elapsed, current_price
        )
        
        # Weight predictions (ML gets more weight as we have more data)
        ml_weight = min(elapsed / 300, 0.7)  # Increase ML weight over time
        bridge_weight = 1 - ml_weight
        
        # Combine expected returns
        ml_return = ml_prediction['predicted_return']
        bridge_return = bridge_forecast['expected_change_pct'] / 100
        
        combined_return = ml_weight * ml_return + bridge_weight * bridge_return
        combined_expected_price = current_price * (1 + combined_return)
        
        # Calculate combined confidence
        ml_confidence = ml_prediction['confidence']
        bridge_confidence = 1 - (elapsed / self.window_duration)  # Bridge confidence decays
        combined_confidence = ml_weight * ml_confidence + bridge_weight * bridge_confidence
        
        # Determine final direction
        if combined_return > 0.001:
            final_direction = "OVER"
        elif combined_return < -0.001:
            final_direction = "UNDER"
        else:
            final_direction = "NEUTRAL"
        
        # Determine confidence rating
        if combined_confidence > 0.8:
            confidence_rating = "Maximum"
        elif combined_confidence > 0.6:
            confidence_rating = "High"
        elif combined_confidence > 0.4:
            confidence_rating = "Moderate"
        else:
            confidence_rating = "Low"
        
        return {
            'elapsed_time': elapsed,
            'time_remaining': time_remaining,
            'current_price': current_price,
            'micro_price': features.get('micro_price_1.0s', current_price),
            'strike_price': self.strike_price,
            'delta': bridge_delta['delta'],
            'edge_pct': bridge_delta['edge_pct'],
            'direction': final_direction,
            'predicted_high': bridge_forecast['predicted_high'],
            'predicted_low': bridge_forecast['predicted_low'],
            'expected_close': combined_expected_price,
            'confidence': combined_confidence,
            'confidence_rating': confidence_rating,
            'ofi_signal': microstructure_signals.get('ofi_signal', 'Neutral'),
            'ofi_score': microstructure_signals.get('ofi_score', 0),
            'depth_imbalance': microstructure_signals.get('depth_imbalance', 'Balanced'),
            'momentum': microstructure_signals.get('momentum', 'Neutral')
        }