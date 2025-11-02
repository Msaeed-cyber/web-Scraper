#!/usr/bin/env python3
"""
Setup script for AI Product Trust & Sentiment Analyzer
"""

import os
import sys
import subprocess
import platform

def run_command(command):
    """Run a command and return success status"""
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✓ {command}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {command}")
        print(f"Error: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8 or higher is required")
        print(f"Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    print(f"✓ Python {version.major}.{version.minor}.{version.micro}")
    return True

def install_dependencies():
    """Install required Python packages"""
    print("\n📦 Installing Python dependencies...")
    return run_command("pip install -r requirements.txt")

def download_nltk_data():
    """Download required NLTK data"""
    print("\n📚 Downloading NLTK data...")
    try:
        import nltk
        nltk.download('punkt', quiet=True)
        nltk.download('stopwords', quiet=True)
        print("✓ NLTK data downloaded")
        return True
    except ImportError:
        print("⚠️  NLTK not available, skipping data download")
        return True
    except Exception as e:
        print(f"⚠️  Error downloading NLTK data: {e}")
        return True

def create_directories():
    """Create necessary directories"""
    print("\n📁 Creating directories...")
    directories = ['models', 'logs', 'static/css', 'static/js', 'templates']
    
    for directory in directories:
        try:
            os.makedirs(directory, exist_ok=True)
            print(f"✓ Created directory: {directory}")
        except Exception as e:
            print(f"✗ Failed to create directory {directory}: {e}")
            return False
    return True

def check_chrome():
    """Check if Chrome is installed"""
    print("\n🌐 Checking Chrome installation...")
    
    system = platform.system().lower()
    chrome_paths = {
        'windows': [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
        ],
        'darwin': [
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        ],
        'linux': [
            "/usr/bin/google-chrome",
            "/usr/bin/chromium-browser",
            "/usr/bin/chromium"
        ]
    }
    
    paths = chrome_paths.get(system, [])
    
    for path in paths:
        if os.path.exists(path):
            print(f"✓ Chrome found at: {path}")
            return True
    
    print("⚠️  Chrome not found. Please install Google Chrome for web scraping functionality.")
    print("   Download from: https://www.google.com/chrome/")
    return True

def create_env_file():
    """Create .env file if it doesn't exist"""
    print("\n⚙️  Setting up environment file...")
    
    if os.path.exists('.env'):
        print("✓ .env file already exists")
        return True
    
    env_content = """# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=your-secret-key-change-this-in-production

# Application Settings
APP_HOST=0.0.0.0
APP_PORT=5000

# Web Scraping Settings
SCRAPING_DELAY=1
MAX_REVIEWS=10
USER_AGENT_ROTATION=True

# Machine Learning Settings
MODEL_PATH=models/
SENTIMENT_MODEL_FILE=sentiment_model.pkl
VECTORIZER_FILE=tfidf_vectorizer.pkl

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/app.log
"""
    
    try:
        with open('.env', 'w') as f:
            f.write(env_content)
        print("✓ Created .env file")
        return True
    except Exception as e:
        print(f"✗ Failed to create .env file: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 AI Product Trust & Sentiment Analyzer Setup")
    print("=" * 50)
    
    success = True
    
    # Check Python version
    if not check_python_version():
        success = False
    
    # Create directories
    if not create_directories():
        success = False
    
    # Check Chrome
    if not check_chrome():
        success = False
    
    # Install dependencies
    if not install_dependencies():
        success = False
    
    # Download NLTK data
    if not download_nltk_data():
        success = False
    
    # Create .env file
    if not create_env_file():
        success = False
    
    print("\n" + "=" * 50)
    
    if success:
        print("🎉 Setup completed successfully!")
        print("\n📋 Next steps:")
        print("1. Run: python app.py")
        print("2. Open: http://localhost:5000")
        print("3. Enter a product URL to analyze")
        print("\n💡 Tip: Start with Amazon or Daraz product links for best results")
    else:
        print("❌ Setup completed with errors")
        print("Please check the error messages above and fix them before running the application")
    
    return success

if __name__ == "__main__":
    main()
