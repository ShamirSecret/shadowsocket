# 快速开始 - 跨平台打包指南

## 🚀 最简单的方法：使用 GitHub Actions（推荐）

### 步骤 1：推送代码到 GitHub

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin <your-github-repo-url>
git push -u origin main
```

### 步骤 2：触发自动打包

1. 访问 GitHub 仓库页面
2. 点击 "Actions" 标签
3. 选择 "Build Windows EXE" 工作流
4. 点击 "Run workflow" -> "Run workflow"

### 步骤 3：下载打包好的文件

1. 等待构建完成（约 5-10 分钟）
2. 在 Actions 页面找到完成的构建
3. 点击 "ShadowsocksServerV3-Windows" artifact
4. 下载 `ShadowsocksServerV3.exe`

✅ **完成！** 现在你有了一个可以在任何 Windows 系统上运行的独立 .exe 文件，无需安装任何依赖。

## 📦 本地打包（可选）

### Windows 系统

```bash
pip install shadowsocks pyinstaller
python build_exe_v3.py
```

输出：`dist/ShadowsocksServerV3.exe`

### macOS 系统

```bash
pip install shadowsocks pyinstaller
python build_macos_app.py
```

输出：`dist/ShadowsocksServerV3.app`

## 🎯 使用打包好的文件

### Windows .exe

1. 双击 `ShadowsocksServerV3.exe` 运行
2. 首次运行可能需要添加杀毒软件信任
3. 配置服务器参数并启动

### macOS .app

1. 双击 `ShadowsocksServerV3.app` 运行
2. 如果提示"无法打开"，右键点击 -> 打开
3. 配置服务器参数并启动

## ✨ 特性

- ✅ **跨平台**: Windows 和 macOS 都支持
- ✅ **独立运行**: 无需安装 Python 或任何依赖
- ✅ **自动打包**: GitHub Actions 自动在云端打包
- ✅ **Python 3.13+**: 完全兼容最新 Python 版本
- ✅ **事件循环架构**: 修复连续下载断开问题

## 📝 更多信息

- 详细打包说明：`BUILD_README.md`
- CI/CD 说明：`CI_BUILD_README.md`
- 项目文档：`shadowsocks_server_ui/README.md`

