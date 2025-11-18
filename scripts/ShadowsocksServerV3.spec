# -*- mode: python ; coding: utf-8 -*-
# Shadowsocks 服务端 V3 Refactored 打包配置

import os
project_root = os.path.dirname(os.path.dirname(os.path.abspath(SPEC)))

a = Analysis(
    [os.path.join(project_root, 'shadowsocks_v2_refactored', 'main.py')],
    pathex=[project_root],
    binaries=[],
    datas=[],
    hiddenimports=[
        'shadowsocks',
        'shadowsocks.encrypt',
        'shadowsocks.eventloop',
        'shadowsocks.tcprelay',
        'shadowsocks.asyncdns',
        'shadowsocks.common',
        'shadowsocks.crypto',
        'shadowsocks.crypto.openssl',
        'shadowsocks.crypto.sodium',
        'shadowsocks.crypto.rc4_md5',
        'shadowsocks.crypto.table',
        'shadowsocks.crypto.util',
        'tkinter',
        'tkinter.ttk',
        'tkinter.scrolledtext',
        'tkinter.messagebox',
        'shadowsocks_v2_refactored',
        'shadowsocks_v2_refactored.server',
        'shadowsocks_v2_refactored.tcprelay_ext',
        'shadowsocks_v2_refactored.config',
        'shadowsocks_v2_refactored.config.manager',
        'shadowsocks_v2_refactored.config.defaults',
        'shadowsocks_v2_refactored.stats',
        'shadowsocks_v2_refactored.stats.collector',
        'shadowsocks_v2_refactored.gui',
        'shadowsocks_v2_refactored.gui.main_window',
        'shadowsocks_v2_refactored.gui.config_panel',
        'shadowsocks_v2_refactored.gui.monitor_panel',
        'shadowsocks_v2_refactored.gui.log_panel',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='ShadowsocksServerV3',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # 无控制台窗口（GUI 应用）
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # 可以添加图标文件路径
)

