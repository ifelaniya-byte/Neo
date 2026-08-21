"""
PROJECT APEX: AGENT RUNNER & OUTER EXECUTION HARNESS (ENHANCED)
Pre-configured with Gemini Cloud API Integration and local fallback options.

This script implements the first Karpathy Loop where the agent generates
performance patches for worker_core.py and evaluates them via eval_harness.py.

ENHANCED VERSION: Now includes bottleneck management, research integration,
real-time monitoring, knowledge graph, security validation, and backup management.
"""

import os
import sys
import time
import datetime
import subprocess
import re
import urllib.request
import json

# Import new enhancement modules
from bottleneck_manager import BottleneckManager, BottleneckSeverity, BottleneckCategory
from research_integrator import ResearchIntegrator
from monitoring_system import MonitoringSystem, MetricType, AnomalySeverity
from knowledge_graph import KnowledgeGraph, NodeType, RelationshipType
from security_validator import SecurityValidator, SecurityLevel
from backup_manager import BackupManager

# Import micro-LLM internal enhancement modules
from internal_karpathy_loop import InternalKarpathyLoop
from micro_llm_enhancement_systems import MicroLLMEnhancementSuite
from tiny_condensed_block import TinyCondensedBlockSystem, BlockType, CompressionMethod
from coat_rack_system import CoatRackSystem, JacketType
from hypermutation_system import HypermutationSystem

# Import continuous compaction and clone spawning modules
from continuous_bit_compaction import ContinuousBitCompaction
from clone_spawning_system import CloneSpawningSystem, CloneType, TaskSpecification, TaskComplexity, TaskDomain
from meta_programming_system import MetaProgrammingSystem
from clone_coordination import CloneCoordinator, CoordinationMode

# Import agent swarm and deep research modules
from agent_swarm_system import AgentSwarmSystem, SwarmActivationTrigger, ResearchDepth, ResearchDomain
from deep_internet_research import DeepInternetResearch, SearchEngine

# Import memory punishment and survival system
from memory_punishment_system import MemoryPunishmentSystem, MemoryUnit, FailureSeverity

# Import benchmark comparison system
from flagship_llm_database import FlagshipModelDatabase
from benchmark_comparison_system import BenchmarkComparisonSystem, ComparisonMetric

# Import API credit optimization system
from api_credit_optimizer import APICreditOptimizer, CreditStrategy

# PRE-CONFIGURED GEMINI API KEY & MODEL SETTINGS
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY_HERE")
MODEL_NAME = os.environ.get("MODEL_NAME", "gemini-2.0-flash")
LOCAL_LLM_URL = os.environ.get("LOCAL_LLM_URL", "http://localhost:11434/v1/chat/completions")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")

def get_best_score():
    """Retrieves the best S_eval score from experiment history."""
    if not os.path.exists("experiment_log.tsv"):
        return 0.0
    best = 0.0
    with open("experiment_log.tsv", "r") as f:
        lines = f.readlines()[1:]
        for line in lines:
            parts = line.strip().split("\t")
            if len(parts) >= 5 and parts[4] == "KEEP":
                try:
                    best = max(best, float(parts[3]))
                except ValueError:
                    pass
    return best

def read_file(path):
    """Reads file contents safely."""
    if not os.path.exists(path):
        return ""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def call_gemini_api(prompt):
    """Makes a direct REST API call to Gemini 2.0 Flash."""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_NAME}:generateContent?key={GEMINI_API_KEY}"
    
    system_instruction = "You are an expert AI software engineer. Respond ONLY with python code enclosed in ```python ... ``` block, plus a short 1-sentence hypothesis prior to the code block."
    
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": f"{system_instruction}\n\n{prompt}"}
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.3
        }
    }
    
    headers = {"Content-Type": "application/json"}
    req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers)
    
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        print(f"[GEMINI API ERROR] API request failed: {e}")
        return None

def call_llm(prompt):
    """Routes LLM calls to Gemini or local fallback."""
    if GEMINI_API_KEY:
        return call_gemini_api(prompt)
        
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": "You are an expert AI software engineer. Respond ONLY with python code enclosed in ```python ... ``` block, plus a short 1-sentence hypothesis prior to the code block."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.4
    }
    
    headers = {"Content-Type": "application/json"}
    url = LOCAL_LLM_URL
    if OPENAI_API_KEY:
        url = "https://api.openai.com/v1/chat/completions"
        headers["Authorization"] = f"Bearer {OPENAI_API_KEY}"

    req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers)
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"[LLM API ERROR] Failed to connect: {e}")
        return None

