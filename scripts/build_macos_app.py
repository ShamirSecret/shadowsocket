#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
macOS application build script - Package Shadowsocks Server UI into macOS .app
Usage: python build_macos_app.py
"""

import PyInstaller.__main__
import os
import sys

def build():
    """Package as macOS .app"""
    print("=" * 60)
    print("Building Shadowsocks Server UI (macOS)...")
    print("=" * 60)
    
    # Check dependencies
    try:
        import shadowsocks
        print("[OK] shadowsocks library installed")
    except ImportError:
        print("[ERROR] shadowsocks library not installed, please run: pip install shadowsocks")
        sys.exit(1)
    
    # Check Flask (required for web UI)
    try:
        import flask
        print("[OK] Flask library installed")
    except ImportError:
        print("[ERROR] Flask library not installed, please run: pip install flask")
        sys.exit(1)
    
    # Get main file path (from script directory back to project root)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    main_file = os.path.join(project_root, 'shadowsocks_server_ui', 'main.py')
    if not os.path.exists(main_file):
        print(f"[ERROR] Main file not found: {main_file}")
        sys.exit(1)
    
    print(f"\nMain file: {main_file}")
    print("Using command line arguments...")
    
    # Build PyInstaller arguments (macOS application)
    args = [
        main_file,
        '--name=ShadowsocksServerV3',  # Generated app name
        '--console',                    # Show console window (for web server logs)
        '--clean',                      # Clean temporary files
        '--noconfirm',                  # Don't ask for overwrite
        '--hidden-import=shadowsocks',  # Ensure shadowsocks library is included
        '--hidden-import=shadowsocks.encrypt',
        '--hidden-import=shadowsocks.eventloop',
        '--hidden-import=shadowsocks.tcprelay',
        '--hidden-import=shadowsocks.asyncdns',
        '--hidden-import=shadowsocks.common',
        '--hidden-import=shadowsocks.crypto',
        '--hidden-import=shadowsocks.crypto.openssl',
        '--hidden-import=shadowsocks.crypto.sodium',
        '--hidden-import=shadowsocks.crypto.rc4_md5',
        '--hidden-import=shadowsocks_server_ui.web',
        '--hidden-import=shadowsocks_server_ui.web.app',
        '--hidden-import=flask',
        '--hidden-import=jinja2',
        '--collect-all=shadowsocks',    # Collect all shadowsocks related files
        '--collect-all=flask',          # Collect all Flask related files
            f'--paths={project_root}',      # Add project root directory to path
        '--osx-bundle-identifier=com.shadowsocks.server.v3',  # Bundle ID
    ]
    
    try:
        print("\nBuilding, please wait...")
        PyInstaller.__main__.run(args)
        
        dist_dir = os.path.join(project_root, 'dist')
        app_path = os.path.join(dist_dir, 'ShadowsocksServerV3.app')
        if os.path.exists(app_path):
            # Calculate app size
            def get_size(path):
                total = 0
                for dirpath, dirnames, filenames in os.walk(path):
                    for f in filenames:
                        fp = os.path.join(dirpath, f)
                        total += os.path.getsize(fp)
                return total
            
            app_size = get_size(app_path) / (1024 * 1024)  # MB
            print("\n" + "=" * 60)
            print("[SUCCESS] Build completed!")
            print("=" * 60)
            print(f"macOS application location: {app_path}")
            print(f"Application size: {app_size:.2f} MB")
            print("\nNotes:")
            print("1. The built .app file can run on macOS systems")
            print("2. First run may require right-click -> Open (bypass Gatekeeper)")
            print("3. To build Windows .exe, run build_exe_v3.py on Windows system")
            print("4. V3 version based on shadowsocks official library's event loop architecture")
            print("5. Fixed continuous download disconnection issues")
        else:
            print("\n[ERROR] Build failed: Generated .app file not found")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n[ERROR] Build failed: {str(e)}")
        print("\nPlease ensure the following dependencies are installed:")
        print("pip install pyinstaller shadowsocks")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    build()

