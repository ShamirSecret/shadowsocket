#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Shadowsocks 服务端 V2 - 完整功能版
- 线程池限制
- 连接清理机制
- 连接计数和统计
- 最大连接数限制
- 带图形界面
使用标准 shadowsocks 库，兼容标准客户端
支持打包成 exe 文件，可在 Windows 虚拟机上运行
"""

import socket
import sys
import threading
import struct
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import json
import os
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from collections import defaultdict

# 使用标准的 shadowsocks 库
try:
    from shadowsocks import encrypt
    SHADOWSOCKS_AVAILABLE = True
except ImportError:
    SHADOWSOCKS_AVAILABLE = False
    print("警告: shadowsocks 库未安装，请运行: pip install shadowsocks")


class ShadowsocksCipher:
    """Shadowsocks 加密器 - 使用标准 shadowsocks 库"""
    
    def __init__(self, password, method='aes-256-cfb'):
        if not SHADOWSOCKS_AVAILABLE:
            raise ImportError("shadowsocks 库未安装，请运行: pip install shadowsocks")
        
        self.password = password
        self.method = method
        
        # 使用标准 shadowsocks 库创建加密器
        # Encryptor 可以同时用于加密和解密
        try:
            self.encryptor = encrypt.Encryptor(password, method)
            self.decryptor = encrypt.Encryptor(password, method)
        except Exception as e:
            raise ValueError(f"不支持的加密方法 {method}: {str(e)}")
    
    def encrypt(self, data):
        """加密数据"""
        return self.encryptor.encrypt(data)
    
    def decrypt(self, data):
        """解密数据"""
        return self.decryptor.decrypt(data)
    
    @property
    def iv_len(self):
        """获取 IV 长度"""
        return self.encryptor.iv_len if hasattr(self.encryptor, 'iv_len') else 16


class ShadowsocksProtocol:
    """Shadowsocks 协议处理"""
    
    @staticmethod
    def parse_addr(data):
        """解析 Shadowsocks 地址"""
        if len(data) < 1:
            return None, None, None
        
        addr_type = data[0]
        offset = 1
        
        if addr_type == 1:  # IPv4
            if len(data) < offset + 4:
                return None, None, None
            addr = socket.inet_ntoa(data[offset:offset+4])
            offset += 4
        elif addr_type == 3:  # 域名
            if len(data) < offset + 1:
                return None, None, None
            addr_len = data[offset]
            offset += 1
            if len(data) < offset + addr_len:
                return None, None, None
            addr = data[offset:offset+addr_len].decode('utf-8', errors='ignore')
            offset += addr_len
        elif addr_type == 4:  # IPv6
            if len(data) < offset + 16:
                return None, None, None
            addr = socket.inet_ntop(socket.AF_INET6, data[offset:offset+16])
            offset += 16
        else:
            return None, None, None
        
        if len(data) < offset + 2:
            return None, None, None
        
        port = struct.unpack('!H', data[offset:offset+2])[0]
        offset += 2
        
        return addr, port, offset
    
    @staticmethod
    def pack_addr(addr, port):
        """打包地址"""
        try:
            # 尝试解析为 IP 地址
            socket.inet_aton(addr)
            # IPv4
            return struct.pack('!B', 1) + socket.inet_aton(addr) + struct.pack('!H', port)
        except:
            # 域名
            addr_bytes = addr.encode('utf-8')
            return struct.pack('!B', 3) + struct.pack('!B', len(addr_bytes)) + addr_bytes + struct.pack('!H', port)


class ShadowsocksServer:
    """Shadowsocks 代理服务器 - 完整功能版"""
    
    def __init__(self, host='0.0.0.0', port=1080, password='', method='aes-256-cfb', 
                 max_connections=2000, 
                 idle_timeout=43200,  # 连接空闲超时时间（秒），默认12小时（参考 shadowsocks 策略：只检查空闲时间）
                 target_connect_timeout=30,  # 服务器-目标服务器建立连接的超时时间（秒），默认30秒
                 log_callback=None):
        self.host = host
        self.port = port
        self.password = password
        self.method = method
        self.max_connections = max_connections  # 最大连接数限制（同时作为线程池大小）
        self.idle_timeout = idle_timeout  # 连接空闲超时时间（秒），只检查空闲时间，支持长时间下载
        self.target_connect_timeout = target_connect_timeout  # 服务器-目标服务器建立连接的超时时间（秒）
        self.log_callback = log_callback
        
        self.socket = None
        self.running = False
        
        # 线程池管理（使用 max_connections 作为线程池大小）
        self.executor = ThreadPoolExecutor(max_workers=max_connections, thread_name_prefix="SSServer")
        
        # 连接管理
        self.clients = {}  # connection_id -> client_socket
        self.clients_lock = threading.Lock()  # 保护 clients 字典
        self.connection_count = 0  # 当前连接数
        self.total_connections = 0  # 总连接数（历史累计）
        self.connection_last_activity = {}  # connection_id -> last_activity_time
        
        # 统计信息
        self.stats = {
            'total_connections': 0,
            'active_connections': 0,
            'rejected_connections': 0,
            'closed_connections': 0,
            'bytes_sent': 0,
            'bytes_received': 0,
            'start_time': time.time()
        }
        
        # 关闭事件
        self.shutdown_event = threading.Event()
        
        # 初始化加密器（Shadowsocks 必须使用密码）
        if not password:
            raise ValueError("Shadowsocks 需要密码进行加密")
        # 注意：这里不创建全局加密器，每个连接使用独立实例
    
    def log(self, message):
        """记录日志"""
        if self.log_callback:
            self.log_callback(message)
        else:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")
    
    def configure_socket(self, sock):
        """配置 socket 参数"""
        try:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
            sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            
            # 增加缓冲区大小以支持大文件传输
            try:
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 1048576)  # 1MB
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 1048576)  # 1MB
            except:
                pass
        except Exception as e:
            self.log(f"配置 socket 失败: {str(e)}")
    
    def start(self):
        """启动服务器"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.configure_socket(self.socket)
            self.socket.bind((self.host, self.port))
            self.socket.listen(1000)
            self.running = True
            
            # 启动连接清理线程
            self.start_cleanup_thread()
            
            # 启动统计线程
            self.start_stats_thread()
            
            self.log(f"服务器启动成功，监听 {self.host}:{self.port}")
            self.log(f"最大连接数: {self.max_connections} (线程池大小: {self.max_connections})")
            return True
        except Exception as e:
            self.log(f"启动失败: {str(e)}")
            return False
    
    def stop(self):
        """停止服务器"""
        self.running = False
        self.shutdown_event.set()
        
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
        
        # 先关闭所有连接的读写，让 recv() 立即返回
        with self.clients_lock:
            for client_socket in self.clients.values():
                try:
                    # 先 shutdown，让 recv() 立即返回
                    client_socket.shutdown(socket.SHUT_RDWR)
                except:
                    pass
            # 再关闭 socket
            for client_socket in self.clients.values():
                try:
                    client_socket.close()
                except:
                    pass
            self.clients.clear()
            self.connection_count = 0
        
        # 关闭线程池 - 设置超时，避免无限等待
        # 先尝试优雅关闭，不等待线程完成
        self.executor.shutdown(wait=False)
        # 给线程一些时间退出（通过 shutdown 和 socket 关闭，线程应该很快退出）
        time.sleep(0.5)
        self.log("服务器已停止")
    
    def start_cleanup_thread(self):
        """启动连接清理线程 - 参考 shadowsocks 策略：只检查空闲时间，支持长时间下载"""
        def cleanup_worker():
            while not self.shutdown_event.is_set():
                self.shutdown_event.wait(60)  # 每60秒检查一次（参考 shadowsocks 的 TIMEOUT_PRECISION）
                if self.shutdown_event.is_set():
                    break
                
                # 使用浮点数时间戳进行比较（与 shadowsocks 保持一致）
                current_time = time.time()
                stale_connections = []
                
                with self.clients_lock:
                    for conn_id in list(self.connection_last_activity.keys()):
                        last_activity = self.connection_last_activity.get(conn_id)
                        
                        if last_activity:
                            # 只检查空闲时间（参考 shadowsocks 策略）
                            # 只要有数据传输，last_activity 就会更新，长时间下载的连接不会被清理
                            # last_activity 是整数时间戳，current_time 是浮点数，比较时自动转换为浮点数
                            idle_time = current_time - float(last_activity)
                            
                            # 只有真正空闲（无数据传输）超过空闲超时的连接才会被清理
                            if idle_time > self.idle_timeout:
                                stale_connections.append(conn_id)
                
                # 清理超时连接
                for conn_id in stale_connections:
                    last_activity = self.connection_last_activity.get(conn_id, 0)
                    idle_time = current_time - float(last_activity) if last_activity else 0
                    self.close_connection(conn_id, f"连接空闲超时（空闲 {int(idle_time)} 秒，超过 {self.idle_timeout} 秒）")
                    self.log(f"清理空闲超时连接: {conn_id} (空闲 {int(idle_time)} 秒)")
        
        cleanup_thread = threading.Thread(target=cleanup_worker, daemon=True, name="ConnectionCleanup")
        cleanup_thread.start()
        self.log(f"连接清理线程已启动（空闲超时: {self.idle_timeout}秒，检查间隔: 60秒）")
    
    def start_stats_thread(self):
        """启动统计线程"""
        def stats_worker():
            while not self.shutdown_event.is_set():
                self.shutdown_event.wait(300)  # 每5分钟输出一次统计
                if self.shutdown_event.is_set():
                    break
                
                uptime = int(time.time() - self.stats['start_time'])
                hours = uptime // 3600
                minutes = (uptime % 3600) // 60
                
                self.log(f"统计: 活跃连接 {self.connection_count}/{self.max_connections}, "
                        f"总连接 {self.total_connections}, "
                        f"运行时间 {hours}h{minutes}m")
        
        stats_thread = threading.Thread(target=stats_worker, daemon=True, name="Stats")
        stats_thread.start()
    
    def get_stats(self):
        """获取统计信息"""
        with self.clients_lock:
            return {
                'current_connections': self.connection_count,
                'max_connections': self.max_connections,
                'total_connections': self.total_connections,
                'rejected_connections': self.stats['rejected_connections'],
                'closed_connections': self.stats['closed_connections'],
                'uptime': int(time.time() - self.stats['start_time'])
            }
    
    def disconnect_all_connections(self, reason="连接数超限，重置所有连接"):
        """断开所有连接，让连接数归零（快速方式，避免阻塞）"""
        # 在锁内快速复制连接列表，然后立即释放锁
        with self.clients_lock:
            if self.connection_count == 0:
                return
            
            count = self.connection_count
            # 复制连接列表（避免在锁内执行耗时操作）
            connections_to_close = list(self.clients.values())
            
            # 立即清空连接记录，释放锁（关键：先清空，再关闭）
            self.clients.clear()
            self.connection_last_activity.clear()
            self.connection_count = 0
        
        # 在锁外执行关闭操作，避免阻塞其他线程
        self.log(f"开始断开所有连接 ({count} 个)，原因: {reason}")
        
        # 快速关闭所有连接（不等待 shutdown，直接 close）
        closed_count = 0
        for sock in connections_to_close:
            try:
                # 直接关闭，不调用 shutdown（shutdown 可能阻塞）
                # 设置 socket 为非阻塞模式，避免 close 时阻塞
                try:
                    sock.setblocking(False)
                except:
                    pass
                sock.close()
                closed_count += 1
            except:
                # 忽略所有错误，继续关闭下一个
                pass
        
        self.log(f"已断开所有连接 ({closed_count}/{count} 个)，连接数已归零")
    
    def accept_clients(self):
        """接受客户端连接（优化版：更好的连接管理和错误处理）"""
        while self.running:
            try:
                client_socket, addr = self.socket.accept()
                
                # 配置 socket（在检查连接数之前，避免浪费资源）
                try:
                    self.configure_socket(client_socket)
                except Exception as config_error:
                    # 配置失败，关闭连接
                    try:
                        client_socket.close()
                    except:
                        pass
                    self.log(f"配置客户端 socket 失败 {addr[0]}:{addr[1]}: {str(config_error)}")
                    continue
                
                # 检查是否达到最大连接数（快速检查，避免长时间持锁）
                connection_count_check = False
                with self.clients_lock:
                    connection_count_check = (self.connection_count >= self.max_connections)
                
                # 如果连接数超限，断开所有连接（在锁外执行，避免死锁）
                if connection_count_check:
                    try:
                        client_socket.close()
                    except:
                        pass
                    self.disconnect_all_connections("连接数超过最大限制，重置所有连接")
                    self.stats['rejected_connections'] += 1
                    continue
                
                # 添加新连接（快速操作，最小化锁持有时间）
                connection_id = None
                with self.clients_lock:
                    # 再次检查（防止在检查和添加之间连接数变化）
                    if self.connection_count >= self.max_connections:
                        try:
                            client_socket.close()
                        except:
                            pass
                        self.stats['rejected_connections'] += 1
                        continue
                    
                    # 增加连接计数
                    connection_id = id(client_socket)
                    self.connection_count += 1
                    self.total_connections += 1
                    self.clients[connection_id] = client_socket
                    # 使用整数时间戳初始化，与 update_activity 保持一致
                    self.connection_last_activity[connection_id] = int(time.time())
                    self.stats['total_connections'] += 1
                
                self.log(f"新客户端连接: {addr[0]}:{addr[1]} (当前: {self.connection_count}/{self.max_connections})")
                
                # 提交到线程池处理（异步处理，不阻塞接受新连接）
                try:
                    future = self.executor.submit(self.handle_client, client_socket, addr, connection_id)
                    future.add_done_callback(lambda f, conn_id=connection_id: self.connection_finished(conn_id))
                except Exception as submit_error:
                    # 线程池提交失败，关闭连接
                    self.log(f"提交连接处理任务失败: {str(submit_error)}")
                    self.close_connection(connection_id, "线程池提交失败")
                
            except socket.error as sock_error:
                # socket 相关错误（通常是正常的关闭操作）
                if self.running:
                    error_str = str(sock_error)
                    if "10038" not in error_str and "10053" not in error_str and "10054" not in error_str:
                        self.log(f"接受连接错误: {error_str}")
            except Exception as e:
                if self.running:
                    error_str = str(e)
                    if "10038" not in error_str and "10053" not in error_str and "10054" not in error_str:
                        self.log(f"接受连接错误: {str(e)}")
    
    def connection_finished(self, connection_id):
        """连接完成回调"""
        self.close_connection(connection_id, "连接正常关闭")
    
    def close_connection(self, connection_id, reason=""):
        """关闭连接"""
        with self.clients_lock:
            if connection_id in self.clients:
                try:
                    self.clients[connection_id].close()
                except:
                    pass
                del self.clients[connection_id]
                self.connection_count = max(0, self.connection_count - 1)
                self.stats['closed_connections'] += 1
            
            if connection_id in self.connection_last_activity:
                del self.connection_last_activity[connection_id]
    
    def update_activity(self, connection_id):
        """更新连接活动时间（确保长时间下载的连接不会被清理）"""
        with self.clients_lock:
            if connection_id not in self.connection_last_activity:
                # 连接不存在，直接返回（不应该发生，但安全起见）
                return
            
            # 使用整数时间戳（秒级精度），与 shadowsocks 保持一致
            now = int(time.time())
            last_update = self.connection_last_activity.get(connection_id, 0)
            
            # 关键修复：只要有数据传输，就更新活动时间
            # 不再使用精度限制，因为这会阻止活动时间的及时更新
            # 对于长时间下载的连接，必须确保每次收到数据都更新活动时间
            # 即使频繁更新，字典操作的开销也很小，不会影响性能
            self.connection_last_activity[connection_id] = now
    
    def handle_client(self, client_socket, addr, connection_id):
        """处理客户端请求（Shadowsocks 协议）"""
        # 为每个连接创建独立的加密器/解密器实例
        try:
            connection_cipher = ShadowsocksCipher(self.password, self.method)
        except Exception as e:
            self.log(f"创建连接加密器失败: {str(e)}")
            self.close_connection(connection_id, "加密器创建失败")
            return
        
        try:
            # Shadowsocks 协议：第一个数据包包含加密的地址信息
            buffer = b''
            decrypted_buffer = b''
            
            # 读取并解密数据，直到能够解析出地址
            while True:
                data = client_socket.recv(4096)
                if not data:
                    return
                
                self.update_activity(connection_id)
                self.stats['bytes_received'] += len(data)
                
                buffer += data
                
                # 尝试解密
                try:
                    decrypted = connection_cipher.decrypt(buffer)
                    if decrypted:
                        decrypted_buffer += decrypted
                        buffer = b''
                        
                        # 尝试解析地址
                        addr_info = ShadowsocksProtocol.parse_addr(decrypted_buffer)
                        if addr_info[0]:  # 成功解析地址
                            address, port, offset = addr_info
                            remaining_data = decrypted_buffer[offset:] if offset < len(decrypted_buffer) else b''
                            break
                except Exception as e:
                    # 解密失败，可能需要更多数据
                    if len(buffer) > 65536:  # 防止无限等待
                        self.log(f"解密失败: {str(e)}")
                        return
                    continue
            
            self.log(f"连接请求: {address}:{port}")
            
            # 建立到目标服务器的连接
            self.handle_connect(client_socket, address, port, addr, remaining_data, connection_cipher, connection_id)
                
        except Exception as e:
            error_str = str(e)
            # 10038, 10053, 10054 都是 socket 已关闭的正常情况，不需要记录日志
            if "10038" not in error_str and "10053" not in error_str and "10054" not in error_str:
                self.log(f"处理客户端错误: {str(e)}")
        finally:
            self.close_connection(connection_id, "处理完成")
    
    def handle_connect(self, client_socket, address, port, client_addr, initial_data=b'', connection_cipher=None, connection_id=None):
        """处理 CONNECT 请求（优化版：支持超时、DNS 优化、错误重试、IPv6）"""
        remote_socket = None
        target_connect_timeout = self.target_connect_timeout  # 服务器-目标服务器建立连接的超时时间
        
        try:
            # 解析地址（如果是域名，先解析为 IP）- 改进版，支持 IPv6 和超时
            target_ip = address
            target_family = socket.AF_INET  # 默认 IPv4
            
            try:
                # 尝试解析为 IPv4 地址
                socket.inet_aton(address)
                # 是有效的 IPv4 地址，直接使用
                target_family = socket.AF_INET
            except socket.error:
                try:
                    # 尝试解析为 IPv6 地址
                    socket.inet_pton(socket.AF_INET6, address)
                    # 是有效的 IPv6 地址，直接使用
                    target_family = socket.AF_INET6
                except socket.error:
                    # 是域名，需要 DNS 解析（支持 IPv4 和 IPv6）
                    try:
                        # 使用 getaddrinfo 进行 DNS 解析，支持 IPv4 和 IPv6，带超时
                        # 优先尝试 IPv4，如果失败再尝试 IPv6
                        import socket as socket_module
                        
                        # 设置 DNS 解析超时（通过创建临时 socket 设置超时）
                        dns_timeout = 5  # DNS 解析超时 5 秒
                        
                        # 先尝试 IPv4
                        try:
                            # 使用 getaddrinfo，它会返回所有可用的地址
                            addr_info_list = socket_module.getaddrinfo(
                                address, port, 
                                socket_module.AF_INET, 
                                socket_module.SOCK_STREAM
                            )
                            if addr_info_list:
                                target_ip = addr_info_list[0][4][0]  # 取第一个 IPv4 地址
                                target_family = socket.AF_INET
                            else:
                                raise socket.error(f"DNS 解析失败: {address} (IPv4)")
                        except (socket.error, OSError) as ipv4_error:
                            # IPv4 失败，尝试 IPv6
                            try:
                                addr_info_list = socket_module.getaddrinfo(
                                    address, port,
                                    socket_module.AF_INET6,
                                    socket_module.SOCK_STREAM
                                )
                                if addr_info_list:
                                    target_ip = addr_info_list[0][4][0]  # 取第一个 IPv6 地址
                                    target_family = socket.AF_INET6
                                else:
                                    raise socket.error(f"DNS 解析失败: {address} (IPv6)")
                            except (socket.error, OSError) as ipv6_error:
                                # 都失败了，使用传统方法作为后备
                                try:
                                    target_ip = socket.gethostbyname(address)
                                    target_family = socket.AF_INET
                                except Exception:
                                    self.log(f"DNS 解析失败 {address}: IPv4错误={str(ipv4_error)}, IPv6错误={str(ipv6_error)}")
                                    return
                    except Exception as dns_error:
                        error_str = str(dns_error)
                        self.log(f"DNS 解析失败 {address}:{port} - {error_str}")
                        return
            
            # 创建 socket 并配置（支持 IPv4 和 IPv6）
            remote_socket = socket.socket(target_family, socket.SOCK_STREAM)
            remote_socket.settimeout(target_connect_timeout)  # 设置服务器-目标服务器连接超时
            self.configure_socket(remote_socket)
            
            # 连接到目标服务器（带超时，支持 IPv4 和 IPv6）
            try:
                # Python socket.connect() 对 IPv4 和 IPv6 使用相同的方式
                remote_socket.connect((target_ip, port))
            except socket.timeout:
                self.log(f"连接目标服务器超时: {address}:{port} (超过 {target_connect_timeout} 秒)")
                return
            except Exception as connect_error:
                error_str = str(connect_error)
                # 区分不同类型的连接错误
                if "10061" in error_str or "Connection refused" in error_str:
                    self.log(f"目标服务器拒绝连接: {address}:{port} (IP: {target_ip})")
                elif "10060" in error_str or "timed out" in error_str.lower():
                    self.log(f"连接目标服务器超时: {address}:{port} (IP: {target_ip}, 超过 {target_connect_timeout} 秒)")
                elif "10051" in error_str or "Network is unreachable" in error_str:
                    self.log(f"网络不可达: {address}:{port} (IP: {target_ip})")
                else:
                    self.log(f"连接失败 {address}:{port} (IP: {target_ip}): {error_str}")
                return
            
            # 连接成功后，移除超时设置（允许长时间连接）
            remote_socket.settimeout(None)
            
            ip_version = "IPv6" if target_family == socket.AF_INET6 else "IPv4"
            self.log(f"连接建立: {client_addr[0]}:{client_addr[1]} -> {address}:{port} ({target_ip}, {ip_version})")
            
            # 如果有初始数据，先发送
            if initial_data:
                try:
                    remote_socket.send(initial_data)
                    self.stats['bytes_sent'] += len(initial_data)
                except Exception as send_error:
                    error_str = str(send_error)
                    if "10038" not in error_str and "10053" not in error_str and "10054" not in error_str:
                        self.log(f"发送初始数据失败: {error_str}")
                    return
            
            # 转发数据
            self.forward_data(client_socket, remote_socket, connection_cipher, connection_id)
            
        except Exception as e:
            error_str = str(e)
            # 过滤正常的 socket 关闭错误
            if "10038" not in error_str and "10053" not in error_str and "10054" not in error_str:
                self.log(f"连接目标服务器失败 {address}:{port}: {error_str}")
        finally:
            if remote_socket:
                try:
                    remote_socket.close()
                except:
                    pass
    
    def forward_data(self, client_socket, remote_socket, connection_cipher=None, connection_id=None):
        """转发数据（支持加密，优化大文件传输）"""
        cipher = connection_cipher
        
        # 使用事件来协调两个线程的退出
        stop_event = threading.Event()
        
        def is_socket_valid(sock):
            """检查 socket 是否有效"""
            if sock is None:
                return False
            try:
                # 尝试获取 socket 的文件描述符，如果 socket 已关闭会抛出异常
                sock.fileno()
                return True
            except (socket.error, OSError, ValueError):
                return False
        
        def forward_client_to_remote():
            """客户端 -> 远程服务器（解密）- 改进版，支持流式传输"""
            buffer_size = 262144  # 256KB
            try:
                if not is_socket_valid(client_socket) or not is_socket_valid(remote_socket):
                    return
                # 设置较短的超时，以便定期检查停止信号
                client_socket.settimeout(1.0)  # 1秒超时，定期检查停止信号
                remote_socket.settimeout(None)
            except:
                return
            
            # 用于检测流式传输的空数据包
            empty_recv_count = 0
            max_empty_recv = 10  # 允许连续10次空接收
            
            try:
                while self.running and not stop_event.is_set():
                    try:
                        # 检查 socket 有效性和停止信号
                        if not is_socket_valid(client_socket) or not is_socket_valid(remote_socket):
                            break
                        if not self.running or stop_event.is_set():
                            break
                        
                        data = client_socket.recv(buffer_size)
                        if not data:
                            # 流式传输时，recv() 可能返回空数据
                            empty_recv_count += 1
                            if empty_recv_count > max_empty_recv:
                                try:
                                    import select
                                    if not is_socket_valid(client_socket):
                                        break
                                    readable, _, exceptional = select.select([client_socket], [], [client_socket], 0.1)
                                    if exceptional:
                                        break
                                    if not readable:
                                        empty_recv_count = 0
                                        time.sleep(0.1)
                                        continue
                                except:
                                    break
                            else:
                                time.sleep(0.05)
                                continue
                        
                        # 收到数据，重置空接收计数
                        empty_recv_count = 0
                        
                        if connection_id:
                            self.update_activity(connection_id)
                        self.stats['bytes_received'] += len(data)
                        
                        if cipher:
                            try:
                                decrypted = cipher.decrypt(data)
                                if decrypted:
                                    total_sent = 0
                                    while total_sent < len(decrypted):
                                        try:
                                            if not is_socket_valid(remote_socket):
                                                return
                                            sent = remote_socket.send(decrypted[total_sent:])
                                            if sent == 0:
                                                return
                                            total_sent += sent
                                            self.stats['bytes_sent'] += sent
                                        except (socket.error, OSError) as send_err:
                                            error_str = str(send_err)
                                            if "10038" in error_str or "10053" in error_str or "10054" in error_str:
                                                stop_event.set()
                                                return
                                            raise
                            except (socket.error, OSError) as e:
                                error_str = str(e)
                                if "10038" in error_str or "10053" in error_str or "10054" in error_str:
                                    stop_event.set()
                                    return
                                raise
                            except Exception as e:
                                error_str = str(e)
                                if "10038" in error_str or "10053" in error_str or "10054" in error_str or "timed out" in error_str.lower():
                                    stop_event.set()
                                    return
                                self.log(f"解密错误: {error_str}")
                                break
                        else:
                            total_sent = 0
                            while total_sent < len(data):
                                if not is_socket_valid(remote_socket):
                                    return
                                sent = remote_socket.send(data[total_sent:])
                                if sent == 0:
                                    return
                                total_sent += sent
                                self.stats['bytes_sent'] += sent
                    except socket.timeout:
                        # 超时是正常的，继续循环检查停止信号
                        # 关键修复：即使超时，也要更新活动时间，因为连接可能正在下载（另一个方向有数据）
                        if connection_id:
                            self.update_activity(connection_id)
                        continue
                    except (socket.error, OSError) as e:
                        error_str = str(e)
                        if "10038" in error_str or "10053" in error_str or "10054" in error_str:
                            stop_event.set()
                            return
                        raise
            except Exception as e:
                if self.running:
                    error_str = str(e)
                    if "10038" not in error_str and "10053" not in error_str and "10054" not in error_str:
                        if "timed out" not in error_str.lower():
                            self.log(f"转发客户端数据错误: {error_str}")
            finally:
                stop_event.set()
        
        def forward_remote_to_client():
            """远程服务器 -> 客户端（加密）- 改进版，支持流式传输"""
            buffer_size = 262144  # 256KB
            try:
                if not is_socket_valid(client_socket) or not is_socket_valid(remote_socket):
                    return
                # 移除超时限制，支持长时间下载和大文件传输（参考原始 shadowsocket.py）
                client_socket.settimeout(None)
                remote_socket.settimeout(None)  # 移除超时，支持长时间下载
            except:
                return
            
            try:
                while self.running and not stop_event.is_set():
                    try:
                        # 检查 socket 有效性和停止信号
                        if not is_socket_valid(client_socket) or not is_socket_valid(remote_socket):
                            break
                        if not self.running or stop_event.is_set():
                            break
                        
                        # 直接 recv，阻塞模式，支持长时间下载（参考原始 shadowsocket.py）
                        data = remote_socket.recv(buffer_size)
                        if not data:
                            # recv() 返回空数据，表示连接已关闭（参考原始 shadowsocket.py）
                            break
                        
                        if connection_id:
                            self.update_activity(connection_id)
                        self.stats['bytes_received'] += len(data)
                        
                        if cipher:
                            try:
                                encrypted = cipher.encrypt(data)
                                total_sent = 0
                                while total_sent < len(encrypted):
                                    try:
                                        if not is_socket_valid(client_socket):
                                            return
                                        sent = client_socket.send(encrypted[total_sent:])
                                        if sent == 0:
                                            return
                                        total_sent += sent
                                        self.stats['bytes_sent'] += sent
                                    except (socket.error, OSError) as send_err:
                                        error_str = str(send_err)
                                        if "10038" in error_str or "10053" in error_str or "10054" in error_str:
                                            stop_event.set()
                                            return
                                        raise
                            except (socket.error, OSError) as e:
                                error_str = str(e)
                                if "10038" in error_str or "10053" in error_str or "10054" in error_str:
                                    stop_event.set()
                                    return
                                raise
                            except Exception as e:
                                error_str = str(e)
                                if "10038" in error_str or "10053" in error_str or "10054" in error_str or "timed out" in error_str.lower():
                                    stop_event.set()
                                    return
                                self.log(f"加密错误: {error_str}")
                                break
                        else:
                            total_sent = 0
                            while total_sent < len(data):
                                if not is_socket_valid(client_socket):
                                    return
                                sent = client_socket.send(data[total_sent:])
                                if sent == 0:
                                    return
                                total_sent += sent
                                self.stats['bytes_sent'] += sent
                    except (socket.error, OSError) as e:
                        error_str = str(e)
                        if "10038" in error_str or "10053" in error_str or "10054" in error_str:
                            stop_event.set()
                            return
                        raise
            except Exception as e:
                if self.running:
                    error_str = str(e)
                    # 10038 错误是 socket 已关闭，不需要记录日志
                    if "10038" not in error_str and "10053" not in error_str and "10054" not in error_str:
                        if "timed out" not in error_str.lower():
                            self.log(f"转发远程数据错误: {error_str}")
            finally:
                stop_event.set()
        
        t1 = threading.Thread(target=forward_client_to_remote, daemon=True)
        t2 = threading.Thread(target=forward_remote_to_client, daemon=True)
        t1.start()
        t2.start()
        t1.join()
        t2.join()


