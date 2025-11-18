# Shadowsocks V3 打包说明

## 环境要求

- Python 3.11、3.12 或 3.13+（已包含 Python 3.13 兼容性修复）
- Windows 系统（用于打包 exe）
- 已安装 shadowsocks 和 pyinstaller

## 打包步骤

### 方法 1：使用 spec 文件（推荐）

```bash
# 在 Windows 上使用 Python 3.11 或 3.12
python build_exe_v3.py
```

### 方法 2：直接使用 PyInstaller

```bash
pyinstaller ShadowsocksServerV3.spec --clean --noconfirm
```

### 方法 3：命令行参数

```bash
pyinstaller shadowsocks_v2_refactored/main.py \
    --name=ShadowsocksServerV3 \
    --onefile \
    --windowed \
    --clean \
    --noconfirm \
    --hidden-import=shadowsocks \
    --hidden-import=shadowsocks.encrypt \
    --hidden-import=shadowsocks.eventloop \
    --hidden-import=shadowsocks.tcprelay \
    --hidden-import=shadowsocks.asyncdns \
    --hidden-import=shadowsocks.common \
    --collect-all=shadowsocks \
    --paths=.
```

## 注意事项

1. **Python 版本兼容性**：本项目已包含 Python 3.13 兼容性修复，支持 Python 3.11、3.12 和 3.13+
2. **打包环境**：建议在 Windows 系统上打包，确保 tkinter 可用
3. **依赖检查**：打包前确保已安装所有依赖：
   ```bash
   pip install shadowsocks pyinstaller
   ```
4. **兼容性修复**：兼容性修复会自动应用，无需手动操作

## 打包后的文件

打包完成后，exe 文件位于 `dist/ShadowsocksServerV3.exe`

## 测试

打包完成后，可以在 Windows 系统上直接运行 exe 文件进行测试。

## Python 3.13 兼容性

本项目已修复 shadowsocks 2.8.2 与 Python 3.13+ 的兼容性问题：
- 问题：Python 3.13 移除了 `collections.MutableMapping`
- 解决方案：在 `compat.py` 中自动修复，将 `collections.abc.MutableMapping` 映射到 `collections.MutableMapping`
- 状态：✅ 已修复，支持 Python 3.13+

