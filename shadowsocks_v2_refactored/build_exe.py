#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
打包脚本 - 将 Shadowsocks V2 Refactored 打包成 exe 文件
使用方法: python -m shadowsocks_v2_refactored.build_exe
"""

import PyInstaller.__main__
import os
import sys

def build():
    """打包成 exe"""
    print("=" * 60)
    print("开始打包 Shadowsocks V2 Refactored...")
    print("=" * 60)
    
    # 检查依赖
    try:
        import shadowsocks
        print("[OK] shadowsocks 库已安装")
    except ImportError:
        print("[ERROR] shadowsocks 库未安装，请先运行: pip install shadowsocks")
        sys.exit(1)
    
    # 获取主文件路径
    main_file = os.path.join(os.path.dirname(__file__), 'main.py')
    if not os.path.exists(main_file):
        print(f"[ERROR] 找不到主文件: {main_file}")
        sys.exit(1)
    
    print(f"\n主文件: {main_file}")
    print("使用命令行参数打包...")
    
    args = [
        main_file,
        '--name=ShadowsocksServerV3',  # 生成的 exe 名称
        '--onefile',                    # 打包成单个文件
        '--windowed',                   # 无控制台窗口（GUI 应用）
        '--clean',                      # 清理临时文件
        '--noconfirm',                  # 不询问覆盖
        '--hidden-import=shadowsocks',  # 确保包含 shadowsocks 库
        '--hidden-import=shadowsocks.encrypt',
        '--hidden-import=shadowsocks.eventloop',
        '--hidden-import=shadowsocks.tcprelay',
        '--hidden-import=shadowsocks.asyncdns',
        '--hidden-import=shadowsocks.common',
        '--hidden-import=tkinter',
        '--hidden-import=tkinter.ttk',
        '--hidden-import=tkinter.scrolledtext',
        '--collect-all=shadowsocks',    # 收集所有 shadowsocks 相关文件
        '--add-data=shadowsocks_v2_refactored;shadowsocks_v2_refactored',  # 包含模块
    ]
    
    try:
        print("\n正在打包，请稍候...")
        PyInstaller.__main__.run(args)
        
        exe_path = os.path.join('dist', 'ShadowsocksServerV3.exe')
        if os.path.exists(exe_path):
            file_size = os.path.getsize(exe_path) / (1024 * 1024)  # MB
            print("\n" + "=" * 60)
            print("[SUCCESS] 打包完成！")
            print("=" * 60)
            print(f"exe 文件位置: {exe_path}")
            print(f"文件大小: {file_size:.2f} MB")
            print("\n提示：")
            print("1. 打包后的 exe 文件可以在任何 Windows 系统上运行，无需安装 Python")
            print("2. 首次运行可能会被杀毒软件拦截，需要添加信任")
            print("3. V3 版本基于 shadowsocks 官方库的事件循环架构")
            print("4. 修复了连续下载断开的问题")
        else:
            print("\n[ERROR] 打包失败：未找到生成的 exe 文件")
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

