#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MacOS 应用打包脚本 - 将 Shadowsocks V2 Refactored 打包成 macOS .app 应用
使用方法: python build_macos_app.py
"""

import PyInstaller.__main__
import os
import sys

def build():
    """打包成 macOS .app"""
    print("=" * 60)
    print("开始打包 Shadowsocks V2 Refactored (macOS)...")
    print("=" * 60)
    
    # 检查依赖
    try:
        import shadowsocks
        print("[OK] shadowsocks 库已安装")
    except ImportError:
        print("[ERROR] shadowsocks 库未安装，请先运行: pip install shadowsocks")
        sys.exit(1)
    
    # 检查 tkinter（macOS 上可能不可用）
    try:
        import tkinter
        print("[OK] tkinter 可用")
    except ImportError:
        print("[WARNING] tkinter 不可用，GUI 功能可能无法使用")
        print("提示：macOS 上可能需要安装 Python 的 tkinter 支持")
    
    # 获取主文件路径
    main_file = os.path.join('shadowsocks_v2_refactored', 'main.py')
    if not os.path.exists(main_file):
        print(f"[ERROR] 找不到主文件: {main_file}")
        sys.exit(1)
    
    print(f"\n主文件: {main_file}")
    print("使用命令行参数打包...")
    
    # 构建 PyInstaller 参数（macOS 应用）
    args = [
        main_file,
        '--name=ShadowsocksServerV3',  # 生成的 app 名称
        '--windowed',                   # 无控制台窗口（GUI 应用）
        '--clean',                      # 清理临时文件
        '--noconfirm',                  # 不询问覆盖
        '--hidden-import=shadowsocks',  # 确保包含 shadowsocks 库
        '--hidden-import=shadowsocks.encrypt',
        '--hidden-import=shadowsocks.eventloop',
        '--hidden-import=shadowsocks.tcprelay',
        '--hidden-import=shadowsocks.asyncdns',
        '--hidden-import=shadowsocks.common',
        '--hidden-import=shadowsocks.crypto',
        '--hidden-import=shadowsocks.crypto.openssl',
        '--hidden-import=shadowsocks.crypto.sodium',
        '--hidden-import=shadowsocks.crypto.rc4_md5',
        '--hidden-import=tkinter',
        '--hidden-import=tkinter.ttk',
        '--hidden-import=tkinter.scrolledtext',
        '--collect-all=shadowsocks',    # 收集所有 shadowsocks 相关文件
        '--paths=.',                    # 添加当前目录到路径
        '--osx-bundle-identifier=com.shadowsocks.server.v3',  # Bundle ID
    ]
    
    try:
        print("\n正在打包，请稍候...")
        PyInstaller.__main__.run(args)
        
        app_path = os.path.join('dist', 'ShadowsocksServerV3.app')
        if os.path.exists(app_path):
            # 计算 app 大小
            def get_size(path):
                total = 0
                for dirpath, dirnames, filenames in os.walk(path):
                    for f in filenames:
                        fp = os.path.join(dirpath, f)
                        total += os.path.getsize(fp)
                return total
            
            app_size = get_size(app_path) / (1024 * 1024)  # MB
            print("\n" + "=" * 60)
            print("[SUCCESS] 打包完成！")
            print("=" * 60)
            print(f"macOS 应用位置: {app_path}")
            print(f"应用大小: {app_size:.2f} MB")
            print("\n提示：")
            print("1. 打包后的 .app 文件可以在 macOS 系统上运行")
            print("2. 首次运行可能需要右键点击 -> 打开（绕过 Gatekeeper）")
            print("3. 如需打包 Windows .exe，请在 Windows 系统上运行 build_exe_v3.py")
            print("4. V3 版本基于 shadowsocks 官方库的事件循环架构")
            print("5. 修复了连续下载断开的问题")
        else:
            print("\n[ERROR] 打包失败：未找到生成的 .app 文件")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n[ERROR] 打包失败: {str(e)}")
        print("\n请确保已安装以下依赖：")
        print("pip install pyinstaller shadowsocks")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    build()

