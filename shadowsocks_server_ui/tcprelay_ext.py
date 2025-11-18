"""TCP 中继扩展 - 继承 shadowsocks.tcprelay，添加统计和连接数限制"""
# 首先导入兼容性修复
from . import compat  # noqa: F401
import time
import logging
import threading
import errno
import socket
from shadowsocks import tcprelay, eventloop, shell


class TCPRelayHandlerExt(tcprelay.TCPRelayHandler):
    """扩展的 TCPRelayHandler，添加统计回调"""
    
    def __init__(self, server, fd_to_handlers, loop, local_sock, config,
                 dns_resolver, is_local, stats_callback=None, log_callback=None):
        # 先设置属性，避免父类初始化时调用方法时出错
        self.stats_callback = stats_callback
        self.log_callback = log_callback
        self.connection_id = id(self)
        self.bytes_sent = 0
        self.bytes_received = 0
        self._start_time = time.time()  # 记录连接开始时间
        
        # 记录客户端地址
        try:
            self.client_ip = local_sock.getpeername()[0] if local_sock else None
        except Exception:
            self.client_ip = None
        self.target_addr = None  # 将在连接建立后设置
        
        # 调用父类初始化
        super().__init__(server, fd_to_handlers, loop, local_sock, config,
                        dns_resolver, is_local)
        
        # 连接建立后，尝试获取目标地址
        self._update_target_addr()
    
    def _update_target_addr(self):
        """更新目标地址"""
        try:
            # shadowsocks 库中，目标地址存储在 _remote_address 属性中
            if hasattr(self, 'remote_address') and self.remote_address:
                # remote_address 是一个属性，返回目标地址
                addr = self.remote_address
                if isinstance(addr, tuple) and len(addr) >= 2:
                    self.target_addr = f"{addr[0]}:{addr[1]}"
                elif addr:
                    self.target_addr = str(addr)
            elif hasattr(self, '_remote_address') and self._remote_address:
                # _remote_address 格式可能是 (host, port) 或字符串
                if isinstance(self._remote_address, tuple) and len(self._remote_address) >= 2:
                    self.target_addr = f"{self._remote_address[0]}:{self._remote_address[1]}"
                else:
                    self.target_addr = str(self._remote_address)
            elif hasattr(self, '_remote_sock') and self._remote_sock:
                # 如果远程 socket 已连接，从 socket 获取地址
                try:
                    addr = self._remote_sock.getpeername()[:2]
                    self.target_addr = f"{addr[0]}:{addr[1]}"
                except Exception:
                    pass
        except Exception:
            pass
    
    def _update_activity(self, data_len=0):
        """更新活动时间，并调用统计回调"""
        super()._update_activity(data_len)
        
        # 在流阶段更新目标地址（此时连接已建立）
        if self._stage == tcprelay.STAGE_STREAM:
            old_target = self.target_addr
            # 尝试更新目标地址
            self._update_target_addr()
            
            # 如果目标地址已更新（从 None 变为有值，或从旧值变为新值），更新统计
            if self.target_addr and self.target_addr != old_target and self.stats_callback:
                # 更新连接信息中的目标地址
                if hasattr(self, 'connection_id'):
                    # 通过回调更新目标地址
                    self.stats_callback('update_target_addr', self.connection_id, self.client_ip, self.target_addr)
        
        if self.stats_callback and data_len > 0:
            # 统计流量
            if self._stage == tcprelay.STAGE_STREAM:
                # 在流阶段，根据数据方向统计
                # 注意：这里无法区分方向，由 TCPRelayExt 在 update_activity 中处理
                pass
    
    def _write_to_sock(self, data, sock):
        """重写写入方法，添加流量统计"""
        if not data or not sock:
            return super()._write_to_sock(data, sock)
        
        bytes_count = len(data)
        # 先调用父类方法写入数据
        result = super()._write_to_sock(data, sock)
        
        # 统计流量（注意：父类的 _write_to_sock 可能只写入部分数据，但这里统计的是尝试写入的数据量）
        # 实际写入的数据量由父类处理，这里统计的是数据包大小
        if result and self.stats_callback and bytes_count > 0:
            # 确保目标地址已更新（在流阶段）
            if self._stage == tcprelay.STAGE_STREAM:
                old_target = self.target_addr
                if not self.target_addr:
                    self._update_target_addr()
                else:
                    # 即使已有目标地址，也尝试更新（以防地址变化）
                    self._update_target_addr()
                
                # 如果目标地址已更新，立即更新统计
                if self.target_addr and self.target_addr != old_target:
                    self.stats_callback('update_target_addr', self.connection_id, self.client_ip, self.target_addr)
            
            if sock == self._local_sock:
                # 发送到客户端（从远程接收的数据，加密后发送）
                # 这是下行流量（服务器接收后发送给客户端）
                self.bytes_received += bytes_count
                # 传递 connection_id 作为第三个参数（用于统计）
                self.stats_callback('add_bytes_received', bytes_count, self.connection_id)
            elif sock == self._remote_sock:
                # 发送到远程（从客户端接收的数据，解密后发送）
                # 这是上行流量（客户端发送给服务器后转发给远程）
                self.bytes_sent += bytes_count
                # 传递 connection_id 作为第三个参数（用于统计）
                self.stats_callback('add_bytes_sent', bytes_count, self.connection_id)
        
        return result
    
    def _on_local_read(self):
        """重写本地读取"""
        # 调用父类方法，流量统计在 _write_to_sock 中处理
        super()._on_local_read()
    
    def _on_remote_read(self):
        """重写远程读取"""
        # 调用父类方法，流量统计在 _write_to_sock 中处理
        super()._on_remote_read()
    
    def destroy(self):
        """销毁连接，调用统计回调"""
        if self.stats_callback:
            self.stats_callback('remove_connection', self.connection_id)
        if self.log_callback:
            try:
                if hasattr(self, '_local_sock') and self._local_sock:
                    client_addr = self._local_sock.getpeername()[:2]
                    # 计算连接持续时间
                    duration_str = ""
                    if hasattr(self, '_start_time'):
                        duration = time.time() - self._start_time
                        if duration < 1:
                            duration_str = f" (持续: {duration*1000:.0f}ms)"
                        else:
                            duration_str = f" (持续: {duration:.1f}秒)"
                    
                    # 显示目标地址
                    target_info = ""
                    if self.target_addr:
                        target_info = f" -> {self.target_addr}"
                    
                    self.log_callback(f"客户端断开连接: {client_addr[0]}:{client_addr[1]}{target_info}{duration_str}")
                else:
                    self.log_callback("客户端断开连接")
            except Exception:
                self.log_callback("客户端断开连接")
        super().destroy()


