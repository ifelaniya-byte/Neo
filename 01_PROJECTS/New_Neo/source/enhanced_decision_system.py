"""
ENHANCED DECISION-MAKING AND PLANNING SYSTEM

Advanced decision-making with:
- Monte Carlo Tree Search for planning
- Multi-objective optimization
- Risk assessment and management
- Temporal difference learning
- Hierarchical task planning
- Scenario analysis and simulation
"""

import random
import math
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Callable
from dataclasses import dataclass, asdict
from enum import Enum
from collections import defaultdict
import hashlib


class PlanningHorizon(Enum):
    """Planning time horizons."""
    IMMEDIATE = "IMMEDIATE"  # < 1 minute
    SHORT_TERM = "SHORT_TERM"  # < 1 hour
    MEDIUM_TERM = "MEDIUM_TERM"  # < 1 day
    LONG_TERM = "LONG_TERM"  # < 1 week
    STRATEGIC = "STRATEGIC"  # > 1 week


class DecisionStyle(Enum):
    """Decision-making styles."""
    ANALYTICAL = "ANALYTICAL"
    INTUITIVE = "INTUITIVE"
    COLLABORATIVE = "COLLABORATIVE"
    DECISIVE = "DECISIVE"
    DELIBERATIVE = "DELIBERATIVE"
    FLEXIBLE = "FLEXIBLE"


class RiskTolerance(Enum):
    """Risk tolerance levels."""
    RISK_AVERSE = "RISK_AVERSE"
    RISK_NEUTRAL = "RISK_NEUTRAL"
    RISK_SEEKING = "RISK_SEEKING"
    CALCULATED = "CALCULATED"


@dataclass
class DecisionObjective:
    """Objective for multi-objective optimization."""
    name: str
    weight: float
    target_value: float
    current_value: float
    importance: float


@dataclass
class Scenario:
    """Potential future scenario."""
    id: str
    name: str
    probability: float
    outcomes: Dict[str, float]
    time_horizon: str
    assumptions: List[str]


@dataclass
class DecisionOption:
    """A decision option with full analysis."""
    id: str
    name: str
    description: str
    expected_value: float
    risk_score: float
    confidence: float
    objectives_scores: Dict[str, float]
    scenario_performance: Dict[str, float]
    implementation_cost: float
    time_toimplement: float
    prerequisites: List[str]
    side_effects: List[str]


@dataclass
class Plan:
    """A structured plan with hierarchical tasks."""
    id: str
    name: str
    description: str
    goal: str
    horizon: str
    tasks: List['Task']
    resources: Dict[str, float]
    timeline: Dict[str, str]
    success_criteria: List[str]
    risk_mitigation: List[str]


@dataclass
class Task:
    """A task within a plan."""
    id: str
    name: str
    description: str
    dependencies: List[str]
    estimated_duration: float
    resources_required: Dict[str, float]
    success_probability: float
    status: str = "PENDING"


class MCTSNode:
    """Node for Monte Carlo Tree Search."""
    
    def __init__(self, state: Any, parent: Optional['MCTSNode'] = None):
        self.state = state
        self.parent = parent
        self.children: List['MCTSNode'] = []
        self.visits = 0
        self.value = 0.0
        self.untried_actions: List[Any] = []
    
    def is_fully_expanded(self) -> bool:
        return len(self.untried_actions) == 0
    
    def is_terminal(self) -> bool:
        return len(self.children) == 0 and self.visits > 0
    
    def best_child(self, exploration_weight: float = 1.414) -> 'MCTSNode':
        """Select best child using UCB1 formula."""
        if not self.children:
            return self
        
        best_score = -float('inf')
        best_child = None
        
        for child in self.children:
            if child.visits == 0:
                continue
            
            exploitation = child.value / child.visits
            exploration = exploration_weight * math.sqrt(
                2 * math.log(self.visits) / child.visits
            )
            score = exploitation + exploration
            
            if score > best_score:
                best_score = score
                best_child = child
        
        return best_child or self.children[0]


