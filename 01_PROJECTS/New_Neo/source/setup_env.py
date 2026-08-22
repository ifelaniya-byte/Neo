"""
PROJECT APEX: SYSTEM BOOTSTRAPPER
Initializes local Git repo and verifies system dependencies.
"""

import os
import subprocess
import sys

def initialize_apex_system():
    """Bootstraps the Project APEX environment with Git and dependencies."""
    print("=" * 50)
    print("      PROJECT APEX: SYSTEM BOOTSTRAPPER          ")
    print("=" * 50)

    # Initialize Git repository
    if not os.path.exists(".git"):
        print("[SETUP] Initializing local Git repository...")
        subprocess.run(["git", "init"], check=True)
        subprocess.run(["git", "config", "user.name", "APEX Autonomous Agent"], check=True)
        subprocess.run(["git", "config", "user.email", "apex-agent@local.internal"], check=True)
    else:
        print("[SETUP] Git repository already initialized.")
    
    # Verify/install required packages
    required_packages = ["psutil"]
    for pkg in required_packages:
        try:
            __import__(pkg)
            print(f"[SETUP] Dependency '{pkg}' verified.")
        except ImportError:
            print(f"[SETUP] Installing missing dependency '{pkg}'...")
            subprocess.run([sys.executable, "-m", "pip", "install", pkg], check=True)
        
    # Initialize experiment log if needed
    if not os.path.exists("experiment_log.tsv"):
        print("[SETUP] Seeding experiment_log.tsv...")
        with open("experiment_log.tsv", "w") as f:
            f.write("Run_ID\tTimestamp\tHypothesis\tS_eval\tResult\tCommit_Hash\n0000\t2026-08-05 18:00\tInitial Baseline\t0.500000\tKEEP\tbase000\n")
        
    # Initial Git commit
    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(["git", "commit", "-m", "APEX System Initial Setup"], check=False)

    print("\n[SUCCESS] Environment bootstrapped!")
    print("To start autonomous Gemini execution loop, run:")
    print("  python agent_runner.py")
    print("=" * 50)

if __name__ == "__main__":
    initialize_apex_system()