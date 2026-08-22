"""
Machine Learning Pipeline for Price Prediction
Uses LightGBM for online learning and real-time inference
"""
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
import lightgbm as lgb
from collections import deque
import joblib
import os
from datetime import datetime


class MLPipeline:
    def __init__(self, model_path=None, retrain_interval=100):
        self.model = None
        self.scaler = StandardScaler()
        self.feature_buffer = deque(maxlen=10000)
        self.target_buffer = deque(maxlen=10000)
        self.retrain_interval = retrain_interval  # Reduced for faster learning
        self.sample_count = 0
        self.model_path = model_path
        self.is_trained = False
        
        # Feature names for model
        self.feature_names = [
            'ofi_0.1s', 'ofi_std_0.1s', 'voi_0.1s', 'depth_ratio_0.1s',
            'micro_price_0.1s', 'micro_price_velocity_0.1s', 'spread_0.1s',
            'realized_volatility_0.1s', 'cancel_to_trade_0.1s',
            'ofi_0.5s', 'ofi_std_0.5s', 'voi_0.5s', 'depth_ratio_0.5s',
            'micro_price_0.5s', 'micro_price_velocity_0.5s', 'spread_0.5s',
            'realized_volatility_0.5s', 'cancel_to_trade_0.5s',
            'ofi_1.0s', 'ofi_std_1.0s', 'voi_1.0s', 'depth_ratio_1.0s',
            'micro_price_1.0s', 'micro_price_velocity_1.0s', 'spread_1.0s',
            'realized_volatility_1.0s', 'cancel_to_trade_1.0s',
            'ofi_5.0s', 'ofi_std_5.0s', 'voi_5.0s', 'depth_ratio_5.0s',
            'micro_price_5.0s', 'micro_price_velocity_5.0s', 'spread_5.0s',
            'realized_volatility_5.0s', 'cancel_to_trade_5.0s',
            'ofi_10.0s', 'ofi_std_10.0s', 'voi_10.0s', 'depth_ratio_10.0s',
            'micro_price_10.0s', 'micro_price_velocity_10.0s', 'spread_10.0s',
            'realized_volatility_10.0s', 'cancel_to_trade_10.0s',
            'time_remaining'
        ]
        
        # Try to load existing model
        if model_path and os.path.exists(model_path):
            self.load_model(model_path)
        else:
            self.initialize_model()
    
    def initialize_model(self):
        """Initialize LightGBM model with online learning parameters"""
        self.model = lgb.LGBMRegressor(
            n_estimators=50,  # Reduced for faster training
            learning_rate=0.1,  # Higher learning rate for faster adaptation
            max_depth=4,  # Simpler model for faster learning
            num_leaves=15,  # Fewer leaves for faster training
            subsample=0.9,
            colsample_bytree=0.9,
            random_state=42,
            verbose=-1
        )
        print("LightGBM model initialized with fast-learning parameters")
    
    def preprocess_features(self, features_dict, time_remaining):
        """
        Preprocess features for model input
        """
        # Add time remaining feature
        features_dict['time_remaining'] = time_remaining
        
        # Create feature vector in correct order
        feature_vector = []
        for feature_name in self.feature_names:
            value = features_dict.get(feature_name, 0)
            # Handle None values
            if value is None or np.isnan(value) or np.isinf(value):
                value = 0
            feature_vector.append(value)
        
        return np.array(feature_vector).reshape(1, -1)
    
    def add_sample(self, features, target):
        """
        Add training sample to buffer
        """
        self.feature_buffer.append(features)
        self.target_buffer.append(target)
        self.sample_count += 1
        
        # Retrain if we have enough samples
        if self.sample_count >= self.retrain_interval:
            self.retrain()
    
    def retrain(self):
        """
        Retrain model with accumulated samples
        """
        if len(self.feature_buffer) < 100:
            print("Not enough samples to retrain")
            return
        
        print(f"Retraining model with {len(self.feature_buffer)} samples...")
        
        # Convert buffers to arrays
        X = np.array(self.feature_buffer)
        y = np.array(self.target_buffer)
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Retrain model
        self.model.fit(X_scaled, y)
        self.is_trained = True
        
        # Clear buffers
        self.feature_buffer.clear()
        self.target_buffer.clear()
        self.sample_count = 0
        
        print("Model retraining completed")
        
        # Save model
        if self.model_path:
            self.save_model(self.model_path)
    
    def predict(self, features_dict, time_remaining):
        """
        Make prediction using current model
        """
        if not self.is_trained:
            # Return neutral prediction if model not trained
            return {
                'predicted_return': 0.0,
                'confidence': 0.0,
                'prediction': 'NEUTRAL'
            }
        
        # Preprocess features
        X = self.preprocess_features(features_dict, time_remaining)
        
        # Scale features
        X_scaled = self.scaler.transform(X)
        
        # Make prediction
        predicted_return = self.model.predict(X_scaled)[0]
        
        # Calculate confidence based on prediction magnitude
        confidence = min(abs(predicted_return) * 10, 1.0)
        
        # Determine direction
        if predicted_return > 0.001:
            prediction = 'OVER'
        elif predicted_return < -0.001:
            prediction = 'UNDER'
        else:
            prediction = 'NEUTRAL'
        
        return {
            'predicted_return': predicted_return,
            'confidence': confidence,
            'prediction': prediction
        }
    
    def save_model(self, path):
        """
        Save model and scaler to disk
        """
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'feature_names': self.feature_names,
            'is_trained': self.is_trained
        }
        joblib.dump(model_data, path)
        print(f"Model saved to {path}")
    
    def load_model(self, path):
        """
        Load model and scaler from disk
        """
        if os.path.exists(path):
            model_data = joblib.load(path)
            self.model = model_data['model']
            self.scaler = model_data['scaler']
            self.feature_names = model_data['feature_names']
            self.is_trained = model_data['is_trained']
            print(f"Model loaded from {path}")
        else:
            print(f"No model found at {path}, initializing new model")
            self.initialize_model()
    
    def get_feature_importance(self):
        """
        Get feature importance from trained model
        """
        if not self.is_trained:
            return None
        
        importance = self.model.feature_importances_
        feature_importance = dict(zip(self.feature_names, importance))
        
        # Sort by importance
        sorted_importance = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)
        
        return sorted_importance


