@echo off
chcp 936 >nul

echo ============================================
echo   灵眸-yolo 环境自动搭建脚本(含 Python)
echo ============================================
echo.

REM ================= 1. 检测/安装 Python =================
set "HAVE_PY="
python --version >nul 2>&1
if errorlevel 1 goto INSPY
echo [1/4] 已检测到 Python:
python --version
goto OUTPY

:INSPY
echo [1/4] 未检测到 Python, 正在通过 winget 自动安装(需联网)...
winget install -e --id Python.Python.3.12 --silent --accept-package-agreements --accept-source-agreements
if errorlevel 1 goto INSTALLFAIL
echo        Python 安装完成, 刷新环境变量...
for /f "tokens=2*" %%A in ('reg query "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v Path 2^>nul') do set "MACHINE_PATH=%%B"
for /f "tokens=2*" %%A in ('reg query "HKCU\Environment" /v Path 2^>nul') do set "USER_PATH=%%B"
set PATH=!MACHINE_PATH!;!USER_PATH!;%PATH%
python --version >nul 2>&1
if errorlevel 1 goto PATHTRYAGAIN
echo        已检测到 Python:
python --version

:OUTPY
echo.

REM ================= 2. 启用长路径支持 =================
echo [2/4] 启用 Windows 长路径支持...
reg add "HKLM\SYSTEM\CurrentControlSet\Control\FileSystem" /v LongPathsEnabled /t REG_DWORD /d 1 /f >nul 2>&1
echo.

REM ================= 3. 安装 torch/torchvision =================
echo [3/4] 安装 torch / torchvision (阿里云 CPU 镜像), 请耐心等待...
pip install -i https://mirrors.aliyun.com/pypi/simple/ --find-links https://mirrors.aliyun.com/pytorch-wheels/cpu/ torch torchvision
if errorlevel 1 goto PIPFAIL
echo.

REM ================= 4. 安装其余依赖 =================
echo [4/4] 安装其余依赖 (ultralytics / PySide6 等, 阿里云镜像)...
pip install -i https://mirrors.aliyun.com/pypi/simple/ -r requirements.txt
if errorlevel 1 goto PIPFAIL
echo.

echo ============================================
echo   全部安装完成! 双击 "启动灵眸.bat" 即可打开程序.
echo ============================================
pause
exit /b 0

:INSTALLFAIL
echo.
echo [错误] Python 自动安装失败, 请手动到 python.org 下载并安装,
echo        安装时务必勾选 "Add Python to PATH", 装完重装运行本脚本.
pause
exit /b 1

:PATHTRYAGAIN
echo [提示] PATH 刷新可能未立即生效, 请关闭本窗口后重新双击运行.
pause
exit /b 1

:PIPFAIL
echo [错误] 依赖安装失败, 请检查网络后重试.
pause
exit /b 1