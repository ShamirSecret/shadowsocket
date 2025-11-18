# -*- mode: python ; coding: utf-8 -*-
# Shadowsocks Server V3 Refactored Build Configuration

import os
# Get project root directory (parent of scripts directory)
spec_dir = os.path.dirname(os.path.abspath(SPEC))
project_root = os.path.dirname(spec_dir)

a = Analysis(
    [os.path.join(project_root, 'shadowsocks_server_ui', '__main__.py')],
    pathex=[project_root],
    binaries=[],
    datas=[
        (os.path.join(project_root, 'shadowsocks_server_ui', 'web', 'templates'), 'shadowsocks_server_ui/web/templates'),
        (os.path.join(project_root, 'shadowsocks_server_ui', 'web', 'static'), 'shadowsocks_server_ui/web/static'),
    ],
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
        'shadowsocks_server_ui',
        'shadowsocks_server_ui.server',
        'shadowsocks_server_ui.tcprelay_ext',
        'shadowsocks_server_ui.config',
        'shadowsocks_server_ui.config.manager',
        'shadowsocks_server_ui.config.defaults',
        'shadowsocks_server_ui.stats',
        'shadowsocks_server_ui.stats.collector',
        'shadowsocks_server_ui.web',
        'shadowsocks_server_ui.web.app',
        'flask',
        'flask.helpers',
        'flask.templating',
        'jinja2',
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
    console=True,  # Show console window (for web server logs)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Can add icon file path
)