class OnlineLearningSystem:
    """
    Online learning system that continuously updates the model
    """
    def __init__(self, ml_pipeline, window_size=900):  # 15 minutes in seconds
        self.ml_pipeline = ml_pipeline
        self.window_size = window_size
        self.price_history = deque(maxlen=1000)
        self.feature_history = deque(maxlen=1000)
        self.window_start_time = None
        self.current_window_features = []
        
    def start_new_window(self, current_price):
        """
        Start a new prediction window
        """
        self.window_start_time = datetime.utcnow()
        self.current_window_features = []
        self.price_history.append(current_price)
        
    def add_observation(self, features, current_price):
        """
        Add observation to current window
        """
        self.current_window_features.append(features)
        self.price_history.append(current_price)
        
    def finalize_window(self, final_price):
        """
        Finalize window and add training sample
        """
        if not self.current_window_features:
            return
        
        # Use average features from window
        avg_features = {}
        for key in self.current_window_features[0].keys():
            values = [f.get(key, 0) for f in self.current_window_features]
            avg_features[key] = np.mean(values)
        
        # Calculate target (price return)
        initial_price = self.price_history[-len(self.current_window_features)]
        target_return = (final_price - initial_price) / initial_price
        
        # Add to ML pipeline
        self.ml_pipeline.add_sample(avg_features, target_return)
        
        # Reset for next window
        self.current_window_features = []
        
    def get_window_progress(self):
        """
        Get progress of current window
        """
        if not self.window_start_time:
            return 0, 0
        
        elapsed = (datetime.utcnow() - self.window_start_time).total_seconds()
        remaining = max(0, self.window_size - elapsed)
        
        return elapsed, remaining