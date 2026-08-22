"""
PROJECT APEX: AGENT SWARM SYSTEM
Massive parallel research system with 300 clones for deep internet research.
Automatically activates when tasks exceed time deadlines.
"""

import time
import threading
import multiprocessing
import queue
import hashlib
import json
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import asyncio

class SwarmActivationTrigger(Enum):
    """Triggers for swarm activation."""
    TIME_DEADLINE_3S = "TIME_DEADLINE_3S"  # 3 seconds over deadline
    TIME_DEADLINE_6S = "TIME_DEADLINE_6S"  # 6 seconds over deadline
    TIME_DEADLINE_9S = "TIME_DEADLINE_9S"  # 9 seconds over deadline
    TASK_COMPLEXITY = "TASK_COMPLEXITY"
    MANUAL_REQUEST = "MANUAL_REQUEST"
    RESOURCE_AVAILABLE = "RESOURCE_AVAILABLE"

class ResearchDepth(Enum):
    """Depth of research required."""
    SURFACE = "SURFACE"           # Quick overview
    STANDARD = "STANDARD"         # Comprehensive research
    DEEP = "DEEP"                 # In-depth analysis
    EXHAUSTIVE = "EXHAUSTIVE"     # Complete exhaustive research
    ACADEMIC = "ACADEMIC"         # Academic paper level depth

class ResearchDomain(Enum):
    """Domains of research expertise."""
    GENERAL = "GENERAL"
    TECHNICAL = "TECHNICAL"
    SCIENTIFIC = "SCIENTIFIC"
    MEDICAL = "MEDICAL"
    LEGAL = "LEGAL"
    FINANCIAL = "FINANCIAL"
    HISTORICAL = "HISTORICAL"
    PROGRAMMING = "PROGRAMMING"
    DATA_SCIENCE = "DATA_SCIENCE"
    MACHINE_LEARNING = "MACHINE_LEARNING"

@dataclass
class ResearchTask:
    """A research task for the swarm."""
    task_id: str
    research_query: str
    domain: ResearchDomain
    depth: ResearchDepth
    sources_required: int
    priority: int
    deadline: float
    created_at: str
    status: str
    assigned_clones: List[str] = field(default_factory=list)
    results: List[Dict] = field(default_factory=list)
    synthesized_result: Optional[Dict] = None
    
    def to_dict(self):
        return self.__dict__

@dataclass
class SwarmClone:
    """A clone in the research swarm."""
    clone_id: str
    clone_type: str
    specialization: ResearchDomain
    current_task: Optional[ResearchTask]
    task_history: List[ResearchTask]
    research_capabilities: List[str]
    performance_metrics: Dict
    status: str
    last_active: str
    research_count: int
    
    def to_dict(self):
        return self.__dict__

@dataclass
class ResearchResult:
    """Result from a research clone."""
    result_id: str
    clone_id: str
    task_id: str
    source_url: str
    content: str
    relevance_score: float
    confidence: float
    extraction_date: str
    metadata: Dict
    
    def to_dict(self):
        return self.__dict__

