"""TCP relay extension - extends shadowsocks.tcprelay, adds statistics and connection limit"""
# Import compatibility fix first
from . import compat  # noqa: F401
import time
import logging
import threading
import errno
import socket
from shadowsocks import tcprelay, eventloop, shell


class TCPRelayHandlerExt(tcprelay.TCPRelayHandler):
    """Extended TCPRelayHandler with statistics callback"""
    
    def __init__(self, server, fd_to_handlers, loop, local_sock, config,
                 dns_resolver, is_local, stats_callback=None, log_callback=None):
        # Set attributes first to avoid errors when parent class calls methods during initialization
        self.stats_callback = stats_callback
        self.log_callback = log_callback
        self.connection_id = id(self)
        self.bytes_sent = 0
        self.bytes_received = 0
        self._start_time = time.time()  # Record connection start time
        
        # Record client address
        try:
            self.client_ip = local_sock.getpeername()[0] if local_sock else None
        except Exception:
            self.client_ip = None
        self.target_addr = None  # Will be set after connection is established
        
        # Call parent class initialization
        super().__init__(server, fd_to_handlers, loop, local_sock, config,
                        dns_resolver, is_local)
        
        # After connection is established, try to get target address
        self._update_target_addr()
    
    def _update_target_addr(self):
        """Update target address"""
        try:
            # In shadowsocks library, target address is stored in _remote_address attribute
            if hasattr(self, 'remote_address') and self.remote_address:
                # remote_address is a property that returns target address
                addr = self.remote_address
                if isinstance(addr, tuple) and len(addr) >= 2:
                    self.target_addr = f"{addr[0]}:{addr[1]}"
                elif addr:
                    self.target_addr = str(addr)
            elif hasattr(self, '_remote_address') and self._remote_address:
                # _remote_address format may be (host, port) or string
                if isinstance(self._remote_address, tuple) and len(self._remote_address) >= 2:
                    self.target_addr = f"{self._remote_address[0]}:{self._remote_address[1]}"
                else:
                    self.target_addr = str(self._remote_address)
            elif hasattr(self, '_remote_sock') and self._remote_sock:
                # If remote socket is connected, get address from socket
                try:
                    addr = self._remote_sock.getpeername()[:2]
                    self.target_addr = f"{addr[0]}:{addr[1]}"
                except Exception:
                    pass
        except Exception:
            pass
    
    def _update_activity(self, data_len=0):
        """Update activity time and call statistics callback"""
        super()._update_activity(data_len)
        
        # Update target address in stream stage (connection is established)
        if self._stage == tcprelay.STAGE_STREAM:
            old_target = self.target_addr
            # Try to update target address
            self._update_target_addr()
            
            # If target address is updated (from None to value, or from old to new), update statistics
            if self.target_addr and self.target_addr != old_target and self.stats_callback:
                # Update target address in connection info
                if hasattr(self, 'connection_id'):
                    # Update target address through callback
                    self.stats_callback('update_target_addr', self.connection_id, self.client_ip, self.target_addr)
        
        if self.stats_callback and data_len > 0:
            # Statistics traffic
            if self._stage == tcprelay.STAGE_STREAM:
                # In stream stage, statistics by data direction
                # Note: Cannot distinguish direction here, handled by TCPRelayExt in update_activity
                pass
    
    def _write_to_sock(self, data, sock):
        """Override write method, add traffic statistics"""
        if not data or not sock:
            return super()._write_to_sock(data, sock)
        
        bytes_count = len(data)
        # Call parent class method to write data first
        result = super()._write_to_sock(data, sock)
        
        # Statistics traffic (Note: parent class _write_to_sock may only write partial data, but here we count attempted write amount)
        # Actual written data amount is handled by parent class, here we count packet size
        if result and self.stats_callback and bytes_count > 0:
            # Ensure target address is updated (in stream stage)
            if self._stage == tcprelay.STAGE_STREAM:
                old_target = self.target_addr
                if not self.target_addr:
                    self._update_target_addr()
                else:
                    # Even if target address exists, try to update (in case address changes)
                    self._update_target_addr()
                
                # If target address is updated, update statistics immediately
                if self.target_addr and self.target_addr != old_target:
                    self.stats_callback('update_target_addr', self.connection_id, self.client_ip, self.target_addr)
            
            if sock == self._local_sock:
                # Send to client (data received from remote, encrypted then sent)
                # This is downstream traffic (server receives then sends to client)
                self.bytes_received += bytes_count
                # Pass connection_id as third parameter (for statistics)
                self.stats_callback('add_bytes_received', bytes_count, self.connection_id)
            elif sock == self._remote_sock:
                # Send to remote (data received from client, decrypted then sent)
                # This is upstream traffic (client sends to server then forwards to remote)
                self.bytes_sent += bytes_count
                # Pass connection_id as third parameter (for statistics)
                self.stats_callback('add_bytes_sent', bytes_count, self.connection_id)
        
        return result
    
    def _on_local_read(self):
        """Override local read"""
        # Call parent class method, traffic statistics handled in _write_to_sock
        super()._on_local_read()
    
    def _on_remote_read(self):
        """Override remote read"""
        # Call parent class method, traffic statistics handled in _write_to_sock
        super()._on_remote_read()
    
    def destroy(self):
        """Destroy connection, call statistics callback"""
        if self.stats_callback:
            self.stats_callback('remove_connection', self.connection_id)
        if self.log_callback:
            try:
                if hasattr(self, '_local_sock') and self._local_sock:
                    client_addr = self._local_sock.getpeername()[:2]
                    # Calculate connection duration
                    duration_str = ""
                    if hasattr(self, '_start_time'):
                        duration = time.time() - self._start_time
                        if duration < 1:
                            duration_str = f" (Duration: {duration*1000:.0f}ms)"
                        else:
                            duration_str = f" (Duration: {duration:.1f}s)"
                    
                    # Display target address
                    target_info = ""
                    if self.target_addr:
                        target_info = f" -> {self.target_addr}"
                    
                    self.log_callback(f"Client disconnected: {client_addr[0]}:{client_addr[1]}{target_info}{duration_str}")
                else:
                    self.log_callback("Client disconnected")
            except Exception:
                self.log_callback("Client disconnected")
        super().destroy()