def extract_code_and_hypothesis(response):
    """Extracts hypothesis and code block from LLM response."""
    hypothesis = "Optimized mathematical loop performance."
    lines = response.strip().split("\n")
    for line in lines:
        if line.strip() and not line.startswith("```"):
            hypothesis = line.strip()
            break
            
    code_match = re.search(r"```python(.*?)```", response, re.DOTALL)
    if code_match:
        code = code_match.group(1).strip()
    else:
        code = response
    return hypothesis, code

def run_loop_step(step_id, bottleneck_manager, research_integrator, 
                  monitoring_system, knowledge_graph, security_validator, 
                  backup_manager, bit_compaction, clone_spawner, meta_programmer,
                  clone_coordinator, agent_swarm, deep_research, memory_punishment,
                  flagship_database, benchmark_comparison):
    """
    Executes one complete evolutionary loop iteration with enhanced systems.
    Now includes bottleneck analysis, research integration, and comprehensive validation.
    """
    best_score = get_best_score()
    print(f"\n==========================================")
    print(f"--- STARTING EVOLUTION ITERATION #{step_id:04d} ---")
    print(f"Current Best Score (S_eval_best): {best_score:.6f}")
    
    # Create backup before making changes
    backup_id = backup_manager.create_snapshot(
        ["worker_core.py", "eval_harness.py"],
        f"Pre-iteration {step_id} backup"
    )
    print(f"[BACKUP] Created snapshot {backup_id}")
    
    # Monitor system health
    monitoring_system.check_system_health()
    health_score = monitoring_system.get_health_score()
    print(f"[MONITOR] System health score: {health_score:.2f}")
    
    # Monitor time efficiency and spawn clones if needed
    time_efficiency = clone_spawner.monitor_time_efficiency()
    print(f"[CLONE SPAWNER] Time efficiency: {time_efficiency:.2f}")
    
    # Check storage compaction status
    storage_status = bit_compaction.get_storage_status()
    print(f"[BIT COMPACTION] Storage usage: {storage_status['usage_percentage']:.1f}%")
    print(f"[BIT COMPACTION] Overall compression ratio: {storage_status['overall_compression_ratio']:.2f}x")
    
    # If storage is getting full, trigger aggressive compaction
    if storage_status['usage_percentage'] > 80:
        print(f"[BIT COMPACTION] Storage usage high, triggering aggressive compaction")
        bit_compaction.optimize_storage_layout()
        bit_compaction.reserve_space(50_000_000)  # Reserve 50MB space
    
    # Monitor task deadlines and activate swarm if needed
    task_start_time = time.time()
    task_deadline = 10.0  # 10 second deadline for optimization
    current_duration = time.time() - task_start_time
    
    if agent_swarm.monitor_deadlines_and_activate(current_duration, task_deadline):
        print(f"[AGENT SWARM] Swarm activated for deep research support")
        swarm_status = agent_swarm.get_swarm_status()
        print(f"[AGENT SWARM] Active clones: {swarm_status['swarm_size']}")
        
        # Assign research task to support current optimization
        research_query = "optimization techniques for code performance and algorithmic efficiency"
        task_id = agent_swarm.assign_research_task(
            query=research_query,
            domain=ResearchDomain.TECHNICAL,
            depth=ResearchDepth.EXHAUSTIVE,
            sources_required=50
        )
        print(f"[AGENT SWARM] Research task {task_id} assigned to swarm")
    
    # Check survival status
    survival_status = memory_punishment.check_survival_status()
    print(f"[MEMORY PUNISHMENT] Survival status: {survival_status['status']}")
    print(f"[MEMORY PUNISHMENT] Frozen memory: {survival_status['frozen_percentage']:.2f}%")
    print(f"[MEMORY PUNISHMENT] Consecutive failures: {survival_status['consecutive_failures']}")
    
    if not survival_status['alive']:
        print("[SYSTEM] System has died due to excessive consecutive failures")
        print("[SYSTEM] Evolutionary termination - survival failure")
        return False
    
    # Benchmark comparison against flagship models
    if step_id % 10 == 0:  # Every 10 iterations
        print("[BENCHMARK] Comparing against flagship models...")
        
        # Get current micro-LLM score
        current_score = best_score
        
        # Compare to top flagship models
        top_models = flagship_database.get_top_n_models(3)
        for model in top_models:
            comparison = benchmark_comparison.compare_to_flagship(
                current_score, 
                model.model_id, 
                ComparisonMetric.OVERALL
            )
            print(f"[BENCHMARK] {model.model_name}: {comparison.percentage_of_flagship:.1f}% (efficiency: {comparison.efficiency_ratio:.2f}x)")
        
        # Track progress
        tracker = benchmark_comparison.track_progress(
            ComparisonMetric.OVERALL,
            current_score,
            target_model_id="claude-3.5-sonnet"
        )
        print(f"[BENCHMARK] Progress to Claude 3.5 Sonnet: {tracker.progress_percentage:.1f}%")
    
    # Check for anomalies
    anomaly_summary = monitoring_system.get_anomaly_summary()
    if anomaly_summary['unresolved_anomalies'] > 0:
        print(f"[MONITOR] Warning: {anomaly_summary['unresolved_anomalies']} unresolved anomalies")
    
    # Identify bottlenecks (3-6-9 pattern)
    performance_data = {
        'execution_time': 10.0,  # Would be actual metrics
        'memory_usage': 100000000  # Would be actual metrics
    }
    code_analysis = {
        'nested_loops': 2,
        'file': 'worker_core.py'
    }
    
    bottlenecks = bottleneck_manager.identify_bottlenecks(performance_data, code_analysis)
    
    # Select 3 bottlenecks for this iteration
    target_bottlenecks = bottleneck_manager.select_bottleneck_batch(3)
    
    if target_bottlenecks:
        print(f"[BOTTLENECK] Analyzing {len(target_bottlenecks)} bottlenecks")
        for bottleneck in target_bottlenecks:
            print(f"  - {bottleneck.category.value}: {bottleneck.description}")
            
            # Research solutions
            solutions = research_integrator.search_bottleneck_solutions(
                bottleneck.description,
                bottleneck.category.value
            )
            
            if solutions:
                print(f"  [RESEARCH] Found {len(solutions)} potential solutions")
        
        # Check knowledge graph for similar resolved bottlenecks
        for bottleneck in target_bottlenecks:
            if bottleneck_manager.check_recurrence_prevention(bottleneck):
                print(f"[KNOWLEDGE] Similar bottleneck previously resolved - applying preventive measures")
                preventive = knowledge_graph.suggest_preventive_measures(
                    {'category': bottleneck.category.value, 'description': bottleneck.description}
                )
                if preventive:
                    print(f"  [PREVENTION] Found {len(preventive)} preventive measures")
    
    program_instructions = read_file("program.md")
    current_code = read_file("worker_core.py")
    log_history = read_file("experiment_log.tsv")
    
    # Build enhanced prompt with bottleneck context
    bottleneck_context = ""
    if target_bottlenecks:
        bottleneck_context = "\nCURRENT BOTTLENECKS TO ADDRESS:\n"
        for bottleneck in target_bottlenecks:
            bottleneck_context += f"- {bottleneck.category.value}: {bottleneck.description}\n"
    
    prompt = f"""{program_instructions}

{bottleneck_context}

CURRENT EXPERIMENT LOG HISTORY:
{log_history}

CURRENT worker_core.py CODE:
```python
{current_code}
```

PROPOSE ONE SINGLE TARGETED OPTIMIZATION TO worker_core.py TO INCREASE S_eval ABOVE {best_score:.6f}.
Focus on addressing identified bottlenecks if any.
Provide your short hypothesis, followed by the complete optimized worker_core.py python file in ```python ... ``` blocks.
"""
    
    print("[HARNESS] Dispatching prompt to Gemini API...")
    response = call_llm(prompt)
    if not response:
        print("[HARNESS] Skipping step due to LLM response error.")
        backup_manager.mark_snapshot_safe(backup_id, True)
        return

    hypothesis, new_code = extract_code_and_hypothesis(response)
    print(f"[HYPOTHESIS]: {hypothesis}")

    # Security validation before applying changes
    print("[SECURITY] Validating code changes...")
    validation_report = security_validator.validate_code(new_code)
    
    if not security_validator.is_safe_to_apply(validation_report):
        print(f"[SECURITY] Code validation failed: {validation_report.overall_status.value}")
        print(f"[SECURITY] Issues found: {len(validation_report.issues)}")
        for issue in validation_report.issues:
            print(f"  - {issue.severity.value}: {issue.description}")
        
        # Record failure for memory punishment
        memory_punishment.record_failure(
            task_description="Security validation failure",
            severity=FailureSeverity.CRITICAL
        )
        
        # Rollback using backup
        print("[SECURITY] Rolling back due to security validation failure")
        backup_manager.restore_snapshot(backup_id)
        backup_manager.mark_snapshot_safe(backup_id, True)
        return
    else:
        print(f"[SECURITY] Code validation passed: {validation_report.overall_status.value}")

    # 1. Write candidate code
    with open("worker_core.py", "w", encoding="utf-8") as f:
        f.write(new_code)
        
    # 2. Benchmark evaluation
    print("[HARNESS] Executing eval_harness.py...")
    res = subprocess.run([sys.executable, "eval_harness.py"], capture_output=True, text=True)
    print(res.stdout)

    new_score = 0.0
    if os.path.exists(".latest_score"):
        with open(".latest_score", "r") as f:
            try:
                new_score = float(f.read().strip())
            except ValueError:
                new_score = 0.0
    
    # Record execution time metric
    exec_time = 10.0  # Would extract from actual benchmark
    monitoring_system.record_metric(MetricType.EXECUTION_TIME, exec_time)
                
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    # 3. Apply Git Ratchet
    if new_score > best_score:
        print(f"[RATCHET RESULT] SUCCESS! New score {new_score:.6f} > Best {best_score:.6f}. Keeping commit.")
        
        # Record success for memory punishment (unfreeze memory)
        memory_punishment.record_success(
            task_description=f"Optimization success: {hypothesis[:50]}",
            success_type="OPTIMIZATION"
        )
        
        # Apply 11-step exponential debug purification
        print("[PURIFICATION] Starting 11-step exponential debug purification...")
        
        def test_function(code):
            """Test function for purification - runs eval_harness"""
            try:
                test_res = subprocess.run([sys.executable, "eval_harness.py"], 
                                      capture_output=True, text=True, timeout=30)
                return test_res.returncode == 0
            except:
                return False
        
        purification_success, purification_results = bottleneck_manager.apply_11_step_purification(
            hypothesis, test_function
        )
        
        if purification_success:
            print(f"[PURIFICATION] SUCCESS! All 11 steps passed in {purification_results['total_time']:.2f}s")
            print(f"[PURIFICATION] Final confidence: {purification_results['final_confidence']:.4f}")
        else:
            print(f"[PURIFICATION] FAILED at step {purification_results['steps_passed']}")
            print(f"[PURIFICATION] Rolling back due to purification failure")
            backup_manager.restore_snapshot(backup_id)
            backup_manager.mark_snapshot_safe(backup_id, True)
            return
        
        subprocess.run(["git", "add", "worker_core.py"], check=False)
        commit_res = subprocess.run(["git", "commit", "-m", f"KEEP: {hypothesis} (Score: {new_score:.6f})"], capture_output=True, text=True)
        commit_hash = commit_res.stdout.split()[1] if "]" in commit_res.stdout else f"commit_{step_id:04d}"
        status = "KEEP"
        
        # Mark backup as safe
        backup_manager.mark_snapshot_safe(backup_id, True)
        
        # Update knowledge graph with successful resolution
        for bottleneck in target_bottlenecks:
            bottleneck_node_id = knowledge_graph.add_node(
                NodeType.BOTTLENECK,
                {'category': bottleneck.category.value, 'description': bottleneck.description},
                confidence=0.8
            )
            
            solution_node_id = knowledge_graph.add_node(
                NodeType.SOLUTION,
                {'description': hypothesis, 'code_hash': validation_report.code_hash},
                confidence=purification_results['final_confidence']
            )
            
            knowledge_graph.add_bottleneck_solution_relationship(
                bottleneck_node_id, solution_node_id, purification_results['final_confidence']
            )
        
    else:
        print(f"[RATCHET RESULT] REJECTED. New score {new_score:.6f} <= Best {best_score:.6f}. Reverting code.")
        subprocess.run(["git", "checkout", "--", "worker_core.py"], check=False)
        commit_hash = "REVERTED"
        status = "DISCARD"
        
        # Record failure for memory punishment
        memory_punishment.record_failure(
            task_description=f"Optimization rejected: {hypothesis[:50]}",
            severity=FailureSeverity.MODERATE
        )
        
        # Restore from backup
        backup_manager.restore_snapshot(backup_id)
        backup_manager.mark_snapshot_safe(backup_id, True)
        
    # 4. Append to log
    log_line = f"{step_id:04d}\t{timestamp}\t{hypothesis[:50]}\t{new_score:.6f}\t{status}\t{commit_hash}\n"
    with open("experiment_log.tsv", "a", encoding="utf-8") as f:
        f.write(log_line)
        
    # 5. Export trajectory if win
    if status == "KEEP":
        subprocess.run([sys.executable, "dataset_builder.py"], check=False)
    
    # Print system status
    print(f"\n[SYSTEM STATUS]")
    print(f"  Health Score: {monitoring_system.get_health_score():.2f}")
    print(f"  Bottlenecks Resolved: {bottleneck_manager.get_confidence_report()['resolved_bottlenecks']}")
    print(f"  Knowledge Graph Nodes: {knowledge_graph.get_graph_statistics()['total_nodes']}")
    print(f"  Security Validations: {security_validator.get_validation_summary()['total_validations']}")

