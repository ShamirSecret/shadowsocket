# Shadowsocks V3 打包说明

## 平台说明

### Windows (.exe)
- **打包脚本**: `build_exe_v3.py`
- **配置文件**: `ShadowsocksServerV3.spec`
- **要求**: Windows 系统 + Python 3.11/3.12/3.13+
- **输出**: `dist/ShadowsocksServerV3.exe`

### macOS (.app)
- **打包脚本**: `build_macos_app.py`
- **要求**: macOS 系统 + Python 3.11/3.12/3.13+
- **输出**: `dist/ShadowsocksServerV3.app`
- **注意**: macOS 上无法打包 Windows .exe 文件

## 重要提示

⚠️ **PyInstaller 不支持交叉编译**
- 在 Mac 上只能打包 macOS 应用（.app）
- 在 Windows 上只能打包 Windows 应用（.exe）
- 要打包 Windows .exe，必须在 Windows 系统上运行打包脚本

## Windows 打包步骤

### 方法 1：使用打包脚本（推荐）

```bash
# 在 Windows 系统上
python build_exe_v3.py
```

### 方法 2：使用 spec 文件

```bash
pyinstaller ShadowsocksServerV3.spec --clean --noconfirm
```

## macOS 打包步骤

```bash
# 在 macOS 系统上
python build_macos_app.py
```

打包完成后，应用位于 `dist/ShadowsocksServerV3.app`

## 环境要求

- Python 3.11、3.12 或 3.13+（已包含 Python 3.13 兼容性修复）
- 已安装 shadowsocks 和 pyinstaller：
  ```bash
  pip install shadowsocks pyinstaller
  ```

## Python 3.13 兼容性

本项目已修复 shadowsocks 2.8.2 与 Python 3.13+ 的兼容性问题：
- ✅ 已修复，支持 Python 3.13+
- 兼容性修复在 `shadowsocks_v2_refactored/compat.py` 中自动应用

## 测试

打包完成后，可以在对应平台上直接运行进行测试。

## 常见问题

### Q: 为什么在 Mac 上不能打包成 .exe？
A: PyInstaller 不支持交叉编译。要在 Windows 上打包 .exe，必须在 Windows 系统上运行打包脚本。

### Q: Mac 上打包的应用无法运行？
A: macOS 的安全机制可能阻止未签名的应用。右键点击应用 -> 打开，选择"打开"。

### Q: 如何在没有 Windows 系统的情况下打包 .exe？
A: 可以使用以下方法：
1. 使用 Windows 虚拟机
2. 使用 GitHub Actions 等 CI/CD 服务
3. 使用 Windows 云服务器
