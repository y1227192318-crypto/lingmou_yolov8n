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