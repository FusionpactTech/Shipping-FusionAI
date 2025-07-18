#!/usr/bin/env python3
"""
Setup script for Vessel Maintenance AI System
Handles installation, configuration, and initial setup
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def print_banner():
    """Print application banner"""
    print("""
🌊 ========================================== 🌊
    VESSEL MAINTENANCE AI SYSTEM - SETUP
🌊 ========================================== 🌊

AI-powered document processing for maritime operations
Automatically classifies maintenance records, sensor alerts,
and incident reports for rapid response and risk mitigation.

""")

def check_python_version():
    """Check if Python version is compatible"""
    print("🐍 Checking Python version...")
    
    major, minor = sys.version_info[:2]
    if major < 3 or (major == 3 and minor < 8):
        print("❌ Error: Python 3.8 or higher is required")
        print(f"   Current version: {major}.{minor}")
        sys.exit(1)
    
    print(f"✅ Python {major}.{minor} is compatible")

def install_dependencies():
    """Install required Python packages"""
    print("\n📦 Installing Python dependencies...")
    
    try:
        subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ], check=True, capture_output=True)
        print("✅ Dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        print("   Please run: pip install -r requirements.txt")
        return False
    
    return True

def setup_spacy_model():
    """Download spaCy language model"""
    print("\n🧠 Setting up NLP language model...")
    
    try:
        subprocess.run([
            sys.executable, "-m", "spacy", "download", "en_core_web_sm"
        ], check=True, capture_output=True)
        print("✅ spaCy English model downloaded")
    except subprocess.CalledProcessError:
        print("⚠️  Warning: spaCy model download failed")
        print("   The system will use basic NLP processing")
        print("   To install manually: python -m spacy download en_core_web_sm")

def create_directories():
    """Create necessary directories"""
    print("\n📁 Creating application directories...")
    
    directories = ["data", "logs", "static"]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Created directory: {directory}")

def setup_database():
    """Initialize the database"""
    print("\n🗄️  Initializing database...")
    
    try:
        from src.database import DatabaseManager
        db_manager = DatabaseManager()
        print("✅ Database initialized successfully")
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        return False
    
    return True

def test_installation():
    """Test the installation"""
    print("\n🧪 Testing installation...")
    
    try:
        # Test imports
        from src.ai_processor import VesselMaintenanceAI
        from src.models import ProcessingRequest
        from src.database import DatabaseManager
        
        # Test AI processor initialization
        ai_processor = VesselMaintenanceAI()
        print("✅ AI processor initialized")
        
        # Test database connection
        db_manager = DatabaseManager()
        print("✅ Database connection successful")
        
        print("✅ Installation test completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Installation test failed: {e}")
        return False

def create_startup_script():
    """Create startup script for the application"""
    print("\n📝 Creating startup script...")
    
    script_content = """#!/bin/bash
# Vessel Maintenance AI System - Startup Script

echo "🚢 Starting Vessel Maintenance AI System..."

# Check if virtual environment should be activated
if [ -d "venv" ]; then
    echo "🔧 Activating virtual environment..."
    source venv/bin/activate
fi

# Start the application
echo "🚀 Launching application on http://localhost:8000"
python app.py
"""
    
    with open("start.sh", "w") as f:
        f.write(script_content)
    
    # Make script executable on Unix systems
    if platform.system() != "Windows":
        os.chmod("start.sh", 0o755)
    
    print("✅ Created start.sh script")

def create_sample_config():
    """Create sample configuration file"""
    print("\n⚙️  Creating sample configuration...")
    
    config_content = """# Vessel Maintenance AI System Configuration

# Database settings
DATABASE_PATH=data/vessel_maintenance.db

# Server settings
HOST=0.0.0.0
PORT=8000

# Logging settings
LOG_LEVEL=INFO
LOG_FILE=logs/application.log

# AI Processing settings
MAX_TEXT_LENGTH=10000
CONFIDENCE_THRESHOLD=0.3

# Cache settings
ANALYTICS_CACHE_MINUTES=30
"""
    
    with open(".env.example", "w") as f:
        f.write(config_content)
    
    print("✅ Created .env.example configuration file")

def print_next_steps():
    """Print next steps for the user"""
    print("""
🎉 =======================================
   INSTALLATION COMPLETED SUCCESSFULLY!
🎉 =======================================

🚀 NEXT STEPS:

1. Start the application:
   ./start.sh
   OR
   python app.py

2. Open your browser to:
   http://localhost:8000

3. Load sample data (optional):
   python sample_data.py

4. Generate real-time demo alerts:
   python sample_data.py --realtime

📚 DOCUMENTATION:
   - Read README.md for detailed usage instructions
   - Check logs/ directory for application logs
   - Modify .env.example for custom configuration

🔧 SUPPORT:
   - Create issues on GitHub for bug reports
   - Review troubleshooting section in README.md

⚡ QUICK TEST:
   Try pasting this text in the web interface:
   "Engine room fire alarm activated. Emergency shutdown initiated."

Happy maritime AI processing! 🌊⚓
""")

def main():
    """Main setup function"""
    print_banner()
    
    # Check requirements
    check_python_version()
    
    # Confirm installation
    response = input("📋 Proceed with installation? (y/N): ").lower().strip()
    if response not in ['y', 'yes']:
        print("❌ Installation cancelled")
        sys.exit(0)
    
    # Perform installation steps
    steps = [
        ("Installing dependencies", install_dependencies),
        ("Creating directories", create_directories),
        ("Setting up database", setup_database),
        ("Testing installation", test_installation),
        ("Creating startup script", create_startup_script),
        ("Creating sample config", create_sample_config),
    ]
    
    for step_name, step_func in steps:
        print(f"\n🔄 {step_name}...")
        if not step_func():
            print(f"❌ Setup failed at: {step_name}")
            sys.exit(1)
    
    # Optional spaCy model (non-critical)
    setup_spacy_model()
    
    # Show completion message
    print_next_steps()

if __name__ == "__main__":
    main()