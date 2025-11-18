# Project Structure

```
shadowsocks-server-v2/
├── shadowsocks_v2_refactored/    # Main application code
│   ├── __init__.py
│   ├── __main__.py
│   ├── main.py                   # Entry point
│   ├── server.py                 # Server implementation
│   ├── tcprelay_ext.py          # Extended TCP relay
│   ├── compat.py                # Python 3.13 compatibility
│   ├── config/                  # Configuration management
│   │   ├── __init__.py
│   │   ├── defaults.py
│   │   └── manager.py
│   ├── gui/                     # GUI components
│   │   ├── __init__.py
│   │   ├── main_window.py
│   │   ├── config_panel.py
│   │   ├── monitor_panel.py
│   │   └── log_panel.py
│   └── stats/                   # Statistics collection
│       ├── __init__.py
│       └── collector.py
├── scripts/                      # Build and utility scripts
│   ├── build_exe_v3.py          # Windows build script
│   ├── build_macos_app.py      # macOS build script
│   ├── ShadowsocksServerV3.spec # PyInstaller spec
│   └── push_to_github.sh       # GitHub push helper
├── docs/                         # Documentation
│   ├── BUILD_V3_README.md       # Build instructions
│   ├── CI_BUILD_README.md       # CI/CD guide
│   ├── QUICK_START.md           # Quick start guide
│   └── PUSH_GUIDE.md            # GitHub push guide
├── .github/workflows/            # GitHub Actions CI/CD
│   ├── build-windows-exe.yml    # Windows build workflow
│   └── build-all-platforms.yml  # Multi-platform workflow
├── README.md                     # Main project documentation
├── CONTRIBUTING.md               # Contribution guidelines
├── LICENSE                       # Apache License 2.0
├── requirements.txt              # Python dependencies
└── .gitignore                    # Git ignore rules
```
