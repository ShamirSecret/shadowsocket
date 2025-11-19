# Shadowsocks Server for Windows

A cross-platform Shadowsocks proxy server with a modern web-based management interface. Supports Windows, macOS, and Linux.

## Features

- ✅ **Cross-Platform**: Runs on Windows, macOS, and Linux
- ✅ **Web Management Interface**: Clean and intuitive web interface for easy configuration
- ✅ **Real-time Statistics**: Monitor connections, traffic, and performance metrics
- ✅ **Easy Configuration**: Simple web form for server settings
- ✅ **Connection Management**: Efficient connection pooling and timeout management
- ✅ **Python 3.11+**: Supports Python 3.11, 3.12, and 3.13

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/ShamirSecret/shadowsock-server-for-windows.git
cd shadowsock-server-for-windows

# Install dependencies
pip install -r requirements.txt
```

### First-Time Setup

1. **Copy the example configuration**:
   ```bash
   cp shadowsocks_config.json.example shadowsocks_config.json
   ```

2. **Start the web interface**:
   ```bash
   python -m shadowsocks_server_ui
   ```

3. **Open your browser** and navigate to: **http://127.0.0.1:8888**

4. **Configure the server**:
   - Set your password (this will be shared with clients)
   - Choose encryption method (recommended: `chacha20-ietf-poly1305`)
   - Configure port and other settings
   - Click "Save Configuration"

5. **Start the server** and share the configuration with users

### Sharing Configuration

Once your server is running, share these details with users:

```
Server Address: [Your server IP or domain]
Port: [Configured port, default: 1080]
Password: [Your configured password]
Encryption Method: [Your configured method, e.g., aes-256-cfb]
```

**Client Setup**:
- **Windows**: Shadowsocks-Windows, Clash for Windows
- **macOS**: ShadowsocksX-NG, ClashX, V2RayU
- **Linux**: shadowsocks-libev, shadowsocks-qt5, V2Ray
- **Mobile**: Shadowsocks Android/iOS apps

## Project Structure

```
shadowsock-server-for-windows/
├── shadowsocks_server_ui/        # Main application code
│   ├── main.py                   # Entry point
│   ├── server.py                 # Server implementation
│   ├── config/                   # Configuration management
│   ├── web/                      # Web interface (Flask)
│   └── stats/                    # Statistics collection
├── scripts/                      # Build scripts
├── requirements.txt              # Python dependencies
├── shadowsocks_config.json.example # Configuration template
└── README.md                     # This file
```

## Building Executables

### Automated Build (Recommended)

GitHub Actions automatically builds executables for Windows and macOS:

1. Push code to GitHub
2. Go to [Actions](https://github.com/ShamirSecret/shadowsock-server-for-windows/actions)
3. Download the built executables from the latest workflow run

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

## Configuration

The server configuration is saved in `shadowsocks_config.json` (this file is gitignored for security):

**⚠️ Security Note**: The `shadowsocks_config.json` file contains your password and is automatically excluded from git. Never commit this file to version control!

### Configuration Options

```json
{
  "server": "0.0.0.0",              // Listen address (0.0.0.0 = all interfaces)
  "server_port": 1080,              // Listening port
  "password": "your_secure_password", // Password (share this with clients)
  "method": "aes-256-cfb",           // Encryption method
  "timeout": 43200,                  // Idle timeout (seconds, default: 12 hours)
  "max_connections": 2000,           // Maximum concurrent connections
  "target_connect_timeout": 30,      // Target connection timeout (seconds)
  "fast_open": false,                // TCP Fast Open (requires kernel support)
  "workers": 1,                      // Worker processes
  "verbose": false                   // Verbose logging
}
```

### Encryption Methods

Recommended encryption methods for better stealth and compatibility:

- **Recommended**: `chacha20-ietf-poly1305` - Most stealthy, harder to detect
- **Alternative**: `chacha20-ietf` - Good balance of speed and stealth
- **Standard**: `aes-256-cfb` - Widely compatible, good performance

## Usage Guide

### For Server Administrators

1. **Deploy the Server**:
   - Run on a server accessible to your team
   - Configure firewall to allow the listening port
   - Set a strong password

2. **Share Configuration**:
   - Provide server address, port, password, and encryption method
   - Recommend compatible clients for each platform
   - Monitor usage through the web interface

3. **Monitor Usage**:
   - View real-time connection statistics
   - Monitor traffic per client
   - Track target addresses and destinations

### For End Users

1. **Get Configuration**:
   - Receive server details from administrator
   - Install a Shadowsocks client for your platform

2. **Configure Client**:
   - Enter server address and port
   - Enter password
   - Select encryption method
   - Connect and enjoy!

3. **Platform-Specific Clients**:
   - **Windows**: Shadowsocks-Windows, Clash for Windows
   - **macOS**: ShadowsocksX-NG, ClashX, V2RayU
   - **Linux**: shadowsocks-libev, shadowsocks-qt5, V2Ray
   - **Android**: Shadowsocks Android
   - **iOS**: Shadowrocket, Quantumult X

## Security Considerations

### Server Security

- **Strong Passwords**: Use complex, unique passwords
- **Firewall**: Only expose necessary ports
- **Access Control**: Consider IP whitelisting if needed
- **Regular Updates**: Keep the server software updated

### Configuration Security

- **Never Commit Config Files**: `shadowsocks_config.json` is gitignored
- **Secure Sharing**: Share passwords through secure channels
- **Rotate Passwords**: Change passwords periodically
- **Monitor Access**: Review connection logs regularly

## Troubleshooting

### Connection Issues

- **Cannot Connect**: Verify password and encryption method match
- **Slow Performance**: Check server resources and network conditions
- **Frequent Disconnections**: Increase timeout value in configuration
- **Port Conflicts**: Change port if default is already in use

### Service-Specific Issues

#### ChatGPT/X "Attestation Denied"

If you encounter "attestation denied" errors:

1. **Change Encryption Method**:
   - Use `chacha20-ietf-poly1305` or `chacha20-ietf`
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

### Build Issues

- **Python Version**: Ensure Python 3.11+ is installed
- **Dependencies**: Run `pip install -r requirements.txt`
- **Platform-Specific**: Some build tools may require additional setup

## Requirements

- **Python**: 3.11, 3.12, or 3.13+
- **Dependencies**:
  - shadowsocks >= 2.8.2
  - Flask >= 2.3.0
  - pyinstaller >= 5.0.0 (for building executables, optional)

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

This project is licensed under Apache License 2.0.

## Links

- **Repository**: https://github.com/ShamirSecret/shadowsock-server-for-windows
- **Issues**: https://github.com/ShamirSecret/shadowsock-server-for-windows/issues
- **Releases**: https://github.com/ShamirSecret/shadowsock-server-for-windows/releases

## Support

For issues, questions, or contributions, please open an issue on GitHub.

---

**Note**: Ensure you comply with all applicable laws and regulations when using proxy/VPN services.
