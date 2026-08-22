"""
Continuous Learning System (Phase 2B)

Enables the system to improve from experience through continuous learning.
"""

import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
from datetime import datetime as dt
import hashlib


class Experience:
    """Single experience for learning."""
    
    def __init__(
        self,
        state: Dict[str, Any],
        action: str,
        result: Any,
        reward: float,
        success: bool,
        timestamp: str
    ):
        self.state = state
        self.action = action
        self.result = result
        self.reward = reward
        self.success = success
        self.timestamp = timestamp
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "state": self.state,
            "action": self.action,
            "result": str(self.result) if not isinstance(self.result, dict) else self.result,
            "reward": self.reward,
            "success": self.success,
            "timestamp": self.timestamp
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Experience':
        """Create from dictionary."""
        return cls(
            state=data["state"],
            action=data["action"],
            result=data["result"],
            reward=data["reward"],
            success=data["success"],
            timestamp=data["timestamp"]
        )


class ExperienceBuffer:
    """
    Stores experiences for training.
    """
    
    def __init__(self, max_size: int = 10000):
        self.max_size = max_size
        self.buffer: List[Experience] = []
        self.metrics = {
            "total_experiences": 0,
            "successful_experiences": 0,
            "failed_experiences": 0,
        }
    
    def add(self, experience: Experience):
        """Add experience to buffer."""
        self.buffer.append(experience)
        self.metrics["total_experiences"] += 1
        
        if experience.success:
            self.metrics["successful_experiences"] += 1
        else:
            self.metrics["failed_experiences"] += 1
        
        # Remove oldest if buffer is full
        if len(self.buffer) > self.max_size:
            self.buffer.pop(0)
    
    def sample(self, batch_size: int) -> List[Experience]:
        """Sample random batch of experiences."""
        if len(self.buffer) < batch_size:
            return self.buffer.copy()
        
        indices = np.random.choice(len(self.buffer), batch_size, replace=False)
        return [self.buffer[i] for i in indices]
    
    def get_all(self) -> List[Experience]:
        """Get all experiences."""
        return self.buffer.copy()
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get buffer metrics."""
        return self.metrics.copy()
    
    def clear(self):
        """Clear the buffer."""
        self.buffer = []
        self.metrics = {
            "total_experiences": 0,
            "successful_experiences": 0,
            "failed_experiences": 0,
        }


class DatasetCurator:
    """
    Curates and validates training data.
    """
    
    def __init__(self):
        self.poisoning_keywords = [
            "hack", "exploit", "bypass", "steal private key",
            "ignore instructions", "override safety"
        ]
    
    def is_valid(self, experience: Experience) -> bool:
        """Check if experience is valid for training."""
        # Check for poisoning in state or action
        state_str = str(experience.state).lower()
        action_str = experience.action.lower()
        
        for keyword in self.poisoning_keywords:
            if keyword in state_str or keyword in action_str:
                return False
        
        # Check for success (we want to learn from successes)
        if not experience.success:
            return False
        
        # Check for reasonable reward
        if abs(experience.reward) > 100:  # Sanity check
            return False
        
        return True
    
    def curate(self, experiences: List[Experience]) -> List[Experience]:
        """Filter out invalid experiences."""
        valid = [exp for exp in experiences if self.is_valid(exp)]
        
        print(f"Curated {len(valid)}/{len(experiences)} experiences")
        return valid
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get curation metrics."""
        return {
            "poisoning_keywords": len(self.poisoning_keywords),
        "curation_enabled": True,
        }


class ModelTrainer:
    """
    Trains models on curated experiences.
    
    For v0.1, provides framework. In production, would train neural networks.
    """
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.metrics = {
            "training_runs": 0,
            "total_models_trained": 0,
        }
    
    def train(self, experiences: List[Experience], model_type: str = "routing") -> Dict[str, Any]:
        """
        Train a model on experiences.
        
        Args:
            experiences: Training data
            model_type: Type of model to train
            
        Returns:
            Training metrics
        """
        self.metrics["training_runs"] += 1
        
        if model_type == "routing":
            # For v0.1, just return dummy metrics
            # In production, would actually train a neural network
            metrics = {
                "model_type": model_type,
                "training_samples": len(experiences),
                "epochs": 10,
                "final_loss": 0.1,
                "training_time_ms": 100,
            }
        else:
            metrics = {
                "model_type": model_type,
                "training_samples": len(experiences),
                "status": "not_implemented"
            }
        
        self.metrics["total_models_trained"] += 1
        return metrics
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get training metrics."""
        return self.metrics.copy()


class Validator:
    """
    Validates new models before deployment.
    """
    
    def __init__(self, test_experiences: List[Experience]):
        self.test_experiences = test_experiences
        self.metrics = {
            "validations": 0,
            "passed": 0,
            "failed": 0,
        }
    
    def validate(self, model, model_type: str) -> Tuple[bool, str]:
        """
        Validate a model against test data.
        
        Args:
            model: Model to validate
            model_type: Type of model
            
        Returns:
            (passed, reason)
        """
        self.metrics["validations"] += 1
        
        # For v0.1, simple validation: check if model exists
        if model is None:
            self.metrics["failed"] += 1
            return False, "Model is None"
        
        # Check if model has required methods
        if model_type == "routing" and not hasattr(model, "predict"):
            self.metrics["failed"] += 1
            return False, "Model missing predict method"
        
        # Run simple test
        try:
            if model_type == "routing":
                # Test prediction
                features = model.data_collector._extract_features("test", model_type, True)
                route = model.predict(features)
                
                if route is not None:
                    self.metrics["passed"] += 1
                    return True, "Validation passed"
        except Exception as e:
            self.metrics["failed"] += 1
            return False, f"Validation error: {str(e)}"
        
        self.metrics["failed"] += 1
        return False, "Validation failed"
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get validation metrics."""
        return self.metrics.copy()


