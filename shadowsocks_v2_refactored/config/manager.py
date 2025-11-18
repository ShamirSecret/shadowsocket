"""配置管理"""
import json
import os
from .defaults import DEFAULT_CONFIG


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_file='shadowsocks_config.json'):
        self.config_file = config_file
        self.config = DEFAULT_CONFIG.copy()
    
    def load(self):
        """加载配置"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    # 更新配置，保留默认值
                    for key, value in loaded.items():
                        if key in self.config:
                            self.config[key] = value
        except Exception:
            pass
        return self.config
    
    def save(self, config=None):
        """保存配置"""
        if config:
            self.config.update(config)
        
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            return True
        except Exception:
            return False
    
    def get(self, key, default=None):
        """获取配置项"""
        return self.config.get(key, default)
    
    def set(self, key, value):
        """设置配置项"""
        self.config[key] = value
    
    def to_shadowsocks_config(self):
        """转换为 shadowsocks 库需要的配置格式"""
        return {
            'server': self.config['server'],
            'server_port': self.config['server_port'],
            'password': self.config['password'],
            'method': self.config['method'],
            'timeout': self.config['timeout'],
            'fast_open': self.config['fast_open'],
            'workers': self.config['workers'],
            'verbose': self.config['verbose'],
        }

