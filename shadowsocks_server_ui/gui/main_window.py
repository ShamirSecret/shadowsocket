"""主窗口"""
import tkinter as tk
from tkinter import messagebox
import threading
from .config_panel import ConfigPanel
from .monitor_panel import MonitorPanel
from .log_panel import LogPanel


class MainWindow:
    """主窗口"""
    
    def __init__(self, root, server_class, config_manager):
        """
        初始化主窗口
        
        Args:
            root: Tkinter 根窗口
            server_class: 服务器类（ShadowsocksServer）
            config_manager: 配置管理器
        """
        self.root = root
        self.server_class = server_class
        self.config_manager = config_manager
        
        self.root.title("Shadowsocks 服务端 V2 - 增强版")
        self.root.geometry("1100x700")
        self.root.resizable(True, True)
        self.root.minsize(900, 600)
        
        # 设置主题颜色
        self.bg_color = "#f5f5f5"
        self.frame_bg = "#ffffff"
        self.text_color = "#333333"
        self.accent_color = "#0078d4"
        self.success_color = "#28a745"
        self.warning_color = "#ffc107"
        self.error_color = "#dc3545"
        
        self.root.configure(bg=self.bg_color)
        
        # 服务器实例
        self.server = None
        
        # 设置界面
        self.setup_ui()
        
        # 加载配置
        self.load_config()
        
        # 启动统计更新
        self.update_stats_loop()
    
    def setup_ui(self):
        """设置界面"""
        # 主容器
        main_container = tk.Frame(self.root, bg=self.bg_color)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 配置 grid 权重
        main_container.grid_columnconfigure(0, weight=3, minsize=500)
        main_container.grid_columnconfigure(1, weight=2, minsize=350)
        main_container.grid_rowconfigure(1, weight=1)
        
        # 标题
        title_label = tk.Label(main_container, text="Shadowsocks 服务端 V2",
                              font=("Microsoft YaHei UI", 18, "bold"),
                              bg=self.bg_color, fg=self.accent_color)
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 10), sticky=tk.W)
        
        # 左侧列
        left_column = tk.Frame(main_container, bg=self.bg_color)
        left_column.grid(row=1, column=0, sticky="nsew", padx=(0, 10))
        left_column.grid_rowconfigure(2, weight=1)
        
        # 配置面板
        self.config_panel = ConfigPanel(left_column, self.bg_color, self.frame_bg, self.text_color)
        
        # 控制按钮
        button_frame = tk.Frame(left_column, bg=self.bg_color)
        button_frame.pack(pady=10, fill=tk.X)
        
        self.start_button = tk.Button(button_frame, text="▶ 启动服务器", command=self.start_server,
                                     bg=self.success_color, fg="white",
                                     font=("Microsoft YaHei UI", 11, "bold"),
                                     width=18, height=2, relief=tk.RAISED, cursor="hand2",
                                     activebackground="#218838", activeforeground="white", bd=1)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = tk.Button(button_frame, text="■ 停止服务器", command=self.stop_server,
                                    bg=self.error_color, fg="white",
                                    font=("Microsoft YaHei UI", 11, "bold"),
                                    width=18, height=2, relief=tk.RAISED, cursor="hand2",
                                    state=tk.DISABLED,
                                    activebackground="#c82333", activeforeground="white", bd=1)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        # 监控面板
        self.monitor_panel = MonitorPanel(left_column, self.bg_color, self.frame_bg, self.text_color,
                                         self.success_color, self.accent_color, self.warning_color, self.error_color)
        
        # 右侧：日志面板
        log_frame = tk.Frame(main_container, bg=self.bg_color)
        log_frame.grid(row=1, column=1, sticky="nsew")
        log_frame.grid_rowconfigure(0, weight=1)
        log_frame.grid_columnconfigure(0, weight=1)
        self.log_panel = LogPanel(log_frame, self.frame_bg, self.text_color)
    
    def log(self, message):
        """记录日志"""
        self.log_panel.log(message)
    
    def start_server(self):
        """启动服务器"""
        try:
            # 获取配置
            config = self.config_panel.get_config()
            
            # 验证配置
            if config['server_port'] < 1 or config['server_port'] > 65535:
                messagebox.showerror("错误", "端口号必须在 1-65535 之间")
                return
            
            if not config['password']:
                messagebox.showerror("错误", "密码是必填项！\n\nShadowsocks 需要密码进行加密。")
                return
            
            if config['max_connections'] < 1 or config['max_connections'] > 10000:
                messagebox.showerror("错误", "最大连接数必须在 1-10000 之间")
                return
            
            if config['timeout'] < 60 or config['timeout'] > 604800:
                messagebox.showerror("错误", "连接空闲超时必须在 60-604800 秒之间（1分钟-7天）")
                return
            
            if config['target_connect_timeout'] < 5 or config['target_connect_timeout'] > 300:
                messagebox.showerror("错误", "目标连接超时必须在 5-300 秒之间（5秒-5分钟）")
                return
            
            # 创建服务器实例
            from ..stats.collector import StatsCollector
            stats_collector = StatsCollector()
            
            self.server = self.server_class(
                config,
                stats_collector=stats_collector,
                log_callback=self.log
            )
            
            # 启动服务器
            if self.server.start():
                self.start_button.config(state=tk.DISABLED)
                self.stop_button.config(state=tk.NORMAL)
                
                method = config['method']
                host = config['server']
                port = config['server_port']
                self.monitor_panel.set_status(
                    f"运行中 - {host}:{port} ({method})",
                    self.success_color
                )
                
                self.log(f"服务器启动成功！加密方法: {method}")
                self.log(f"最大连接数: {config['max_connections']}")
                self.log(f"连接空闲超时: {config['timeout']}秒 ({config['timeout']//3600}小时)")
                self.log(f"目标连接超时: {config['target_connect_timeout']}秒")
                
                # 保存配置
                self.config_manager.save(config)
            else:
                messagebox.showerror("错误", "服务器启动失败，请检查端口是否被占用")
                
        except ValueError as e:
            messagebox.showerror("错误", f"配置错误: {str(e)}")
        except Exception as e:
            messagebox.showerror("错误", f"启动失败: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def stop_server(self):
        """停止服务器"""
        if self.server:
            self.server.stop()
            self.server = None
            
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            self.monitor_panel.set_status("已停止", self.error_color)
            self.log("服务器已停止")
            self.monitor_panel.reset_stats()
    
    def load_config(self):
        """加载配置"""
        config = self.config_manager.load()
        self.config_panel.set_config(config)
    
    def update_stats_loop(self):
        """更新统计信息循环"""
        if self.server and self.server.is_running():
            stats = self.server.get_stats()
            config = self.config_panel.get_config()
            self.monitor_panel.update_stats(stats, config.get('max_connections'))
        else:
            self.monitor_panel.reset_stats()
        
        # 每1秒更新一次
        self.root.after(1000, self.update_stats_loop)
    
    def on_closing(self):
        """关闭窗口时的处理"""
        if self.server and self.server.is_running():
            if messagebox.askokcancel("退出", "服务器正在运行，确定要退出吗？"):
                self.stop_server()
                self.root.destroy()
        else:
            self.root.destroy()

