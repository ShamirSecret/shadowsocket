"""服务器封装类 - 集成 EventLoop 和 TCPRelayExt"""
# 首先导入兼容性修复
from . import compat  # noqa: F401
import threading
import logging
from shadowsocks import eventloop, asyncdns
# 在 shadowsocks 导入后再次尝试修复 OpenSSL
compat._patch_shadowsocks_openssl()
from .tcprelay_ext import TCPRelayExt
from .stats.collector import StatsCollector


class ShadowsocksServer:
    """Shadowsocks 服务器 - 基于事件循环架构"""
    
    def __init__(self, config, stats_collector=None, log_callback=None):
        """
        初始化服务器
        
        Args:
            config: shadowsocks 配置字典
            stats_collector: 统计收集器实例
            log_callback: 日志回调函数
        """
        self.config = config
        self.stats_collector = stats_collector or StatsCollector()
        self.log_callback = log_callback
        
        self.eventloop = None
        self.tcp_relay = None
        self.dns_resolver = None
        self.server_thread = None
        self.running = False
        self._lock = threading.Lock()
    
    def _log(self, message):
        """记录日志"""
        if self.log_callback:
            self.log_callback(message)
        else:
            logging.info(message)
    
    def log_info(self, message):
        """记录信息日志"""
        self._log(f"INFO: {message}")
    
    def log_error(self, message):
        """记录错误日志"""
        self._log(f"ERROR: {message}")
    
    def log_warning(self, message):
        """记录警告日志"""
        self._log(f"WARNING: {message}")
    
    def _stats_callback(self, action, value=None, client_ip=None, target_addr=None):
        """统计回调"""
        if action == 'add_connection':
            self.stats_collector.add_connection(value, client_ip, target_addr)
        elif action == 'remove_connection':
            self.stats_collector.remove_connection(value)
        elif action == 'reject_connection':
            self.stats_collector.reject_connection()
        elif action == 'update_target_addr':
            # value 是 connection_id, client_ip 是 client_ip, target_addr 是 target_addr
            self.stats_collector.update_target_addr(value, target_addr)
        elif action == 'add_bytes_sent':
            self.stats_collector.add_bytes_sent(value, client_ip)  # client_ip 实际是 connection_id
        elif action == 'add_bytes_received':
            self.stats_collector.add_bytes_received(value, client_ip)  # client_ip 实际是 connection_id
    
    def start(self):
        """启动服务器"""
        with self._lock:
            if self.running:
                self._log("服务器已在运行")
                return False
            
            try:
                # 创建事件循环
                self.eventloop = eventloop.EventLoop()
                
                # 创建 DNS 解析器
                self.dns_resolver = asyncdns.DNSResolver()
                self.dns_resolver.add_to_loop(self.eventloop)
                
                # 创建 TCP 中继（服务端模式）
                max_connections = self.config.get('max_connections', 2000)
                self.tcp_relay = TCPRelayExt(
                    self.config,
                    self.dns_resolver,
                    is_local=False,  # 服务端模式
                    stats_callback=self._stats_callback,
                    log_callback=self._log,
                    max_connections=max_connections
                )
                
                # 添加到事件循环
                self.tcp_relay.add_to_loop(self.eventloop)
                
                # 启动事件循环（在独立线程中）
                self.running = True
                self.server_thread = threading.Thread(
                    target=self._run_eventloop,
                    daemon=True,
                    name="ShadowsocksServer"
                )
                self.server_thread.start()
                
                server_addr = self.config.get('server', '0.0.0.0')
                server_port = self.config.get('server_port', 1080)
                self.log_info(f"服务器启动成功，监听 {server_addr}:{server_port}")
                self.log_info(f"最大连接数: {max_connections}")
                self.log_info(f"连接空闲超时: {self.config.get('timeout', 43200)}秒")
                self.log_info(f"加密方法: {self.config.get('method', 'aes-256-cfb')}")
                
                return True
            except Exception as e:
                self._log(f"启动失败: {str(e)}")
                import traceback
                traceback.print_exc()
                self.running = False
                return False
    
    def _run_eventloop(self):
        """运行事件循环（在独立线程中）"""
        try:
            self.eventloop.run()
        except Exception as e:
            self._log(f"事件循环错误: {str(e)}")
            import traceback
            traceback.print_exc()
        finally:
            with self._lock:
                self.running = False
    
    def stop(self):
        """停止服务器"""
        with self._lock:
            if not self.running:
                return
            
            self.running = False
            
            # 停止事件循环
            if self.eventloop:
                self.eventloop.stop()
            
            # 关闭 TCP 中继
            if self.tcp_relay:
                self.tcp_relay.close(next_tick=False)
            
            # 关闭 DNS 解析器
            if self.dns_resolver:
                self.dns_resolver.close()
            
            # 等待线程结束
            if self.server_thread and self.server_thread.is_alive():
                self.server_thread.join(timeout=2.0)
            
            self._log("服务器已停止")
    
    def get_stats(self):
        """获取统计信息"""
        return self.stats_collector.get_stats()
    
    def is_running(self):
        """检查服务器是否运行中"""
        with self._lock:
            return self.running

