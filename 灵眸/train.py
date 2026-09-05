"""YOLOv8 缺陷检测模型训练脚本

用法:
    python train.py                          # 使用默认配置训练
    python train.py --data 你的数据集/data.yaml --epochs 150
"""
import argparse
import shutil
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_DATA = BASE_DIR / "dataset" / "data.yaml"
MODELS_DIR = BASE_DIR / "models"


def main():
    parser = argparse.ArgumentParser(description="训练 YOLOv8 缺陷检测模型")
    parser.add_argument("--data", type=str, default=str(DEFAULT_DATA),
                        help="YOLO 数据集配置文件 data.yaml 路径")
    parser.add_argument("--model", type=str, default="yolov8n.pt",
                        help="预训练权重（首次运行会自动下载）")
    parser.add_argument("--epochs", type=int, default=100, help="训练轮数")
    parser.add_argument("--imgsz", type=int, default=640, help="输入图片尺寸")
    parser.add_argument("--batch", type=int, default=8, help="批大小")
    parser.add_argument("--device", type=str, default=None,
                        help="cpu 或 cuda，默认自动检测")
    parser.add_argument("--name", type=str, default="defect_detect", help="训练任务名")
    args = parser.parse_args()

    import os
    import torch
    from ultralytics import YOLO

    device = args.device or ("cuda" if torch.cuda.is_available() else "cpu")
    print(f"使用设备: {device}")

    # CPU 训练时限制线程数并禁用多进程加载，避免吃满内存/核心导致系统卡死
    if device == "cpu":
        os.environ.setdefault("OMP_NUM_THREADS", "4")
        try:
            torch.set_num_threads(4)
        except Exception:
            pass
        workers = 0
    else:
        workers = 8

    data = Path(args.data)
    if not data.exists():
        print(f"错误: 找不到数据集配置 {data}")
        print("请确认数据集已放到 dataset/ 目录，并包含 data.yaml")
        print("标准 YOLO 目录结构:")
        print("  dataset/")
        print("    ├── images/train/")
        print("    ├── images/val/")
        print("    ├── labels/train/")
        print("    ├── labels/val/")
        print("    └── data.yaml")
        sys.exit(1)

    print(f"数据集配置: {data}")
    print(f"训练轮数: {args.epochs} | 图片尺寸: {args.imgsz} | 批大小: {args.batch}")

    model_file = Path(args.model)
    if not model_file.exists() and not model_file.suffix:
        print(f"提示: 未找到本地模型 {args.model}，将尝试联网下载")
        print("若下载失败（GitHub 被墙），请手动下载 yolov8n.pt 放到本目录：")
        print("  https://hf-mirror.com/Ultralytics/YOLOv8/resolve/main/yolov8n.pt")

    print("开始训练...")
    model = YOLO(args.model)
    results = model.train(
        data=str(data),
        epochs=args.epochs,
        imgsz=args.imgsz,
        batch=args.batch,
        device=device,
        name=args.name,
        project=str(BASE_DIR / "runs"),
        workers=workers,
        deterministic=False,
    )

    # 优先用返回值定位保存目录，兜底全局搜索
    save_dir = Path(getattr(results, "save_dir", None) or ""
                    ) if getattr(results, "save_dir", None) else None
    best = save_dir / "weights" / "best.pt" if save_dir else None
    if best is None or not best.exists():
        cands = sorted((BASE_DIR / "runs").rglob("best.pt"),
                       key=lambda p: p.stat().st_mtime)
        best = cands[-1] if cands else None

    if best and best.exists():
        MODELS_DIR.mkdir(exist_ok=True)
        target = MODELS_DIR / "best.pt"
        shutil.copy(best, target)
        print(f"\n训练完成！模型已保存到 {target}")
        print("现在可以双击 run_app.bat 打开桌面程序进行检测")
    else:
        print("\n训练完成，但未找到 best.pt，请检查训练输出")


if __name__ == "__main__":
    main()
