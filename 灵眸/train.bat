@echo off
chcp 65001 >nul
python train.py %*
pause
