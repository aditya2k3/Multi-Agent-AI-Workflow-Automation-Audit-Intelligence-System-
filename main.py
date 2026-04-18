#!/usr/bin/env python3
"""
AI Audit Automation System - Main Entry Point

This script provides a unified entry point for running the complete system:
- Start API server and dashboard
- Initialize all components
- Handle configuration and setup
"""

import os
import sys
import argparse
import subprocess
import threading
import time
from pathlib import Path

def setup_environment():
    """Setup the environment and check dependencies"""
    
    print("🔍 AI Audit Automation System - Starting up...")
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Error: Python 3.8+ is required")
        sys.exit(1)
    
    # Create necessary directories
    directories = ["logs", "reports", "uploads", "models"]
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Directory ready: {directory}")
    
    # Check if data exists
    if not os.path.exists("data/transactions.csv"):
        print("📊 Generating sample data...")
        try:
            subprocess.run([sys.executable, "data/generate_synthetic_data.py"], 
                         cwd=".", check=True)
            print("✅ Sample data generated")
        except subprocess.CalledProcessError:
            print("⚠️  Warning: Could not generate sample data")
    
    print("✅ Environment setup complete")

def start_api_server():
    """Start the FastAPI server"""
    
    print("🚀 Starting API server on http://localhost:8000")
    try:
        subprocess.run([sys.executable, "api/main.py"], check=True)
    except KeyboardInterrupt:
        print("\n🛑 API server stopped")
    except subprocess.CalledProcessError as e:
        print(f"❌ API server failed: {e}")

def start_dashboard():
    """Start the Streamlit dashboard"""
    
    print("📊 Starting dashboard on http://localhost:8501")
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            "frontend/dashboard.py",
            "--server.port=8501",
            "--server.address=0.0.0.0",
            "--server.headless=true"
        ], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Dashboard stopped")
    except subprocess.CalledProcessError as e:
        print(f"❌ Dashboard failed: {e}")

def run_full_system():
    """Run both API server and dashboard"""
    
    print("🔄 Starting complete system...")
    
    # Start API server in background
    api_thread = threading.Thread(target=start_api_server, daemon=True)
    api_thread.start()
    
    # Wait a moment for API to start
    time.sleep(3)
    
    # Start dashboard in main thread
    try:
        start_dashboard()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down system...")
        sys.exit(0)

def run_tests():
    """Run the test suite"""
    
    print("🧪 Running tests...")
    try:
        # Check if pytest is available
        subprocess.run([sys.executable, "-m", "pytest", "--version"], 
                     check=True, capture_output=True)
        
        # Run tests
        subprocess.run([sys.executable, "-m", "pytest", "-v"], check=True)
        print("✅ All tests passed")
        
    except subprocess.CalledProcessError:
        print("❌ Tests failed or pytest not installed")
        print("💡 Install with: pip install pytest pytest-asyncio")

def show_system_info():
    """Show system information and status"""
    
    print("📋 System Information")
    print("=" * 50)
    
    # Python version
    print(f"Python Version: {sys.version}")
    
    # Check dependencies
    dependencies = [
        "fastapi", "streamlit", "pandas", "numpy", 
        "langgraph", "transformers", "plotly"
    ]
    
    print("\n📦 Dependencies:")
    for dep in dependencies:
        try:
            __import__(dep)
            print(f"✅ {dep}")
        except ImportError:
            print(f"❌ {dep} (missing)")
    
    # Check data files
    print("\n📊 Data Files:")
    data_files = [
        "data/transactions.csv",
        "data/invoices.csv", 
        "data/data_summary.csv"
    ]
    
    for file_path in data_files:
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            print(f"✅ {file_path} ({size:,} bytes)")
        else:
            print(f"❌ {file_path} (missing)")
    
    # Check directories
    print("\n📁 Directories:")
    directories = ["logs", "reports", "uploads", "models"]
    for directory in directories:
        if os.path.exists(directory):
            print(f"✅ {directory}")
        else:
            print(f"❌ {directory} (missing)")
    
    print("\n🔗 URLs:")
    print("📡 API Documentation: http://localhost:8000/docs")
    print("📊 Dashboard: http://localhost:8501")
    print("🏥 Health Check: http://localhost:8000/health")

def main():
    """Main entry point"""
    
    parser = argparse.ArgumentParser(
        description="AI Audit Automation System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                    # Run complete system
  python main.py --api-only         # Run API server only
  python main.py --dashboard-only    # Run dashboard only
  python main.py --test             # Run tests
  python main.py --info             # Show system info
        """
    )
    
    parser.add_argument("--api-only", action="store_true", 
                      help="Run only the API server")
    parser.add_argument("--dashboard-only", action="store_true", 
                      help="Run only the dashboard")
    parser.add_argument("--test", action="store_true", 
                      help="Run the test suite")
    parser.add_argument("--info", action="store_true", 
                      help="Show system information")
    parser.add_argument("--setup", action="store_true", 
                      help="Setup environment only")
    
    args = parser.parse_args()
    
    # Setup environment
    setup_environment()
    
    if args.info:
        show_system_info()
    elif args.setup:
        print("✅ Setup complete")
    elif args.test:
        run_tests()
    elif args.api_only:
        start_api_server()
    elif args.dashboard_only:
        start_dashboard()
    else:
        run_full_system()

if __name__ == "__main__":
    main()
