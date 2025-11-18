# Troubleshooting Guide

## ChatGPT/X "Attestation Denied" 问题

### 问题描述
使用 Shadowsocks 代理后，无法登录 ChatGPT、X (Twitter) 等服务，出现 "attestation denied" 错误。

### 原因分析

1. **IP 被检测为代理/VPN**
   - ChatGPT 和 X 等服务会检测代理 IP
   - 拒绝来自已知代理/VPN IP 的访问

2. **TLS 指纹识别**
   - 服务可能通过 TLS 指纹识别代理流量
   - Shadowsocks 的流量特征可能被识别

3. **浏览器环境检测**
   - Attestation 与浏览器的安全验证机制有关
   - 浏览器可能检测到代理环境

4. **DNS 泄漏**
   - DNS 查询可能泄漏真实位置
   - 客户端 DNS 设置不正确

### 解决方案

#### 方案 1：更换加密方法（推荐）

使用更隐蔽的加密方法，如 ChaCha20 系列：

1. 在 Web 界面中：
   - 加密方法选择：`chacha20-ietf-poly1305` 或 `chacha20-ietf`
   - 保存配置
   - 重启服务器

2. 客户端配置：
   - 使用相同的加密方法
   - 确保密码完全一致

#### 方案 2：检查客户端 DNS 设置

**iOS/Android 客户端：**
- 确保使用代理 DNS（通常客户端会自动处理）
- 避免使用系统 DNS

**桌面客户端：**
- 配置使用代理 DNS（如 8.8.8.8 或 1.1.1.1）
- 禁用系统 DNS

#### 方案 3：浏览器设置

1. **禁用 WebRTC**（防止 IP 泄漏）：
   - Chrome/Edge: 安装扩展 "WebRTC Leak Prevent"
   - Firefox: 在 about:config 中设置 `media.peerconnection.enabled = false`

2. **清除浏览器数据**：
   - 清除 Cookies 和缓存
   - 使用隐私模式/无痕模式

3. **检查浏览器扩展**：
   - 禁用可能干扰的扩展
   - 确保代理扩展配置正确

#### 方案 4：使用更高级的代理协议

如果 Shadowsocks 无法解决问题，考虑使用：
- **V2Ray/Xray**：更好的 TLS 伪装和流量特征隐藏
- **Trojan**：使用真实 TLS 流量，更难被检测

#### 方案 5：服务器 IP 问题

如果服务器 IP 已被标记：
1. 更换服务器 IP 地址
2. 使用住宅 IP（而非数据中心 IP）
3. 使用未被标记的 IP 段

### 验证方法

1. **检查 DNS 泄漏**：
   - 访问 https://dnsleaktest.com
   - 确保显示的 DNS 服务器是代理服务器的 DNS

2. **检查 IP 泄漏**：
   - 访问 https://ipleak.net
   - 确保显示的 IP 是代理服务器 IP

3. **测试连接**：
   - 先测试其他网站（如 Google）
   - 再测试 ChatGPT/X

### 常见错误

- **"Attestation Denied"**：通常是代理检测或浏览器环境问题
- **"Access Denied"**：IP 被封锁
- **"Too Many Requests"**：请求频率过高

### 注意事项

1. Shadowsocks 是一个相对简单的代理协议，可能无法完全隐藏代理特征
2. 对于严格检测的服务，可能需要使用更高级的代理协议
3. 确保客户端和服务器配置完全一致
4. 定期更换密码和加密方法

