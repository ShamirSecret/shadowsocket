"""监控面板"""
import tkinter as tk
import time


class MonitorPanel:
    """实时监控面板"""
    
    def __init__(self, parent, bg_color="#f5f5f5", frame_bg="#ffffff", 
                 text_color="#333333", success_color="#28a745", 
                 accent_color="#0078d4", warning_color="#ffc107", 
                 error_color="#dc3545"):
        self.parent = parent
        self.bg_color = bg_color
        self.frame_bg = frame_bg
        self.text_color = text_color
        self.success_color = success_color
        self.accent_color = accent_color
        self.warning_color = warning_color
        self.error_color = error_color
        
        # 创建监控框架
        monitor_frame = tk.LabelFrame(parent, text="实时监控", bg=frame_bg, fg=text_color,
                                     font=("Microsoft YaHei UI", 10, "bold"), padx=10, pady=10)
        monitor_frame.pack(fill=tk.BOTH, expand=True)
        
        # 状态显示
        self.status_label = tk.Label(monitor_frame, text="状态: 未启动",
                                     font=("Microsoft YaHei UI", 10, "bold"),
                                     bg=frame_bg, fg=text_color, anchor=tk.W)
        self.status_label.pack(fill=tk.X, pady=(0, 8))
        
        # 统计信息容器
        stats_container = tk.Frame(monitor_frame, bg=frame_bg)
        stats_container.pack(fill=tk.BOTH, expand=True)
        
        # 连接统计
        conn_frame = tk.LabelFrame(stats_container, text="连接", bg="#f8f9fa", fg=text_color,
                                  font=("Microsoft YaHei UI", 9, "bold"), padx=8, pady=6,
                                  relief=tk.RAISED, bd=1)
        conn_frame.pack(fill=tk.X, pady=(0, 6))
        
        self.conn_stats_label = tk.Label(conn_frame, text="当前: 0/0",
                                         font=("Consolas", 9), bg="#f8f9fa", fg=text_color,
                                         anchor=tk.W, justify=tk.LEFT)
        self.conn_stats_label.pack(fill=tk.X, pady=1)
        
        self.total_conn_label = tk.Label(conn_frame, text="总计: 0 | 拒绝: 0 | 关闭: 0",
                                         font=("Consolas", 8), bg="#f8f9fa", fg=text_color,
                                         anchor=tk.W, justify=tk.LEFT)
        self.total_conn_label.pack(fill=tk.X, pady=1)
        
        # 流量统计
        traffic_frame = tk.LabelFrame(stats_container, text="流量", bg="#f8f9fa", fg=text_color,
                                     font=("Microsoft YaHei UI", 9, "bold"), padx=8, pady=6,
                                     relief=tk.RAISED, bd=1)
        traffic_frame.pack(fill=tk.X, pady=(0, 6))
        
        self.bytes_sent_label = tk.Label(traffic_frame, text="发送: 0 B (0 B/s)",
                                        font=("Consolas", 9), bg="#f8f9fa", fg=success_color,
                                        anchor=tk.W, justify=tk.LEFT)
        self.bytes_sent_label.pack(fill=tk.X, pady=1)
        
        self.bytes_received_label = tk.Label(traffic_frame, text="接收: 0 B (0 B/s)",
                                            font=("Consolas", 9), bg="#f8f9fa", fg=accent_color,
                                            anchor=tk.W, justify=tk.LEFT)
        self.bytes_received_label.pack(fill=tk.X, pady=1)
        
        self.total_traffic_label = tk.Label(traffic_frame, text="总计: 0 B",
                                            font=("Consolas", 8), bg="#f8f9fa", fg=text_color,
                                            anchor=tk.W, justify=tk.LEFT)
        self.total_traffic_label.pack(fill=tk.X, pady=1)
        
        # 运行时间
        self.uptime_label = tk.Label(stats_container, text="运行时间: 00:00:00",
                                     font=("Consolas", 9), bg=frame_bg, fg=accent_color,
                                     anchor=tk.W, justify=tk.LEFT)
        self.uptime_label.pack(fill=tk.X, pady=(6, 0))
        
        # 统计更新相关
        self.last_bytes_sent = 0
        self.last_bytes_received = 0
        self.last_stats_time = time.time()
    
    def format_bytes(self, bytes_value):
        """格式化字节数"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_value < 1024.0:
                return f"{bytes_value:.2f} {unit}"
            bytes_value /= 1024.0
        return f"{bytes_value:.2f} PB"
    
    def update_stats(self, stats, max_connections=None):
        """更新统计信息"""
        if not stats:
            self.reset_stats()
            return
        
        # 连接统计
        current_conn = stats.get('current_connections', 0)
        max_conn = max_connections or stats.get('max_connections', 0)
        
        conn_color = self.success_color
        if max_conn > 0:
            if current_conn > max_conn * 0.8:
                conn_color = self.warning_color
            if current_conn > max_conn * 0.95:
                conn_color = self.error_color
        
        self.conn_stats_label.config(
            text=f"当前: {current_conn}/{max_conn}",
            fg=conn_color
        )
        self.total_conn_label.config(
            text=f"总计: {stats.get('total_connections', 0)} | "
                 f"拒绝: {stats.get('rejected_connections', 0)} | "
                 f"关闭: {stats.get('closed_connections', 0)}"
        )
        
        # 运行时间
        uptime = stats.get('uptime', 0)
        hours = uptime // 3600
        minutes = (uptime % 3600) // 60
        seconds = uptime % 60
        self.uptime_label.config(
            text=f"运行时间: {hours:02d}:{minutes:02d}:{seconds:02d}"
        )
        
        # 流量统计
        bytes_sent = stats.get('bytes_sent', 0)
        bytes_received = stats.get('bytes_received', 0)
        total_traffic = stats.get('total_traffic', bytes_sent + bytes_received)
        
        # 计算速率
        current_time = time.time()
        time_diff = current_time - self.last_stats_time
        if time_diff > 0:
            sent_speed = (bytes_sent - self.last_bytes_sent) / time_diff
            received_speed = (bytes_received - self.last_bytes_received) / time_diff
        else:
            sent_speed = 0
            received_speed = 0
        
        self.bytes_sent_label.config(
            text=f"发送: {self.format_bytes(bytes_sent)} ({self.format_bytes(sent_speed)}/s)"
        )
        self.bytes_received_label.config(
            text=f"接收: {self.format_bytes(bytes_received)} ({self.format_bytes(received_speed)}/s)"
        )
        self.total_traffic_label.config(
            text=f"总计: {self.format_bytes(total_traffic)}"
        )
        
        # 更新上次统计值
        self.last_bytes_sent = bytes_sent
        self.last_bytes_received = bytes_received
        self.last_stats_time = current_time
    
    def set_status(self, status, color=None):
        """设置状态"""
        self.status_label.config(
            text=f"状态: {status}",
            fg=color or self.text_color
        )
    
    def reset_stats(self):
        """重置统计显示"""
        self.conn_stats_label.config(text="当前: 0/0", fg=self.text_color)
        self.total_conn_label.config(text="总计: 0 | 拒绝: 0 | 关闭: 0")
        self.uptime_label.config(text="运行时间: 00:00:00")
        self.bytes_sent_label.config(text="发送: 0 B (0 B/s)")
        self.bytes_received_label.config(text="接收: 0 B (0 B/s)")
        self.total_traffic_label.config(text="总计: 0 B")
        self.last_bytes_sent = 0
        self.last_bytes_received = 0
        self.last_stats_time = time.time()

