"""Flask web application"""
from flask import Flask, render_template, jsonify, request
import threading
import json
import os
from ..server import ShadowsocksServer
from ..config.manager import ConfigManager
from ..stats.collector import StatsCollector


class WebApp:
    """Flask web application wrapper"""
    
    def __init__(self, host='127.0.0.1', port=5000):
        self.host = host
        self.port = port
        # Get the directory where this file is located
        import os
        web_dir = os.path.dirname(os.path.abspath(__file__))
        self.app = Flask(__name__, 
                        template_folder=os.path.join(web_dir, 'templates'),
                        static_folder=os.path.join(web_dir, 'static'))
        self.server = None
        self.stats_collector = StatsCollector()
        self.config_manager = ConfigManager()
        self.server_lock = threading.Lock()
        self.logs = []  # 存储日志
        self.max_logs = 500  # 最大日志条数
        self.logs_lock = threading.Lock()
        
        # Register routes
        self._register_routes()
    
    def _register_routes(self):
        """Register Flask routes"""
        
        @self.app.route('/')
        def index():
            """Main page"""
            return render_template('index.html')
        
        @self.app.route('/api/config', methods=['GET'])
        def get_config():
            """Get current configuration"""
            config = self.config_manager.load()
            # Don't expose password in response
            safe_config = config.copy()
            safe_config['password'] = '***' if config.get('password') else ''
            return jsonify(safe_config)
        
        @self.app.route('/api/config', methods=['POST'])
        def update_config():
            """Update configuration"""
            try:
                data = request.json
                current_config = self.config_manager.load()
                
                # Handle password: if empty or '***', keep existing password
                if not data.get('password') or data.get('password') == '***' or data.get('password').strip() == '':
                    # Keep existing password if not provided
                    data['password'] = current_config.get('password', '')
                # Otherwise use the new password
                
                self.config_manager.save(data)
                return jsonify({'success': True, 'message': 'Configuration saved'})
            except Exception as e:
                return jsonify({'success': False, 'message': str(e)}), 400
        
        @self.app.route('/api/server/start', methods=['POST'])
        def start_server():
            """Start the server"""
            with self.server_lock:
                if self.server and self.server.is_running():
                    return jsonify({'success': False, 'message': 'Server is already running'}), 400
                
                try:
                    config = self.config_manager.load()
                    
                    # Validate configuration
                    if not config.get('password'):
                        return jsonify({'success': False, 'message': 'Password is required'}), 400
                    
                    if not config.get('server_port') or config['server_port'] < 1 or config['server_port'] > 65535:
                        return jsonify({'success': False, 'message': 'Invalid port number'}), 400
                    
                    # Create and start server
                    self.server = ShadowsocksServer(
                        config,
                        stats_collector=self.stats_collector,
                        log_callback=self._log_callback
                    )
                    
                    if self.server.start():
                        return jsonify({'success': True, 'message': 'Server started successfully'})
                    else:
                        return jsonify({'success': False, 'message': 'Failed to start server'}), 500
                        
                except Exception as e:
                    return jsonify({'success': False, 'message': str(e)}), 500
        
        @self.app.route('/api/server/stop', methods=['POST'])
        def stop_server():
            """Stop the server"""
            with self.server_lock:
                if not self.server or not self.server.is_running():
                    return jsonify({'success': False, 'message': 'Server is not running'}), 400
                
                try:
                    self.server.stop()
                    self.server = None
                    self.stats_collector.reset()
                    return jsonify({'success': True, 'message': 'Server stopped successfully'})
                except Exception as e:
                    return jsonify({'success': False, 'message': str(e)}), 500
        
        @self.app.route('/api/server/status', methods=['GET'])
        def get_server_status():
            """Get server status"""
            with self.server_lock:
                is_running = self.server is not None and self.server.is_running()
                stats = self.stats_collector.get_stats() if self.stats_collector else {}
                
                return jsonify({
                    'running': is_running,
                    'stats': stats
                })
        
        @self.app.route('/api/logs', methods=['GET'])
        def get_logs():
            """Get server logs"""
            with self.logs_lock:
                # 返回最近的日志（倒序，最新的在前）
                return jsonify({'logs': self.logs[-100:]})  # 返回最近100条
    
    def _log_callback(self, message):
        """Log callback for server"""
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        
        # 打印到控制台
        print(f"[SERVER] {message}")
        
        # 存储到日志列表
        with self.logs_lock:
            self.logs.append(log_entry)
            # 限制日志数量，避免内存占用过大
            if len(self.logs) > self.max_logs:
                self.logs = self.logs[-self.max_logs:]
    
    def run(self, debug=False):
        """Run the Flask app"""
        self.app.run(host=self.host, port=self.port, debug=debug, threaded=True)
    
    def stop(self):
        """Stop the Flask app and server"""
        with self.server_lock:
            if self.server and self.server.is_running():
                self.server.stop()
                self.server = None

