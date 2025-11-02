#!/usr/bin/env python3
"""
Simple startup script for AI Product Trust & Sentiment Analyzer
"""

import os
import sys
import webbrowser
from threading import Timer

def open_browser():
    """Open browser after a short delay"""
    webbrowser.open('http://localhost:5000')

def main():
    """Main startup function"""
    print("=" * 60)
    print("AI Product Trust & Sentiment Analyzer")
    print("=" * 60)
    print("Starting the application...")
    print("Please wait while the system initializes...")
    print()
    
    # Open browser after 3 seconds
    Timer(3.0, open_browser).start()
    
    # Import and run the Flask app
    try:
        from app import app
        print("Application ready!")
        print("Opening browser at: http://localhost:5000")
        print("Press Ctrl+C to stop the server")
        print("=" * 60)
        
        # Run the app
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=False,
            use_reloader=False,
            threaded=True
        )
        
    except KeyboardInterrupt:
        print("\n\nShutting down server...")
        print("Thank you for using AI Product Trust & Sentiment Analyzer!")
    except Exception as e:
        print(f"Error starting application: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
