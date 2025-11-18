# Shadowsocks Server UI

A refactored Shadowsocks server based on the official shadowsocks library's event loop architecture, fixing continuous download disconnection issues.

## Architecture

### Core Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        GUI Layer                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │ Config Panel │  │ Monitor Panel│  │  Log Panel   │   │
│  └──────────────┘  └──────────────┘  └──────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    Server Layer                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         ShadowsocksServer                            │  │
│  │  ┌──────────────┐  ┌──────────────┐               │  │
│  │  │  EventLoop    │  │  TCPRelayExt │               │  │
│  │  │ (shadowsocks) │  │  (extended)  │               │  │
│  │  └──────────────┘  └──────────────┘               │  │
│  │         │                  │                        │  │
│  │         └──────────┬───────┘                        │  │
│  │                    ▼                                 │  │
│  │         ┌──────────────────┐                        │  │
│  │         │  DNSResolver     │                        │  │
│  │         │  (shadowsocks)   │                        │  │
│  │         └──────────────────┘                        │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              Shadowsocks Library (Official)                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │  eventloop   │  │   tcprelay   │  │   encrypt    │   │
│  │  common      │  │  asyncdns    │  │              │   │
│  └──────────────┘  └──────────────┘  └──────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## Module Description

### Core Modules

- **server.py**: Server wrapper class, integrates EventLoop and TCPRelayExt
- **tcprelay_ext.py**: Extended TCP relay, inherits shadowsocks.tcprelay, adds statistics and connection limits

### GUI Modules

- **gui/main_window.py**: Main window, integrates all GUI components
- **gui/config_panel.py**: Configuration input panel
- **gui/monitor_panel.py**: Real-time monitoring panel
- **gui/log_panel.py**: Log display panel

### Configuration and Statistics Modules

- **config/manager.py**: Configuration manager
- **config/defaults.py**: Default configuration
- **stats/collector.py**: Statistics collector

## Differences from Official Library

### Architecture Differences

1. **Event Loop Architecture** vs **Thread Pool Architecture**
   - Official library: Uses epoll/kqueue/select event-driven
   - Original version: Uses ThreadPoolExecutor thread pool
   - Refactored version: Adopts official library's event loop architecture

2. **Non-blocking I/O** vs **Blocking I/O**
   - Official library: All sockets are non-blocking, notified via events
   - Original version: Uses blocking recv()/send()
   - Refactored version: Adopts official library's non-blocking I/O

3. **Timeout Management**
   - Official library: Timestamp queue + periodic cleanup (handle_periodic)
   - Original version: Independent cleanup thread periodically checks idle connections
   - Refactored version: Adopts official library's timeout management mechanism

### Feature Extensions

1. **Statistics**: Added connection count and traffic statistics
2. **Connection Limits**: Added maximum connection limit
3. **GUI Interface**: Provides graphical configuration and monitoring interface

## Usage

### Run GUI Version

```bash
python -m shadowsocks_server_ui
```

### Configuration

Configuration file: `shadowsocks_config.json`

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

## Fixed Issues

### Continuous Download Disconnection Issue

**Root Cause Analysis**:
- Original version used thread pool + blocking I/O, which could cause timeout misjudgment during long downloads
- Original version's timeout management mechanism was not precise enough

**Solution**:
- Adopts official library's event loop architecture for precise connection timeout management
- Uses non-blocking I/O to avoid long blocking
- Updates activity time promptly during data transmission, ensuring long download connections are not misjudged as idle

## Technical Highlights

1. **Event Loop Integration**: Directly uses shadowsocks EventLoop
2. **Timeout Management Fix**: Uses timestamp queue mechanism for precise connection timeout management
3. **Data Forwarding Optimization**: Uses non-blocking socket + event-driven
4. **Statistics Integration**: Adds statistics callbacks in TCPRelayExt

## Dependencies

- shadowsocks >= 2.8.2
- tkinter (Python standard library)

## Python 3.13 Compatibility

This project includes Python 3.13 compatibility fixes, resolving the `collections.MutableMapping` issue in shadowsocks 2.8.2.

Compatibility fixes are implemented in `compat.py` and automatically applied before importing shadowsocks.

## License

Apache License 2.0
