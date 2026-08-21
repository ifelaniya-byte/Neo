"""
Learned Routing Model (Phase 1B)

Replaces rule-based routing with a learned model that adapts from experience.
Uses simple neural network to predict optimal routes based on task features.
"""

import numpy as np
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum

# Import UAIR contracts
import sys
sys.path.append("C:/Users/AIAli/OneDrive/Desktop/World Model")
from uair.contracts import TaskClass, RoutePath


@dataclass
class RoutingFeatures:
    """Features for routing decision."""
    task_length: float
    has_numbers: bool
    has_math: bool
    has_code_keywords: bool
    has_knowledge_keywords: bool
    task_type_encoded: float  # Encoded task type
    complexity_estimate: float
    historical_success_rate: float = 0.5


class RoutingModel:
    """
    Simple neural network for routing decisions.
    
    For v0.1, uses a small feedforward network.
    In production, could use gradient boosting or more complex models.
    """
    
    def __init__(self, input_dim: int = 7, hidden_dim: int = 16, output_dim: int = 5):
        """
        Initialize routing model.
        
        Args:
            input_dim: Number of input features
            hidden_dim: Hidden layer size
            output_dim: Number of output routes
        """
        self.input_dim = input_dim
        self.hidden_dim = hidden_dim
        self.output_dim = output_dim
        
        # Simple neural network weights (for v0.1, using numpy)
        # In production, use PyTorch/TensorFlow
        np.random.seed(42)
        self.W1 = np.random.randn(input_dim, hidden_dim) * 0.1
        self.b1 = np.zeros(hidden_dim)
        self.W2 = np.random.randn(hidden_dim, output_dim) * 0.1
        self.b2 = np.zeros(output_dim)
        
        # Training metrics
        self.is_trained = False
        self.training_epochs = 0
        
        # Route encoding
        self.route_to_idx = {
            RoutePath.CACHE: 0,
            RoutePath.DETERMINISTIC: 1,
            RoutePath.RETRIEVAL: 2,
            RoutePath.SPECIALIST: 3,
            RoutePath.LLM: 4,
        }
        self.idx_to_route = {v: k for k, v in self.route_to_idx.items()}
    
    def forward(self, x: np.ndarray) -> np.ndarray:
        """Forward pass through the network."""
        # Hidden layer with ReLU
        h = np.maximum(0, np.dot(x, self.W1) + self.b1)
        # Output layer with softmax
        logits = np.dot(h, self.W2) + self.b2
        # Softmax
        exp_logits = np.exp(logits - np.max(logits))
        return exp_logits / np.sum(exp_logits)
    
    def predict(self, features: RoutingFeatures) -> RoutePath:
        """
        Predict best route for given features.
        
        Args:
            features: Routing features
            
        Returns:
            Predicted route
        """
        x = self._features_to_array(features)
        probs = self.forward(x)
        best_idx = np.argmax(probs)
        return self.idx_to_route[best_idx]
    
    def predict_proba(self, features: RoutingFeatures) -> Dict[RoutePath, float]:
        """
        Predict probability distribution over routes.
        
        Args:
            features: Routing features
            
        Returns:
            Dictionary mapping routes to probabilities
        """
        x = self._features_to_array(features)
        probs = self.forward(x)
        
        return {self.idx_to_route[i]: probs[i] for i in range(len(probs))}
    
    def _features_to_array(self, features: RoutingFeatures) -> np.ndarray:
        """Convert features to numpy array."""
        return np.array([
            features.task_length / 1000,  # Normalize
            1.0 if features.has_numbers else 0.0,
            1.0 if features.has_math else 0.0,
            1.0 if features.has_code_keywords else 0.0,
            1.0 if features.has_knowledge_keywords else 0.0,
            features.task_type_encoded,
            features.complexity_estimate,
            features.historical_success_rate
        ])
    
    def train(self, training_data: List[tuple[RoutingFeatures, RoutePath]], epochs: int = 100):
        """
        Train the routing model.
        
        Args:
            training_data: List of (features, correct_route) tuples
            epochs: Number of training epochs
        """
        if not training_data:
            print("Warning: No training data provided")
            return
        
        learning_rate = 0.01
        
        for epoch in range(epochs):
            total_loss = 0
            
            for features, correct_route in training_data:
                # Forward pass
                x = self._features_to_array(features)
                probs = self.forward(x)
                
                # Target: one-hot encoding
                target_idx = self.route_to_idx[correct_route]
                target = np.zeros(self.output_dim)
                target[target_idx] = 1.0
                
                # Compute loss (cross-entropy)
                loss = -np.sum(target * np.log(probs + 1e-10))
                total_loss += loss
                
                # Backward pass (gradient descent)
                # Gradient of loss w.r.t. logits
                dlogits = probs - target
                
                # Gradient w.r.t. W2, b2
                h = np.maximum(0, np.dot(x, self.W1) + self.b1)
                dW2 = np.outer(h, dlogits)
                db2 = dlogits
                
                # Gradient w.r.t. W1, b1
                dh = (h > 0).astype(float) * np.dot(dlogits, self.W2.T)
                dW1 = np.outer(x, dh)
                db1 = dh
                
                # Update weights
                self.W2 -= learning_rate * dW2
                self.b2 -= learning_rate * db2
                self.W1 -= learning_rate * dW1
                self.b1 -= learning_rate * db1
            
            if epoch % 20 == 0:
                print(f"Epoch {epoch}, Loss: {total_loss / len(training_data):.4f}")
        
        self.is_trained = True
        self.training_epochs = epochs
        print(f"Training complete. Epochs: {epochs}")


