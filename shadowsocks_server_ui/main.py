#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Shadowsocks Server UI - Main Entry Point
Web-based interface using Flask
"""
import sys
import os

# Add the package directory to sys.path for PyInstaller compatibility
if getattr(sys, 'frozen', False):
    # Running as compiled executable
    base_path = sys._MEIPASS
else:
    # Running as script
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if base_path not in sys.path:
        sys.path.insert(0, base_path)

# First import compatibility fix (must be before importing shadowsocks)
try:
    from shadowsocks_server_ui import compat  # noqa: F401
except ImportError:
    # Fallback for relative import when running as module
    from . import compat  # noqa: F401

try:
    from shadowsocks_server_ui.web.app import WebApp
except ImportError:
    # Fallback for relative import when running as module
    from .web.app import WebApp


def main():
    """Main function"""
    print("=" * 60)
    print("Shadowsocks Server UI")
    print("=" * 60)
    print("\nStarting web interface...")
    print("Open your browser and navigate to: http://127.0.0.1:8888")
    print("\nPress Ctrl+C to stop the server")
    print("=" * 60)
    
    # Create and run web app
    # Use 0.0.0.0 to allow access from any interface (including localhost and 127.0.0.1)
    # Use port 8888 to avoid conflict with macOS AirPlay Receiver (port 5000)
    web_app = WebApp(host='0.0.0.0', port=8888)
    
    try:
        web_app.run(debug=False)
    except KeyboardInterrupt:
        print("\n\nShutting down...")
        web_app.stop()
        sys.exit(0)


if __name__ == "__main__":
    main()
