#!/usr/bin/env python3
"""
🚀 AI Data Analyst - Main Launcher

Comprehensive launcher with multiple options for running the AI Data Analyst system.
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    """Main launcher with menu options"""
    print("🤖 AI Data Analyst - Universal Data Analysis Platform")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not Path("src/main.py").exists():
        print("❌ Error: Please run this script from the AI_Data_Analyst root directory")
        sys.exit(1)
    
    print("\nAvailable launch options:")
    print("1. 🌐 Web Interface (Streamlit) - Main Application")
    print("2. 🧪 Run Test Suite - Comprehensive System Tests")
    print("3. 🔧 Database Enhancements - Optimize Database")
    print("4. 📊 Create Sample Datasets - Generate Test Data")
    print("5. ❌ Exit")
    
    while True:
        try:
            choice = input("\nSelect option (1-5): ").strip()
            
            if choice == "1":
                launch_web_interface()
            elif choice == "2":
                run_test_suite()
            elif choice == "3":
                enhance_database()
            elif choice == "4":
                create_sample_datasets()
            elif choice == "5":
                print("👋 Goodbye!")
                break
            else:
                print("❌ Invalid choice. Please select 1-5.")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break

def launch_web_interface():
    """Launch the Streamlit web interface"""
    print("\n🌐 Launching AI Data Analyst Web Interface...")
    
    # Check for virtual environment
    venv_python = Path("venv/Scripts/python.exe")
    if not venv_python.exists():
        print("❌ Virtual environment not found!")
        print("Please run: python -m venv venv")
        print("Then activate and install requirements")
        return
    
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
        print("\n👋 Web interface closed")
    except Exception as e:
        print(f"❌ Error launching web interface: {e}")

def run_test_suite():
    """Run the comprehensive test suite"""
    print("\n🧪 Running Comprehensive Test Suite...")
    
    try:
        subprocess.run([sys.executable, "test_unified.py"], check=True)
        print("✅ All tests completed!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Tests failed with exit code {e.returncode}")
    except Exception as e:
        print(f"❌ Error running tests: {e}")

def enhance_database():
    """Run database enhancement utilities"""
    print("\n🔧 Running Database Enhancements...")
    
    # Check for virtual environment
    venv_python = Path("venv/Scripts/python.exe")
    if not venv_python.exists():
        print("❌ Virtual environment not found!")
        return
    
    try:
        subprocess.run([str(venv_python), "utilities/enhance_database.py"], check=True)
        print("✅ Database enhancements completed!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Database enhancement failed with exit code {e.returncode}")
    except Exception as e:
        print(f"❌ Error enhancing database: {e}")

def create_sample_datasets():
    """Create sample datasets for testing"""
    print("\n📊 Creating Sample Datasets...")
    
    # Check for virtual environment
    venv_python = Path("venv/Scripts/python.exe")
    if not venv_python.exists():
        print("❌ Virtual environment not found!")
        return
    
    try:
        subprocess.run([str(venv_python), "utilities/create_sample_datasets.py"], check=True)
        print("✅ Sample datasets created in sample_datasets/ folder!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Sample dataset creation failed with exit code {e.returncode}")
    except Exception as e:
        print(f"❌ Error creating sample datasets: {e}")

if __name__ == "__main__":
    main()
