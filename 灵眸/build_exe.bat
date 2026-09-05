@echo off
chcp 65001 >nul
echo ============================================
echo   正在打包为独立 exe（可能需要几分钟）...
echo ============================================
pip install pyinstaller
pyinstaller --noconfirm --windowed --onedir --name 灵眸 ^
  --collect-all ultralytics ^
  --collect-all torch ^
  --collect-all torchvision ^
  --collect-all cv2 ^
  --collect-all PIL ^
  app.py
echo.
echo 打包完成！
echo 程序位置: dist\灵眸\灵眸.exe
echo 请把 yolov8n.pt 复制到 exe 同目录下，然后整个文件夹即可拷到其他电脑使用。
pause