class TCPRelayExt(tcprelay.TCPRelay):
    """Extended TCPRelay with connection limit and statistics"""
    
    def __init__(self, config, dns_resolver, is_local, 
                 stats_callback=None, log_callback=None, max_connections=2000):
        # Call parent class initialization
        super().__init__(config, dns_resolver, is_local)
        self.stats_callback = stats_callback
        self.log_callback = log_callback
        self.max_connections = max_connections
        self._connection_count_lock = threading.Lock()
    
    def _get_connection_count(self):
        """Get current connection count"""
        # _fd_to_handlers contains server socket and all client connections
        # Server socket handler is self, client connection handlers are TCPRelayHandlerExt instances
        with self._connection_count_lock:
            count = len(self._fd_to_handlers)
            # If server socket is in _fd_to_handlers, subtract 1
            if self._server_socket and self._server_socket.fileno() in self._fd_to_handlers:
                count -= 1
            return max(0, count)
    
    def handle_event(self, sock, fd, event):
        """Handle event, add connection limit"""
        if sock == self._server_socket:
            if event & eventloop.POLL_ERR:
                raise Exception('server_socket error')
            
            # Check connection limit
            current_count = self._get_connection_count()
            if current_count >= self.max_connections:
                if self.log_callback:
                    self.log_callback(f"Connection limit exceeded ({current_count}/{self.max_connections}), rejecting new connection")
                if self.stats_callback:
                    self.stats_callback('reject_connection', None)
                # Accept connection then close immediately
                try:
                    conn = self._server_socket.accept()
                    conn[0].close()
                except:
                    pass
                return
            
            try:
                conn = self._server_socket.accept()
                # Create extended Handler
                handler = TCPRelayHandlerExt(
                    self, self._fd_to_handlers,
                    self._eventloop, conn[0], self._config,
                    self._dns_resolver, self._is_local,
                    stats_callback=self._stats_wrapper,
                    log_callback=self.log_callback
                )
                # Notify connection established (after handler created, connection count is updated)
                current_count = self._get_connection_count()
                if self.stats_callback:
                    # Pass client IP and target address (target address may not be established yet, will update later)
                    client_ip = handler.client_ip if hasattr(handler, 'client_ip') else None
                    target_addr = handler.target_addr if hasattr(handler, 'target_addr') else None
                    # Use _stats_wrapper to pass parameters
                    self._stats_wrapper('add_connection', handler.connection_id, client_ip, target_addr)
                if self.log_callback:
                    try:
                        client_addr = conn[0].getpeername()[:2]
                        self.log_callback(f"New client connected: {client_addr[0]}:{client_addr[1]} "
                                        f"(Current: {current_count}/{self.max_connections})")
                    except Exception:
                        self.log_callback(f"New client connected (Current: {current_count}/{self.max_connections})")
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
        """Statistics callback wrapper"""
        if self.stats_callback:
            self.stats_callback(action, value, client_ip, target_addr)
    
    def update_activity(self, handler, data_len):
        """Update activity time, add traffic statistics"""
        # Call parent class method
        super().update_activity(handler, data_len)
        
        # Add traffic statistics
        if data_len > 0 and self.stats_callback:
            # Note: Cannot distinguish direction here, but can get from handler bytes_sent/received
            # Actual statistics completed in TCPRelayHandlerExt._write_to_sock
            pass
    
    def remove_handler(self, handler):
        """Remove handler"""
        super().remove_handler(handler)
        # Notify connection closed
        if isinstance(handler, TCPRelayHandlerExt) and self.stats_callback:
            self.stats_callback('remove_connection', handler.connection_id)