class AgentSwarmSystem:
    """
    Massive parallel research system with 300 clones.
    Automatically activates for deep internet research when time deadlines are exceeded.
    """
    
    def __init__(self, max_clones=300, activation_triggers=None):
        self.max_clones = max_clones
        self.activation_triggers = activation_triggers or [
            SwarmActivationTrigger.TIME_DEADLINE_3S,
            SwarmActivationTrigger.TIME_DEADLINE_6S,
            SwarmActivationTrigger.TIME_DEADLINE_9S
        ]
        
        self.swarm_clones = {}
        self.active_research_tasks = {}
        self.completed_research_tasks = {}
        self.research_queue = queue.PriorityQueue()
        self.result_aggregator = ResultAggregator()
        self.deadline_monitor = DeadlineMonitor()
        
        self.swarm_active = False
        self.swarm_size = 0
        self.activation_count = 0
        self.research_stats = {
            'total_tasks': 0,
            'completed_tasks': 0,
            'total_sources_analyzed': 0,
            'avg_research_time': 0.0,
            'activation_history': []
        }
        
        # Initialize specialized clone pools
        self.domain_specialists = self._initialize_domain_specialists()
        
    def _initialize_domain_specialists(self) -> Dict[ResearchDomain, int]:
        """Initialize distribution of clones across research domains."""
        total_domains = len(ResearchDomain)
        clones_per_domain = self.max_clones // total_domains
        
        distribution = {}
        for domain in ResearchDomain:
            distribution[domain] = clones_per_domain
        
        # Add remaining clones to general research
        remaining = self.max_clones % total_domains
        distribution[ResearchDomain.GENERAL] += remaining
        
        return distribution
    
    def monitor_deadlines_and_activate(self, current_task_duration: float, 
                                     task_deadline: float) -> bool:
        """
        Monitor task deadlines and activate swarm if exceeded.
        Returns True if swarm was activated.
        """
        time_over_deadline = current_task_duration - task_deadline
        
        # Check activation triggers
        if time_over_deadline >= 9.0:
            trigger = SwarmActivationTrigger.TIME_DEADLINE_9S
            activation_strength = 1.0  # Maximum strength
        elif time_over_deadline >= 6.0:
            trigger = SwarmActivationTrigger.TIME_DEADLINE_6S
            activation_strength = 0.7
        elif time_over_deadline >= 3.0:
            trigger = SwarmActivationTrigger.TIME_DEADLINE_3S
            activation_strength = 0.4
        else:
            return False  # No activation needed
        
        print(f"[SWARM] Task deadline exceeded by {time_over_deadline:.1f}s")
        print(f"[SWARM] Activation trigger: {trigger.value}")
        print(f"[SWARM] Activation strength: {activation_strength:.1f}")
        
        # Activate swarm
        swarm_size = self.calculate_swarm_size(activation_strength)
        self.activate_research_swarm(swarm_size, trigger)
        
        return True
    
    def calculate_swarm_size(self, activation_strength: float) -> int:
        """Calculate swarm size based on activation strength."""
        if activation_strength >= 1.0:
            return self.max_clones  # Full swarm (300 clones)
        elif activation_strength >= 0.7:
            return int(self.max_clones * 0.7)  # 210 clones
        elif activation_strength >= 0.4:
            return int(self.max_clones * 0.4)  # 120 clones
        else:
            return int(self.max_clones * 0.2)  # 60 clones
    
    def activate_research_swarm(self, swarm_size: int, trigger: SwarmActivationTrigger):
        """Activate the research swarm with specified size."""
        if self.swarm_active:
            print(f"[SWARM] Swarm already active, scaling to {swarm_size} clones")
            self.scale_swarm(swarm_size)
            return
        
        print(f"[SWARM] Activating research swarm with {swarm_size} clones")
        print(f"[SWARM] Activation trigger: {trigger.value}")
        
        # Spawn research clones
        for domain, target_count in self.domain_specialists.items():
            clones_for_domain = min(target_count, swarm_size // len(self.domain_specialists))
            
            for i in range(clones_for_domain):
                clone_id = self.spawn_research_clone(domain, i)
                if clone_id:
                    self.swarm_size += 1
        
        self.swarm_active = True
        self.activation_count += 1
        
        # Record activation
        self.research_stats['activation_history'].append({
            'timestamp': time.strftime("%Y-%m-%d %H:%M:%S"),
            'trigger': trigger.value,
            'swarm_size': self.swarm_size,
            'active_clones': list(self.swarm_clones.keys())
        })
        
        print(f"[SWARM] Swarm activated: {self.swarm_size} clones ready")
    
    def spawn_research_clone(self, domain: ResearchDomain, index: int) -> Optional[str]:
        """Spawn a specialized research clone."""
        clone_id = f"research_{domain.value}_{index}_{hashlib.md5(str(time.time()).encode()).hexdigest()[:8]}"
        
        clone = SwarmClone(
            clone_id=clone_id,
            clone_type="RESEARCH_SPECIALIST",
            specialization=domain,
            current_task=None,
            task_history=[],
            research_capabilities=self.get_domain_capabilities(domain),
            performance_metrics={},
            status="SPAWNING",
            last_active=time.strftime("%Y-%m-%d %H:%M:%S"),
            research_count=0
        )
        
        self.swarm_clones[clone_id] = clone
        clone.status = "READY"
        
        return clone_id
    
    def get_domain_capabilities(self, domain: ResearchDomain) -> List[str]:
        """Get research capabilities for a domain."""
        capabilities = {
            ResearchDomain.GENERAL: [
                "web_search", "information_extraction", "content_analysis",
                "summarization", "fact_checking", "source_validation"
            ],
            ResearchDomain.TECHNICAL: [
                "technical_documentation", "api_research", "code_analysis",
                "troubleshooting_guides", "best_practices", "version_tracking"
            ],
            ResearchDomain.SCIENTIFIC: [
                "paper_search", "citation_analysis", "experimental_data",
                "methodology_review", "peer_review_analysis", "theory_exploration"
            ],
            ResearchDomain.MEDICAL: [
                "medical_literature", "clinical_studies", "drug_information",
                "symptom_analysis", "treatment_protocols", "medical_guidelines"
            ],
            ResearchDomain.LEGAL: [
                "legal_precedent", "regulation_search", "case_law_analysis",
                "compliance_checking", "patent_research", "contract_analysis"
            ],
            ResearchDomain.FINANCIAL: [
                "market_data", "financial_reports", "trend_analysis",
                "risk_assessment", "investment_research", "economic_indicators"
            ],
            ResearchDomain.HISTORICAL: [
                "historical_records", "archive_search", "timeline_analysis",
                "context_reconstruction", "primary_sources", "historical_trends"
            ],
            ResearchDomain.PROGRAMMING: [
                "code_repositories", "documentation_search", "stack_overflow",
                "github_analysis", "programming_tutorials", "debugging_guides"
            ],
            ResearchDomain.DATA_SCIENCE: [
                "dataset_search", "methodology_papers", "tool_evaluation",
                "statistical_analysis", "visualization_techniques", "data_cleaning"
            ],
            ResearchDomain.MACHINE_LEARNING: [
                "arxiv_papers", "model_architectures", "training_techniques",
                "benchmark_results", "framework_documentation", "research_trends"
            ]
        }
        
        return capabilities.get(domain, [])
    
    def assign_research_task(self, query: str, domain: ResearchDomain,
                            depth: ResearchDepth, sources_required: int = 10,
                            deadline: float = 60.0) -> str:
        """Assign a research task to the swarm."""
        task_id = f"research_{hashlib.md5(f"{query}{time.time()}".encode()).hexdigest()[:12]}"
        
        task = ResearchTask(
            task_id=task_id,
            research_query=query,
            domain=domain,
            depth=depth,
            sources_required=sources_required,
            priority=1,
            deadline=deadline,
            created_at=time.strftime("%Y-%m-%d %H:%M:%S"),
            status="PENDING"
        )
        
        self.active_research_tasks[task_id] = task
        self.research_queue.put((priority, task_id))
        
        # Distribute task to specialized clones
        self.distribute_research_task(task)
        
        return task_id
    
    def distribute_research_task(self, task: ResearchTask):
        """Distribute research task to appropriate clones."""
        # Find clones specializing in the task domain
        domain_clones = [
            clone_id for clone_id, clone in self.swarm_clones.items()
            if clone.specialization == task.domain and clone.status == "READY"
        ]
        
        # Assign task to available clones
        clones_per_task = min(len(domain_clones), task.sources_required)
        clones_per_task = max(1, clones_per_task)  # At least 1 clone
        
        for i in range(min(clones_per_task, len(domain_clones))):
            clone_id = domain_clones[i]
            clone = self.swarm_clones[clone_id]
            
            clone.current_task = task
            clone.status = "WORKING"
            clone.last_active = time.strftime("%Y-%m-%d %H:%M:%S")
            task.assigned_clones.append(clone_id)
            
            # Start research
            self.execute_research(clone_id, task)
    
    def execute_research(self, clone_id: str, task: ResearchTask):
        """Execute research task in a clone."""
        # In production, this would dispatch to actual clone process
        # For now, simulate research execution
        
        research_thread = threading.Thread(
            target=self._simulate_research_execution,
            args=(clone_id, task),
            daemon=True
        )
        research_thread.start()
    
    def _simulate_research_execution(self, clone_id: str, task: ResearchTask):
        """Simulate research execution (placeholder for actual implementation)."""
        clone = self.swarm_clones[clone_id]
        
        # Simulate research time based on depth
        depth_multiplier = {
            ResearchDepth.SURFACE: 1.0,
            ResearchDepth.STANDARD: 2.0,
            ResearchDepth.DEEP: 5.0,
            ResearchDepth.EXHAUSTIVE: 10.0,
            ResearchDepth.ACADEMIC: 15.0
        }
        
        research_time = depth_multiplier.get(task.depth, 2.0)
        time.sleep(research_time)  # Simulate research
        
        # Generate simulated research results
        sources_analyzed = min(task.sources_required, 10)
        
        for i in range(sources_analyzed):
            result = ResearchResult(
                result_id=f"result_{clone_id}_{i}",
                clone_id=clone_id,
                task_id=task.task_id,
                source_url=f"https://example.com/source_{i}",
                content=f"Research content for source {i} about {task.research_query}",
                relevance_score=0.8 + (i * 0.02),
                confidence=0.85,
                extraction_date=time.strftime("%Y-%m-%d %H:%M:%S"),
                metadata={'source_type': 'web', 'domain': task.domain.value}
            )
            
            task.results.append(result)
            clone.research_count += 1
        
        # Update clone status
        clone.current_task = None
        clone.status = "READY"
        clone.last_active = time.strftime("%Y-%m-%d %H:%M:%S")
        
        # Check if task is complete
        if len(task.results) >= task.sources_required:
            self.complete_research_task(task.task_id)
    
    def complete_research_task(self, task_id: str):
        """Mark research task as complete and synthesize results."""
        if task_id not in self.active_research_tasks:
            return
        
        task = self.active_research_tasks[task_id]
        task.status = "COMPLETED"
        
        # Synthesize results
        task.synthesized_result = self.result_aggregator.synthesize_results(task.results)
        
        # Move to completed tasks
        self.completed_research_tasks[task_id] = task
        del self.active_research_tasks[task_id]
        
        # Update stats
        self.research_stats['completed_tasks'] += 1
        self.research_stats['total_sources_analyzed'] += len(task.results)
        
        print(f"[SWARM] Research task {task_id} completed with {len(task.results)} sources")
    
    def scale_swarm(self, target_size: int):
        """Scale swarm up or down to target size."""
        current_size = len(self.swarm_clones)
        
        if target_size > current_size:
            # Scale up
            clones_to_add = target_size - current_size
            self.scale_up_swarm(clones_to_add)
        elif target_size < current_size:
            # Scale down
            clones_to_remove = current_size - target_size
            self.scale_down_swarm(clones_to_remove)
    
    def scale_up_swarm(self, clones_to_add: int):
        """Scale up swarm by adding more clones."""
        print(f"[SWARM] Scaling up by {clones_to_add} clones")
        
        # Add clones proportionally across domains
        for domain, base_count in self.domain_specialists.items():
            additional = int((clones_to_add / len(self.domain_specialists)) * (base_count / self.max_clones))
            
            for i in range(additional):
                if len(self.swarm_clones) < self.max_clones:
                    clone_id = self.spawn_research_clone(domain, i)
                    if clone_id:
                        self.swarm_size += 1
    
    def scale_down_swarm(self, clones_to_remove: int):
        """Scale down swarm by removing idle clones."""
        print(f"[SWARM] Scaling down by {clones_to_remove} clones")
        
        # Remove idle clones first
        idle_clones = [
            clone_id for clone_id, clone in self.swarm_clones.items()
            if clone.status == "READY" and not clone.current_task
        ]
        
        clones_to_remove = min(clones_to_remove, len(idle_clones))
        
        for i in range(clones_to_remove):
            if idle_clones:
                clone_id = idle_clones.pop()
                del self.swarm_clones[clone_id]
                self.swarm_size -= 1
    
    def deactivate_swarm(self):
        """Deactivate the research swarm."""
        print(f"[SWARM] Deactivating research swarm")
        
        # Complete current tasks
        for task_id, task in list(self.active_research_tasks.items()):
            if task.status != "COMPLETED":
                self.complete_research_task(task_id)
        
        # Remove all clones
        self.swarm_clones.clear()
        self.swarm_size = 0
        self.swarm_active = False
        
        print(f"[SWARM] Swarm deactivated")
    
    def get_swarm_status(self) -> Dict:
        """Get current status of the research swarm."""
        domain_distribution = {}
        for clone in self.swarm_clones.values():
            domain = clone.specialization.value
            domain_distribution[domain] = domain_distribution.get(domain, 0) + 1
        
        return {
            'swarm_active': self.swarm_active,
            'swarm_size': self.swarm_size,
            'max_clones': self.max_clones,
            'domain_distribution': domain_distribution,
            'active_tasks': len(self.active_research_tasks),
            'completed_tasks': len(self.completed_research_tasks),
            'activation_count': self.activation_count,
            'research_stats': self.research_stats
        }

class DeadlineMonitor:
    """Monitors task deadlines and triggers swarm activation."""
    
    def __init__(self):
        self.task_deadlines = {}
        self.monitoring_active = False
        self.monitor_thread = None
    
    def set_deadline(self, task_id: str, deadline: float):
        """Set deadline for a task."""
        self.task_deadlines[task_id] = {
            'deadline': deadline,
            'start_time': time.time(),
            'task_id': task_id
        }
    
    def check_deadline(self, task_id: str) -> Tuple[bool, float]:
        """Check if task has exceeded deadline."""
        if task_id not in self.task_deadlines:
            return False, 0.0
        
        task_info = self.task_deadlines[task_id]
        elapsed = time.time() - task_info['start_time']
        time_over = elapsed - task_info['deadline']
        
        return time_over > 0, time_over
    
    def start_monitoring(self, callback: Callable):
        """Start deadline monitoring with callback."""
        self.monitoring_active = True
        self.monitor_thread = threading.Thread(
            target=self._monitoring_loop,
            args=(callback,),
            daemon=True
        )
        self.monitor_thread.start()
    
    def _monitoring_loop(self, callback: Callable):
        """Monitoring loop for deadlines."""
        while self.monitoring_active:
            for task_id, task_info in list(self.task_deadlines.items()):
                exceeded, time_over = self.check_deadline(task_id)
                if exceeded:
                    callback(task_id, time_over)
            
            time.sleep(0.1)  # Check every 100ms
    
    def stop_monitoring(self):
        """Stop deadline monitoring."""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5.0)

