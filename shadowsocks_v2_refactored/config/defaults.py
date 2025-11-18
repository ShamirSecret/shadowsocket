"""默认配置"""

DEFAULT_CONFIG = {
    'server': '0.0.0.0',
    'server_port': 1080,
    'password': '',
    'method': 'aes-256-cfb',
    'timeout': 43200,  # 连接空闲超时（秒），默认12小时
    'max_connections': 2000,  # 最大连接数
    'target_connect_timeout': 30,  # 服务器-目标服务器连接超时（秒）
    'fast_open': False,
    'workers': 1,
    'verbose': False,
}

