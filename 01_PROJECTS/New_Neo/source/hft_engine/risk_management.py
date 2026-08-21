"""
Risk Management System for HFT Engine
Handles position sizing, stop-loss, and confidence thresholds
"""
import numpy as np
from collections import deque
import config


class RiskManager:
    def __init__(self):
        self.bankroll = config.TOTAL_BANKROLL
        self.max_position_size = self.bankroll * config.MAX_POSITION_SIZE_PERCENT
        self.default_position_size = self.bankroll * config.DEFAULT_POSITION_SIZE_PERCENT
        self.stop_loss_percent = config.STOP_LOSS_PERCENT
        self.take_profit_percent = config.TAKE_PROFIT_PERCENT
        
        # Performance tracking
        self.trade_history = []
        self.current_position = None
        self.entry_price = None
        self.entry_time = None
        self.unrealized_pnl = 0.0
        
        # Volatility tracking
        self.price_history = deque(maxlen=60)
        self.current_volatility = 0.0
        
    def calculate_position_size(self, confidence, expected_move_percent, volatility):
        """
        Calculate optimal position size based on multiple factors
        """
        base_size = self.default_position_size
        
        # Adjust based on confidence
        if confidence >= config.HIGH_CONFIDENCE_THRESHOLD:
            base_size *= 1.5  # Increase size for high confidence
        elif confidence >= config.MAX_CONFIDENCE_THRESHOLD:
            base_size *= 2.0  # Maximum size for maximum confidence
        elif confidence < config.MIN_CONFIDENCE_TO_BET:
            return 0.0  # No bet if below minimum confidence
        
        # Adjust based on expected move
        if expected_move_percent < config.MIN_EXPECTED_MOVE_PERCENT:
            base_size *= 0.5  # Reduce size for small expected moves
        elif expected_move_percent >= config.OPTIMAL_EXPECTED_MOVE_PERCENT:
            base_size *= 1.2  # Increase size for optimal moves
        
        # Adjust based on volatility
        if volatility > config.HIGH_VOLATILITY_THRESHOLD:
            base_size *= 0.5  # Reduce size in high volatility
        elif volatility < config.LOW_VOLATILITY_THRESHOLD:
            base_size *= 1.2  # Increase size in low volatility
        
        # Apply maximum limit
        position_size = min(base_size, self.max_position_size)
        
        return position_size
    
    def calculate_kelly_criterion(self, win_rate, avg_win, avg_loss):
        """
        Calculate Kelly Criterion for optimal position sizing
        f* = (bp - q) / b
        where:
        b = average win / average loss
        p = win rate
        q = 1 - win rate
        """
        if avg_loss == 0:
            return 0.0
        
        win_rate = win_rate
        loss_rate = 1 - win_rate
        
        if win_rate <= 0 or avg_loss <= 0:
            return 0.0
        
        b = avg_win / avg_loss
        kelly_percent = (win_rate * b - loss_rate) / b
        
        # Cap Kelly at 25% to avoid overbetting
        kelly_percent = min(kelly_percent, 0.25)
        
        return kelly_percent * self.bankroll
    
    def calculate_stop_loss(self, entry_price, direction):
        """Calculate stop loss price based on percentage"""
        if direction == "UP":
            stop_loss = entry_price * (1 - self.stop_loss_percent)
        else:
            stop_loss = entry_price * (1 + self.stop_loss_percent)
        return stop_loss
    
    def calculate_take_profit(self, entry_price, direction):
        """Calculate take profit price based on percentage"""
        if direction == "UP":
            take_profit = entry_price * (1 + self.take_profit_percent)
        else:
            take_profit = entry_price * (1 - self.take_profit_percent)
        return take_profit
    
    def update_volatility(self, current_price):
        """Update volatility measurement"""
        self.price_history.append(current_price)
        
        if len(self.price_history) > 10:
            returns = []
            for i in range(1, min(len(self.price_history), config.VOLATILITY_WINDOW + 1)):
                if self.price_history[-i] and self.price_history[-i-1]:
                    ret = (self.price_history[-i] - self.price_history[-i-1]) / self.price_history[-i-1]
                    returns.append(ret)
            
            if returns:
                self.current_volatility = np.std(returns) * np.sqrt(len(returns))
    
    def assess_market_conditions(self, current_price, confidence, signals):
        """
        Assess if market conditions are suitable for betting
        Returns decision dictionary with reasoning
        """
        conditions = {
            'can_bet': False,
            'reasons': [],
            'confidence_check': False,
            'expected_move_check': False,
            'signal_alignment': False,
            'timing_check': False,
            'volatility_check': False,
            'recommended_position_size': 0.0
        }
        
        # Confidence check
        if confidence >= config.MIN_CONFIDENCE_TO_BET:
            conditions['confidence_check'] = True
        else:
            conditions['reasons'].append(f"Confidence too low: {confidence:.1%} < {config.MIN_CONFIDENCE_TO_BET:.1%}")
        
        # Expected move check
        expected_move = abs((signals.get('expected_close', current_price) - current_price) / current_price)
        if expected_move >= config.MIN_EXPECTED_MOVE_PERCENT:
            conditions['expected_move_check'] = True
        else:
            conditions['reasons'].append(f"Expected move too small: {expected_move:.2%} < {config.MIN_EXPECTED_MOVE_PERCENT:.2%}")
        
        # Signal alignment check
        if config.SIGNAL_ALIGNMENT_REQUIRED:
            bullish_signals = 0
            bearish_signals = 0
            
            if signals.get('ofi_signal') == 'Positive':
                bullish_signals += 1
            elif signals.get('ofi_signal') == 'Negative':
                bearish_signals += 1
            
            if 'Bullish' in signals.get('momentum', 'Neutral'):
                bullish_signals += 1
            elif 'Bearish' in signals.get('momentum', 'Neutral'):
                bearish_signals += 1
            
            prediction_direction = signals.get('direction', 'NEUTRAL')
            
            if prediction_direction == 'UP' and bullish_signals >= config.MIN_BULLISH_SIGNALS:
                conditions['signal_alignment'] = True
            elif prediction_direction == 'DOWN' and bearish_signals >= config.MIN_BEARISH_SIGNALS:
                conditions['signal_alignment'] = True
            else:
                conditions['reasons'].append(f"Signals not aligned: {bullish_signals} bullish vs {bearish_signals} bearish for {prediction_direction}")
        
        # Timing check (this will be called with time remaining)
        # This is handled in the main loop, but we store the threshold
        conditions['optimal_entry_time'] = config.OPTIMAL_ENTRY_TIME_REMAINING
        conditions['late_entry_threshold'] = config.LATE_ENTRY_THRESHOLD
        conditions['no_entry_threshold'] = config.NO_ENTRY_THRESHOLD
        
        # Volatility check
        if self.current_volatility < config.HIGH_VOLATILITY_THRESHOLD:
            conditions['volatility_check'] = True
        else:
            conditions['reasons'].append(f"Volatility too high: {self.current_volatility:.4f}")
        
        # Final decision
        if all([
            conditions['confidence_check'],
            conditions['expected_move_check'],
            conditions['signal_alignment'],
            conditions['volatility_check']
        ]):
            conditions['can_bet'] = True
            conditions['recommended_position_size'] = self.calculate_position_size(
                confidence, expected_move, self.current_volatility
            )
        
        return conditions
    
    def get_risk_assessment_display(self, conditions):
        """Format risk assessment for display"""
        display_lines = []
        
        display_lines.append("🎯 RISK ASSESSMENT")
        display_lines.append("=" * 40)
        
        if conditions['can_bet']:
            display_lines.append("✅ BETTING CONDITIONS MET")
            display_lines.append(f"   Position Size: ${conditions['recommended_position_size']:,.2f}")
            display_lines.append(f"   Risk Level: {'LOW' if conditions['recommended_position_size'] < self.default_position_size else 'MODERATE'}")
        else:
            display_lines.append("❌ DO NOT BET - CONDITIONS NOT MET")
            display_lines.append("   Reasons:")
            for reason in conditions['reasons']:
                display_lines.append(f"   - {reason}")
        
        display_lines.append("")
        display_lines.append("📊 REQUIREMENTS:")
        display_lines.append(f"   Min Confidence: {config.MIN_CONFIDENCE_TO_BET:.0%}")
        display_lines.append(f"   Min Expected Move: {config.MIN_EXPECTED_MOVE_PERCENT:.2%}")
        display_lines.append(f"   Signal Alignment: {'Required' if config.SIGNAL_ALIGNMENT_REQUIRED else 'Optional'}")
        display_lines.append(f"   Max Position: {config.MAX_POSITION_SIZE_PERCENT:.0%} of bankroll")
        
        return "\n".join(display_lines)


