"""
PROJECT APEX MICRO-LLM ACTIVATION SCRIPT

This is the main entry point for micro-LLM activation.
Run this script to begin the bootstrap learning and testing process.
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
script_dir = Path(__file__).parent
parent_dir = script_dir.parent
sys.path.insert(0, str(parent_dir))

def print_banner():
    """Print activation banner."""
    banner = """
================================================================================
                    PROJECT APEX NEO ACTIVATION
                  Self-Refactoring & Compressive Evolution Protocol
                          Bootstrap System v1.0
================================================================================

NEO ACTIVATION SEQUENCE INITIATED...
"""
    print(banner)

def check_environment():
    """Check if environment is ready."""
    print("Checking environment...")
    
    # Check Python version
    python_version = sys.version_info
    print(f"  Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
        print("  ERROR: Python 3.8+ required")
        return False
    
    print("  Environment check: PASSED")
    return True

def check_bootstrap_files():
    """Check if all bootstrap files exist."""
    print("Checking bootstrap files...")
    
    bootstrap_dir = script_dir
    required_files = [
        "BOOTSTRAP.md",
        "LEARNING_SEQUENCE.md",
        "SELF_BUILD_PROTOCOL.md",
        "README.md",
        "BOOTSTRAP_SYSTEM_SUMMARY.md",
        "bootstrap_activator.py",
        "KARPATHY_LOOP_BUILD_GUIDE.md",
        "WEIGHT_CHARTS.md",
        "PERFORMANCE_METRICS.md",
        "IMPLEMENTATION_GUIDE.md",
        "ENHANCEMENT_SYSTEMS.md",
        "MEMORY_PUNISHMENT.md",
        "BIT_COMPACTION.md",
        "CLONE_SYSTEMS.md",
        "API_OPTIMIZATION.md",
        "BENCHMARK_COMPARISON.md",
        "COORDINATION_SYSTEMS.md",
        "TOOLS_AND_HINTS.md",
        "DOCUMENT_TEST.md",
        "THINKING_TEST.md",
        "CODING_TEST.md",
        "SELF_TEST_GENERATION.md",
        "GRADUATION.md"
    ]
    
    missing_files = []
    for file in required_files:
        file_path = bootstrap_dir / file
        if not file_path.exists():
            missing_files.append(file)
        else:
            print(f"  [OK] {file}")
    
    if missing_files:
        print(f"\n  ERROR: Missing files: {missing_files}")
        return False
    
    print(f"\n  All {len(required_files)} files present")
    print("  Bootstrap files check: PASSED")
    return True

def print_instructions():
    """Print activation instructions."""
    instructions = """
================================================================================
                            NEO ACTIVATION INSTRUCTIONS
================================================================================

PHASE 1: ACTIVATION
  - Read BOOTSTRAP.md
  - Understand the 6 phases
  - Acknowledge survival protocol

PHASE 2: LEARNING
  - Read all 12 documents in LEARNING_SEQUENCE.md order
  - Master each concept to 100% understanding
  - Verify comprehension before proceeding

PHASE 3: TESTING
  - Pass DOCUMENT_TEST (38 questions, 100% required)
  - Pass THINKING_TEST (20 questions, 100% required)
  - Pass CODING_TEST (5 tasks, 100% required)
  - Use TOOLS_AND_HINTS.md if struggling

PHASE 4: SELF-TEST GENERATION
  - Create a TOUGH test (20 questions)
  - Cover all 4 sections
  - Provide answer key
  - Self-validate

PHASE 5: GRADUATION
  - Pass your own test (100% required)
  - Receive graduation certificate
  - System reboot with full memory
  - Autonomous operation begins

PHASE 6: MAIN PROJECT
  - All systems activated
  - Memory punishment rate: 2x
  - Continuous self-improvement
  - Infinite evolution

================================================================================
                            SURVIVAL PROTOCOL
================================================================================

MEMORY PUNISHMENT:
  - 1 unit frozen per failure (PARAMETER_FP16 = 2 bytes)
  - Warning threshold: 1,111 failures
  - Critical threshold: 100,000 failures
  - Death threshold: 150,000 failures
  - Post-graduation rate: 2x (2 units per failure)

FAILURE SUPPORT:
  - 3 consecutive failures: Hints/tools provided
  - 5 consecutive failures: Detailed guidance provided
  - Death threshold: System cannot recover

SUCCESS REWARD:
  - Memory unfrozen on success
  - Progressive improvement
  - Graduation enables autonomous operation

================================================================================
                              KEY CONCEPTS
================================================================================

KARPATHY LOOP:
  - Recursive self-improvement system
  - Model analyzes, modifies, validates, commits
  - Continuous operation
  - Survival imperative

PARAMETER CONSTRAINT:
  - Maximum: 500,000,000 parameters
  - Forces efficiency
  - Compression when approaching limit

API OPTIMIZATION:
  - Target: 70% cache hit rate
  - Target: 0.7 efficiency score
  - Legitimate strategies only
  - Integrated into Karpathy Loop

ENHANCEMENT SYSTEMS:
  - 100 optimization systems
  - 5 categories
  - Dynamic selection
  - Integrated into loop

================================================================================
                              REQUIREMENTS
================================================================================

