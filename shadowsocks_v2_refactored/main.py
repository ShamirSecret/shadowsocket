#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Shadowsocks 服务端 V2 - 主入口
基于 shadowsocks 官方库的事件循环架构
"""
# 首先导入兼容性修复（必须在导入 shadowsocks 之前）
from . import compat  # noqa: F401
import sys
import tkinter as tk
from .server import ShadowsocksServer
from .config.manager import ConfigManager
from .gui.main_window import MainWindow


def main():
    """主函数"""
    # 创建配置管理器
    config_manager = ConfigManager()
    
    # 创建根窗口
    root = tk.Tk()
    
    # 创建主窗口
    app = MainWindow(root, ShadowsocksServer, config_manager)
    
    # 设置关闭事件
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    
    # 运行主循环
    root.mainloop()


if __name__ == "__main__":
    main()

