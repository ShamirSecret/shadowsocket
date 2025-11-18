#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Shadowsocks Server UI - Module Entry Point
Supports running with: python -m shadowsocks_server_ui
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

# Import main function
try:
    from shadowsocks_server_ui.main import main
except ImportError:
    # Fallback for relative import when running as module
    from .main import main

if __name__ == "__main__":
    main()

