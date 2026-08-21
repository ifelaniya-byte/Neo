"""
World Model with Simulation (Phase 2A)

Enables reasoning about consequences of actions through state prediction and planning.
"""

import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


@dataclass
class WorldState:
    """Representation of world state."""
    mathematical_knowledge: Dict[str, Any]  # Formulas, theorems
    computational_resources: Dict[str, float]  # Available computation
    time_budget: float  # Time remaining
    cost_budget: float  # Cost budget remaining
    tool_availability: Dict[str, bool]  # Which tools are available
    context_stack: List[str]  # Contextual information


@dataclass
class Action:
    """Action that can be taken in the world."""
    tool_name: str
    parameters: Dict[str, Any]
    estimated_cost: float
    estimated_time: float


@dataclass
class Prediction:
    """Prediction of action outcome."""
    next_state: WorldState
    reward: float  # Quality of outcome
    success_probability: float
    uncertainty: float


class TransitionModel:
    """
    Predicts state transitions given actions.
    
    For v0.1, uses simple heuristic models.
    In production, would use learned neural networks.
    """
    
    def __init__(self):
        pass
    
    def predict(self, state: WorldState, action: Action) -> Prediction:
        """
        Predict the outcome of taking an action in a state.
        
        Args:
            state: Current world state
            action: Action to take
            
        Returns:
            Prediction of next state and reward
        """
        # Create predicted next state
        next_state = WorldState(
            mathematical_knowledge=state.mathematical_knowledge.copy(),
            computational_resources=state.computational_resources.copy(),
            time_budget=max(0, state.time_budget - action.estimated_time),
            cost_budget=max(0, state.cost_budget - action.estimated_cost),
            tool_availability=state.tool_availability.copy(),
            context_stack=state.context_stack.copy()
        )
        
        # Update resources based on action
        if action.tool_name in next_state.computational_resources:
            next_state.computational_resources[action.tool_name] += 1
        
        # Calculate reward (negative cost is reward)
        reward = -action.estimated_cost
        
        # Success probability based on resources
        if next_state.time_budget > 0 and next_state.cost_budget > 0:
            success_probability = 0.9
        else:
            success_probability = 0.3
        
        # Uncertainty based on resource constraints
        uncertainty = 1.0 - success_probability
        
        return Prediction(
            next_state=next_state,
            reward=reward,
            success_probability=success_probability,
            uncertainty=uncertainty
        )


class RewardModel:
    """
    Evaluates the quality of outcomes.
    
    For v0.1, uses simple heuristics.
    """
    
    def __init__(self):
        pass
    
    def evaluate(self, state: WorldState, result: Any) -> float:
        """
        Evaluate the quality of a result in a state.
        
        Args:
            state: World state when result was produced
            result: The result produced
            
        Returns:
            Reward value (higher is better)
        """
        reward = 0.0
        
        # Reward for successful computation
        if result is not None and result != "error":
            reward += 1.0
        
        # Reward for staying within budget
        if state.cost_budget >= 0:
            reward += 0.5
        
        # Reward for staying within time budget
        if state.time_budget >= 0:
            reward += 0.5
        
        return reward


class WorldModel:
    """
    Complete world model combining transition and reward models.
    """
    
    def __init__(self):
        self.transition_model = TransitionModel()
        self.reward_model = RewardModel()
        
        # Metrics
        self.metrics = {
            "total_predictions": 0,
            "total_reward": 0.0,
            "successful_predictions": 0,
        }
    
    def predict(self, state: WorldState, action: Action) -> Prediction:
        """
        Predict outcome of action.
        
        Args:
            state: Current state
            action: Action to take
            
        Returns:
            Prediction of next state and reward
        """
        self.metrics["total_predictions"] += 1
        
        prediction = self.transition_model.predict(state, action)
        
        if prediction.success_probability > 0.5:
            self.metrics["successful_predictions"] += 1
        
        self.metrics["total_reward"] += prediction.reward
        
        return prediction
    
    def evaluate(self, state: WorldState, result: Any) -> float:
        """Evaluate result quality."""
        return self.reward_model.evaluate(state, result)
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get world model metrics."""
        return self.metrics.copy()


class Planner:
    """
    Plans sequences of actions using the world model.
    
    For v0.1, uses simple greedy search.
    In production, would use Monte Carlo Tree Search or other algorithms.
    """
    
    def __init__(self, world_model: WorldModel, max_depth: int = 3):
        self.world_model = world_model
        self.max_depth = max_depth
        
        # Metrics
        self.metrics = {
            "total_plans": 0,
            "average_plan_length": 0.0,
        }
    
    def plan(self, initial_state: WorldState, goal: str, available_actions: List[Action]) -> List[Action]:
        """
        Plan a sequence of actions to achieve a goal.
        
        Args:
            initial_state: Starting world state
            goal: Goal description
            available_actions: Actions that can be taken
            
        Returns:
            List of actions in optimal order
        """
        self.metrics["total_plans"] += 1
        
        # Simple greedy planning
        best_plan = []
        current_state = initial_state
        
        for _ in range(self.max_depth):
            best_action = None
            best_value = -float('inf')
            
            for action in available_actions:
                prediction = self.world_model.predict(current_state, action)
                
                # Value = expected reward
                expected_value = prediction.success_probability * prediction.reward
                
                if expected_value > best_value:
                    best_value = expected_value
                    best_action = action
            
            if best_action is None:
                break
            
            best_plan.append(best_action)
            current_state = self.world_model.transition_model.predict(current_state, best_action).next_state
            
            # Stop if we've achieved goal (simplified check)
            if self._goal_achieved(current_state, goal):
                break
        
        # Update metrics
        self.metrics["average_plan_length"] = (
            (self.metrics["average_plan_length"] * (self.metrics["total_plans"] - 1) + len(best_plan)) /
            self.metrics["total_plans"]
        )
        
        return best_plan
    
    def _goal_achieved(self, state: WorldState, goal: str) -> bool:
        """Check if goal is achieved in state (simplified)."""
        # For v0.1, assume goal achieved if we have positive resources
        return state.cost_budget > 0 and state.time_budget > 0
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get planner metrics."""
        return self.metrics.copy()
