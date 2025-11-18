"""日志面板"""
import tkinter as tk
from tkinter import scrolledtext
from datetime import datetime


class LogPanel:
    """日志显示面板"""
    
    def __init__(self, parent, bg_color="#ffffff", text_color="#333333"):
        self.parent = parent
        self.bg_color = bg_color
        self.text_color = text_color
        self.frame = None
        self.log_text = None
        self.setup_ui()
    
    def setup_ui(self):
        """设置界面"""
        # 创建日志框架
        self.frame = tk.LabelFrame(self.parent, text="运行日志", bg=self.bg_color, fg=self.text_color,
                                   font=("Microsoft YaHei UI", 10, "bold"), padx=5, pady=5)
        self.frame.pack(fill=tk.BOTH, expand=True)
        self.frame.grid_rowconfigure(0, weight=1)
        self.frame.grid_columnconfigure(0, weight=1)
        
        # 创建滚动文本框
        self.log_text = scrolledtext.ScrolledText(
            self.frame,
            bg=self.bg_color,
            fg=self.text_color,
            insertbackground=self.text_color,
            font=("Consolas", 8),
            relief=tk.SUNKEN,
            bd=1,
            wrap=tk.WORD
        )
        self.log_text.grid(row=0, column=0, sticky="nsew")
    
    def log(self, message):
        """添加日志"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        
        # 限制日志行数，避免内存占用过大
        lines = int(self.log_text.index('end-1c').split('.')[0])
        if lines > 1000:
            self.log_text.delete(1.0, f"{lines - 500}.0")
        
        self.parent.update_idletasks()
    
    def clear(self):
        """清空日志"""
        self.log_text.delete(1.0, tk.END)

