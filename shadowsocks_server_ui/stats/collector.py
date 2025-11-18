"""统计信息收集器"""
import time
import threading
from collections import defaultdict


class StatsCollector:
    """统计信息收集器"""
    
    def __init__(self):
        self.lock = threading.Lock()
        self.stats = {
            'total_connections': 0,
            'active_connections': 0,
            'rejected_connections': 0,
            'closed_connections': 0,
            'bytes_sent': 0,
            'bytes_received': 0,
            'start_time': time.time(),
        }
        self.connection_times = {}  # connection_id -> connect_time
    
    def add_connection(self, connection_id):
        """添加连接"""
        with self.lock:
            self.stats['total_connections'] += 1
            self.stats['active_connections'] += 1
            self.connection_times[connection_id] = time.time()
    
    def remove_connection(self, connection_id):
        """移除连接"""
        with self.lock:
            if connection_id in self.connection_times:
                del self.connection_times[connection_id]
            self.stats['active_connections'] = max(0, self.stats['active_connections'] - 1)
            self.stats['closed_connections'] += 1
    
    def reject_connection(self):
        """拒绝连接"""
        with self.lock:
            self.stats['rejected_connections'] += 1
    
    def add_bytes_sent(self, bytes_count):
        """增加发送字节数"""
        with self.lock:
            self.stats['bytes_sent'] += bytes_count
    
    def add_bytes_received(self, bytes_count):
        """增加接收字节数"""
        with self.lock:
            self.stats['bytes_received'] += bytes_count
    
    def get_stats(self):
        """获取统计信息"""
        with self.lock:
            return {
                'current_connections': self.stats['active_connections'],
                'total_connections': self.stats['total_connections'],
                'rejected_connections': self.stats['rejected_connections'],
                'closed_connections': self.stats['closed_connections'],
                'bytes_sent': self.stats['bytes_sent'],
                'bytes_received': self.stats['bytes_received'],
                'total_traffic': self.stats['bytes_sent'] + self.stats['bytes_received'],
                'uptime': int(time.time() - self.stats['start_time']),
            }
    
    def reset(self):
        """重置统计"""
        with self.lock:
            self.stats = {
                'total_connections': 0,
                'active_connections': 0,
                'rejected_connections': 0,
                'closed_connections': 0,
                'bytes_sent': 0,
                'bytes_received': 0,
                'start_time': time.time(),
            }
            self.connection_times.clear()

