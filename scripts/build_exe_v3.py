#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Build script V3 - Package Shadowsocks Server UI into exe file
Usage: python build_exe_v3.py

Supports:
- Windows: Package as .exe
- macOS: Package as .app (requires parameter modification)
- GitHub Actions: Automatic cloud packaging
"""

import PyInstaller.__main__
import os
import sys
import platform

# Set Windows console encoding to UTF-8
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except:
        pass

def build():
    """Build executable"""
    print("=" * 60)
    print("Building Shadowsocks Server UI...")
    print(f"Platform: {platform.system()} {platform.release()}")
    print("=" * 60)
    
    # Check dependencies
    try:
        import shadowsocks
        print("[OK] shadowsocks library installed")
    except ImportError:
        print("[ERROR] shadowsocks library not installed, please run: pip install shadowsocks")
        sys.exit(1)
    
    # Get main file path (from script directory back to project root)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    main_file = os.path.join(project_root, 'shadowsocks_server_ui', 'main.py')
    if not os.path.exists(main_file):
        print(f"[ERROR] Main file not found: {main_file}")
        print(f"[DEBUG] Project root: {project_root}")
        print(f"[DEBUG] Script dir: {script_dir}")
        print(f"[DEBUG] Current working directory: {os.getcwd()}")
        sys.exit(1)
    
    print(f"\nMain file: {main_file}")
    
    # Select build parameters based on platform
    is_windows = platform.system() == 'Windows'
    is_macos = platform.system() == 'Darwin'
    
    # Check if spec file exists
    spec_file = os.path.join(script_dir, 'ShadowsocksServerV3.spec')
    if os.path.exists(spec_file) and is_windows:
        print(f"\nUsing spec file: {spec_file}")
        args = [
            spec_file,
            '--clean',
            '--noconfirm',
        ]
    else:
        # Build PyInstaller arguments
        print("\nUsing command line arguments...")
        args = [
            main_file,
            '--name=ShadowsocksServerV3',  # Output name
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
            '--hidden-import=shadowsocks_server_ui',
            '--hidden-import=shadowsocks_server_ui.server',
            '--hidden-import=shadowsocks_server_ui.tcprelay_ext',
            '--hidden-import=shadowsocks_server_ui.config',
            '--hidden-import=shadowsocks_server_ui.config.manager',
            '--hidden-import=shadowsocks_server_ui.config.defaults',
            '--hidden-import=shadowsocks_server_ui.stats',
            '--hidden-import=shadowsocks_server_ui.stats.collector',
            '--hidden-import=shadowsocks_server_ui.web',
            '--hidden-import=shadowsocks_server_ui.web.app',
            '--hidden-import=flask',
            '--hidden-import=jinja2',
            '--collect-all=shadowsocks',    # Collect all shadowsocks related files
            '--collect-all=flask',          # Collect all Flask related files
            f'--paths={project_root}',      # Add project root to path
        ]
        
        # Windows specific parameters
        if is_windows:
            args.append('--onefile')  # Windows: package as single .exe file
        
        # macOS specific parameters
        if is_macos:
            args.append('--osx-bundle-identifier=com.shadowsocks.server.v3')
    
    try:
        print("\nBuilding, please wait...")
        # Change to project root directory for build
        original_cwd = os.getcwd()
        os.chdir(project_root)
        try:
            PyInstaller.__main__.run(args)
        finally:
            os.chdir(original_cwd)
        
        # Determine output file path based on platform
        dist_dir = os.path.join(project_root, 'dist')
        if is_windows:
            output_path = os.path.join(dist_dir, 'ShadowsocksServerV3.exe')
            output_name = "exe file"
            platform_name = "Windows"
        elif is_macos:
            output_path = os.path.join(dist_dir, 'ShadowsocksServerV3.app')
            output_name = "application"
            platform_name = "macOS"
        else:
            output_path = os.path.join(dist_dir, 'ShadowsocksServerV3')
            output_name = "executable"
            platform_name = platform.system()
        
        if os.path.exists(output_path):
            if is_macos:
                # macOS .app is a directory, need to calculate total size
                def get_size(path):
                    total = 0
                    for dirpath, dirnames, filenames in os.walk(path):
                        for f in filenames:
                            fp = os.path.join(dirpath, f)
                            total += os.path.getsize(fp)
                    return total
                file_size = get_size(output_path) / (1024 * 1024)  # MB
            else:
                file_size = os.path.getsize(output_path) / (1024 * 1024)  # MB
            
            print("\n" + "=" * 60)
            print("[SUCCESS] Build completed!")
            print("=" * 60)
            print(f"{output_name} location: {output_path}")
            print(f"File size: {file_size:.2f} MB")
            print("\nNotes:")
            if is_windows:
                print("1. The exe file can run on any Windows system without Python installation")
                print("2. First run may be blocked by antivirus, add to whitelist")
            elif is_macos:
                print("1. The .app file can run on macOS systems")
                print("2. First run may require right-click -> Open (bypass Gatekeeper)")
            print("3. Based on shadowsocks official library's event loop architecture")
            print("4. Fixed continuous download disconnection issues")
            print("5. Supports long downloads without idle timeout disconnection")
            print("6. Supports Python 3.13+")
        else:
            print(f"\n[ERROR] Build failed: {output_name} not found")
            print(f"[DEBUG] Expected path: {output_path}")
            print(f"[DEBUG] Project root: {project_root}")
            print(f"[DEBUG] Dist directory exists: {os.path.exists(dist_dir)}")
            if os.path.exists(dist_dir):
                print(f"[DEBUG] Files in dist: {os.listdir(dist_dir)}")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n[ERROR] Build failed: {str(e)}")
        print("\nPlease ensure the following dependencies are installed:")
        print("pip install -r requirements.txt pyinstaller")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    build()

