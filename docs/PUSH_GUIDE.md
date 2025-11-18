# 推送到 GitHub 指南

## 方法 1：使用推送脚本（推荐）

```bash
./push_to_github.sh
```

脚本会引导你完成推送过程。

## 方法 2：手动推送

### 步骤 1：创建 GitHub 仓库

1. 访问 https://github.com/new
2. 输入仓库名称（例如：`shadowsocks-server-v2`）
3. 选择 Public 或 Private
4. **不要**初始化 README、.gitignore 或 license（我们已经有了）
5. 点击 "Create repository"

### 步骤 2：设置远程仓库并推送

```bash
# 替换 <你的GitHub用户名> 和 <仓库名>
git remote add origin https://github.com/<你的GitHub用户名>/<仓库名>.git
git push -u origin main
```

### 步骤 3：触发自动打包

1. 访问你的 GitHub 仓库页面
2. 点击 "Actions" 标签
3. 选择 "Build Windows EXE" 工作流
4. 点击 "Run workflow" -> "Run workflow"
5. 等待构建完成（约 5-10 分钟）
6. 下载打包好的 `ShadowsocksServerV3.exe`

## GitHub 认证

如果推送时提示需要认证，可以使用以下方法之一：

### 方法 A：使用 Personal Access Token（推荐）

1. 访问 https://github.com/settings/tokens
2. 点击 "Generate new token" -> "Generate new token (classic)"
3. 选择权限：至少需要 `repo` 权限
4. 生成后复制 token
5. 推送时使用 token 作为密码：
   ```bash
   git push -u origin main
   # Username: 你的GitHub用户名
   # Password: 粘贴你的token
   ```

### 方法 B：使用 SSH Key

1. 生成 SSH key：
   ```bash
   ssh-keygen -t ed25519 -C "your_email@example.com"
   ```
2. 添加 SSH key 到 GitHub：
   ```bash
   cat ~/.ssh/id_ed25519.pub
   # 复制输出，添加到 https://github.com/settings/keys
   ```
3. 使用 SSH URL：
   ```bash
   git remote set-url origin git@github.com:<用户名>/<仓库名>.git
   git push -u origin main
   ```

## 快速命令参考

```bash
# 查看当前状态
git status

# 查看远程仓库
git remote -v

# 添加远程仓库
git remote add origin <仓库URL>

# 推送代码
git push -u origin main

# 如果推送失败，强制推送（谨慎使用）
git push -u origin main --force
```

## 故障排除

### 问题：推送被拒绝
- 检查是否有推送权限
- 确保仓库 URL 正确
- 检查是否已配置认证

### 问题：找不到 Actions
- 确保已推送代码到 GitHub
- 检查 `.github/workflows/` 目录是否存在
- 刷新 GitHub 页面

### 问题：构建失败
- 查看 Actions 日志
- 确保所有依赖正确
- 检查 Python 版本兼容性