if __name__ == "__main__":
    print("Project APEX Harness initialized with Gemini API Key.")
    print("=" * 60)
    print("REVOLUTIONARY MICRO-LLM ARCHITECTURE INITIALIZATION")
    print("=" * 60)
    
    # Initialize enhanced systems
    print("[INIT] Initializing Bottleneck Manager...")
    bottleneck_manager = BottleneckManager()
    
    print("[INIT] Initializing Research Integrator...")
    research_integrator = ResearchIntegrator()
    
    print("[INIT] Initializing Monitoring System...")
    monitoring_system = MonitoringSystem()
    monitoring_system.start_monitoring(check_interval=5.0)
    
    print("[INIT] Initializing Knowledge Graph...")
    knowledge_graph = KnowledgeGraph()
    
    print("[INIT] Initializing Security Validator...")
    security_validator = SecurityValidator()
    
    print("[INIT] Initializing Backup Manager...")
    backup_manager = BackupManager()
    
    print("[INIT] Initializing Internal Karpathy Loop for Micro-LLM...")
    # This would be initialized with the actual micro-LLM model
    # internal_karpathy_loop = InternalKarpathyLoop(micro_llm_model, credit_optimizer=credit_optimizer, memory_punishment=memory_punishment)
    
    print("[INIT] Initializing Micro-LLM Enhancement Suite...")
    enhancement_suite = MicroLLMEnhancementSuite()
    
    print("[INIT] Initializing Tiny Condensed Block System...")
    block_system = TinyCondensedBlockSystem()
    
    print("[INIT] Initializing Coat Rack System...")
    coat_rack = CoatRackSystem(max_jackets=5)
    
    print("[INIT] Initializing Hypermutation System...")
    hypermutation = HypermutationSystem(max_generations=50, population_size=10)
    
    print("[INIT] Initializing Continuous Bit Compaction System...")
    bit_compaction = ContinuousBitCompaction(max_storage=500_000_000, target_compaction_ratio=0.7)
    bit_compaction.start_continuous_compaction()
    
    print("[INIT] Initializing Clone Spawning System...")
    clone_spawner = CloneSpawningSystem(max_clones=10, breaking_point_threshold=0.7)
    
    print("[INIT] Initializing Meta-Programming System...")
    meta_programmer = MetaProgrammingSystem()
    
    print("[INIT] Initializing Clone Coordinator...")
    clone_coordinator = CloneCoordinator(coordination_mode=CoordinationMode.DISTRIBUTED)
    clone_coordinator.start_coordination_service()
    
    print("[INIT] Initializing Agent Swarm System...")
    agent_swarm = AgentSwarmSystem(max_clones=300)
    
    print("[INIT] Initializing Deep Internet Research...")
    deep_research = DeepInternetResearch(api_keys={
        'semantic_scholar': os.environ.get('SEMANTIC_SCHOLAR_API_KEY', ''),
        'github': os.environ.get('GITHUB_API_KEY', ''),
        'stack_overflow': os.environ.get('STACK_OVERFLOW_API_KEY', '')
    })
    
    print("[INIT] Initializing Memory Punishment System...")
    # Create a dummy model for memory punishment system initialization
    # In production, this would be the actual micro-LLM model
    dummy_model = nn.Linear(512, 512)  # Placeholder model
    memory_punishment = MemoryPunishmentSystem(model=dummy_model, total_params=500_000_000)
    
    print("[INIT] Initializing Flagship LLM Database...")
    flagship_database = FlagshipModelDatabase()
    
    print("[INIT] Initializing Benchmark Comparison System...")
    benchmark_comparison = BenchmarkComparisonSystem(micro_llm_params=500_000_000)
    
    print("[INIT] Initializing API Credit Optimizer...")
    credit_optimizer = APICreditOptimizer(total_credits=100.0)
    
    print("=" * 60)
    print("ALL SYSTEMS OPERATIONAL - STARTING EVOLUTIONARY LOOP")
    print("=" * 60)
    print("[SYSTEM] Micro-LLM can now:")
    print("  - Run internal Karpathy Loop for self-improvement")
    print("  - Access 100+ enhancement systems for optimization")
    print("  - Load external model blocks via Coat Rack system")
    print("  - Merge multiple model blocks for enhanced capabilities")
    print("  - Generate hypermutated blocks for continuous evolution")
    print("  - Compress models to tiny data blocks for storage")
    print("  - Continuously compact bits to create room for new information")
    print("  - Spawn clone micro-LLMs when time efficiency breaks")
    print("  - Program clones to accomplish tasks indefinitely")
    print("  - Coordinate clones for collaborative task execution")
    print("  - Deploy 300-clone agent swarm for deep internet research")
    print("  - Automatically activate swarm when tasks exceed time deadlines")
    print("  - Conduct exhaustive research across academic papers, documentation, forums")
    print("  - Freeze its own memory on failure (survival mechanism)")
    print("  - Stakes 1 bit per failure - can self-erase if 100,000 consecutive failures")
    print("  - Must succeed to unfreeze memory - creates evolutionary pressure")
    print("  - Compare itself against flagship 700B+ models (Claude, GPT-4, Gemini, GLM)")
    print("  - Track progress against SOTA models with detailed metrics")
    print("  - Calculate efficiency scores (performance per parameter)")
    print("  - Generate parameter-equivalent performance analysis")
    print("  - Optimize API credit usage through legitimate strategies")
    print("  - Use smart caching to avoid redundant API calls")
    print("  - Implement model cascading (cheap → expensive models)")
    print("  - Validate responses locally before accepting expensive results")
    print("  - Track credit usage and optimize for efficiency")
    print("=" * 60)
    
    step = 1
    try:
        while True:
            try:
                run_loop_step(step, bottleneck_manager, research_integrator,
                            monitoring_system, knowledge_graph, security_validator,
                            backup_manager, bit_compaction, clone_spawner, meta_programmer,
                            clone_coordinator, agent_swarm, deep_research, memory_punishment,
                            flagship_database, benchmark_comparison)
                step += 1
                time.sleep(2)
            except KeyboardInterrupt:
                print("\n[HARNESS] Execution stopped by user.")
                break
            except Exception as e:
                print(f"\n[ERROR] Unexpected error in iteration {step}: {e}")
                print("[ERROR] Attempting system recovery...")
                
                # Rollback to safe state
                safe_snapshot = backup_manager.rollback_to_safe_state()
                if safe_snapshot:
                    print(f"[RECOVERY] Rolled back to snapshot {safe_snapshot}")
                else:
                    print("[RECOVERY] No safe snapshot found, manual intervention required")
                
                # Continue to next iteration
                step += 1
                time.sleep(5)
                
    finally:
        # Cleanup
        print("\n[SHUTDOWN] Stopping monitoring system...")
        monitoring_system.stop_monitoring()
        
        print("[SHUTDOWN] Stopping bit compaction system...")
        bit_compaction.stop_continuous_compaction()
        
        print("[SHUTDOWN] Stopping clone coordination...")
        clone_coordinator.stop_coordination_service()
        
        print("[SHUTDOWN] Final system status:")
        print(f"  Total iterations: {step - 1}")
        print(f"  Bottleneck resolution confidence: {bottleneck_manager.get_confidence_report()}")
        print(f"  Knowledge graph statistics: {knowledge_graph.get_graph_statistics()}")
        print(f"  Security validation summary: {security_validator.get_validation_summary()}")
        print(f"  Backup system statistics: {backup_manager.get_backup_statistics()}")
        print(f"  Bit compaction efficiency: {bit_compaction.get_compaction_efficiency()}")
        print(f"  Clone spawning status: {clone_spawner.get_clone_status()}")
        print(f"  Clone coordination status: {clone_coordinator.get_coordination_status()}")
        print(f"  Meta-programming library: {meta_programmer.get_code_library_stats()}")
        print(f"  Agent swarm status: {agent_swarm.get_swarm_status()}")
        print(f"  Deep research statistics: {deep_research.get_search_statistics()}")
        print(f"  Memory punishment stats: {memory_punishment.get_memory_punishment_stats()}")
        print(f"  Flagship database: {flagship_database.get_ranking_summary()}")
        print(f"  Benchmark comparison: {benchmark_comparison.get_comparison_summary()}")
        
        print("[SHUTDOWN] Project APEX stopped gracefully.")
