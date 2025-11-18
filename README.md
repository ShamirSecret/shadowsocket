# Shadowsocks Server V3

A modern, cross-platform Shadowsocks proxy server with GUI, built on the official shadowsocks library's event loop architecture. Features Python 3.13+ compatibility and automated CI/CD for Windows and macOS builds.

## Features

- ✅ **Event Loop Architecture**: Based on shadowsocks official library, fixes continuous download disconnection issues
- ✅ **Cross-Platform**: Supports Windows and macOS
- ✅ **Modern GUI**: Clean, responsive interface with real-time monitoring
- ✅ **Python 3.13+ Compatible**: Includes compatibility fixes for Python 3.13+
- ✅ **Automated Builds**: GitHub Actions automatically builds Windows .exe and macOS .app
- ✅ **Standalone Executables**: No Python installation required to run
- ✅ **Connection Management**: Advanced connection pooling and timeout management
- ✅ **Real-time Statistics**: Connection count, traffic monitoring, and performance metrics

## Quick Start

### Option 1: Download Pre-built Executable (Recommended)

1. Go to [Releases](https://github.com/ShamirSecret/shadowsocket/releases)
2. Download `ShadowsocksServerV3.exe` (Windows) or `ShadowsocksServerV3.app` (macOS)
3. Run the executable - no dependencies needed!

### Option 2: Run from Source

```bash
# Install dependencies
pip install -r requirements.txt

# Run the server
python -m shadowsocks_server_ui
```

## Project Structure

```
shadowsocks-server-v2/
├── shadowsocks_server_ui/        # Main application code
│   ├── main.py                   # Entry point
│   ├── server.py                 # Server implementation
│   ├── tcprelay_ext.py          # Extended TCP relay
│   ├── compat.py                # Python 3.13 compatibility
│   ├── config/                  # Configuration management
│   ├── gui/                     # GUI components
│   └── stats/                   # Statistics collection
├── scripts/                      # Build and utility scripts
│   ├── build_exe_v3.py          # Windows build script
│   ├── build_macos_app.py       # macOS build script
│   └── ShadowsocksServerV3.spec # PyInstaller spec
├── docs/                         # Documentation
│   ├── BUILD_V3_README.md       # Build instructions
│   ├── CI_BUILD_README.md       # CI/CD guide
│   └── QUICK_START.md           # Quick start guide
├── .github/workflows/            # GitHub Actions CI/CD
├── requirements.txt              # Python dependencies
└── README.md                     # This file
```

## Building

### Automated Build (Recommended)

The project uses GitHub Actions to automatically build executables:

1. Push code to GitHub
2. Go to Actions tab
3. Select "Build Windows EXE" workflow
4. Click "Run workflow"
5. Download the built executable from Artifacts

See [docs/CI_BUILD_README.md](docs/CI_BUILD_README.md) for detailed instructions.

### Manual Build

#### Windows

```bash
python scripts/build_exe_v3.py
```

Output: `dist/ShadowsocksServerV3.exe`

#### macOS

```bash
python scripts/build_macos_app.py
```

Output: `dist/ShadowsocksServerV3.app`

See [docs/BUILD_V3_README.md](docs/BUILD_V3_README.md) for detailed build instructions.

## Requirements

- Python 3.11, 3.12, or 3.13+ (for building from source)
- shadowsocks >= 2.8.2
- tkinter (usually included with Python)
- pyinstaller >= 5.0.0 (for building executables)

## Configuration

The server configuration is saved in `shadowsocks_config.json`:

```json
{
  "server": "0.0.0.0",
  "server_port": 1080,
  "password": "your_password",
  "method": "aes-256-cfb",
  "max_connections": 2000,
  "timeout": 43200,
  "target_connect_timeout": 30
}
```

## Architecture

This project refactors the original implementation to use the official shadowsocks library's event loop architecture:

- **Event Loop**: Uses epoll/kqueue/select for efficient I/O
- **Non-blocking I/O**: All sockets are non-blocking with event-driven reads/writes
- **Timeout Management**: Precise timeout handling using timestamp queues
- **Connection Pooling**: Advanced connection management with limits

### Key Improvements

1. **Fixed Download Issues**: The event loop architecture prevents connection timeouts during long downloads
2. **Better Performance**: Non-blocking I/O improves throughput
3. **Python 3.13 Support**: Compatibility layer fixes `collections.MutableMapping` issue

## Python 3.13 Compatibility

This project includes compatibility fixes for Python 3.13+, which removed `collections.MutableMapping`. The fix is automatically applied in `compat.py` before importing shadowsocks.

## Usage

1. **Start Server**
   - Configure listening address and port (default: 0.0.0.0:1080)
   - Set password (required)
   - Choose encryption method (default: aes-256-cfb)
   - Configure max connections and timeouts
   - Click "Start Server"

2. **Monitor Server**
   - View real-time connection statistics
   - Monitor traffic (sent/received bytes and rates)
   - Check server logs

3. **Client Configuration**
   - Use standard Shadowsocks clients
   - Connect using the configured server address, port, password, and method

## Troubleshooting

### Build Issues

- Ensure Python 3.11+ is installed
- Install dependencies: `pip install shadowsocks pyinstaller`
- Check [docs/BUILD_V3_README.md](docs/BUILD_V3_README.md)

### Runtime Issues

- **Antivirus Blocking**: Add executable to antivirus whitelist
- **Port Already in Use**: Change the port in configuration
- **Firewall**: Ensure firewall allows the listening port

### Connection Issues

- Verify password and encryption method match client configuration
- Check firewall settings
- Ensure server is running and listening on correct address

## Development

### Running Tests

```bash
# Test imports
python -c "from shadowsocks_server_ui import compat; print('OK')"

# Test server
python -m shadowsocks_server_ui
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project uses the shadowsocks library, which is licensed under Apache License 2.0.

## Acknowledgments

- Built on [shadowsocks](https://github.com/shadowsocks/shadowsocks) library
- Uses PyInstaller for executable packaging
- GitHub Actions for automated builds

## Links

- **Repository**: https://github.com/ShamirSecret/shadowsocket
- **Issues**: https://github.com/ShamirSecret/shadowsocket/issues
- **Releases**: https://github.com/ShamirSecret/shadowsocket/releases