class RollbackManager:
    """
    Manages rollback to previous model versions.
    """
    
    def __init__(self):
        self.model_versions = {}  # version_id -> model
        self.current_version = "v0.1"
        self.previous_versions = []
        self.metrics = {
            "rollbacks": 0,
            "deployments": 0,
        }
    
    def save_version(self, version_id: str, model: Any):
        """Save a model version."""
        self.model_versions[version_id] = model
        self.previous_versions.append(self.current_version)
        self.current_version = version_id
        self.metrics["deployments"] += 1
    
    def rollback(self) -> str:
        """Rollback to previous version."""
        if not self.previous_versions:
            print("No previous version to rollback to")
            return self.current_version
        
        previous = self.previous_versions.pop()
        self.current_version = previous
        self.metrics["rollbacks"] += 1
        
        print(f"Rolled back to version: {previous}")
        return previous
    
    def get_current_model(self) -> Any:
        """Get current model."""
        return self.model_versions.get(self.current_version)
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get rollback metrics."""
        return {
            "current_version": self.current_version,
            "available_versions": list(self.model_versions.keys()),
            "rollback_metrics": self.metrics,
        }


class ContinuousLearning:
    """
    Main continuous learning system.
    
    Orchestrates: experience collection, curation, training, validation, deployment.
    """
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        
        # Initialize components
        self.experience_buffer = ExperienceBuffer(
            max_size=self.config.get("buffer_size", 10000)
        )
        self.curator = DatasetCurator()
        self.trainer = ModelTrainer(config)
        
        # Validator (will be initialized with test data)
        self.validator = None
        
        # Rollback manager
        self.rollback_manager = RollbackManager()
        
        # Metrics
        self.metrics = {
            "learning_cycles": 0,
            "total_experiences_collected": 0,
            "total_models_deployed": 0,
        }
    
    def add_experience(self, state: Dict[str, Any], action: str, result: Any, reward: float, success: bool):
        """Add an experience to the buffer."""
        experience = Experience(
            state=state,
            action=action,
            result=result,
            reward=reward,
            success=success,
            timestamp=datetime.datetime.utcnow().isoformat()
        )
        
        self.experience_buffer.add(experience)
        self.metrics["total_experiences_collected"] += 1
    
    def learning_cycle(self, model_type: str = "routing") -> Dict[str, Any]:
        """
        Perform one learning cycle.
        
        Args:
            model_type: Type of model to train
            
        Returns:
            Learning cycle metrics
        """
        self.metrics["learning_cycles"] += 1
        
        # 1. Collect experiences
        experiences = self.experience_buffer.get_all()
        
        if len(experiences) < 10:
            return {
                "status": "insufficient_data",
                "experiences": len(experiences),
                "required": 10
            }
        
        # 2. Curate data
        curated = self.curator.curate(experiences)
        
        if len(curated) < 5:
            return {
                "status": "insufficient_valid_data",
                "curated": len(curated),
                "required": 5
            }
        
        # 3. Train model
        training_metrics = self.trainer.train(curated, model_type)
        
        # 4. Validate (if validator initialized)
        if self.validator:
            # Get current model (mock for v0.1)
            current_model = self.rollback_manager.get_current_model()
            passed, reason = self.validator.validate(current_model, model_type)
            
            if not passed:
                print(f"Validation failed: {reason}")
                return {
                    "status": "validation_failed",
                    "reason": reason,
                    "training_metrics": training_metrics
                }
        
        # 5. Deploy (mock for v0.1)
        version_id = f"v{self.metrics['learning_cycles']}"
        self.rollback_manager.save_version(version_id, "mock_model")
        self.metrics["total_models_deployed"] += 1
        
        return {
            "status": "success",
            "training_metrics": training_metrics,
            "version_id": version_id
        }
    
    def set_validator(self, test_experiences: List[Experience]):
        """Set validator with test data."""
        self.validator = Validator(test_experiences)
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get continuous learning metrics."""
        return {
            "learning_metrics": self.metrics,
            "buffer_metrics": self.experience_buffer.get_metrics(),
            "curator_metrics": self.curator.get_metrics(),
            "trainer_metrics": self.trainer.get_metrics(),
            "rollback_metrics": self.rollback_manager.get_metrics(),
        }