class ResultAggregator:
    """Aggregates and synthesizes research results from multiple clones."""
    
    def __init__(self):
        self.aggregation_strategies = {
            'consensus': self.consensus_aggregation,
            'voting': self.voting_aggregation,
            'weighted': self.weighted_aggregation,
            'hierarchical': self.hierarchical_aggregation
        }
    
    def synthesize_results(self, results: List[ResearchResult]) -> Dict:
        """Synthesize multiple research results into coherent output."""
        if not results:
            return {'error': 'No results to synthesize'}
        
        # Sort by relevance
        sorted_results = sorted(results, key=lambda r: r.relevance_score, reverse=True)
        
        # Extract key information
        synthesized = {
            'query': results[0].task_id if results else '',
            'total_sources': len(results),
            'avg_relevance': sum(r.relevance_score for r in results) / len(results),
            'avg_confidence': sum(r.confidence for r in results) / len(results),
            'top_sources': [
                {
                    'url': r.source_url,
                    'relevance': r.relevance_score,
                    'confidence': r.confidence,
                    'summary': r.content[:200]  # First 200 chars
                }
                for r in sorted_results[:5]
            ],
            'key_findings': self.extract_key_findings(sorted_results),
            'consensus_points': self.find_consensus_points(sorted_results),
            'conflicting_information': self.find_conflicts(sorted_results),
            'recommended_actions': self.generate_recommendations(sorted_results)
        }
        
        return synthesized
    
    def extract_key_findings(self, results: List[ResearchResult]) -> List[str]:
        """Extract key findings from research results."""
        # Simple extraction - in production would use NLP
        findings = []
        for result in results[:10]:  # Top 10 results
            findings.append(f"Finding from {result.source_url}: {result.content[:100]}")
        return findings
    
    def find_consensus_points(self, results: List[ResearchResult]) -> List[str]:
        """Find points of consensus across sources."""
        # Simple consensus detection
        return ["Consensus point detected across multiple sources"]
  # Placeholder
    
    def find_conflicts(self, results: List[ResearchResult]) -> List[str]:
        """Find conflicting information across sources."""
        return ["No major conflicts detected"]  # Placeholder
    
    def generate_recommendations(self, results: List[ResearchResult]) -> List[str]:
        """Generate recommendations based on research."""
        return [
            "Recommendation based on research synthesis",
            "Additional research suggested for specific areas"
        ]  # Placeholder
    
    def consensus_aggregation(self, results: List[Dict]) -> Dict:
        """Aggregate using consensus approach."""
        return {}
    
    def voting_aggregation(self, results: List[Dict]) -> Dict:
        """Aggregate using voting approach."""
        return {}
    
    def weighted_aggregation(self, results: List[Dict]) -> Dict:
        """Aggregate using weighted approach."""
        return {}
    
    def hierarchical_aggregation(self, results: List[Dict]) -> Dict:
        """Aggregate using hierarchical approach."""
        return {}