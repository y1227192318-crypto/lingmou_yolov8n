@echo off
chcp 936 >nul

echo ============================================
echo   灵眸-yolo 环境自动搭建脚本(GPU/CUDA 版)
echo   适用: 带 NVIDIA 独立显卡的新电脑
echo ============================================
echo.

REM ================= 1. 检测/安装 Python =================
set "HAVE_PY="
python --version >nul 2>&1
if errorlevel 1 goto INSPY
echo [1/5] 已检测到 Python:
python --version
goto OUTPY

:INSPY
echo [1/5] 未检测到 Python, 正在通过 winget 自动安装(需联网)...
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
echo [2/5] 启用 Windows 长路径支持...
reg add "HKLM\SYSTEM\CurrentControlSet\Control\FileSystem" /v LongPathsEnabled /t REG_DWORD /d 1 /f >nul 2>&1
echo.

REM ================= 3. 安装 CUDA 版 PyTorch =================
echo [3/5] 安装 CUDA 版 PyTorch (阿里云镜像, CUDA 11.8), 请耐心等待...
echo        本脚本默认 Python 3.9~3.12 (torch 最新版).
echo        Python 3.8 用户: 请查看脚本内"方案B"注释切换.
REM 方案A (Python 3.9~3.12, 最新版 torch, 默认启用):
pip install torch torchvision --index-url https://mirrors.aliyun.com/pytorch-wheels/cu118/
if errorlevel 1 goto PIPFAIL
REM 方案B (Python 3.8, 锁定 torch 2.3.1): 如需启用, 将上面"方案A"的pip行前加"rem "注释, 并去掉下面这行的"rem "
rem pip install torch==2.3.1 torchvision==0.18.1 --index-url https://mirrors.aliyun.com/pytorch-wheels/cu118/
echo.

REM ================= 4. 安装其余依赖 =================
echo [4/5] 安装其余依赖 (ultralytics / PySide6 等)...
pip install -i https://mirrors.aliyun.com/pypi/simple/ ultralytics PySide6 opencv-python numpy Pillow
if errorlevel 1 goto PIPFAIL
echo.

REM ================= 5. 验证 GPU =================
echo [5/5] 验证 GPU 是否可用...
python -c "import torch; print('CUDA:', torch.cuda.is_available(), '| GPU:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'None')"
echo.

echo ============================================
echo   全部安装完成! 输出 CUDA: True 即 GPU 正常.
echo   然后双击 "启动灵眸.bat" 启动程序.
echo ============================================
pause
exit /b 0

:INSTALLFAIL
echo.
echo [错误] Python 自动安装失败, 请手动到 python.org 下载并安装,
echo        安装时务必勾选 "Add Python to PATH", 装完重新运行本脚本.
pause
exit /b 1

:PATHTRYAGAIN
echo [提示] PATH 刷新可能未立即生效, 请关闭本窗口后重新双击运行.
pause
exit /b 1

:PIPFAIL
echo [错误] 依赖安装失败, 请检查 网络/显卡驱动 后重试.
pause
exit /b 1