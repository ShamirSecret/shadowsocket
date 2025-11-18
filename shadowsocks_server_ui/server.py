"""Server wrapper class - integrates EventLoop and TCPRelayExt"""
# Import compatibility fix first
try:
    from shadowsocks_server_ui import compat  # noqa: F401
except ImportError:
    from . import compat  # noqa: F401

import threading
import logging
from shadowsocks import eventloop, asyncdns
# Try to fix OpenSSL again after shadowsocks import
compat._patch_shadowsocks_openssl()

try:
    from shadowsocks_server_ui.tcprelay_ext import TCPRelayExt
    from shadowsocks_server_ui.stats.collector import StatsCollector
except ImportError:
    from .tcprelay_ext import TCPRelayExt
    from .stats.collector import StatsCollector


class ShadowsocksServer:
    """Shadowsocks server - based on event loop architecture"""
    
    def __init__(self, config, stats_collector=None, log_callback=None):
        """
        Initialize server
        
        Args:
            config: shadowsocks configuration dictionary
            stats_collector: statistics collector instance
            log_callback: log callback function
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
        """Log message"""
        if self.log_callback:
            self.log_callback(message)
        else:
            logging.info(message)
    
    def log_info(self, message):
        """Log info message"""
        self._log(f"INFO: {message}")
    
    def log_error(self, message):
        """Log error message"""
        self._log(f"ERROR: {message}")
    
    def log_warning(self, message):
        """Log warning message"""
        self._log(f"WARNING: {message}")
    
    def _stats_callback(self, action, value=None, client_ip=None, target_addr=None):
        """Statistics callback"""
        if action == 'add_connection':
            self.stats_collector.add_connection(value, client_ip, target_addr)
        elif action == 'remove_connection':
            self.stats_collector.remove_connection(value)
        elif action == 'reject_connection':
            self.stats_collector.reject_connection()
        elif action == 'update_target_addr':
            # value is connection_id, client_ip is client_ip, target_addr is target_addr
            self.stats_collector.update_target_addr(value, target_addr)
        elif action == 'add_bytes_sent':
            self.stats_collector.add_bytes_sent(value, client_ip)  # client_ip is actually connection_id
        elif action == 'add_bytes_received':
            self.stats_collector.add_bytes_received(value, client_ip)  # client_ip is actually connection_id
    
    def start(self):
        """Start server"""
        with self._lock:
            if self.running:
                self._log("Server is already running")
                return False
            
            try:
                # Create event loop
                self.eventloop = eventloop.EventLoop()
                
                # Create DNS resolver
                self.dns_resolver = asyncdns.DNSResolver()
                self.dns_resolver.add_to_loop(self.eventloop)
                
                # Create TCP relay (server mode)
                max_connections = self.config.get('max_connections', 2000)
                self.tcp_relay = TCPRelayExt(
                    self.config,
                    self.dns_resolver,
                    is_local=False,  # Server mode
                    stats_callback=self._stats_callback,
                    log_callback=self._log,
                    max_connections=max_connections
                )
                
                # Add to event loop
                self.tcp_relay.add_to_loop(self.eventloop)
                
                # Start event loop (in separate thread)
                self.running = True
                self.server_thread = threading.Thread(
                    target=self._run_eventloop,
                    daemon=True,
                    name="ShadowsocksServer"
                )
                self.server_thread.start()
                
                server_addr = self.config.get('server', '0.0.0.0')
                server_port = self.config.get('server_port', 1080)
                self.log_info(f"Server started successfully, listening on {server_addr}:{server_port}")
                self.log_info(f"Max connections: {max_connections}")
                self.log_info(f"Idle timeout: {self.config.get('timeout', 43200)} seconds")
                self.log_info(f"Encryption method: {self.config.get('method', 'aes-256-cfb')}")
                
                return True
            except Exception as e:
                self._log(f"Failed to start: {str(e)}")
                import traceback
                traceback.print_exc()
                self.running = False
                return False
    
    def _run_eventloop(self):
        """Run event loop (in separate thread)"""
        try:
            self.eventloop.run()
        except Exception as e:
            self._log(f"Event loop error: {str(e)}")
            import traceback
            traceback.print_exc()
        finally:
            with self._lock:
                self.running = False
    
    def stop(self):
        """Stop server"""
        with self._lock:
            if not self.running:
                return
            
            self.running = False
            
            # Stop event loop
            if self.eventloop:
                self.eventloop.stop()
            
            # Close TCP relay
            if self.tcp_relay:
                self.tcp_relay.close(next_tick=False)
            
            # Close DNS resolver
            if self.dns_resolver:
                self.dns_resolver.close()
            
            # Wait for thread to finish
            if self.server_thread and self.server_thread.is_alive():
                self.server_thread.join(timeout=2.0)
            
            self._log("Server stopped")
    
    def get_stats(self):
        """Get statistics"""
        return self.stats_collector.get_stats()
    
    def is_running(self):
        """Check if server is running"""
        with self._lock:
            return self.running

