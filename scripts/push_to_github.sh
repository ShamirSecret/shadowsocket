#!/bin/bash
# GitHub 推送脚本

echo "=========================================="
echo "GitHub 推送助手"
echo "=========================================="
echo ""

# 检查是否已设置远程仓库
if git remote get-url origin >/dev/null 2>&1; then
    echo "✓ 已设置远程仓库: $(git remote get-url origin)"
    echo ""
    read -p "是否推送到现有仓库? (y/n): " confirm
    if [ "$confirm" != "y" ]; then
        echo "已取消"
        exit 0
    fi
else
    echo "尚未设置远程仓库"
    echo ""
    echo "请选择："
    echo "1. 使用现有 GitHub 仓库"
    echo "2. 创建新 GitHub 仓库（需要手动在 GitHub 上创建）"
    echo ""
    read -p "请选择 (1/2): " choice
    
    if [ "$choice" == "1" ]; then
        read -p "请输入 GitHub 仓库 URL (例如: https://github.com/username/repo.git): " repo_url
        if [ -n "$repo_url" ]; then
            git remote add origin "$repo_url"
            echo "✓ 已设置远程仓库: $repo_url"
        else
            echo "错误: 仓库 URL 不能为空"
            exit 1
        fi
    elif [ "$choice" == "2" ]; then
        echo ""
        echo "请按以下步骤操作："
        echo "1. 访问 https://github.com/new 创建新仓库"
        echo "2. 复制仓库 URL（例如: https://github.com/username/repo.git）"
        echo "3. 运行以下命令："
        echo "   git remote add origin <你的仓库URL>"
        echo "   git push -u origin main"
        echo ""
        exit 0
    else
        echo "无效选择"
        exit 1
    fi
fi

echo ""
echo "正在推送到 GitHub..."
git push -u origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo "✓ 推送成功！"
    echo "=========================================="
    echo ""
    echo "下一步："
    echo "1. 访问 GitHub 仓库页面"
    echo "2. 点击 'Actions' 标签"
    echo "3. 选择 'Build Windows EXE' 工作流"
    echo "4. 点击 'Run workflow' 开始自动打包"
    echo ""
else
    echo ""
    echo "推送失败，请检查："
    echo "1. GitHub 仓库 URL 是否正确"
    echo "2. 是否有推送权限"
    echo "3. 是否已配置 GitHub 认证（SSH key 或 Personal Access Token）"
    echo ""
fi

