#!/usr/bin/env python3
"""
🚀 Quick Launch Script for AI Data Analyst

Simple launcher that starts the web interface directly.
"""

import subprocess
import sys
import os
from pathlib import Path

def main():
    """Launch the AI Data Analyst web interface"""
    print("🚀 Starting AI Data Analyst Web Interface...")
    
    # Ensure we're in the right directory
    project_root = Path(__file__).parent.absolute()
    os.chdir(project_root)
    
    # Check for virtual environment
    venv_python = project_root / "venv" / "Scripts" / "python.exe"
    if not venv_python.exists():
        print("❌ Virtual environment not found!")
        print("Please run: python -m venv venv")
        print("Then activate and install requirements")
        sys.exit(1)
    
    # Launch Streamlit app
    try:
        cmd = [
            str(venv_python), 
            "-m", "streamlit", "run", 
            "web_interface/app.py", 
            "--server.port", "8502"
        ]
        
        print("🌐 Opening at: http://localhost:8502")
        subprocess.run(cmd)
        
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