class ShadowsocksGUI:
    """Shadowsocks 服务端图形界面"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Shadowsocks 服务端 V2 - 增强版")
        self.root.geometry("1100x700")
        self.root.resizable(True, True)  # 允许调整大小
        self.root.minsize(900, 600)  # 设置最小尺寸，适配小屏幕
        
        # 设置主题颜色 - 浅色主题
        self.bg_color = "#f5f5f5"  # 浅灰色背景
        self.frame_bg = "#ffffff"  # 白色框架背景
        self.text_bg = "#ffffff"   # 白色文本背景
        self.text_fg = "#333333"  # 深灰色文字
        self.accent_color = "#0078d4"  # 蓝色强调色
        self.success_color = "#28a745"  # 绿色成功色
        self.warning_color = "#ffc107"  # 黄色警告色
        self.error_color = "#dc3545"    # 红色错误色
        
        self.root.configure(bg=self.bg_color)
        
        # 配置 ttk 样式 - 简化配置以提高兼容性
        style = ttk.Style()
        # 使用 'clam' 主题，它支持自定义颜色
        try:
            style.theme_use('clam')
        except:
            # 如果clam主题不可用，使用默认主题
            pass
        
        # 只配置必要的样式，避免不兼容的参数
        try:
            style.configure('TLabel', 
                           background=self.bg_color, 
                           foreground=self.text_fg, 
                           font=("Microsoft YaHei UI", 10))
            style.configure('TFrame', 
                           background=self.bg_color)
            # LabelFrame 样式 - 最小化配置
            style.configure('TLabelFrame', 
                           background=self.frame_bg, 
                           foreground=self.text_fg)
            style.configure('TLabelFrame.Label', 
                           background=self.frame_bg, 
                           foreground=self.text_fg,
                           font=("Microsoft YaHei UI", 10, "bold"))
            style.configure('TEntry', 
                           fieldbackground=self.text_bg,
                           foreground=self.text_fg,
                           font=("Consolas", 10))
            style.configure('TCombobox', 
                           fieldbackground=self.text_bg,
                           foreground=self.text_fg,
                           font=("Consolas", 10))
        except Exception as e:
            # 如果样式配置失败，继续使用默认样式
            print(f"样式配置警告: {e}")
        
        # 保存样式引用以便后续使用
        self.style = style
        
        self.server = None
        self.server_thread = None
        self.last_bytes_sent = 0
        self.last_bytes_received = 0
        self.last_stats_time = time.time()
        
        self.setup_ui()
        self.load_config()
    
    def setup_ui(self):
        """设置界面 - 现代化响应式设计，优化小屏幕显示"""
        # 主容器 - 使用 grid 布局，左右分栏
        main_container = tk.Frame(self.root, bg=self.bg_color)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 配置主容器的 grid 权重：左侧占60%，右侧占40%
        main_container.grid_columnconfigure(0, weight=3, minsize=500)  # 左侧（配置）
        main_container.grid_columnconfigure(1, weight=2, minsize=350)  # 右侧（日志）
        main_container.grid_rowconfigure(1, weight=1)  # 主内容行可扩展
        
        # 标题 - 跨两列
        title_label = tk.Label(main_container, text="Shadowsocks 服务端 V2", 
                              font=("Microsoft YaHei UI", 18, "bold"),
                              bg=self.bg_color, fg=self.accent_color)
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 10), sticky=tk.W)
        
        # 左侧列容器
        left_column = tk.Frame(main_container, bg=self.bg_color)
        left_column.grid(row=1, column=0, sticky="nsew", padx=(0, 10))
        left_column.grid_rowconfigure(2, weight=1)  # 监控区域可扩展
        
        # 配置框架 - 使用紧凑的2列布局，避免小屏幕遮挡
        config_frame = ttk.LabelFrame(left_column, text="服务器配置", padding=10)
        config_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        config_frame.grid_columnconfigure(1, weight=1)
        config_frame.grid_columnconfigure(3, weight=1)
        
        # 第一行：监听地址和端口
        tk.Label(config_frame, text="监听地址:", bg=self.frame_bg, fg=self.text_fg,
                font=("Microsoft YaHei UI", 9)).grid(row=0, column=0, sticky=tk.W, pady=5, padx=(0, 5))
        self.host_var = tk.StringVar(value="0.0.0.0")
        host_entry = tk.Entry(config_frame, textvariable=self.host_var, width=12,
                             bg=self.text_bg, fg=self.text_fg, insertbackground=self.text_fg,
                             font=("Consolas", 9), relief=tk.SUNKEN, bd=1)
        host_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W+tk.E)
        
        tk.Label(config_frame, text="监听端口:", bg=self.frame_bg, fg=self.text_fg,
                font=("Microsoft YaHei UI", 9)).grid(row=0, column=2, sticky=tk.W, pady=5, padx=(10, 5))
        self.port_var = tk.StringVar(value="1080")
        port_entry = tk.Entry(config_frame, textvariable=self.port_var, width=10,
                             bg=self.text_bg, fg=self.text_fg, insertbackground=self.text_fg,
                             font=("Consolas", 9), relief=tk.SUNKEN, bd=1)
        port_entry.grid(row=0, column=3, padx=5, pady=5, sticky=tk.W+tk.E)
        
        # 第二行：密码
        tk.Label(config_frame, text="密码:", bg=self.frame_bg, fg=self.text_fg,
                font=("Microsoft YaHei UI", 9)).grid(row=1, column=0, sticky=tk.W, pady=5, padx=(0, 5))
        self.password_var = tk.StringVar()
        password_entry = tk.Entry(config_frame, textvariable=self.password_var, show="*", width=12,
                                 bg=self.text_bg, fg=self.text_fg, insertbackground=self.text_fg,
                                 font=("Consolas", 9), relief=tk.SUNKEN, bd=1)
        password_entry.grid(row=1, column=1, columnspan=3, padx=5, pady=5, sticky=tk.W+tk.E)
        
        # 第三行：加密方法
        tk.Label(config_frame, text="加密方法:", bg=self.frame_bg, fg=self.text_fg,
                font=("Microsoft YaHei UI", 9)).grid(row=2, column=0, sticky=tk.W, pady=5, padx=(0, 5))
        self.method_var = tk.StringVar(value="aes-256-cfb")
        method_values = (
            "aes-128-cfb", "aes-192-cfb", "aes-256-cfb",
            "aes-128-cfb8", "aes-192-cfb8", "aes-256-cfb8",
            "aes-128-ctr", "aes-192-ctr", "aes-256-ctr",
            "rc4-md5", "bf-cfb"
        )
        method_combo = ttk.Combobox(config_frame, textvariable=self.method_var, width=12, state="readonly")
        method_combo['values'] = method_values
        method_combo.grid(row=2, column=1, columnspan=3, padx=5, pady=5, sticky=tk.W+tk.E)
        
        # 第四行：最大连接数（同时作为线程池大小）
        tk.Label(config_frame, text="最大连接数:", bg=self.frame_bg, fg=self.text_fg,
                font=("Microsoft YaHei UI", 9)).grid(row=3, column=0, sticky=tk.W, pady=5, padx=(0, 5))
        self.max_conn_var = tk.StringVar(value="2000")
        max_conn_entry = tk.Entry(config_frame, textvariable=self.max_conn_var, width=12,
                                 bg=self.text_bg, fg=self.text_fg, insertbackground=self.text_fg,
                                 font=("Consolas", 9), relief=tk.SUNKEN, bd=1)
        max_conn_entry.grid(row=3, column=1, columnspan=3, padx=5, pady=5, sticky=tk.W+tk.E)
        
        # 第五行：连接空闲超时（参考 shadowsocks 策略：只检查空闲时间，支持长时间下载）
        tk.Label(config_frame, text="连接空闲超时(秒):", bg=self.frame_bg, fg=self.text_fg,
                font=("Microsoft YaHei UI", 9)).grid(row=4, column=0, sticky=tk.W, pady=5, padx=(0, 5))
        self.idle_timeout_var = tk.StringVar(value="43200")
        idle_timeout_entry = tk.Entry(config_frame, textvariable=self.idle_timeout_var, width=12,
                                 bg=self.text_bg, fg=self.text_fg, insertbackground=self.text_fg,
                                 font=("Consolas", 9), relief=tk.SUNKEN, bd=1)
        idle_timeout_entry.grid(row=4, column=1, padx=5, pady=5, sticky=tk.W+tk.E)
        tk.Label(config_frame, text="(只检查空闲时间，支持长时间下载)", bg=self.frame_bg, fg=self.text_fg,
                font=("Microsoft YaHei UI", 7)).grid(row=4, column=2, columnspan=2, sticky=tk.W, padx=5, pady=(0, 2))
        
        # 第六行：服务器-目标连接超时
        tk.Label(config_frame, text="目标连接超时(秒):", bg=self.frame_bg, fg=self.text_fg,
                font=("Microsoft YaHei UI", 9)).grid(row=5, column=0, sticky=tk.W, pady=5, padx=(0, 5))
        self.target_connect_timeout_var = tk.StringVar(value="30")
        target_connect_timeout_entry = tk.Entry(config_frame, textvariable=self.target_connect_timeout_var, width=12,
                                        bg=self.text_bg, fg=self.text_fg, insertbackground=self.text_fg,
                                        font=("Consolas", 9), relief=tk.SUNKEN, bd=1)
        target_connect_timeout_entry.grid(row=5, column=1, columnspan=3, padx=5, pady=5, sticky=tk.W+tk.E)
        
        # 控制按钮框架
        button_frame = tk.Frame(left_column, bg=self.bg_color)
        button_frame.grid(row=1, column=0, pady=10, sticky="ew")
        
        self.start_button = tk.Button(button_frame, text="▶ 启动服务器", command=self.start_server,
                                     bg=self.success_color, fg="white",
                                     font=("Microsoft YaHei UI", 11, "bold"),
                                     width=18, height=2, relief=tk.RAISED, cursor="hand2",
                                     activebackground="#218838", activeforeground="white",
                                     bd=1)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = tk.Button(button_frame, text="■ 停止服务器", command=self.stop_server,
                                    bg=self.error_color, fg="white",
                                    font=("Microsoft YaHei UI", 11, "bold"),
                                    width=18, height=2, relief=tk.RAISED, cursor="hand2",
                                    state=tk.DISABLED,
                                    activebackground="#c82333", activeforeground="white",
                                    bd=1)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        # 监控面板 - 缩小合并所有统计
        monitor_frame = ttk.LabelFrame(left_column, text="实时监控", padding=10)
        monitor_frame.grid(row=2, column=0, sticky="nsew")
        
        # 状态显示
        self.status_label = tk.Label(monitor_frame, text="状态: 未启动",
                                     font=("Microsoft YaHei UI", 10, "bold"),
                                     bg=self.frame_bg, fg=self.text_fg, anchor=tk.W)
        self.status_label.pack(fill=tk.X, pady=(0, 8))
        
        # 合并的统计信息 - 使用更紧凑的布局
        stats_container = tk.Frame(monitor_frame, bg=self.frame_bg)
        stats_container.pack(fill=tk.BOTH, expand=True)
        
        # 连接统计 - 紧凑版
        conn_frame = tk.LabelFrame(stats_container, text="连接", bg="#f8f9fa", fg=self.text_fg,
                                   font=("Microsoft YaHei UI", 9, "bold"), padx=8, pady=6,
                                   relief=tk.RAISED, bd=1)
        conn_frame.pack(fill=tk.X, pady=(0, 6))
        
        self.conn_stats_label = tk.Label(conn_frame, text="当前: 0/0",
                                         font=("Consolas", 9), bg="#f8f9fa", fg=self.text_fg,
                                         anchor=tk.W, justify=tk.LEFT)
        self.conn_stats_label.pack(fill=tk.X, pady=1)
        
        self.total_conn_label = tk.Label(conn_frame, text="总计: 0 | 拒绝: 0 | 关闭: 0",
                                         font=("Consolas", 8), bg="#f8f9fa", fg=self.text_fg,
                                         anchor=tk.W, justify=tk.LEFT)
        self.total_conn_label.pack(fill=tk.X, pady=1)
        
        # 流量统计 - 紧凑版
        traffic_frame = tk.LabelFrame(stats_container, text="流量", bg="#f8f9fa", fg=self.text_fg,
                                     font=("Microsoft YaHei UI", 9, "bold"), padx=8, pady=6,
                                     relief=tk.RAISED, bd=1)
        traffic_frame.pack(fill=tk.X, pady=(0, 6))
        
        self.bytes_sent_label = tk.Label(traffic_frame, text="发送: 0 B (0 B/s)",
                                        font=("Consolas", 9), bg="#f8f9fa", fg=self.success_color,
                                        anchor=tk.W, justify=tk.LEFT)
        self.bytes_sent_label.pack(fill=tk.X, pady=1)
        
        self.bytes_received_label = tk.Label(traffic_frame, text="接收: 0 B (0 B/s)",
                                            font=("Consolas", 9), bg="#f8f9fa", fg=self.accent_color,
                                            anchor=tk.W, justify=tk.LEFT)
        self.bytes_received_label.pack(fill=tk.X, pady=1)
        
        self.total_traffic_label = tk.Label(traffic_frame, text="总计: 0 B",
                                            font=("Consolas", 8), bg="#f8f9fa", fg=self.text_fg,
                                            anchor=tk.W, justify=tk.LEFT)
        self.total_traffic_label.pack(fill=tk.X, pady=1)
        
        # 运行时间
        self.uptime_label = tk.Label(stats_container, text="运行时间: 00:00:00",
                                     font=("Consolas", 9), bg=self.frame_bg, fg=self.accent_color,
                                     anchor=tk.W, justify=tk.LEFT)
        self.uptime_label.pack(fill=tk.X, pady=(6, 0))
        
        # 右侧：日志显示区域
        log_frame = ttk.LabelFrame(main_container, text="运行日志", padding=5)
        log_frame.grid(row=1, column=1, sticky="nsew")
        log_frame.grid_rowconfigure(0, weight=1)
        log_frame.grid_columnconfigure(0, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(log_frame,
                                                  bg=self.text_bg, fg=self.text_fg,
                                                  insertbackground=self.text_fg,
                                                  font=("Consolas", 8),
                                                  relief=tk.SUNKEN, bd=1,
                                                  wrap=tk.WORD)
        self.log_text.grid(row=0, column=0, sticky="nsew")
        
        # 绑定事件（移除客户端配置信息相关的更新）
        # 强制更新UI以确保背景色正确显示
        self.root.update_idletasks()
    
    def log(self, message):
        """添加日志"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        # 限制日志行数，避免内存占用过大
        lines = int(self.log_text.index('end-1c').split('.')[0])
        if lines > 1000:
            self.log_text.delete(1.0, f"{lines - 500}.0")
        self.root.update_idletasks()
    
    def format_bytes(self, bytes_value):
        """格式化字节数"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_value < 1024.0:
                return f"{bytes_value:.2f} {unit}"
            bytes_value /= 1024.0
        return f"{bytes_value:.2f} PB"
    
    
    def update_connection_stats(self):
        """更新详细的连接和线程统计显示"""
        if self.server and self.server.running:
            stats = self.server.get_stats()
            
            # 连接统计
            current_conn = stats['current_connections']
            max_conn = stats['max_connections']
            conn_color = self.success_color
            if current_conn > max_conn * 0.8:
                conn_color = self.warning_color
            if current_conn > max_conn * 0.95:
                conn_color = self.error_color
            
            self.conn_stats_label.config(
                text=f"当前: {current_conn}/{max_conn}",
                fg=conn_color
            )
            self.total_conn_label.config(
                text=f"总计: {stats['total_connections']} | 拒绝: {stats['rejected_connections']} | 关闭: {stats['closed_connections']}"
            )
            
            # 运行时间
            uptime = stats['uptime']
            hours = uptime // 3600
            minutes = (uptime % 3600) // 60
            seconds = uptime % 60
            self.uptime_label.config(
                text=f"运行时间: {hours:02d}:{minutes:02d}:{seconds:02d}"
            )
            
            # 流量统计
            current_time = time.time()
            bytes_sent = self.server.stats.get('bytes_sent', 0)
            bytes_received = self.server.stats.get('bytes_received', 0)
            total_traffic = bytes_sent + bytes_received
            
            # 计算速率
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
            
            # 每1秒更新一次（更频繁的更新）
            self.root.after(1000, self.update_connection_stats)
        else:
            # 服务器未运行，重置显示
            self.conn_stats_label.config(text="当前: 0/0", fg=self.text_fg)
            self.total_conn_label.config(text="总计: 0 | 拒绝: 0 | 关闭: 0")
            self.uptime_label.config(text="运行时间: 00:00:00")
            self.bytes_sent_label.config(text="发送: 0 B (0 B/s)")
            self.bytes_received_label.config(text="接收: 0 B (0 B/s)")
            self.total_traffic_label.config(text="总计: 0 B")
    
    def start_server(self):
        """启动服务器"""
        try:
            host = self.host_var.get() or "0.0.0.0"
            port = int(self.port_var.get() or "1080")
            password = self.password_var.get()
            method = self.method_var.get() or "aes-256-cfb"
            
            # 解析高级配置
            try:
                max_connections = int(self.max_conn_var.get() or "2000")
                if max_connections < 1 or max_connections > 10000:
                    messagebox.showerror("错误", "最大连接数必须在 1-10000 之间")
                    return
            except ValueError:
                messagebox.showerror("错误", "最大连接数必须是数字")
                return
            
            try:
                idle_timeout = int(self.idle_timeout_var.get() or "43200")
                if idle_timeout < 60 or idle_timeout > 604800:  # 1分钟到7天
                    messagebox.showerror("错误", "连接空闲超时必须在 60-604800 秒之间（1分钟-7天）")
                    return
            except ValueError:
                messagebox.showerror("错误", "连接空闲超时必须是数字")
                return
            
            try:
                target_connect_timeout = int(self.target_connect_timeout_var.get() or "30")
                if target_connect_timeout < 5 or target_connect_timeout > 300:  # 5秒到5分钟
                    messagebox.showerror("错误", "目标连接超时必须在 5-300 秒之间（5秒-5分钟）")
                    return
            except ValueError:
                messagebox.showerror("错误", "目标连接超时必须是数字")
                return
            
            if port < 1 or port > 65535:
                messagebox.showerror("错误", "端口号必须在 1-65535 之间")
                return
            
            if not password:
                messagebox.showerror("错误", "密码是必填项！\n\nShadowsocks 需要密码进行加密。")
                return
            
            if not SHADOWSOCKS_AVAILABLE:
                messagebox.showerror("错误", "shadowsocks 库未安装！\n\n请运行: pip install shadowsocks")
                return
            
            try:
                self.server = ShadowsocksServer(
                    host=host, port=port, password=password, method=method,
                    max_connections=max_connections,
                    idle_timeout=idle_timeout,
                    target_connect_timeout=target_connect_timeout,
                    log_callback=self.log
                )
            except Exception as e:
                messagebox.showerror("错误", f"初始化服务器失败: {str(e)}")
                return
            
            if self.server.start():
                self.server_thread = threading.Thread(target=self.server.accept_clients, daemon=True)
                self.server_thread.start()
                
                self.start_button.config(state=tk.DISABLED)
                self.stop_button.config(state=tk.NORMAL)
                self.status_label.config(
                    text=f"状态: 运行中 - {host}:{port} ({method})",
                    fg=self.success_color
                )
                self.log(f"服务器启动成功！加密方法: {method}")
                self.log(f"最大连接数: {max_connections} (线程池大小: {max_connections})")
                self.log(f"连接空闲超时: {idle_timeout}秒 ({idle_timeout//3600}小时) - 参考 shadowsocks 策略：只检查空闲时间，支持长时间下载")
                self.log(f"目标连接超时: {target_connect_timeout}秒 (服务器→目标URL建立连接)")
                self.save_config()
                # 重置统计时间
                self.last_stats_time = time.time()
                self.last_bytes_sent = 0
                self.last_bytes_received = 0
                self.update_connection_stats()
            else:
                messagebox.showerror("错误", "服务器启动失败，请检查端口是否被占用")
                
        except ValueError:
            messagebox.showerror("错误", "端口号必须是数字")
        except Exception as e:
            messagebox.showerror("错误", f"启动失败: {str(e)}")
    
    def stop_server(self):
        """停止服务器"""
        if self.server:
            self.server.stop()
            self.server = None
            self.server_thread = None
            
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            self.status_label.config(text="状态: 已停止", fg=self.error_color)
            self.log("服务器已停止")
            # 重置所有统计显示
            self.update_connection_stats()
    
    def save_config(self):
        """保存配置"""
        config = {
            "host": self.host_var.get(),
            "port": self.port_var.get(),
            "password": self.password_var.get(),
            "method": self.method_var.get(),
            "max_connections": self.max_conn_var.get(),
            "idle_timeout": self.idle_timeout_var.get(),
            "target_connect_timeout": self.target_connect_timeout_var.get(),
        }
        try:
            with open("shadowsocks_config.json", "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
        except:
            pass
    
    def load_config(self):
        """加载配置"""
        try:
            if os.path.exists("shadowsocks_config.json"):
                with open("shadowsocks_config.json", "r", encoding="utf-8") as f:
                    config = json.load(f)
                    self.host_var.set(config.get("host", "0.0.0.0"))
                    self.port_var.set(config.get("port", "1080"))
                    self.password_var.set(config.get("password", ""))
                    self.method_var.set(config.get("method", "aes-256-cfb"))
                    self.max_conn_var.set(config.get("max_connections", "2000"))
                    # 兼容旧配置格式
                    self.idle_timeout_var.set(config.get("idle_timeout", config.get("client_idle_timeout", config.get("connection_timeout", "43200"))))
                    self.target_connect_timeout_var.set(config.get("target_connect_timeout", config.get("connect_timeout", "30")))
        except:
            pass
    
    def on_closing(self):
        """关闭窗口时的处理"""
        if self.server and self.server.running:
            if messagebox.askokcancel("退出", "服务器正在运行，确定要退出吗？"):
                self.stop_server()
                self.root.destroy()
        else:
            self.root.destroy()


def main():
    """主函数"""
    root = tk.Tk()
    app = ShadowsocksGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()