class RoutingDataCollector:
    """
    Collects and labels routing data for training.
    """
    
    def __init__(self):
        self.data = []  # List of (features, route, success) tuples
        self.route_success_rates = {}  # Track success rates per route
    
    def add_sample(
        self,
        task: str,
        route: RoutePath,
        success: bool,
        cost_usd: float
    ):
        """
        Add a routing sample.
        
        Args:
            task: Task string
            route: Route that was used
            success: Whether the route succeeded
            cost_usd: Cost of the route
        """
        features = self._extract_features(task, route, success)
        self.data.append((features, route, success))
        
        # Update success rates
        route_str = route.value
        if route_str not in self.route_success_rates:
            self.route_success_rates[route_str] = {"success": 0, "total": 0}
        
        self.route_success_rates[route_str]["total"] += 1
        if success:
            self.route_success_rates[route_str]["success"] += 1
    
    def _extract_features(self, task: str, route: RoutePath, success: bool) -> RoutingFeatures:
        """Extract features from task and result."""
        import re
        
        # Length
        task_length = len(task)
        
        # Feature detection
        has_numbers = bool(re.search(r"\d+", task))
        has_math = bool(re.search(r"[\+\-\*\/\^]", task))
        has_code_keywords = bool(re.search(r"(code|function|class|def |import |print\()", task, re.IGNORECASE))
        has_knowledge_keywords = bool(re.search(r"(what|how|why|when|where|who|which)", task, re.IGNORECASE))
        
        # Task type encoding (simple heuristic)
        if has_math:
            task_type_encoded = 0.0  # arithmetic
        elif has_code_keywords:
            task_type_encoded = 0.25  # code
        elif has_knowledge_keywords:
            task_type_encoded = 0.5  # knowledge
        else:
            task_type_encoded = 0.75  # unknown
        
        # Complexity estimate
        complexity = 0.0
        complexity += min(task_length / 1000, 0.4)
        complexity += 0.2 if has_numbers else 0
        complexity += 0.2 if has_math else 0
        
        # Historical success rate for this route
        route_str = route.value
        if route_str in self.route_success_rates:
            stats = self.route_success_rates[route_str]
            historical_success_rate = stats["success"] / stats["total"] if stats["total"] > 0 else 0.5
        else:
            historical_success_rate = 0.5
        
        return RoutingFeatures(
            task_length=task_length,
            has_numbers=has_numbers,
            has_math=has_math,
            has_code_keywords=has_code_keywords,
            has_knowledge_keywords=has_knowledge_keywords,
            task_type_encoded=task_type_encoded,
            complexity_estimate=complexity,
            historical_success_rate=historical_success_rate
        )
    
    def get_training_data(self) -> List[tuple[RoutingFeatures, RoutePath]]:
        """Get training data for the routing model."""
        return [(features, route) for features, route, success in self.data if success]
    
    def get_data_summary(self) -> Dict[str, Any]:
        """Get summary of collected data."""
        return {
            "total_samples": len(self.data),
            "route_success_rates": self.route_success_rates,
            "successful_samples": sum(1 for _, _, success in self.data if success),
            "failed_samples": sum(1 for _, _, success in self.data if not success),
        }


class LearnedRouter:
    """
    Router that uses learned model instead of rules.
    """
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        
        # Initialize model
        self.model = RoutingModel()
        
        # Data collector
        self.data_collector = RoutingDataCollector()
        
        # Fallback to rule-based when model not trained
        self.use_learned = False
        
        # Metrics
        self.metrics = {
            "learned_predictions": 0,
            "rule_predictions": 0,
            "correct_predictions": 0,
        }
    
    def route(self, task: str, payload: Any = None) -> RoutePath:
        """
        Route using learned model if available, otherwise rule-based.
        
        Args:
            task: Task string
            payload: Optional payload
            
        Returns:
            Predicted route
        """
        if self.use_learned and self.model.is_trained:
            # Extract features
            features = self.data_collector._extract_features(task, RoutePath.LLM, True)
            
            # Predict with learned model
            route = self.model.predict(features)
            self.metrics["learned_predictions"] += 1
            return route
        else:
            # Fallback to rule-based
            self.metrics["rule_predictions"] += 1
            return self._rule_based_route(task)
    
    def _rule_based_route(self, task: str) -> RoutePath:
        """Simple rule-based routing fallback."""
        import re
        
        if re.search(r"\d+\s*[\+\-\*\/]\s*\d+", task):
            return RoutePath.DETERMINISTIC
        elif re.search(r"^(what|how|why|when|where|who|which)", task, re.IGNORECASE):
            return RoutePath.RETRIEVAL
        else:
            return RoutePath.LLM
    
    def add_experience(self, task: str, route: RoutePath, success: bool, cost_usd: float):
        """Add routing experience for learning."""
        self.data_collector.add_sample(task, route, success, cost_usd)
    
    def train_model(self, epochs: int = 100):
        """Train the routing model on collected data."""
        training_data = self.data_collector.get_training_data()
        
        if len(training_data) < 10:
            print("Not enough data to train (need at least 10 samples)")
            return
        
        print(f"Training on {len(training_data)} samples...")
        self.model.train(training_data, epochs)
        self.use_learned = True
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get routing metrics."""
        return {
            "router_metrics": self.metrics,
            "data_summary": self.data_collector.get_data_summary(),
            "model_is_trained": self.model.is_trained,
            "training_epochs": self.model.training_epochs,
        }
