"""配置面板"""
import tkinter as tk
from tkinter import ttk


class ConfigPanel:
    """配置输入面板"""
    
    def __init__(self, parent, bg_color="#f5f5f5", frame_bg="#ffffff", 
                 text_color="#333333"):
        self.parent = parent
        self.bg_color = bg_color
        self.frame_bg = frame_bg
        self.text_color = text_color
        
        # 创建配置框架
        config_frame = ttk.LabelFrame(parent, text="服务器配置", padding=10)
        config_frame.pack(fill=tk.X, pady=(0, 10))
        config_frame.grid_columnconfigure(1, weight=1)
        config_frame.grid_columnconfigure(3, weight=1)
        
        # 配置变量
        self.host_var = tk.StringVar(value="0.0.0.0")
        self.port_var = tk.StringVar(value="1080")
        self.password_var = tk.StringVar()
        self.method_var = tk.StringVar(value="aes-256-cfb")
        self.max_conn_var = tk.StringVar(value="2000")
        self.idle_timeout_var = tk.StringVar(value="43200")
        self.target_connect_timeout_var = tk.StringVar(value="30")
        
        # 第一行：监听地址和端口
        tk.Label(config_frame, text="监听地址:", bg=frame_bg, fg=text_color,
                font=("Microsoft YaHei UI", 9)).grid(row=0, column=0, sticky=tk.W, pady=5, padx=(0, 5))
        host_entry = tk.Entry(config_frame, textvariable=self.host_var, width=12,
                             bg="#ffffff", fg=text_color, insertbackground=text_color,
                             font=("Consolas", 9), relief=tk.SUNKEN, bd=1)
        host_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W+tk.E)
        
        tk.Label(config_frame, text="监听端口:", bg=frame_bg, fg=text_color,
                font=("Microsoft YaHei UI", 9)).grid(row=0, column=2, sticky=tk.W, pady=5, padx=(10, 5))
        port_entry = tk.Entry(config_frame, textvariable=self.port_var, width=10,
                             bg="#ffffff", fg=text_color, insertbackground=text_color,
                             font=("Consolas", 9), relief=tk.SUNKEN, bd=1)
        port_entry.grid(row=0, column=3, padx=5, pady=5, sticky=tk.W+tk.E)
        
        # 第二行：密码
        tk.Label(config_frame, text="密码:", bg=frame_bg, fg=text_color,
                font=("Microsoft YaHei UI", 9)).grid(row=1, column=0, sticky=tk.W, pady=5, padx=(0, 5))
        password_entry = tk.Entry(config_frame, textvariable=self.password_var, show="*", width=12,
                                 bg="#ffffff", fg=text_color, insertbackground=text_color,
                                 font=("Consolas", 9), relief=tk.SUNKEN, bd=1)
        password_entry.grid(row=1, column=1, columnspan=3, padx=5, pady=5, sticky=tk.W+tk.E)
        
        # 第三行：加密方法
        tk.Label(config_frame, text="加密方法:", bg=frame_bg, fg=text_color,
                font=("Microsoft YaHei UI", 9)).grid(row=2, column=0, sticky=tk.W, pady=5, padx=(0, 5))
        method_values = (
            "aes-128-cfb", "aes-192-cfb", "aes-256-cfb",
            "aes-128-cfb8", "aes-192-cfb8", "aes-256-cfb8",
            "aes-128-ctr", "aes-192-ctr", "aes-256-ctr",
            "rc4-md5", "bf-cfb"
        )
        method_combo = ttk.Combobox(config_frame, textvariable=self.method_var, width=12, state="readonly")
        method_combo['values'] = method_values
        method_combo.grid(row=2, column=1, columnspan=3, padx=5, pady=5, sticky=tk.W+tk.E)
        
        # 第四行：最大连接数
        tk.Label(config_frame, text="最大连接数:", bg=frame_bg, fg=text_color,
                font=("Microsoft YaHei UI", 9)).grid(row=3, column=0, sticky=tk.W, pady=5, padx=(0, 5))
        max_conn_entry = tk.Entry(config_frame, textvariable=self.max_conn_var, width=12,
                                 bg="#ffffff", fg=text_color, insertbackground=text_color,
                                 font=("Consolas", 9), relief=tk.SUNKEN, bd=1)
        max_conn_entry.grid(row=3, column=1, columnspan=3, padx=5, pady=5, sticky=tk.W+tk.E)
        
        # 第五行：连接空闲超时
        tk.Label(config_frame, text="连接空闲超时(秒):", bg=frame_bg, fg=text_color,
                font=("Microsoft YaHei UI", 9)).grid(row=4, column=0, sticky=tk.W, pady=5, padx=(0, 5))
        idle_timeout_entry = tk.Entry(config_frame, textvariable=self.idle_timeout_var, width=12,
                                     bg="#ffffff", fg=text_color, insertbackground=text_color,
                                     font=("Consolas", 9), relief=tk.SUNKEN, bd=1)
        idle_timeout_entry.grid(row=4, column=1, padx=5, pady=5, sticky=tk.W+tk.E)
        tk.Label(config_frame, text="(只检查空闲时间，支持长时间下载)", bg=frame_bg, fg=text_color,
                font=("Microsoft YaHei UI", 7)).grid(row=4, column=2, columnspan=2, sticky=tk.W, padx=5, pady=(0, 2))
        
        # 第六行：目标连接超时
        tk.Label(config_frame, text="目标连接超时(秒):", bg=frame_bg, fg=text_color,
                font=("Microsoft YaHei UI", 9)).grid(row=5, column=0, sticky=tk.W, pady=5, padx=(0, 5))
        target_connect_timeout_entry = tk.Entry(config_frame, textvariable=self.target_connect_timeout_var, width=12,
                                                bg="#ffffff", fg=text_color, insertbackground=text_color,
                                                font=("Consolas", 9), relief=tk.SUNKEN, bd=1)
        target_connect_timeout_entry.grid(row=5, column=1, columnspan=3, padx=5, pady=5, sticky=tk.W+tk.E)
    
    def get_config(self):
        """获取配置"""
        return {
            'server': self.host_var.get() or "0.0.0.0",
            'server_port': int(self.port_var.get() or "1080"),
            'password': self.password_var.get(),
            'method': self.method_var.get() or "aes-256-cfb",
            'max_connections': int(self.max_conn_var.get() or "2000"),
            'timeout': int(self.idle_timeout_var.get() or "43200"),
            'target_connect_timeout': int(self.target_connect_timeout_var.get() or "30"),
            'fast_open': False,
            'workers': 1,
            'verbose': False,
        }
    
    def set_config(self, config):
        """设置配置"""
        self.host_var.set(config.get('server', '0.0.0.0'))
        self.port_var.set(str(config.get('server_port', 1080)))
        self.password_var.set(config.get('password', ''))
        self.method_var.set(config.get('method', 'aes-256-cfb'))
        self.max_conn_var.set(str(config.get('max_connections', 2000)))
        self.idle_timeout_var.set(str(config.get('timeout', 43200)))
        self.target_connect_timeout_var.set(str(config.get('target_connect_timeout', 30)))

