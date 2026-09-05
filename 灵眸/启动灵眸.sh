#!/usr/bin/env bash
# 启动灵眸-yolo（macOS / Linux）
# 优先使用本目录虚拟环境，未创建则用系统 python3
cd "$(dirname "$0")"

if [ -x ".venv/bin/python" ]; then
    PY=".venv/bin/python"
elif command -v python3 >/dev/null 2>&1; then
    PY="python3"
else
    PY="python"
fi

exec "$PY" app.py