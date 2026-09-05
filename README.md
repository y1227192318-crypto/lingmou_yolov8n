# 灵眸-yolo · 桌面视觉识别工具

> 基于 YOLOv8 的桌面视觉识别工具 —— 开箱即用，支持图片检测、批量处理、摄像头实时监测、自动保存、CSV 报表导出、AI 统计总结。

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![YOLOv8](https://img.shields.io/badge/YOLO-v8-brightgreen)](https://github.com/ultralytics/ultralytics)
[![PySide6](https://img.shields.io/badge/PySide-6-orange)](https://wiki.qt.io/Qt_for_Python)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

---

## 项目背景

灵眸-YOLO 是一款基于 YOLOv8 的桌面端视觉识别应用，提供单张、批量、摄像头实时三种检测方式，并内置自动保存、CSV 报表导出与 AI 统计总结。适用于不熟悉命令行的普通使用者，也便于开发者在此框架上进行扩展。

## 功能一览

| 功能 | 说明 |
|---|---|
| 单张检测 | 对单张图片检测目标并画框标注 |
| 批量检测 | 批量处理文件夹内图片，导出 CSV 统计报表 |
| 摄像头实时监测 | 实时识别摄像头画面，结果逐帧刷新 |
| 自动保存 | 按置信度阈值自动保存检测结果图片 |
| 多格式输出 | 支持 JPG / PNG / BMP / WEBP / TIFF |
| 模型热切换 | 运行中随时更换模型，无需重启 |
| 参数持久化 | 设置自动保存至 config.json，重启恢复 |
| AI 统计总结 | 批量检测后生成客观的目标统计总结，自动导出文本 |

## 与其他开源项目的对比

| 对比项 | 灵眸-YOLO | 多数同类 YOLO GUI |
|---|---|---|
| 交互形态 | 图形界面 | 命令行或简易界面 |
| 检测方式 | 图片 / 批量 / 摄像头 三合一 | 通常仅其一 |
| 报表导出 | 内置 CSV + AI 报告 | 多数无 |
| 自动保存 | 阈值化自动保存 | 少见 |
| 配置持久化 | 自动保存至 config.json | 一般无 |
| 安装 / 部署 | 一键安装脚本 + exe 打包 | 需自行配置 |

## 模型说明

> 程序通过「选择模型」加载任意 YOLO 格式的 `.pt` 权重文件，可随时切换，无需重启。
>
> - **预训练模型**：内置官方通用模型，随程序交付。
> - **自定义模型**：使用 YOLO 格式标注工具（如 LabelImg、labelme）标注数据后训练，将生成的 `.pt` 放入 `models/` 即可在程序中加载。

### AI 大模型接入（用于 AI 智能报告）

- **DeepSeek（默认）**：在 [DeepSeek 开放平台](https://platform.deepseek.com/) 申请 API Key 后，将其填入 `config.json` 中 `"ai"` 配置段：
  - `api_key`：你的接口密钥
  - `base_url`：`https://api.deepseek.com/v1/chat/completions`
  - `model`：`deepseek-v4-flash`（测试模型，官方推荐；另有 `deepseek-v4-pro`、视觉版 `deepseek-v4-flash-vision-exp`）
- **其他 AI 厂家**：接入采用 **OpenAI 兼容的 Chat Completions 协议**。凡提供 OpenAI 兼容接口的厂商，仅需将上述 `base_url`、`api_key`、`model` 三项改为对方提供的值即可接入，无需改动代码；若对方不兼容该协议，则需自行改写请求逻辑。
- AI 功能默认关闭（`enabled: false`）；未配置密钥时自动禁用，不影响本地检测。

## 快速开始

### 安装依赖（只需一次）

**方式一：一键安装（推荐）**

- **Windows**：直接双击 `install.bat`（CPU）或 `install_gpu.bat`（GPU），脚本会自动检测/安装 Python、配置国内镜像并装好全部依赖。
- **macOS / Linux**：在项目目录执行
  ```bash
  bash install.sh        # 默认官方源
  bash install.sh aliyun # 国内网络用阿里云镜像加速
  ```
  脚本会自动检测 Python 3.8+、创建 `.venv` 虚拟环境并安装全部依赖。

**方式二：命令行手动安装**

如果你不想用一键脚本，可以在命令行中按以下步骤自行搭建环境。

**① 安装 Python（仅需一次）**

去 [python.org](https://www.python.org/downloads/) 下载 **3.8 及以上**版本（建议 3.10 或 3.12），安装时务必勾选 **「Add Python to PATH」**。装完后在命令行验证：

```bash
python --version
```

出现版本号即安装成功。

**② 安装 PyTorch（CPU 或 GPU 二选一）**

```bash
# 无 NVIDIA 独显 → CPU 版
pip install -i https://mirrors.aliyun.com/pypi/simple/ --find-links https://mirrors.aliyun.com/pytorch-wheels/cpu/ torch torchvision

# 有 NVIDIA 独显 → GPU 版（CUDA 11.8）
pip install torch torchvision --index-url https://mirrors.aliyun.com/pytorch-wheels/cu118/
```

> GPU 版装完后可验证显卡是否可用：`python -c "import torch; print(torch.cuda.is_available())"`，输出 `True` 即正常。

**③ 安装其余依赖**

```bash
# 方案 A：用 requirements.txt（CPU 通用依赖）
pip install -i https://mirrors.aliyun.com/pypi/simple/ -r requirements.txt

# 方案 B：GPU 版逐个安装（不含 torch，避免覆盖 CUDA 版）
pip install -i https://mirrors.aliyun.com/pypi/simple/ ultralytics PySide6 opencv-python numpy Pillow
```

**④ 验证环境**

```bash
python -c "import ultralytics, PySide6, cv2, numpy, PIL; print('环境 OK')"
```

无报错即环境搭建完成，然后按下面的步骤启动程序。

### 启动

```bash
python app.py
```

- **Windows**：双击 `启动灵眸.bat`
- **macOS / Linux**：在项目目录执行 `bash 启动灵眸.sh`（自动优先使用 `.venv` 虚拟环境）

程序自动加载 `yolov8n.pt`（COCO 80 类通用目标），即可开始识别。

## 界面概览

```
┌─────────────────────────────────────────────────────┐
│  灵眸-yolo                                           │
│  视觉识别（demo版）                     模型：yolov8n.pt │
│                                                     │
│  [📷 选择图片] [📂 批量检测] [🧠 选择模型] [🗑 清空]     │
│  [📷 实时监测] [🌓 主题]                               │
│  ┌──────────────────────┬──────────────────────────┐ │
│  │                      │ 检测结果                  │ │
│  │   图片预览区域         │  1. person  0.92         │ │
│  │                      │  2. cup     0.78         │ │
│  │   (滚轮缩放 + 拖拽)    │  3. cell phone 0.65     │ │
│  │                      ├──────────────────────────┤ │
│  │                      │ 检测设置                  │ │
│  │                      │ 置信度阈值: 0.25  ───●──  │ │
│  │                      ├──────────────────────────┤ │
│  │                      │ 自动保存（图片）▸          │ │
│  │                      │ 实时监测▸                 │ │
│  │                      ├──────────────────────────┤ │
│  │                      │ 保存设置                  │ │
│  │                      │ 保存位置: output/         │ │
│  │                      │ 输出格式: JPG ▼           │ │
│  │                      │ [💾 保存结果]              │ │
│  └──────────────────────┴──────────────────────────┘ │
│  就绪                                                   │
└─────────────────────────────────────────────────────┘
```

## 界面与操作说明

| 按钮 / 分组 | 作用 |
|---|---|
| 选择图片 | 选择单张图片检测 |
| 批量检测 | 对整个文件夹的所有图片依次检测 |
| 选择模型 | 手动加载其他 `.pt` 模型 |
| 清空 | 清空当前画面与结果 |
| 实时监测 | 开关摄像头实时识别（需电脑有摄像头） |
| 主题 | 浅色 / 深色主题切换 |

### 检测结果
逐条列出识别到的目标：`序号 + 类别 + 置信度`，支持上下滚动。

### 检测设置
- **置信度阈值**：滑块调节，低于该置信度的目标不显示（范围 0.05～0.95，默认 0.25）。

### 自动保存（图片）
勾选分组标题展开，用于**单张 / 批量图片检测**自动保存：
- 「🔴 自动保存检测结果」：总开关
- 「置信度 ≥ XX 才保存」：目标最高置信度达到阈值才保存（默认 0.5）

### 实时监测
勾选分组标题展开，用于**摄像头实时监测**的自动保存：
- 「🔴 自动保存监测结果」：总开关
- 「置信 / 稳定帧 / 冷却秒」三个触发条件（默认 0.5 / 6 / 3），三者同时满足才保存一张：
  - **置信**：目标最高置信度 ≥ 该值
  - **稳定帧**：目标连续 N 帧被检测到
  - **冷却秒**：距上次保存至少 T 秒（防止同一目标重复保存）

### 保存设置
- **保存位置**：标注结果输出目录（默认 `output/`）
- **输出格式**：JPG / PNG / BMP / WEBP / TIFF 任选

> 文件命名规则：图片检测结果为 `原文件名_detected.后缀`；实时监测自动保存为 `monitor_日期_时间.后缀`。

## AI 统计总结

可选接入云端 AI 大模型，把批量检测的统计数据加工成客观、易读的总结。

- **触发方式**：完成一次「批量检测」后，点击顶部 **「🤖 AI 报告总结」** 按钮（该按钮仅用于批量检测）。
- **总结内容**：图片总数、目标总数、各类目标的数量分布等客观统计，不做任何"合格 / 不合格"之类的质量判定，也不对目标作主观定性。
- **自动导出**：生成同时自动存为 `AI报告_<批量文件夹名>_<日期时间>.txt`，与 CSV 报表同目录，时间精确到秒，重复检测不会覆盖。
- **隐私友好**：仅把批量统计文本（数量、类别）发送给云端，**不会上传任何图片**；未配置接口密钥时 AI 功能自动禁用，完全不影响本地检测流程。
- **厂商兼容**：接入采用 **OpenAI 兼容的 Chat Completions 协议**，默认指向 DeepSeek；凡提供 OpenAI 兼容接口的厂商，只需修改 `config.json` 中 `"ai"` 段的 `base_url`、`api_key`、`model` 即可切换，无需改动代码。若某厂商不兼容该协议，则需自行改写请求部分。

### 开启步骤

1. 在 `config.json` 的 `"ai"` 配置段，填入你的接口地址、接口密钥，以及所用对话模型名称（模型名请按所购服务的官方文档填写）。
2. 重启程序 → 完成一次批量检测 → 点击「🤖 AI 报告总结」，报告会显示在右侧并在 `output/`（或你设置的保存目录）自动落盘。

## 技术栈

| 领域 | 技术 |
|---|---|
| 检测框架 | YOLOv8（ultralytics） |
| 界面框架 | PySide6（Qt6） |
| 图像处理 | OpenCV + Pillow |
| 深度学习 | PyTorch |
| 打包部署 | PyInstaller |
| 国内镜像 | 阿里云 PyPI + 阿里云 CUDA wheels |

## 目录结构

```
灵眸/
├── app.py            # 桌面程序主文件
├── train.py          # 训练脚本
├── voc2yolo.py       # VOC XML → YOLO 格式转换脚本
├── requirements.txt  # 依赖清单
├── install.bat       # 依赖一键安装（CPU，国内镜像）
├── install_gpu.bat   # 依赖一键安装（NVIDIA GPU）
├── 启动灵眸.bat       # 一键启动程序
├── train.bat         # 一键训练
├── build_exe.bat     # 打包为独立 exe
├── config.json       # 用户配置（自动生成）
├── yolov8n.pt        # 预训练模型
├── dataset/          # 数据集（YOLO 格式）
│   ├── images/train/
│   ├── images/val/
│   ├── labels/train/
│   ├── labels/val/
│   └── data.yaml
├── models/           # 训练好的模型
├── output/           # 默认标注结果保存位置
└── runs/             # 训练过程记录（自动生成）
```

## 模型说明

| 模型 | 来源 | 说明 |
|---|---|---|
| `yolov8n.pt` | 官方预训练 | COCO 80 类通用目标，程序默认加载 |
| `models/best.pt` | 自己训练 | 训练后自动生成，用「选择模型」加载 |

- 想识别其它官方模型（如 `yolov8s.pt`、`yolov8m.pt`），下载后放本目录，用「选择模型」加载即可。
- 预训练模型下载（国内镜像）：
  `https://hf-mirror.com/Ultralytics/YOLOv8/resolve/main/yolov8n.pt`

## 训练自己的模型

默认模型只能识别 COCO 的 80 类通用目标。若要识别你自己的特定目标，按下面流程训练。

### 1. 准备数据（YOLO 格式）

```
dataset/
├── images/train/    # 训练图片
├── images/val/      # 验证图片
├── labels/train/    # 每张训练图的同名 .txt 标注
├── labels/val/
└── data.yaml
```

`data.yaml` 示例（类别按 0 开始编号）：

```yaml
path: dataset
train: images/train
val: images/val
names:
  0: person
  1: cup
  2: cell phone
```

### 2. VOC XML 转 YOLO（若标注是 Pascal VOC 格式）

支持 `Annotations/` + `JPEGImages/` 结构：

```bash
python voc2yolo.py --input "你的标注文件夹" --output dataset
```

| 参数 | 含义 | 默认值 |
|---|---|---|
| `--input` | XML 和图片所在文件夹 | `voc_data` |
| `--output` | 转换后 YOLO 数据集输出目录 | `dataset` |
| `--val-ratio` | 验证集比例 | `0.2`（8:2 划分） |

转换完成后自动：解析 XML → 归一化坐标写入 `.txt` → 8:2 划分 → 复制图片 → 生成 `data.yaml`。

### 3. 训练

```bash
python train.py --epochs 100 --imgsz 640 --batch 8
```

| 参数 | 建议 |
|---|---|
| `--epochs` | 100 起步，数据少可 150 |
| `--imgsz` | 默认 640，显存小降到 512 |
| `--batch` | 默认 8，2G 显存设 4 或 2 |

训练完成后模型自动保存到 `models/best.pt`。打开程序点「选择模型」加载即可。

### 4. 新增多个数据集（保留旧模型）

如果已经训练过一个数据集（比如咖啡），现在想训练新数据集又**保留旧模型**：

1. **备份旧模型**：
   ```
   灵眸/models/
   ├── best.pt             ← 旧模型（咖啡），直接改名为 coffee_best.pt
   └── coffee_best.pt      ← 备份完成，之后随时可以切回来用
   ```

2. **准备新数据集**：
   - 推荐方案：新数据集放在灵眸目录外面，比如 `C:\Users\你的用户名\Desktop\我的新数据集`：
     ```
     我的新数据集/
     ├── images/train/
     ├── images/val/
     ├── labels/train/
     ├── labels/val/
     └── data.yaml
     ```
   - 也可以在灵眸目录里分开放：`灵眸/dataset_coffee/` 和 `灵眸/dataset_xxx/`

3. **训练新数据集**：
   ```bash
   cd 灵眸
   python train.py --data "C:\Users\你的用户名\Desktop\我的新数据集\data.yaml" --epochs 100
   ```
   训练完成后，新模型自动保存为 `models/best.pt`，不影响你备份好的 `coffee_best.pt`。

4. **切换模型**：
   - 想识别旧目标 → 打开程序 → 点「选择模型」→ `models/coffee_best.pt`
   - 想识别新目标 → 点「选择模型」→ `models/best.pt`（新模型）

> 训练前一定要备份旧模型，否则新训练会覆盖 `best.pt`，旧模型找不回来。

## 打包为独立 exe

```bash
pip install pyinstaller
build_exe.bat
```

完成后：
- 程序位置：`dist\灵眸\灵眸.exe`
- 把 `yolov8n.pt` 复制到 exe 同目录，整个文件夹即可拷到其它电脑使用

## 常见问题

**Q1：双击 `启动灵眸.bat` 提示找不到模块**
A：先双击 `install.bat`（或 `install_gpu.bat`）安装依赖。

**Q2：检测一直「未检测到目标」**
A：默认模型是 COCO 80 类通用目标，不是所有物体都能识别；可降低置信度阈值，或训练自己的模型。

**Q3：实时监测提示「无法打开摄像头」**
A：确认电脑有摄像头、摄像头未被其它程序占用。

**Q4：训练报 Out of Memory / OOM（显存不足）**
A：把 `--batch` 调小（16→8→4→2），或 `--imgsz` 调小（640→512）。

**Q5：想离线使用、不联网？**
A：检测过程本身 100% 本地运行、不上传图片。首次安装依赖与首次下载模型需联网；模型 `yolov8n.pt` 已预置在本目录，依赖装好后即可完全离线检测。

## 为什么选择灵眸-yolo

- **真正开箱即用**：下载下来，装一次依赖，双击就能跑，不是玩具 demo
- **功能完整**：检测、批量、实时、自动保存、报表导出一条龙，真实场景可以直接用
- **国内用户友好**：所有依赖安装脚本已配置阿里云镜像，不卡 pip，不翻墙
- **可扩展**：代码结构清晰，可以在此基础上加功能、改界面、接自己的模型
- **隐私安全**：所有检测本地运行，不上传任何图片到云端

## 开源协议

本项目基于 [MIT License](LICENSE) 开源，欢迎使用、修改、分发。

**第三方组件说明**：本仓库包含 YOLOv8 官方预训练权重 `yolov8n.pt`，该文件由 Ultralytics 发布，遵循 **AGPL-3.0** 许可（与本体 MIT 许可不同），详见 [NOTICE](NOTICE)。其余运行时依赖通过安装脚本自动下载，按其各自许可条款使用。

## 贡献

欢迎提交 Issue 和 PR！如果你有好的想法或者发现了 bug，欢迎一起改进。

# LINGMOU-YOLO · Desktop Vision Recognition Tool

> A YOLOv8-based desktop vision recognition tool — ready to use out of the box. Supports single-image detection, batch processing, real-time camera monitoring, auto-save, CSV report export, and an AI stats summary.

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![YOLOv8](https://img.shields.io/badge/YOLO-v8-brightgreen)](https://github.com/ultralytics/ultralytics)
[![PySide6](https://img.shields.io/badge/PySide-6-orange)](https://wiki.qt.io/Qt_for_Python)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

---

## About This Project

LINGMOU-YOLO is a YOLOv8-based desktop vision application offering three detection modes — single-image, batch processing, and real-time camera monitoring — with auto-save, CSV report export and an AI stats summary. It suits end users unfamiliar with the command line, and is easy for developers to extend.

## Features

| Feature | Description |
|---|---|
| Single-image detection | Detect objects on a single image and draw bounding boxes |
| Batch detection | Process all images in a folder, export a CSV report |
| Real-time camera monitoring | Live recognition from camera feed, results updated frame by frame |
| Auto-save | Save result images based on a confidence threshold |
| Multiple output formats | JPG / PNG / BMP / WEBP / TIFF |
| Hot model switching | Swap models at runtime without restarting |
| Settings persistence | Preferences auto-saved to config.json, restored on next launch |
| AI stats summary | Generate an objective target-count summary after batch detection, auto-exported as text |

## Comparison with Other Open-Source Projects

| Aspect | LINGMOU-YOLO | Most similar YOLO GUIs |
|---|---|---|
| Interface | Graphical | CLI or minimal UI |
| Detection modes | Image / batch / camera, all-in-one | Usually only one |
| Report export | Built-in CSV + AI report | Most lack it |
| Auto-save | Threshold-based auto-save | Rare |
| Settings persistence | Auto-saved to config.json | Usually none |
| Install / deploy | One-click scripts + exe packaging | Manual setup required |

## Model Notes

> Load any YOLO-format `.pt` weight file via **"Select Model"** and switch at any time without restarting.
>
> - **Pretrained model**: An official general-purpose model ships with the app.
> - **Custom model**: Label data with a YOLO-format labeling tool (e.g. LabelImg, labelme), train, then drop the resulting `.pt` into `models/` to load it in the app.

### AI Large Model Access (For AI Smart Report)

- **DeepSeek (default)**: After requesting an API Key from the [DeepSeek Open Platform](https://platform.deepseek.com/), fill in the `"ai"` section in `config.json`:
  - `api_key`: your API key
  - `base_url`: `https://api.deepseek.com/v1/chat/completions`
  - `model`: `deepseek-v4-flash` (test model, officially recommended; also available: `deepseek-v4-pro`, vision model `deepseek-v4-flash-vision-exp`)
- **Other providers**: The integration uses the **OpenAI-compatible Chat Completions protocol**. Any provider that offers an OpenAI-compatible endpoint can be connected by changing the above three values (`base_url`, `api_key`, `model`) — no code changes required. If the provider does not follow this protocol, you need to rewrite the request logic yourself.
- The AI feature is disabled by default (`enabled: false`). If no key is configured, it is automatically disabled and does not affect local detection.

## Quick Start

### Install dependencies (one-time)

**Option 1: One-click script (recommended)**

- **Windows**: Double-click `install.bat` (CPU) or `install_gpu.bat` (GPU). The script auto-detects/installs Python, configures China mirrors, and installs all dependencies.
- **macOS / Linux**: In the project directory run
  ```bash
  bash install.sh        # default official PyPI source
  bash install.sh aliyun # use Aliyun mirror if you're in China
  ```
  The script auto-detects Python 3.8+, creates a `.venv` virtual environment, and installs all dependencies.

**Option 2: Manual install from the command line**

If you prefer not to use the one-click script, you can set up the environment step by step in a terminal.

**① Install Python (once only)**

Go to [python.org](https://www.python.org/downloads/) and download **Python 3.8+** (recommend 3.10 or 3.12). During installation, be sure to check **"Add Python to PATH"**. Verify in the terminal:

```bash
python --version
```

You'll see a version number if it's installed successfully.

**② Install PyTorch (CPU or GPU — choose one)**

```bash
# No NVIDIA GPU → CPU version
pip install -i https://mirrors.aliyun.com/pypi/simple/ --find-links https://mirrors.aliyun.com/pytorch-wheels/cpu/ torch torchvision

# NVIDIA GPU → GPU version (CUDA 11.8)
pip install torch torchvision --index-url https://mirrors.aliyun.com/pytorch-wheels/cu118/
```

> For the GPU version you can verify the GPU afterward: `python -c "import torch; print(torch.cuda.is_available())"`. Output `True` means it's working.

**③ Install the remaining dependencies**

```bash
# Option A: Install from requirements.txt (generic CPU deps)
pip install -i https://mirrors.aliyun.com/pypi/simple/ -r requirements.txt

# Option B: For GPU, install packages individually (excluding torch, to avoid overwriting the CUDA build)
pip install -i https://mirrors.aliyun.com/pypi/simple/ ultralytics PySide6 opencv-python numpy Pillow
```

**④ Verify the environment**

```bash
python -c "import ultralytics, PySide6, cv2, numpy, PIL; print('Env OK')"
```

If there's no error, the environment is ready. Then follow the launch steps below.

### Launch

```bash
python app.py
```

- **Windows**: Double-click `启动灵眸.bat`
- **macOS / Linux**: Run `bash 启动灵眸.sh` in the project directory (it auto-prefers the `.venv` virtual environment)

The program auto-loads `yolov8n.pt` (COCO, 80 classes) and is ready to detect.

## UI Overview

```
┌─────────────────────────────────────────────────────┐
│  LINGMOU-YOLO                                        │
│  Vision Recognition (demo)            Model: yolov8n.pt│
│                                                     │
│  [📷 Select Image] [📂 Batch] [🧠 Select Model] [🗑 Clear]│
│  [📷 Live Monitor] [🌓 Theme]                        │
│  ┌──────────────────────┬──────────────────────────┐ │
│  │                      │ Detection Results        │ │
│  │    Image Preview      │  1. person  0.92         │ │
│  │                      │  2. cup     0.78         │ │
│  │   (wheel zoom + drag) │  3. cell phone 0.65     │ │
│  │                      ├──────────────────────────┤ │
│  │                      │ Detection Settings       │ │
│  │                      │ Confidence: 0.25  ───●──  │ │
│  │                      ├──────────────────────────┤ │
│  │                      │ Auto-save (images) ▸     │ │
│  │                      │ Live Monitor ▸           │ │
│  │                      ├──────────────────────────┤ │
│  │                      │ Save Settings            │ │
│  │                      │ Path: output/            │ │
│  │                      │ Format: JPG ▼            │ │
│  │                      │ [💾 Save]                │ │
│  └──────────────────────┴──────────────────────────┘ │
│  Ready                                                 │
└─────────────────────────────────────────────────────┘
```

## Interface & Usage

| Button / Group | Purpose |
|---|---|
| Choose Image | Detect a single image |
| Batch Detect | Detect all images in a folder |
| Choose Model | Load another `.pt` model manually |
| Clear | Clear current preview and results |
| Live Monitor | Toggle camera real-time detection |
| Theme | Toggle light / dark theme |

### Detection Results
Lists detected targets one by one: `index + class + confidence`, scrollable.

### Detection Settings
- **Confidence threshold**: slider, objects below this confidence are hidden (range 0.05–0.95, default 0.25).

### Auto-save (Images)
Check the group title to expand, used for **single / batch image detection** auto-save:
- "🔴 Auto-save results": master switch
- "Save only if confidence ≥ XX": saves only when max confidence reaches threshold (default 0.5)

### Live Monitor
Check the group title to expand, used for **camera real-time monitoring** auto-save:
- "🔴 Auto-save monitoring": master switch
- "Confidence / Stable frames / Cooldown seconds" three triggers (default 0.5 / 6 / 3). A frame is saved only when all three are satisfied:
  - **Confidence**: max target confidence ≥ value
  - **Stable frames**: target continuously detected for N frames
  - **Cooldown seconds**: at least T seconds since last save (prevents duplicate saves)

### Save Settings
- **Save location**: output directory (default `output/`)
- **Output format**: JPG / PNG / BMP / WEBP / TIFF

> Naming rules: image detection results are `original_detected.ext`; live monitor auto-saves are `monitor_date_time.ext`.

## AI Stats Summary

Optionally connects a cloud AI large language model to turn batch detection statistics into an objective, easy-to-read summary.

- **How to trigger**: after a batch detection finishes, click **"🤖 AI Report"** in the top bar (this button works for batch detection only).
- **Summary content**: total images, total targets, per-class target distribution — purely objective statistics, with no "pass / fail" quality judgment and no subjective labeling of targets.
- **Auto export**: saved beside the CSV report as `AI_report_<batch folder>_<date_time>.txt` (time to the second, so re-detecting never overwrites).
- **Privacy**: only the batch statistics text (counts, classes) is sent to the cloud — **images are never uploaded**. The AI feature is disabled automatically when no API key is set, so local detection is unaffected.
- **Vendor compatibility**: uses the **OpenAI-compatible Chat Completions protocol**, pointing to DeepSeek by default. Any provider that offers an OpenAI-compatible endpoint can be used by editing `base_url`, `api_key` and `model` in the `"ai"` section of `config.json` — no code changes needed. If a provider does not follow this protocol, the request part must be rewritten by you.

### Enabling steps

1. In the `"ai"` section of `config.json`, fill in the endpoint URL, API key, and the model name you use (use the name from your provider's official docs).
2. Restart the app → run a batch detection → click **"🤖 AI Report"**. The report appears on the right and is auto-saved to `output/` (or your configured save folder).

## Tech Stack

| Area | Technology |
|---|---|
| Detection | YOLOv8 (ultralytics) |
| GUI framework | PySide6 (Qt6) |
| Image processing | OpenCV + Pillow |
| Deep learning | PyTorch |
| Packaging | PyInstaller |
| China mirror | Aliyun PyPI + Aliyun CUDA wheels |

## Directory Structure

```
lingmou-yolo/
├── app.py            # Main desktop program
├── train.py          # Training script
├── voc2yolo.py       # VOC XML → YOLO format conversion script
├── requirements.txt  # Dependencies
├── install.bat       # One-click dependency install (CPU, China mirror)
├── install_gpu.bat   # One-click dependency install (NVIDIA GPU)
├── 启动灵眸.bat       # One-click launcher
├── train.bat         # One-click training
├── build_exe.bat     # Package into a standalone exe
├── config.json       # User config (auto-generated)
├── yolov8n.pt        # Pretrained model (COCO 80 classes)
├── dataset/          # Dataset (YOLO format)
│   ├── images/train/
│   ├── images/val/
│   ├── labels/train/
│   ├── labels/val/
│   └── data.yaml
├── models/           # Trained models
├── output/           # Default save location
└── runs/             # Training logs (auto-generated)
```

## Model Notes

| Model | Source | Description |
|---|---|---|
| `yolov8n.pt` | Official pretrained | COCO 80 classes, loaded by default |
| `models/best.pt` | Self-trained | Auto-generated after training, load via "Select Model" |

- To use other official models (e.g. `yolov8s.pt`, `yolov8m.pt`), download them, place in the folder, and load via "Select Model".
- Pretrained model download (China mirror):
  `https://hf-mirror.com/Ultralytics/YOLOv8/resolve/main/yolov8n.pt`

## Training Your Own Model

The default model only recognizes 80 COCO general classes. To recognize your own custom targets, train as follows.

### 1. Prepare data (YOLO format)

```
dataset/
├── images/train/    # Training images
├── images/val/      # Validation images
├── labels/train/    # A `.txt` label with the same name for each training image
├── labels/val/
└── data.yaml
```

`data.yaml` example (classes numbered from 0):

```yaml
path: dataset
train: images/train
val: images/val
names:
  0: person
  1: cup
  2: cell phone
```

### 2. Convert VOC XML to YOLO (if labels are Pascal VOC)

Supports `Annotations/` + `JPEGImages/` structure:

```bash
python voc2yolo.py --input "your-label-folder" --output dataset
```

| Parameter | Meaning | Default |
|---|---|---|
| `--input` | Folder containing XML and images | `voc_data` |
| `--output` | Output YOLO dataset directory | `dataset` |
| `--val-ratio` | Validation ratio | `0.2` (80/20 split) |

After conversion: parse XML → write normalized coordinates to `.txt` → 80/20 split → copy images → generate `data.yaml`.

### 3. Train

```bash
python train.py --epochs 100 --imgsz 640 --batch 8
```

| Parameter | Suggestion |
|---|---|
| `--epochs` | Start at 100; more if data is scarce |
| `--imgsz` | Default 640, reduce to 512 if GPU memory is small |
| `--batch` | Default 8; set to 4 or 2 for 2GB VRAM |

After training, the model is auto-saved to `models/best.pt`. Load it via "Select Model".

### 4. Adding Multiple Datasets (Keep Old Models)

If you've trained one dataset (e.g. coffee) and want to train a new one while **keeping the old model**:

1. **Back up the old model**:
   ```
   models/
   ├── best.pt             ← old model (coffee), rename to coffee_best.pt
   └── coffee_best.pt      ← backed up, switch back anytime
   ```

2. **Prepare the new dataset**:
   - Recommended: place the new dataset outside the project folder, e.g. `C:\YourNewDataset` with standard YOLO structure (images/train, images/val, labels/train, labels/val, data.yaml).

3. **Train the new dataset**:
   ```bash
   python train.py --data "C:\YourNewDataset\data.yaml" --epochs 100
   ```
   After training, the new model is saved as `models/best.pt`, leaving your backed-up `coffee_best.pt` untouched.

4. **Switch models**:
   - To recognize old targets → "Select Model" → `models/coffee_best.pt`
   - To recognize new targets → "Select Model" → `models/best.pt` (new model)

> Always back up the old model before training, otherwise new training will overwrite `best.pt` and you'll lose the old one.

## Package into a Standalone exe (Optional)

```bash
pip install pyinstaller
build_exe.bat
```

After completion:
- Executable location: `dist\灵眸\灵眸.exe`
- Copy `yolov8n.pt` to the exe directory; the whole folder can then be copied to other machines.

## FAQ

**Q1: "Cannot find module" when launching**
A: Run `install.bat` (or `install_gpu.bat`) first to install dependencies.

**Q2: Detection always returns "no targets"**
A: The default model recognizes 80 COCO classes, not everything. Lower the confidence threshold, or train your own model.

**Q3: "Cannot open camera" in live monitor**
A: Make sure the computer has a camera and it isn't occupied by another app.

**Q4: Out of Memory / OOM during training**
A: Reduce `--batch` (16→8→4→2), or reduce `--imgsz` (640→512).

**Q5: Offline / no internet?**
A: Detection runs 100% locally and never uploads images. Only the first dependency installation and first model download need internet; `yolov8n.pt` is already included, so after installing dependencies you can detect fully offline.

## Why LINGMOU-YOLO

- **Truly out of the box**: download, install once, double-click to run — not a toy demo
- **Feature complete**: detection, batch, real-time, auto-save, and report export in one workflow, usable in production
- **China-user friendly**: all dependency scripts use the Aliyun mirror — no VPN needed
- **Extensible**: clean code structure; easy to add features, change the UI, or plug in your own models
- **Privacy-safe**: all detection runs locally, no images uploaded to the cloud

## License

This project is released under the [MIT License](LICENSE). Feel free to use, modify, and distribute.

**Third-party components**: this repository bundles the official YOLOv8 pretrained weights `yolov8n.pt`, which are released by Ultralytics under the **AGPL-3.0** license (different from this project's MIT license). See [NOTICE](NOTICE) for details. All other runtime dependencies are downloaded by the install scripts and are used under their respective licenses.

## Contributing

Issues and pull requests are welcome! If you have ideas or find bugs, let's improve it together.

---

> If this project helps you, please give it a Star ⭐ !
---

> 如果这个项目对你有帮助，欢迎 Star ⭐ 支持一下！
