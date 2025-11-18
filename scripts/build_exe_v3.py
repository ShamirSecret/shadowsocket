#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
打包脚本 V3 - 将 Shadowsocks V2 Refactored 打包成 exe 文件
使用方法: python build_exe_v3.py

支持：
- Windows: 打包成 .exe
- macOS: 打包成 .app（需要修改参数）
- GitHub Actions: 自动在云端打包
"""

import PyInstaller.__main__
import os
import sys
import platform

# 设置 Windows 控制台编码为 UTF-8
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except:
        pass

def build():
    """打包成可执行文件"""
    print("=" * 60)
    print("开始打包 Shadowsocks V2 Refactored...")
    print(f"平台: {platform.system()} {platform.release()}")
    print("=" * 60)
    
    # 检查依赖
    try:
        import shadowsocks
        print("[OK] shadowsocks 库已安装")
    except ImportError:
        print("[ERROR] shadowsocks 库未安装，请先运行: pip install shadowsocks")
        sys.exit(1)
    
    # 获取主文件路径（从脚本目录回到项目根目录）
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    main_file = os.path.join(project_root, 'shadowsocks_server_ui', 'main.py')
    if not os.path.exists(main_file):
        print(f"[ERROR] 找不到主文件: {main_file}")
        sys.exit(1)
    
    print(f"\n主文件: {main_file}")
    
    # 根据平台选择打包参数
    is_windows = platform.system() == 'Windows'
    is_macos = platform.system() == 'Darwin'
    
    # 检查是否有 spec 文件
    spec_file = os.path.join(script_dir, 'ShadowsocksServerV3.spec')
    if os.path.exists(spec_file) and is_windows:
        print(f"\n使用配置文件: {spec_file}")
        args = [
            spec_file,
            '--clean',
            '--noconfirm',
        ]
    else:
        # 构建 PyInstaller 参数
        print("\n使用命令行参数打包...")
        args = [
            main_file,
            '--name=ShadowsocksServerV3',  # 生成的名称
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
            f'--paths={project_root}',      # 添加项目根目录到路径
        ]
        
        # Windows 特定参数
        if is_windows:
            args.append('--onefile')  # Windows 打包成单个 .exe 文件
        
        # macOS 特定参数
        if is_macos:
            args.append('--osx-bundle-identifier=com.shadowsocks.server.v3')
    
    try:
        print("\n正在打包，请稍候...")
        PyInstaller.__main__.run(args)
        
        # 根据平台确定输出文件路径
        dist_dir = os.path.join(project_root, 'dist')
        if is_windows:
            output_path = os.path.join(dist_dir, 'ShadowsocksServerV3.exe')
            output_name = "exe 文件"
            platform_name = "Windows"
        elif is_macos:
            output_path = os.path.join(dist_dir, 'ShadowsocksServerV3.app')
            output_name = "应用"
            platform_name = "macOS"
        else:
            output_path = os.path.join(dist_dir, 'ShadowsocksServerV3')
            output_name = "可执行文件"
            platform_name = platform.system()
        
        if os.path.exists(output_path):
            if is_macos:
                # macOS .app 是目录，需要计算总大小
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
            print("[SUCCESS] 打包完成！")
            print("=" * 60)
            print(f"{output_name}位置: {output_path}")
            print(f"文件大小: {file_size:.2f} MB")
            print("\n提示：")
            if is_windows:
                print("1. 打包后的 exe 文件可以在任何 Windows 系统上运行，无需安装 Python")
                print("2. 首次运行可能会被杀毒软件拦截，需要添加信任")
            elif is_macos:
                print("1. 打包后的 .app 文件可以在 macOS 系统上运行")
                print("2. 首次运行可能需要右键点击 -> 打开（绕过 Gatekeeper）")
            print("3. V3 版本基于 shadowsocks 官方库的事件循环架构")
            print("4. 修复了连续下载断开的问题")
            print("5. 支持长时间下载，不会因为空闲超时而断开")
            print("6. 支持 Python 3.13+")
        else:
            print(f"\n[ERROR] 打包失败：未找到生成的 {output_name}")
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