class TCPRelayExt(tcprelay.TCPRelay):
    """扩展的 TCPRelay，添加连接数限制和统计"""
    
    def __init__(self, config, dns_resolver, is_local, 
                 stats_callback=None, log_callback=None, max_connections=2000):
        # 调用父类初始化
        super().__init__(config, dns_resolver, is_local)
        self.stats_callback = stats_callback
        self.log_callback = log_callback
        self.max_connections = max_connections
        self._connection_count_lock = threading.Lock()
    
    def _get_connection_count(self):
        """获取当前连接数"""
        # _fd_to_handlers 包含服务器 socket 和所有客户端连接
        # 服务器 socket 的 handler 是 self，客户端连接的 handler 是 TCPRelayHandlerExt 实例
        with self._connection_count_lock:
            count = len(self._fd_to_handlers)
            # 如果服务器 socket 在 _fd_to_handlers 中，减去1
            if self._server_socket and self._server_socket.fileno() in self._fd_to_handlers:
                count -= 1
            return max(0, count)
    
    def handle_event(self, sock, fd, event):
        """处理事件，添加连接数限制"""
        if sock == self._server_socket:
            if event & eventloop.POLL_ERR:
                raise Exception('server_socket error')
            
            # 检查连接数限制
            current_count = self._get_connection_count()
            if current_count >= self.max_connections:
                if self.log_callback:
                    self.log_callback(f"连接数超限 ({current_count}/{self.max_connections})，拒绝新连接")
                if self.stats_callback:
                    self.stats_callback('reject_connection', None)
                # 接受连接后立即关闭
                try:
                    conn = self._server_socket.accept()
                    conn[0].close()
                except:
                    pass
                return
            
            try:
                conn = self._server_socket.accept()
                # 创建扩展的 Handler
                handler = TCPRelayHandlerExt(
                    self, self._fd_to_handlers,
                    self._eventloop, conn[0], self._config,
                    self._dns_resolver, self._is_local,
                    stats_callback=self._stats_wrapper,
                    log_callback=self.log_callback
                )
                # 通知连接建立（在 handler 创建后，连接数已更新）
                current_count = self._get_connection_count()
                if self.stats_callback:
                    # 传递客户端 IP 和目标地址（目标地址可能还未建立，稍后更新）
                    client_ip = handler.client_ip if hasattr(handler, 'client_ip') else None
                    target_addr = handler.target_addr if hasattr(handler, 'target_addr') else None
                    # 使用 _stats_wrapper 传递参数
                    self._stats_wrapper('add_connection', handler.connection_id, client_ip, target_addr)
                if self.log_callback:
                    try:
                        client_addr = conn[0].getpeername()[:2]
                        self.log_callback(f"新客户端连接: {client_addr[0]}:{client_addr[1]} "
                                        f"(当前: {current_count}/{self.max_connections})")
                    except Exception:
                        self.log_callback(f"新客户端连接 (当前: {current_count}/{self.max_connections})")
            except Exception as e:
                error_no = eventloop.errno_from_exception(e)
                if error_no in (errno.EAGAIN, errno.EINPROGRESS, errno.EWOULDBLOCK):
                    return
                else:
                    shell.print_exception(e)
                    if self._config['verbose']:
                        import traceback
                        traceback.print_exc()
        else:
            if sock:
                handler = self._fd_to_handlers.get(fd, None)
                if handler:
                    handler.handle_event(sock, event)
            else:
                logging.warn('poll removed fd')
    
    def _stats_wrapper(self, action, value=None, client_ip=None, target_addr=None):
        """统计回调包装器"""
        if self.stats_callback:
            self.stats_callback(action, value, client_ip, target_addr)
    
    def update_activity(self, handler, data_len):
        """更新活动时间，添加流量统计"""
        # 调用父类方法
        super().update_activity(handler, data_len)
        
        # 添加流量统计
        if data_len > 0 and self.stats_callback:
            # 注意：这里无法区分方向，但可以通过 handler 的 bytes_sent/received 获取
            # 实际统计在 TCPRelayHandlerExt._write_to_sock 中完成
            pass
    
    def remove_handler(self, handler):
        """移除处理器"""
        super().remove_handler(handler)
        # 通知连接关闭
        if isinstance(handler, TCPRelayHandlerExt) and self.stats_callback:
            self.stats_callback('remove_connection', handler.connection_id)

