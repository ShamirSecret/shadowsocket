#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
打包脚本 V2 - 将 Shadowsocks 服务端 V2 打包成 exe 文件
使用方法: python build_exe_v2.py
"""

import PyInstaller.__main__
import os
import sys

# 设置 Windows 控制台编码为 UTF-8
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except:
        pass

def build():
    """打包成 exe"""
    print("=" * 60)
    print("开始打包 Shadowsocks 服务端 V2...")
    print("=" * 60)
    
    # 检查依赖
    try:
        import shadowsocks
        print("[OK] shadowsocks 库已安装")
    except ImportError:
        print("[ERROR] shadowsocks 库未安装，正在尝试安装...")
        import subprocess
        result = subprocess.run([sys.executable, '-m', 'pip', 'install', 'shadowsocks'], 
                               capture_output=True, text=True)
        if result.returncode != 0:
            print("[ERROR] 安装 shadowsocks 失败，请手动运行: pip install shadowsocks")
            sys.exit(1)
        print("[OK] shadowsocks 库安装成功")
    
    # 使用 spec 文件打包（推荐方式）
    spec_file = 'ShadowsocksServerV2.spec'
    if os.path.exists(spec_file):
        print(f"\n使用配置文件: {spec_file}")
        args = [
            spec_file,
            '--clean',
            '--noconfirm',
        ]
    else:
        # 如果没有 spec 文件，使用命令行参数
        print("\n使用命令行参数打包...")
        args = [
            'shadowsocket_v2.py',        # 主文件
            '--name=ShadowsocksServerV2', # 生成的 exe 名称
            '--onefile',                  # 打包成单个文件
            '--windowed',                 # 无控制台窗口（GUI 应用）
            '--clean',                    # 清理临时文件
            '--noconfirm',                # 不询问覆盖
            '--hidden-import=shadowsocks', # 确保包含 shadowsocks 库
            '--hidden-import=shadowsocks.encrypt', # 确保包含加密模块
            '--hidden-import=tkinter',    # 确保包含 tkinter
            '--hidden-import=tkinter.ttk', # 确保包含 ttk
        ]
    
    try:
        print("\n正在打包，请稍候...")
        PyInstaller.__main__.run(args)
        
        exe_path = os.path.join('dist', 'ShadowsocksServerV2.exe')
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
            print("3. V2 版本包含以下功能：")
            print("   - 现代化深色主题 UI")
            print("   - 详细的连接和线程监控")
            print("   - 实时流量统计")
            print("   - 响应式布局")
            print("   - 线程池和连接管理")
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