class EnhancedDecisionSystem:
    """
    Enhanced decision-making and planning system with advanced AI techniques.
    """
    
    def __init__(self):
        self.decision_history: List[Dict] = []
        self.objectives: List[DecisionObjective] = []
        self.scenarios: List[Scenario] = []
        self.current_plan: Optional[Plan] = None
        self.decision_style = DecisionStyle.ANALYTICAL
        self.risk_tolerance = RiskTolerance.CALCULATED
        self.learning_rate = 0.1
        self.discount_factor = 0.95
        self.exploration_weight = 1.414
        
    def add_objective(self, name: str, weight: float, target_value: float, 
                     current_value: float, importance: float = 1.0):
        """Add a decision objective."""
        objective = DecisionObjective(
            name=name,
            weight=weight,
            target_value=target_value,
            current_value=current_value,
            importance=importance
        )
        self.objectives.append(objective)
    
    def generate_scenarios(self, context: Dict, num_scenarios: int = 5) -> List[Scenario]:
        """Generate potential future scenarios."""
        scenarios = []
        
        for i in range(num_scenarios):
            scenario_id = hashlib.md5(f"{context}_{i}_{datetime.now().isoformat()}".encode()).hexdigest()[:8]
            
            # Random scenario parameters
            probability = random.random()
            outcomes = {}
            
            # Generate outcomes for each objective
            for obj in self.objectives:
                outcome_range = obj.target_value - obj.current_value
                outcome = obj.current_value + outcome_range * random.uniform(-0.5, 1.5)
                outcomes[obj.name] = outcome
            
            scenario = Scenario(
                id=scenario_id,
                name=f"Scenario_{i+1}",
                probability=probability,
                outcomes=outcomes,
                time_horizon=PlanningHorizon.MEDIUM_TERM.value,
                assumptions=[f"Assumption_{j}" for j in range(3)]
            )
            
            scenarios.append(scenario)
        
        self.scenarios = scenarios
        return scenarios
    
    def evaluate_option(self, option: DecisionOption) -> DecisionOption:
        """
        Evaluate a decision option across all objectives and scenarios.
        """
        # Calculate objective scores
        for obj in self.objectives:
            if obj.name in option.objectives_scores:
                # Score based on progress toward target
                progress = option.objectives_scores[obj.name] / obj.target_value
                option.objectives_scores[obj.name] = min(1.0, max(0.0, progress))
        
        # Calculate scenario performance
        for scenario in self.scenarios:
            scenario_score = 0.0
            for obj in self.objectives:
                if obj.name in option.objectives_scores:
                    outcome = scenario.outcomes.get(obj.name, obj.current_value)
                    performance = option.objectives_scores[obj.name] * (outcome / obj.target_value)
                    scenario_score += performance * obj.weight
            
            option.scenario_performance[scenario.id] = scenario_score
        
        # Calculate expected value
        expected_value = 0.0
        for scenario in self.scenarios:
            scenario_value = option.scenario_performance.get(scenario.id, 0.0)
            expected_value += scenario_value * scenario.probability
        
        option.expected_value = expected_value
        
        # Calculate risk score (variance across scenarios)
        if len(self.scenarios) > 1:
            values = list(option.scenario_performance.values())
            mean = sum(values) / len(values)
            variance = sum((v - mean) ** 2 for v in values) / len(values)
            option.risk_score = math.sqrt(variance)
        else:
            option.risk_score = 0.0
        
        # Adjust confidence based on risk tolerance
        if self.risk_tolerance == RiskTolerance.RISK_AVERSE:
            option.confidence = max(0.0, option.confidence - option.risk_score)
        elif self.risk_tolerance == RiskTolerance.RISK_SEEKING:
            option.confidence = min(1.0, option.confidence + option.risk_score * 0.5)
        
        return option
    
    def multi_objective_optimization(self, options: List[DecisionOption]) -> List[DecisionOption]:
        """
        Perform multi-objective optimization to find Pareto-optimal solutions.
        """
        pareto_front = []
        
        for option in options:
            is_dominated = False
            
            for other in options:
                if other.id == option.id:
                    continue
                
                # Check if other dominates option
                dominates = True
                for obj in self.objectives:
                    other_score = other.objectives_scores.get(obj.name, 0.0)
                    option_score = option.objectives_scores.get(obj.name, 0.0)
                    
                    if other_score < option_score:
                        dominates = False
                        break
                
                if dominates:
                    is_dominated = True
                    break
            
            if not is_dominated:
                pareto_front.append(option)
        
        return pareto_front
    
    def monte_carlo_tree_search(self, initial_state: Any, 
                                get_actions: Callable,
                                apply_action: Callable,
                                is_terminal: Callable,
                                evaluate_state: Callable,
                                iterations: int = 1000) -> Tuple[Any, float]:
        """
        Perform Monte Carlo Tree Search for planning.
        """
        root = MCTSNode(initial_state)
        root.untried_actions = get_actions(initial_state)
        
        for _ in range(iterations):
            # Selection
            node = root
            while not node.is_terminal() and node.is_fully_expanded():
                node = node.best_child(self.exploration_weight)
            
            # Expansion
            if not node.is_terminal() and node.untried_actions:
                action = random.choice(node.untried_actions)
                node.untried_actions.remove(action)
                new_state = apply_action(node.state, action)
                child_node = MCTSNode(new_state, parent=node)
                child_node.untried_actions = get_actions(new_state)
                node.children.append(child_node)
                node = child_node
            
            # Simulation
            if not is_terminal(node.state):
                simulation_state = node.state
                while not is_terminal(simulation_state):
                    actions = get_actions(simulation_state)
                    if actions:
                        action = random.choice(actions)
                        simulation_state = apply_action(simulation_state, action)
                    else:
                        break
            
            # Backpropagation
            value = evaluate_state(node.state)
            while node is not None:
                node.visits += 1
                node.value += value
                node = node.parent
        
        # Return best action from root
        best_child = root.best_child(0)  # Pure exploitation
        if best_child:
            # Find the action that led to best child
            for child in root.children:
                if child == best_child:
                    # This is simplified - in practice, track actions better
                    return child.state, child.value / child.visits if child.visits > 0 else 0.0
        
        return initial_state, 0.0
    
    def create_hierarchical_plan(self, goal: str, horizon: PlanningHorizon,
                                 context: Dict) -> Plan:
        """
        Create a hierarchical plan for achieving a goal.
        """
        plan_id = hashlib.md5(f"{goal}_{datetime.now().isoformat()}".encode()).hexdigest()[:8]
        
        # Decompose goal into main tasks
        main_tasks = self._decompose_goal(goal, context)
        
        # Estimate resources
        resources = self._estimate_resources(main_tasks)
        
        # Create timeline
        timeline = self._create_timeline(main_tasks, horizon)
        
        plan = Plan(
            id=plan_id,
            name=f"Plan for {goal}",
            description=f"Plan to achieve {goal} with {horizon.value} horizon",
            goal=goal,
            horizon=horizon.value,
            tasks=main_tasks,
            resources=resources,
            timeline=timeline,
            success_criteria=self._define_success_criteria(goal),
            risk_mitigation=self._identify_risks(main_tasks)
        )
        
        self.current_plan = plan
        return plan
    
    def _decompose_goal(self, goal: str, context: Dict) -> List[Task]:
        """Decompose goal into hierarchical tasks."""
        # Simplified task decomposition
        tasks = []
        
        # Create main phases
        phases = ["Analysis", "Planning", "Execution", "Monitoring", "Completion"]
        
        for i, phase in enumerate(phases):
            task_id = hashlib.md5(f"{goal}_{phase}".encode()).hexdigest()[:8]
            
            dependencies = []
            if i > 0:
                dependencies.append(tasks[i-1].id)
            
            task = Task(
                id=task_id,
                name=f"{phase} Phase",
                description=f"Execute {phase.lower()} for goal: {goal}",
                dependencies=dependencies,
                estimated_duration=random.uniform(1, 8) * 3600,  # 1-8 hours
                resources_required={"compute": random.uniform(0.1, 1.0), "time": random.uniform(1, 8)},
                success_probability=random.uniform(0.7, 0.95)
            )
            
            tasks.append(task)
        
        return tasks
    
    def _estimate_resources(self, tasks: List[Task]) -> Dict[str, float]:
        """Estimate total resources required for plan."""
        total_resources = defaultdict(float)
        
        for task in tasks:
            for resource, amount in task.resources_required.items():
                total_resources[resource] += amount
        
        return dict(total_resources)
    
    def _create_timeline(self, tasks: List[Task], horizon: PlanningHorizon) -> Dict[str, str]:
        """Create timeline for plan execution."""
        timeline = {}
        current_time = datetime.now()
        
        horizon_durations = {
            PlanningHorizon.IMMEDIATE: timedelta(minutes=5),
            PlanningHorizon.SHORT_TERM: timedelta(hours=1),
            PlanningHorizon.MEDIUM_TERM: timedelta(days=1),
            PlanningHorizon.LONG_TERM: timedelta(weeks=1),
            PlanningHorizon.STRATEGIC: timedelta(weeks=4)
        }
        
        total_duration = horizon_durations.get(horizon, timedelta(days=1))
        time_per_task = total_duration / len(tasks)
        
        for task in tasks:
            timeline[task.id] = current_time.isoformat()
            current_time += time_per_task
        
        return timeline
    
    def _define_success_criteria(self, goal: str) -> List[str]:
        """Define success criteria for goal."""
        return [
            f"Goal '{goal}' achieved",
            "All tasks completed successfully",
            "Resource usage within budget",
            "Timeline adhered to",
            "Quality standards met"
        ]
    
    def _identify_risks(self, tasks: List[Task]) -> List[str]:
        """Identify potential risks in plan."""
        risks = []
        
        for task in tasks:
            if task.success_probability < 0.8:
                risks.append(f"Task '{task.name}' has low success probability")
            if task.estimated_duration > 4 * 3600:  # > 4 hours
                risks.append(f"Task '{task.name}' may take longer than expected")
        
        return risks
    
    def make_decision(self, options: List[DecisionOption], 
                    context: Dict) -> DecisionOption:
        """
        Make a decision using enhanced analysis.
        """
        # Evaluate all options
        evaluated_options = [self.evaluate_option(opt) for opt in options]
        
        # Get Pareto-optimal solutions
        pareto_options = self.multi_objective_optimization(evaluated_options)
        
        # Select based on decision style
        if self.decision_style == DecisionStyle.ANALYTICAL:
            # Choose highest expected value
            selected = max(pareto_options, key=lambda x: x.expected_value)
        elif self.decision_style == DecisionStyle.DECISIVE:
            # Choose quickly based on confidence
            selected = max(pareto_options, key=lambda x: x.confidence)
        elif self.decision_style == DecisionStyle.DELIBERATIVE:
            # Consider trade-offs carefully
            selected = min(pareto_options, key=lambda x: x.risk_score)
        else:
            # Default to balanced approach
            selected = max(pareto_options, 
                         key=lambda x: x.expected_value * x.confidence)
        
        # Record decision
        self.decision_history.append({
            'timestamp': datetime.now().isoformat(),
            'selected_option': selected.id,
            'context': context,
            'style': self.decision_style.value,
            'risk_tolerance': self.risk_tolerance.value
        })
        
        return selected
    
    def update_from_feedback(self, outcome: float, expected: float):
        """
        Update decision-making based on feedback.
        """
        # Calculate prediction error
        error = outcome - expected
        
        # Adjust risk tolerance based on performance
        if error > 0:  # Better than expected
            if self.risk_tolerance == RiskTolerance.RISK_AVERSE:
                self.risk_tolerance = RiskTolerance.RISK_NEUTRAL
            elif self.risk_tolerance == RiskTolerance.RISK_NEUTRAL:
                self.risk_tolerance = RiskTolerance.CALCULATED
        elif error < 0:  # Worse than expected
            if self.risk_tolerance == RiskTolerance.RISK_SEEKING:
                self.risk_tolerance = RiskTolerance.CALCULATED
            elif self.risk_tolerance == RiskTolerance.CALCULATED:
                self.risk_tolerance = RiskTolerance.RISK_NEUTRAL
        
        # Update learning rate based on error magnitude
        if abs(error) > 0.5:
            self.learning_rate = min(0.5, self.learning_rate * 1.1)
        else:
            self.learning_rate = max(0.01, self.learning_rate * 0.9)
    
    def get_decision_statistics(self) -> Dict:
        """Get statistics about decision-making."""
        if not self.decision_history:
            return {}
        
        total_decisions = len(self.decision_history)
        style_counts = defaultdict(int)
        tolerance_counts = defaultdict(int)
        
        for decision in self.decision_history:
            style_counts[decision['style']] += 1
            tolerance_counts[decision['risk_tolerance']] += 1
        
        return {
            'total_decisions': total_decisions,
            'decision_style_distribution': dict(style_counts),
            'risk_tolerance_distribution': dict(tolerance_counts),
            'current_style': self.decision_style.value,
            'current_risk_tolerance': self.risk_tolerance.value,
            'learning_rate': self.learning_rate
        }


