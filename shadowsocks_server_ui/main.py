#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Shadowsocks Server UI - Main Entry Point
Web-based interface using Flask
"""
# First import compatibility fix (must be before importing shadowsocks)
from . import compat  # noqa: F401
import sys
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
    # 使用 0.0.0.0 允许从任何接口访问（包括 localhost 和 127.0.0.1）
    # 使用 8888 端口避免与 macOS AirPlay Receiver 冲突（5000 端口）
    web_app = WebApp(host='0.0.0.0', port=8888)
    
    try:
        web_app.run(debug=False)
    except KeyboardInterrupt:
        print("\n\nShutting down...")
        web_app.stop()
        sys.exit(0)


if __name__ == "__main__":
    main()