class PerformanceTracker:
    """Track performance metrics for strategy validation"""
    def __init__(self):
        self.predictions = []
        self.outcomes = []
        self.win_count = 0
        self.loss_count = 0
        self.total_pnl = 0.0
        self.max_drawdown = 0.0
        self.peak_balance = 0.0
        self.current_balance = 0.0
    
    def add_prediction(self, prediction, entry_price, target_price, direction):
        """Record a prediction"""
        self.predictions.append({
            'timestamp': prediction.get('timestamp'),
            'prediction': direction,
            'entry_price': entry_price,
            'target_price': target_price,
            'predicted_close': prediction.get('expected_close'),
            'confidence': prediction.get('confidence'),
            'expected_move': prediction.get('expected_change_pct', 0)
        })
    
    def add_outcome(self, actual_close, entry_price, target_price):
        """Record actual outcome and calculate PnL"""
        if not self.predictions:
            return
        
        last_prediction = self.predictions[-1]
        predicted_direction = last_prediction['prediction']
        actual_direction = 'UP' if actual_close > target_price else 'DOWN'
        
        was_correct = (predicted_direction == actual_direction)
        
        if was_correct:
            self.win_count += 1
            pnl = abs(target_price - entry_price) * 0.95  # Assume 5% fees
        else:
            self.loss_count += 1
            pnl = -abs(target_price - entry_price) * 0.95
        
        self.total_pnl += pnl
        self.current_balance += pnl
        
        # Track drawdown
        if self.current_balance > self.peak_balance:
            self.peak_balance = self.current_balance
        current_drawdown = (self.peak_balance - self.current_balance) / self.peak_balance if self.peak_balance > 0 else 0
        if current_drawdown > self.max_drawdown:
            self.max_drawdown = current_drawdown
        
        self.outcomes.append({
            'timestamp': datetime.utcnow(),
            'actual_close': actual_close,
            'was_correct': was_correct,
            'pnl': pnl,
            'win_rate': self.win_count / (self.win_count + self.loss_count) if (self.win_count + self.loss_count) > 0 else 0
        })
    
    def get_performance_metrics(self):
        """Calculate and return performance metrics"""
        total_trades = self.win_count + self.loss_count
        if total_trades == 0:
            return None
        
        win_rate = self.win_count / total_trades
        total_return = self.total_pnl / (self.peak_balance if self.peak_balance > 0 else 1)
        sharpe_ratio = win_rate / 0.5 if win_rate > 0 else 0  # Simplified Sharpe
        
        return {
            'total_trades': total_trades,
            'win_rate': win_rate,
            'total_pnl': self.total_pnl,
            'max_drawdown': self.max_drawdown,
            'sharpe_ratio': sharpe_ratio,
            'current_balance': self.current_balance
        }