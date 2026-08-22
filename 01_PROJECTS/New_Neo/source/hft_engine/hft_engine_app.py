# -*- coding: utf-8 -*-
"""
HFT Engine Windows Application Wrapper
This provides a Windows executable interface for the HFT Engine
"""
import subprocess
import sys
import os

def main():
    """Main entry point for the Windows application"""
    # Get the directory where this exe is located
    if getattr(sys, 'frozen', False):
        # Running as compiled exe
        app_dir = os.path.dirname(sys.executable)
    else:
        # Running as script
        app_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Start the actual HFT engine
    script_path = os.path.join(app_dir, "start_hft.bat")
    
    if os.path.exists(script_path):
        try:
            subprocess.call(script_path, shell=True)
        except Exception as e:
            print(f"Error starting HFT Engine: {e}")
            input("Press Enter to exit...")
    else:
        print(f"Error: Could not find {script_path}")
        print("Please ensure you're running this from the HFT Engine directory")
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()