"""Statistics collector"""
import time
import threading
from collections import defaultdict


class StatsCollector:
    """Statistics collector"""
    
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
        # Statistics for each client IP
        self.client_stats = {}  # client_ip -> {
        #     'connections': set of connection_ids,
        #     'total_bytes_sent': int,
        #     'total_bytes_received': int,
        #     'targets': {target_addr: {'connections': int, 'bytes_sent': int, 'bytes_received': int}}
        # }
    
    def add_connection(self, connection_id, client_ip=None, target_addr=None):
        """Add connection"""
        with self.lock:
            self.stats['total_connections'] += 1
            self.stats['active_connections'] += 1
            self.connection_times[connection_id] = {
                'time': time.time(),
                'client_ip': client_ip,
                'target_addr': target_addr
            }
            
            # Update client statistics
            if client_ip:
                if client_ip not in self.client_stats:
                    self.client_stats[client_ip] = {
                        'connections': set(),
                        'total_bytes_sent': 0,
                        'total_bytes_received': 0,
                        'targets': {}
                    }
                self.client_stats[client_ip]['connections'].add(connection_id)
                
                # Update target address statistics
                if target_addr:
                    if target_addr not in self.client_stats[client_ip]['targets']:
                        self.client_stats[client_ip]['targets'][target_addr] = {
                            'connections': 0,
                            'bytes_sent': 0,
                            'bytes_received': 0
                        }
                    self.client_stats[client_ip]['targets'][target_addr]['connections'] += 1
    
    def remove_connection(self, connection_id):
        """Remove connection"""
        with self.lock:
            conn_info = self.connection_times.get(connection_id)
            if conn_info:
                client_ip = conn_info.get('client_ip') if isinstance(conn_info, dict) else None
                target_addr = conn_info.get('target_addr') if isinstance(conn_info, dict) else None
                del self.connection_times[connection_id]
                
                # Update client statistics
                if client_ip and client_ip in self.client_stats:
                    self.client_stats[client_ip]['connections'].discard(connection_id)
                    
                    # Update active connection count for target address
                    if target_addr and target_addr in self.client_stats[client_ip]['targets']:
                        self.client_stats[client_ip]['targets'][target_addr]['connections'] = max(0, 
                            self.client_stats[client_ip]['targets'][target_addr]['connections'] - 1)
            
            self.stats['active_connections'] = max(0, self.stats['active_connections'] - 1)
            self.stats['closed_connections'] += 1
    
    def reject_connection(self):
        """Reject connection"""
        with self.lock:
            self.stats['rejected_connections'] += 1
    
    def update_target_addr(self, connection_id, target_addr):
        """Update target address of connection"""
        with self.lock:
            conn_info = self.connection_times.get(connection_id)
            if conn_info and isinstance(conn_info, dict):
                client_ip = conn_info.get('client_ip')
                old_target = conn_info.get('target_addr')
                
                # If target address has not changed, no need to update
                if old_target == target_addr:
                    return
                
                # Update target address in connection info
                conn_info['target_addr'] = target_addr
                
                # If client IP exists, update client statistics
                if client_ip and client_ip in self.client_stats:
                    # If there was a previous target address, need to remove connection from old target address
                    if old_target and old_target in self.client_stats[client_ip]['targets']:
                        self.client_stats[client_ip]['targets'][old_target]['connections'] = max(0, 
                            self.client_stats[client_ip]['targets'][old_target]['connections'] - 1)
                    
                    # Add to new target address
                    if target_addr:
                        if target_addr not in self.client_stats[client_ip]['targets']:
                            self.client_stats[client_ip]['targets'][target_addr] = {
                                'connections': 0,
                                'bytes_sent': 0,
                                'bytes_received': 0
                            }
                        self.client_stats[client_ip]['targets'][target_addr]['connections'] += 1
    
    def add_bytes_sent(self, bytes_count, connection_id=None):
        """Increase bytes sent"""
        with self.lock:
            self.stats['bytes_sent'] += bytes_count
    
            # Update connection and client statistics
            if connection_id:
                conn_info = self.connection_times.get(connection_id)
                if conn_info and isinstance(conn_info, dict):
                    client_ip = conn_info.get('client_ip')
                    target_addr = conn_info.get('target_addr')
                    
                    if client_ip and client_ip in self.client_stats:
                        self.client_stats[client_ip]['total_bytes_sent'] += bytes_count
                        if target_addr and target_addr in self.client_stats[client_ip]['targets']:
                            self.client_stats[client_ip]['targets'][target_addr]['bytes_sent'] += bytes_count
    
    def add_bytes_received(self, bytes_count, connection_id=None):
        """Increase bytes received"""
        with self.lock:
            self.stats['bytes_received'] += bytes_count
            
            # Update connection and client statistics
            if connection_id:
                conn_info = self.connection_times.get(connection_id)
                if conn_info and isinstance(conn_info, dict):
                    client_ip = conn_info.get('client_ip')
                    target_addr = conn_info.get('target_addr')
                    
                    if client_ip and client_ip in self.client_stats:
                        self.client_stats[client_ip]['total_bytes_received'] += bytes_count
                        if target_addr and target_addr in self.client_stats[client_ip]['targets']:
                            self.client_stats[client_ip]['targets'][target_addr]['bytes_received'] += bytes_count
    
    def get_stats(self):
        """Get statistics"""
        with self.lock:
            # Build client statistics
            client_stats_list = []
            for client_ip, stats in self.client_stats.items():
                active_conns = len(stats['connections'])
                # Only show clients with active connections
                if active_conns > 0:
                    targets_list = []
                    for target_addr, target_stats in stats['targets'].items():
                        # Only show target addresses with active connections
                        if target_stats['connections'] > 0:
                            target_total = target_stats['bytes_sent'] + target_stats['bytes_received']
                            targets_list.append({
                                'address': target_addr,
                                'active_connections': target_stats['connections'],
                                'bytes_sent': target_stats['bytes_sent'],
                                'bytes_received': target_stats['bytes_received'],
                                'total_bytes': target_total
                            })
                    # Sort by active connections, then by total traffic
                    targets_list.sort(key=lambda x: (x['active_connections'], x['total_bytes']), reverse=True)
                    
                    client_stats_list.append({
                        'client_ip': client_ip,
                        'active_connections': active_conns,
                        'total_bytes_sent': stats['total_bytes_sent'],
                        'total_bytes_received': stats['total_bytes_received'],
                        'total_bytes': stats['total_bytes_sent'] + stats['total_bytes_received'],
                        'targets': targets_list
                    })
            
            # Sort by total traffic
            client_stats_list.sort(key=lambda x: x['total_bytes'], reverse=True)
            
            return {
                'current_connections': self.stats['active_connections'],
                'total_connections': self.stats['total_connections'],
                'rejected_connections': self.stats['rejected_connections'],
                'closed_connections': self.stats['closed_connections'],
                'bytes_sent': self.stats['bytes_sent'],
                'bytes_received': self.stats['bytes_received'],
                'total_traffic': self.stats['bytes_sent'] + self.stats['bytes_received'],
                'uptime': int(time.time() - self.stats['start_time']),
                'client_stats': client_stats_list  # Statistics for each client
            }
    
    def reset(self):
        """Reset statistics"""
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
            self.client_stats.clear()

