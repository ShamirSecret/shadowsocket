// Shadowsocks Server UI - Frontend JavaScript

class ShadowsocksUI {
    constructor() {
        this.apiBase = '/api';
        this.updateInterval = null;
        this.init();
    }

    init() {
        this.loadConfig();
        this.setupEventListeners();
        this.startStatusUpdates();
    }

    setupEventListeners() {
        // Start/Stop buttons
        document.getElementById('start-btn').addEventListener('click', () => this.startServer());
        document.getElementById('stop-btn').addEventListener('click', () => this.stopServer());
        
        // Config form
        document.getElementById('config-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.saveConfig();
        });
        
        // Password toggle button
        const togglePasswordBtn = document.getElementById('toggle-password');
        if (togglePasswordBtn) {
            togglePasswordBtn.addEventListener('click', () => {
                const passwordInput = document.getElementById('password');
                if (passwordInput.type === 'password') {
                    passwordInput.type = 'text';
                    togglePasswordBtn.textContent = '🙈';
                } else {
                    passwordInput.type = 'password';
                    togglePasswordBtn.textContent = '👁️';
                }
            });
        }
    }

    async loadConfig() {
        try {
            const response = await fetch(`${this.apiBase}/config`);
            const config = await response.json();
            
            // Populate form
            Object.keys(config).forEach(key => {
                const element = document.getElementById(key);
                if (element) {
                    if (key === 'password') {
                        // Password field: If returned value is '***', password exists, set placeholder hint
                        if (config[key] === '***') {
                            element.value = '';
                            element.placeholder = 'Password is set (enter new password to change)';
                        } else {
                            element.value = config[key];
                            element.placeholder = '';
                        }
                    } else if (config[key] !== '***') {
                        element.value = config[key];
                    }
                }
            });
        } catch (error) {
            this.addLog(`Error loading config: ${error.message}`, 'error');
        }
    }

    async saveConfig() {
        const form = document.getElementById('config-form');
        const formData = new FormData(form);
        const config = {};
        
        formData.forEach((value, key) => {
            if (key === 'server_port' || key === 'max_connections' || 
                key === 'timeout' || key === 'target_connect_timeout') {
                config[key] = parseInt(value);
            } else {
                config[key] = value;
            }
        });

        try {
            const response = await fetch(`${this.apiBase}/config`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(config)
            });

            const result = await response.json();
            if (result.success) {
                this.addLog('Configuration saved successfully', 'success');
                this.showNotification('Configuration saved', 'success');
            } else {
                this.addLog(`Error: ${result.message}`, 'error');
                this.showNotification(result.message, 'error');
            }
        } catch (error) {
            this.addLog(`Error saving config: ${error.message}`, 'error');
            this.showNotification('Failed to save configuration', 'error');
        }
    }

    async startServer() {
        try {
            const response = await fetch(`${this.apiBase}/server/start`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });

            const result = await response.json();
            if (result.success) {
                this.addLog('Server started successfully', 'success');
                this.updateServerStatus(true);
                this.showNotification('Server started', 'success');
            } else {
                this.addLog(`Failed to start server: ${result.message}`, 'error');
                this.showNotification(result.message, 'error');
            }
        } catch (error) {
            this.addLog(`Error starting server: ${error.message}`, 'error');
            this.showNotification('Failed to start server', 'error');
        }
    }

    async stopServer() {
        try {
            const response = await fetch(`${this.apiBase}/server/stop`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });

            const result = await response.json();
            if (result.success) {
                this.addLog('Server stopped successfully', 'info');
                this.updateServerStatus(false);
                this.showNotification('Server stopped', 'info');
            } else {
                this.addLog(`Failed to stop server: ${result.message}`, 'error');
                this.showNotification(result.message, 'error');
            }
        } catch (error) {
            this.addLog(`Error stopping server: ${error.message}`, 'error');
            this.showNotification('Failed to stop server', 'error');
        }
    }

    async updateStatus() {
        try {
            const response = await fetch(`${this.apiBase}/server/status`);
            const data = await response.json();
            
            if (data.running) {
                this.updateServerStatus(true);
                this.updateStatistics(data.stats);
            } else {
                this.updateServerStatus(false);
            }
        } catch (error) {
            console.error('Error updating status:', error);
        }
    }

    updateServerStatus(running) {
        const statusDot = document.getElementById('status-dot');
        const statusText = document.getElementById('status-text');
        const startBtn = document.getElementById('start-btn');
        const stopBtn = document.getElementById('stop-btn');

        if (running) {
            statusDot.className = 'dot running';
            statusText.textContent = 'Running';
            startBtn.disabled = true;
            stopBtn.disabled = false;
        } else {
            statusDot.className = 'dot stopped';
            statusText.textContent = 'Stopped';
            startBtn.disabled = false;
            stopBtn.disabled = true;
        }
    }

    updateStatistics(stats) {
        if (!stats) return;

        // Calculate total active connections (sum of all clients' active connections)
        const clientStats = stats.client_stats || [];
        const totalActiveConnections = clientStats.reduce((sum, client) => sum + (client.active_connections || 0), 0);
        
        const maxConn = stats.max_connections || 0;
        // Current Connections display: total active connections / max connections
        document.getElementById('current-connections').textContent = 
            `${totalActiveConnections}/${maxConn}`;
        document.getElementById('total-connections').textContent = 
            stats.total_connections || 0;
        document.getElementById('rejected-connections').textContent = 
            stats.rejected_connections || 0;
        document.getElementById('closed-connections').textContent = 
            stats.closed_connections || 0;
        document.getElementById('bytes-sent').textContent = 
            this.formatBytes(stats.bytes_sent || 0);
        document.getElementById('bytes-received').textContent = 
            this.formatBytes(stats.bytes_received || 0);
        document.getElementById('total-traffic').textContent = 
            this.formatBytes(stats.total_traffic || 0);
        document.getElementById('uptime').textContent = 
            this.formatUptime(stats.uptime || 0);
        
        // Update client statistics
        this.updateClientStats(stats.client_stats || []);
    }

    updateClientStats(clientStats) {
        const container = document.getElementById('client-stats-container');
        if (!container) return;

        if (!clientStats || clientStats.length === 0) {
            container.innerHTML = '<div class="no-data">No active clients</div>';
            return;
        }

        let html = '';
        clientStats.forEach(client => {
            html += `<div class="client-stat-item">`;
            html += `<div class="client-stat-header">`;
            html += `<span class="client-ip">${client.client_ip}</span>`;
            html += `<span class="client-conn-info">${client.active_connections} active connection(s)</span>`;
            html += `</div>`;
            html += `<div class="client-traffic">`;
            html += `<span class="traffic-item"><span class="traffic-label">↑</span>${this.formatBytes(client.total_bytes_sent || 0)}</span>`;
            html += `<span class="traffic-item"><span class="traffic-label">↓</span>${this.formatBytes(client.total_bytes_received || 0)}</span>`;
            html += `<span class="traffic-item"><span class="traffic-label">Total:</span>${this.formatBytes(client.total_bytes || 0)}</span>`;
            html += `</div>`;
            
            if (client.targets && client.targets.length > 0) {
                html += `<div class="target-list">`;
                client.targets.forEach(target => {
                    html += `<div class="target-item">`;
                    html += `<span class="target-address">${target.address}</span>`;
                    html += `<span class="target-traffic">`;
                    html += `${target.active_connections} conn · ${this.formatBytes(target.total_bytes || 0)}`;
                    html += `</span>`;
                    html += `</div>`;
                });
                html += `</div>`;
            }
            
            html += `</div>`;
        });

        container.innerHTML = html;
    }

    formatBytes(bytes) {
        if (bytes === 0) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
    }

    formatUptime(seconds) {
        const hours = Math.floor(seconds / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);
        const secs = seconds % 60;
        return `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
    }

    addLog(message, type = 'info') {
        const logsContainer = document.getElementById('logs-container');
        const timestamp = new Date().toLocaleTimeString();
        const logEntry = document.createElement('div');
        logEntry.className = `log-entry log-${type}`;
        logEntry.textContent = `[${timestamp}] ${message}`;
        logsContainer.appendChild(logEntry);
        logsContainer.scrollTop = logsContainer.scrollHeight;

        // Keep only last 100 log entries
        while (logsContainer.children.length > 100) {
            logsContainer.removeChild(logsContainer.firstChild);
        }
    }

    showNotification(message, type = 'info') {
        // Simple notification (can be enhanced with toast library)
        console.log(`[${type.toUpperCase()}] ${message}`);
    }

    startStatusUpdates() {
        // Update status every second
        this.updateInterval = setInterval(() => {
            this.updateStatus();
            this.updateLogs();  // Also update logs
        }, 1000);
        
        // Initial update
        this.updateStatus();
        this.updateLogs();
    }
    
    async updateLogs() {
        try {
            const response = await fetch(`${this.apiBase}/logs`);
            const data = await response.json();
            
            if (data.logs && data.logs.length > 0) {
                const logsContainer = document.getElementById('logs-container');
                const currentLogs = Array.from(logsContainer.children).map(el => el.textContent);
                
                // Only add new logs
                data.logs.forEach(log => {
                    if (!currentLogs.includes(log)) {
                        const logEntry = document.createElement('div');
                        logEntry.className = 'log-entry';
                        logEntry.textContent = log;
                        logsContainer.appendChild(logEntry);
                    }
                });
                
                // Keep scrolling to bottom
                logsContainer.scrollTop = logsContainer.scrollHeight;
                
                // Limit displayed log count (avoid too many DOM elements)
                while (logsContainer.children.length > 200) {
                    logsContainer.removeChild(logsContainer.firstChild);
                }
            }
        } catch (error) {
            console.error('Error updating logs:', error);
        }
    }

    stopStatusUpdates() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
            this.updateInterval = null;
        }
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.app = new ShadowsocksUI();
});

