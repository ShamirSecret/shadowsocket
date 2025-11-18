@echo off
chcp 65001 >nul
echo ============================================================
echo Shadowsocks 服务端 V2 打包脚本
echo ============================================================
echo.

REM 检查 Python 是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Python，请先安装 Python 3.7+
    pause
    exit /b 1
)

echo [1/3] 检查依赖...
python -c "import shadowsocks" >nul 2>&1
if errorlevel 1 (
    echo [警告] shadowsocks 库未安装，正在安装...
    pip install shadowsocks
    if errorlevel 1 (
        echo [错误] 安装 shadowsocks 失败
        pause
        exit /b 1
    )
)

python -c "import PyInstaller" >nul 2>&1
if errorlevel 1 (
    echo [警告] PyInstaller 未安装，正在安装...
    pip install pyinstaller
    if errorlevel 1 (
        echo [错误] 安装 PyInstaller 失败
        pause
        exit /b 1
    )
)

echo [2/3] 开始打包...
python build_exe_v2.py

if errorlevel 1 (
    echo.
    echo [错误] 打包失败，请检查错误信息
    pause
    exit /b 1
)

echo.
echo [3/3] 打包完成！
echo.
echo 生成的 exe 文件位于: dist\ShadowsocksServerV2.exe
echo.
pause

