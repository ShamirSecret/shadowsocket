# Shadowsocks 服务端 V2

现代化的 Shadowsocks 代理服务器，带图形界面和详细的监控功能。

## 文件说明

### 核心文件
- **shadowsocket_v2.py** - 主程序文件，包含服务器和GUI界面
- **ShadowsocksServerV2.spec** - PyInstaller 打包配置文件

### 打包相关
- **build_exe_v2.py** - Python 打包脚本
- **build_v2.bat** - Windows 批处理打包脚本（双击运行）
- **BUILD_README.md** - 详细的打包说明文档
- **requirements.txt** - Python 依赖包列表

### 可执行文件
- **ShadowsocksServerV2.exe** - 打包后的可执行文件（如果存在）

## 快速开始

### 直接运行 Python 脚本

1. 安装依赖：
```bash
pip install -r requirements.txt
```

2. 运行程序：
```bash
python shadowsocket_v2.py
```

### 打包成 exe 文件

**方法一：使用批处理文件（推荐）**
```bash
双击运行 build_v2.bat
```

**方法二：使用 Python 脚本**
```bash
python build_exe_v2.py
```

**方法三：使用 PyInstaller**
```bash
pyinstaller ShadowsocksServerV2.spec
```

打包完成后，exe 文件会生成在 `dist` 目录中。

## 功能特性

- ✅ 现代化深色主题 UI
- ✅ 响应式布局（可调整窗口大小）
- ✅ 详细的连接统计（当前连接、总连接、拒绝连接、已关闭连接）
- ✅ 详细的线程统计（活跃线程、线程池大小、空闲线程）
- ✅ 实时流量统计（发送/接收流量及速率）
- ✅ 运行时间显示
- ✅ 线程池和连接管理
- ✅ 自动连接清理机制
- ✅ 支持流式传输（AI 应用）

## 使用说明

1. **启动服务器**
   - 设置监听地址和端口（默认：0.0.0.0:1080）
   - 设置密码（必填）
   - 选择加密方法（默认：aes-256-cfb）
   - 配置最大线程数和连接数
   - 点击"启动服务器"按钮

2. **监控服务器**
   - 实时查看连接数和线程数
   - 监控流量统计
   - 查看运行日志

3. **客户端配置**
   - 查看"客户端配置信息"区域获取连接参数
   - 使用标准 Shadowsocks 客户端连接

## 配置说明

程序会在运行目录生成 `shadowsocks_config.json` 配置文件，自动保存服务器配置。

## 系统要求

- Python 3.7+（如果运行 Python 脚本）
- Windows 7+（exe 文件）
- shadowsocks 库（运行 Python 脚本时需要）

## 依赖包

- shadowsocks >= 3.0.0
- pyinstaller >= 5.0.0（打包时需要）

## 注意事项

1. **杀毒软件拦截**：首次运行 exe 文件可能会被杀毒软件拦截，需要添加信任。

2. **端口占用**：如果端口被占用，程序会提示错误。

3. **防火墙**：确保防火墙允许程序监听端口。

4. **管理员权限**：某些情况下可能需要管理员权限运行。

## 故障排除

### 打包失败
- 确保已安装 shadowsocks 和 pyinstaller
- 检查 Python 版本是否为 3.7+

### 运行错误
- 检查是否有杀毒软件拦截
- 尝试以管理员身份运行
- 查看错误日志

### UI 显示问题
- 确保系统支持 tkinter
- 检查字体是否安装（Microsoft YaHei UI）

## 版本历史

### V2 版本
- 现代化深色主题 UI
- 详细的监控功能
- 响应式布局
- 改进的错误处理

## 许可证

本项目使用标准 Shadowsocks 协议，遵循相关开源协议。

