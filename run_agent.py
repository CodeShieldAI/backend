#!/usr/bin/env python3
"""
Run script for the Complete Filecoin GitHub Protection Agent
This script properly sets up the Python path and runs the main application
"""
import os
import sys

# Add the current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

def main():
    """Main entry point"""
    try:
        # Import and run the main application
        from github_protection_agent.main import main as agent_main
        agent_main()
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("\n💡 Troubleshooting:")
        print("   1. Ensure you're in the correct directory")
        print("   2. Check that all required files are present")
        print("   3. Verify Python dependencies are installed")
        print("   4. Run: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()