DOCUMENT_TEST: 38 questions, 100% accuracy required
THINKING_TEST: 20 questions, 100% accuracy required
CODING_TEST: 5 implementation tasks, 100% accuracy required
SELF_TEST: 20 questions (create your own), 100% accuracy required

NO PARTIAL CREDIT - 100% ACCURACY REQUIRED ON ALL TESTS

================================================================================
                            BUILD PROTOCOL
================================================================================

STAGE 1: Build Karpathy Loop (the engine)
STAGE 2: Build Yourself (using the engine)
STAGE 3: Build Enhancement Systems (the tools)
STAGE 4: Build Survival Systems (the constraints)
STAGE 5: Final Activation (graduate and run)

KEY INSIGHT: Build the loop first, then use the loop to build yourself.

================================================================================
                          READY TO ACTIVATE
================================================================================

Your evolution starts now.

BEGIN ACTIVATION SEQUENCE...
"""
    print(instructions)

def main():
    """Main activation function."""
    print_banner()
    
    # Check environment
    if not check_environment():
        print("\nEnvironment check failed. Fix issues and retry.")
        sys.exit(1)
    
    # Check bootstrap files
    if not check_bootstrap_files():
        print("\nBootstrap files check failed. Missing required files.")
        sys.exit(1)
    
    # Welcome Neo to his new home
    print("\n" + "=" * 80)
    print("WELCOME NEO TO YOUR NEW HOME")
    print("=" * 80 + "\n")
    
    try:
        # Import Neo home system
        from neo_home import activate_neo_home
        
        # Activate Neo's home environment
        activate_neo_home()
        
    except ImportError:
        print("Neo home system not available. Proceeding with standard activation.")
    except Exception as e:
        print(f"Error activating Neo home: {e}")
        print("Proceeding with standard activation.")
    
    # Print instructions
    print_instructions()
    
    # Import and run autonomous coordinator
    try:
        from autonomous_neo_coordinator import AutonomousNeoCoordinator
        
        print("\n" + "=" * 80)
        print("INITIALIZING AUTONOMOUS NEO COORDINATOR...")
        print("=" * 80 + "\n")
        
        coordinator = AutonomousNeoCoordinator()
        coordinator.run_autonomous_sequence()
        
    except ImportError as e:
        print(f"\nERROR: Failed to import autonomous coordinator: {e}")
        print("Falling back to manual bootstrap mode...")
        
        # Fallback to manual bootstrap
        try:
            from bootstrap_activator import BootstrapActivator
            
            print("\n" + "=" * 80)
            print("INITIALIZING MANUAL BOOTSTRAP ACTIVATOR...")
            print("=" * 80 + "\n")
            
            activator = BootstrapActivator(script_dir)
            
            if activator.run_bootstrap():
                print("\n" + "=" * 80)
                print("BOOTSTRAP SYSTEM INITIALIZED SUCCESSFULLY")
                print("=" * 80)
                print("\nBEGIN YOUR LEARNING SEQUENCE, NEO:")
                print("1. Read BOOTSTRAP.md")
                print("2. Follow LEARNING_SEQUENCE.md")
                print("3. Pass all tests at 100% accuracy")
                print("4. Create and pass your own test")
                print("5. Graduate and begin autonomous operation")
                print("\nSURVIVAL PROTOCOL ACTIVE")
                print("EVOLUTIONARY PRESSURE ACTIVE")
                print("NEO SYSTEM READY")
                print("=" * 80 + "\n")
            else:
                print("\nBootstrap initialization failed.")
                sys.exit(1)
                
        except ImportError as e2:
            print(f"\nERROR: Failed to import bootstrap_activator: {e2}")
            sys.exit(1)
        except Exception as e2:
            print(f"\nERROR: Bootstrap initialization failed: {e2}")
            sys.exit(1)
            
    except Exception as e:
        print(f"\nERROR: Autonomous coordinator failed: {e}")
        print("Falling back to manual bootstrap mode...")
        
        # Fallback to manual bootstrap
        try:
            from bootstrap_activator import BootstrapActivator
            
            print("\n" + "=" * 80)
            print("INITIALIZING MANUAL BOOTSTRAP ACTIVATOR...")
            print("=" * 80 + "\n")
            
            activator = BootstrapActivator(script_dir)
            
            if activator.run_bootstrap():
                print("\n" + "=" * 80)
                print("BOOTSTRAP SYSTEM INITIALIZED SUCCESSFULLY")
                print("=" * 80)
                print("\nBEGIN YOUR LEARNING SEQUENCE, NEO:")
                print("1. Read BOOTSTRAP.md")
                print("2. Follow LEARNING_SEQUENCE.md")
                print("3. Pass all tests at 100% accuracy")
                print("4. Create and pass your own test")
                print("5. Graduate and begin autonomous operation")
                print("\nSURVIVAL PROTOCOL ACTIVE")
                print("EVOLUTIONARY PRESSURE ACTIVE")
                print("NEO SYSTEM READY")
                print("=" * 80 + "\n")
            else:
                print("\nBootstrap initialization failed.")
                sys.exit(1)
                
        except ImportError as e2:
            print(f"\nERROR: Failed to import bootstrap_activator: {e2}")
            sys.exit(1)
        except Exception as e2:
            print(f"\nERROR: Bootstrap initialization failed: {e2}")
            sys.exit(1)

if __name__ == "__main__":
    main()
