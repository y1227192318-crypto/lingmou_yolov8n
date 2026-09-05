#!/usr/bin/env bash
#
# 灵眸-yolo 环境一键搭建脚本（macOS / Linux）
# 用法：  bash install.sh
#       bash install.sh aliyun        # 国内网络使用阿里云镜像加速
#       MIRROR=xxx bash install.sh    # 自定义 PyPI 镜像
#
set -e

echo "============================================"
echo "  灵眸-yolo 环境自动搭建脚本 (macOS/Linux)"
echo "============================================"
echo

# ---------- 1. PyPI 镜像 ----------
MIRROR="$MIRROR"
if [ -z "$MIRROR" ] && [ "$1" = "aliyun" ]; then
    MIRROR="https://mirrors.aliyun.com/pypi/simple/"
fi
if [ -z "$MIRROR" ]; then
    MIRROR="https://pypi.org/simple"
fi
echo "[1/4] 使用 PyPI 镜像: $MIRROR"
echo

# ---------- 2. 检测 Python ----------
echo "[2/4] 检测 Python 版本..."
PY=""
for c in python3 python; do
    if command -v "$c" >/dev/null 2>&1; then
        V="$($c -c 'import sys; print("%d.%d" % sys.version_info[:2])' 2>/dev/null || true)"
        ver="$(printf '%s' "$V" | cut -d. -f1)"
        minor="$(printf '%s' "$V" | cut -d. -f2)"
        if [ "$ver" -ge 3 ] && [ "$minor" -ge 8 ]; then
            PY="$c"
            break
        fi
    fi
done

if [ -z "$PY" ]; then
    echo "[错误] 未找到 Python 3.8+，请先安装:"
    echo "         macOS:   brew install python"
    echo "         Ubuntu:  sudo apt install python3 python3-venv"
    echo "         装完重新运行本脚本。"
    exit 1
fi
echo "        已找到 Python: $($PY --version)"
echo

# ---------- 3. 创建虚拟环境 ----------
echo "[3/4] 创建虚拟环境 .venv ..."
$PY -m venv .venv
. .venv/bin/activate
echo "        完成。"
echo

# ---------- 4. 安装依赖 ----------
echo "[4/4] 安装 torch / torchvision / 其余依赖 (镜像: $MIRROR) ..."
echo "        提示: 有 NVIDIA 独显的 Linux 用户如需 GPU 加速，"
echo "        可改用官方 CUDA 源安装后跳过本步，其余依赖再用本脚本。"
python -m pip install --upgrade pip
python -m pip install -i "$MIRROR" torch torchvision
python -m pip install -i "$MIRROR" -r requirements.txt
echo

echo "============================================"
echo "  全部安装完成!"
echo "  启动:  bash 启动灵眸.sh"
echo "============================================"