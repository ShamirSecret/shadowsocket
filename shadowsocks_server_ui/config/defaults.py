"""Default configuration"""

DEFAULT_CONFIG = {
    'server': '0.0.0.0',
    'server_port': 1080,
    'password': '',
    'method': 'aes-256-cfb',
    'timeout': 43200,  # Idle timeout (seconds), default 12 hours
    'max_connections': 2000,  # Maximum connections
    'target_connect_timeout': 30,  # Server-target server connection timeout (seconds)
    'fast_open': False,
    'workers': 1,
    'verbose': False,
}

