"""
NEO AUTONOMOUS REBOOT

Reboots Neo's system with autonomous coordinator for fully automatic operation.
"""

import sys
import os
from pathlib import Path

# Add project directory to path
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))

def reboot_neo_autonomous():
    """Reboot Neo with autonomous coordinator."""
    print("\n" + "=" * 80)
    print("NEO AUTONOMOUS REBOOT")
    print("=" * 80)
    print()
    print("🔄 Rebooting Neo with autonomous coordinator...")
    print("🚀 Neo will automatically:")
    print("   • Read all learning documents")
    print("   • Take all tests")
    print("   • Create and pass self-test")
    print("   • Graduate")
    print("   • Start autonomous operation")
    print()
    print("⏳ Rebooting...")
    print()
    
    # Import and run autonomous coordinator
    try:
        from autonomous_neo_coordinator import AutonomousNeoCoordinator
        
        coordinator = AutonomousNeoCoordinator()
        coordinator.run_autonomous_sequence()
        
    except ImportError as e:
        print(f"❌ Error: Could not import autonomous coordinator: {e}")
        print("   Please ensure autonomous_neo_coordinator.py is in the main directory")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error during autonomous reboot: {e}")
        sys.exit(1)

if __name__ == "__main__":
    reboot_neo_autonomous()