def test_enhanced_decision_system():
    """Test the enhanced decision system."""
    decision_system = EnhancedDecisionSystem()
    
    # Add objectives
    decision_system.add_objective("accuracy", 0.4, 1.0, 0.7, 1.0)
    decision_system.add_objective("speed", 0.3, 0.5, 0.3, 0.8)
    decision_system.add_objective("efficiency", 0.3, 0.8, 0.5, 0.9)
    
    # Generate scenarios
    scenarios = decision_system.generate_scenarios({"project": "test"}, 5)
    print(f"Generated {len(scenarios)} scenarios")
    
    # Create decision options
    options = [
        DecisionOption(
            id="opt1",
            name="Conservative Approach",
            description="Safe and steady",
            expected_value=0.0,
            risk_score=0.0,
            confidence=0.9,
            objectives_scores={"accuracy": 0.85, "speed": 0.4, "efficiency": 0.6},
            scenario_performance={},
            implementation_cost=100.0,
            time_toimplement=1.0,
            prerequisites=[],
            side_effects=[]
        ),
        DecisionOption(
            id="opt2",
            name="Aggressive Approach",
            description="Fast but risky",
            expected_value=0.0,
            risk_score=0.0,
            confidence=0.7,
            objectives_scores={"accuracy": 0.75, "speed": 0.8, "efficiency": 0.7},
            scenario_performance={},
            implementation_cost=200.0,
            time_toimplement=0.5,
            prerequisites=[],
            side_effects=["Higher risk", "Faster results"]
        )
    ]
    
    # Make decision
    selected = decision_system.make_decision(options, {"context": "test"})
    print(f"\nSelected option: {selected.name}")
    print(f"Expected value: {selected.expected_value:.3f}")
    print(f"Risk score: {selected.risk_score:.3f}")
    print(f"Confidence: {selected.confidence:.3f}")
    
    # Create plan
    plan = decision_system.create_hierarchical_plan(
        "Improve system performance",
        PlanningHorizon.MEDIUM_TERM,
        {"resources": "limited"}
    )
    print(f"\nCreated plan: {plan.name}")
    print(f"Tasks: {len(plan.tasks)}")
    print(f"Resources: {plan.resources}")
    
    # Get statistics
    stats = decision_system.get_decision_statistics()
    print(f"\nDecision statistics: {stats}")


if __name__ == "__main__":
    test_enhanced_decision_system()