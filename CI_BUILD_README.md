# 使用 GitHub Actions 自动打包跨平台应用

## 概述

本项目使用 GitHub Actions 在云端自动打包 Windows .exe 和 macOS .app，无需本地 Windows 或 macOS 环境。

## 使用方法

### 方法 1：手动触发（推荐）

1. **推送代码到 GitHub**
   ```bash
   git add .
   git commit -m "Add GitHub Actions workflow"
   git push origin main
   ```

2. **在 GitHub 上触发构建**
   - 访问 GitHub 仓库页面
   - 点击 "Actions" 标签
   - 选择 "Build Windows EXE" 工作流
   - 点击 "Run workflow" -> "Run workflow"

3. **下载打包好的文件**
   - 等待构建完成（约 5-10 分钟）
   - 在 Actions 页面找到完成的构建
   - 点击 "ShadowsocksServerV3-Windows" artifact
   - 下载 `ShadowsocksServerV3.exe`

### 方法 2：创建 Release 自动打包

1. **创建 Git 标签**
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```

2. **自动打包和发布**
   - GitHub Actions 会自动检测标签并开始构建
   - 构建完成后会自动创建 Release
   - 在 Release 页面下载打包好的文件

## 工作流说明

### build-windows-exe.yml
- **平台**: Windows
- **输出**: `ShadowsocksServerV3.exe`
- **触发**: 手动触发或推送标签

### build-all-platforms.yml
- **平台**: Windows + macOS
- **输出**: Windows .exe 和 macOS .app
- **触发**: 手动触发或推送标签

## 优势

✅ **无需 Windows 环境**: 在 Mac/Linux 上也能获得 Windows .exe  
✅ **自动化**: 推送代码即可自动打包  
✅ **跨平台**: 同时支持 Windows 和 macOS  
✅ **可重复**: 每次构建环境一致  
✅ **免费**: GitHub Actions 免费额度足够使用  

## 下载文件

构建完成后，可以在以下位置下载：

1. **Artifacts**: Actions 页面 -> 完成的构建 -> Artifacts
2. **Release**: 如果使用标签，会在 Release 页面自动创建

## 注意事项

1. **首次使用**: 需要将代码推送到 GitHub 仓库
2. **构建时间**: 首次构建可能需要 10-15 分钟（下载依赖）
3. **文件大小**: Windows .exe 约 20-30 MB
4. **保留时间**: Artifacts 保留 30 天

## 本地打包（可选）

如果需要本地打包：

- **Windows**: `python build_exe_v3.py`
- **macOS**: `python build_macos_app.py`

## 故障排除

### 构建失败
1. 检查 Actions 日志查看错误信息
2. 确保所有依赖已正确安装
3. 检查 Python 版本兼容性

### 找不到 Artifact
1. 确保构建已完成（绿色勾号）
2. 检查 Artifact 是否已过期（30 天）
3. 重新触发构建

