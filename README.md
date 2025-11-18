# Shadowsocks Server UI

A modern, cross-platform Shadowsocks proxy server with GUI, built on the official shadowsocks library's event loop architecture. Features Python 3.13+ compatibility and automated CI/CD for Windows and macOS builds.

## Features

- ✅ **Event Loop Architecture**: Based on shadowsocks official library, fixes continuous download disconnection issues
- ✅ **Cross-Platform**: Supports Windows, macOS, and Linux
- ✅ **Modern Web UI**: Beautiful, responsive web interface accessible from any browser
- ✅ **Python 3.13+ Compatible**: Includes compatibility fixes for Python 3.13+
- ✅ **No GUI Dependencies**: Web-based interface works on all platforms without tkinter
- ✅ **Connection Management**: Advanced connection pooling and timeout management
- ✅ **Real-time Statistics**: Live connection count, traffic monitoring, and performance metrics
- ✅ **Easy Configuration**: Simple web form for server settings

## Quick Start

### Run from Source

```bash
# Install dependencies
pip install -r requirements.txt

# Start the web interface
python -m shadowsocks_server_ui
```

Then open your browser and navigate to: **http://127.0.0.1:8888**

**Note**: The web interface uses port 8888 to avoid conflicts with macOS AirPlay Receiver (port 5000).

### Features

- 🌐 **Web-based UI**: Modern, responsive web interface accessible from any browser
- 📱 **Cross-platform**: Works on Windows, macOS, and Linux
- 🎨 **Beautiful Design**: Clean, modern interface with real-time updates
- ⚡ **Real-time Monitoring**: Live statistics and connection monitoring
- 🔧 **Easy Configuration**: Simple web form for server configuration

## Project Structure

```
shadowsocks-server-v2/
├── shadowsocks_server_ui/        # Main application code
│   ├── main.py                   # Entry point
│   ├── server.py                 # Server implementation
│   ├── tcprelay_ext.py          # Extended TCP relay
│   ├── compat.py                # Python 3.13 compatibility
│   ├── config/                  # Configuration management
│   ├── web/                     # Web interface (Flask)
│   │   ├── app.py              # Flask application
│   │   ├── templates/          # HTML templates
│   │   └── static/             # CSS, JS, images
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

- Python 3.11, 3.12, or 3.13+
- shadowsocks >= 2.8.2
- Flask >= 2.3.0
- pyinstaller >= 5.0.0 (for building executables, optional)

## Configuration

The server configuration is saved in `shadowsocks_config.json` (this file is gitignored for security):

**⚠️ Security Note**: The `shadowsocks_config.json` file contains your password and is automatically excluded from git. Never commit this file to version control!

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

1. **Start Web Interface**
   ```bash
   python -m shadowsocks_server_ui
   ```
   The web interface will start on http://127.0.0.1:5000

2. **Configure Server**
   - Open http://127.0.0.1:5000 in your browser
   - Fill in the configuration form:
     - Listen Address (default: 0.0.0.0)
     - Port (default: 1080)
     - Password (required)
     - Encryption Method (default: aes-256-cfb)
     - Max Connections (default: 2000)
     - Timeout settings
   - Click "Save Configuration"

3. **Start Server**
   - Click "Start Server" button
   - Monitor real-time statistics
   - View server logs

4. **Client Configuration**
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

### ChatGPT/X "Attestation Denied" Issues

If you encounter "attestation denied" errors when accessing ChatGPT, X (Twitter), or similar services:

1. **Change Encryption Method**:
   - Use `chacha20-ietf-poly1305` or `chacha20-ietf` instead of AES methods
   - These methods are harder to detect

2. **Check DNS Settings**:
   - Ensure client uses proxy DNS
   - Prevent DNS leaks

3. **Browser Configuration**:
   - Disable WebRTC (prevents IP leaks)
   - Clear cookies and cache
   - Use private/incognito mode

4. **Server IP**:
   - Server IP may be flagged as proxy/VPN
   - Consider using residential IP instead of datacenter IP

See [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) for detailed troubleshooting guide.

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
