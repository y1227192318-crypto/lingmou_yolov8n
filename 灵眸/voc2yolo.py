"""VOC XML 标注 → YOLO 格式 转换脚本

把 Pascal VOC 格式的 XML 标注转换为 YOLOv8 训练所需的格式：
    - 自动扫描 XML，解析类别和边界框
    - 转换为 YOLO txt（归一化坐标）
    - 按 8:2 划分训练/验证集
    - 生成 data.yaml

用法:
    python voc2yolo.py --input 你的标注文件夹 --output dataset
"""
import argparse
import random
import shutil
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def parse_voc_xml(xml_path):
    """解析 VOC XML，返回 (filename, width, height, [(name, xmin, ymin, xmax, ymax), ...])"""
    tree = ET.parse(xml_path)
    root = tree.getroot()
    filename = root.findtext("filename", "").strip()
    size = root.find("size")
    width = int(size.findtext("width", "0"))
    height = int(size.findtext("height", "0"))
    objects = []
    for obj in root.findall("object"):
        name = obj.findtext("name", "").strip()
        box = obj.find("bndbox")
        xmin = float(box.findtext("xmin", "0"))
        ymin = float(box.findtext("ymin", "0"))
        xmax = float(box.findtext("xmax", "0"))
        ymax = float(box.findtext("ymax", "0"))
        objects.append((name, xmin, ymin, xmax, ymax))
    return filename, width, height, objects


def find_image(xml_path, filename, input_dir):
    """在常见位置查找 XML 对应的图片文件"""
    candidates = [
        input_dir / filename,
        input_dir / "JPEGImages" / filename,
        input_dir.parent / "JPEGImages" / filename,
    ]
    for c in candidates:
        if c.exists():
            return c
    # 尝试替换扩展名
    stem = Path(filename).stem
    for ext in IMAGE_EXTS:
        for c in candidates:
            alt = c.with_suffix(ext)
            if alt.exists():
                return alt
    return None


def main():
    parser = argparse.ArgumentParser(description="VOC XML 转 YOLO 格式")
    parser.add_argument("--input", type=str, default="voc_data",
                        help="包含 XML 标注的文件夹（或 Annotations 子文件夹）")
    parser.add_argument("--output", type=str, default="dataset",
                        help="输出 YOLO 数据集目录")
    parser.add_argument("--val-ratio", type=float, default=0.2,
                        help="验证集比例（默认 0.2）")
    args = parser.parse_args()

    input_dir = Path(args.input)
    if not input_dir.exists():
        print(f"错误: 找不到输入文件夹 {input_dir}")
        sys.exit(1)

    # 定位 XML 文件（支持 Annotations 子文件夹）
    xml_dir = input_dir / "Annotations" if (input_dir / "Annotations").exists() else input_dir
    xml_files = sorted(xml_dir.glob("*.xml"))
    if not xml_files:
        print(f"错误: 在 {xml_dir} 中未找到任何 .xml 文件")
        sys.exit(1)
    print(f"找到 {len(xml_files)} 个 XML 标注文件")

    # 解析所有 XML，收集类别
    parsed = []
    class_names = []
    for xml_path in xml_files:
        try:
            filename, width, height, objects = parse_voc_xml(xml_path)
        except Exception as e:
            print(f"警告: 解析 {xml_path.name} 失败: {e}")
            continue
        if not objects:
            print(f"警告: {xml_path.name} 没有标注目标，已跳过")
            continue
        img_path = find_image(xml_path, filename, input_dir)
        if img_path is None:
            print(f"警告: 找不到 {xml_path.name} 对应的图片，已跳过")
            continue
        for name, *_ in objects:
            if name not in class_names:
                class_names.append(name)
        parsed.append((xml_path, img_path, filename, width, height, objects))

    if not parsed:
        print("错误: 没有可用的标注数据")
        sys.exit(1)

    print(f"有效标注: {len(parsed)} 个，类别: {class_names}")

    # 划分训练/验证集（用索引避免不可哈希问题）
    random.seed(42)
    indices = list(range(len(parsed)))
    random.shuffle(indices)
    val_count = max(1, int(len(parsed) * args.val_ratio))
    val_indices = set(indices[:val_count])
    train_indices = set(indices[val_count:])

    # 创建输出目录
    out = Path(args.output)
    for sub in ("images/train", "images/val", "labels/train", "labels/val"):
        (out / sub).mkdir(parents=True, exist_ok=True)

    # 转换并写入
    def write_split(idx_set, split_name):
        for i in idx_set:
            xml_path, img_path, filename, width, height, objects = parsed[i]
            stem = img_path.stem
            # 复制图片
            dst_img = out / "images" / split_name / img_path.name
            shutil.copy(img_path, dst_img)
            # 写入 YOLO txt
            lines = []
            for name, xmin, ymin, xmax, ymax in objects:
                cls_id = class_names.index(name)
                # 归一化并夹取到 [0,1]
                cx = ((xmin + xmax) / 2) / width
                cy = ((ymin + ymax) / 2) / height
                w = (xmax - xmin) / width
                h = (ymax - ymin) / height
                cx = max(0.0, min(1.0, cx))
                cy = max(0.0, min(1.0, cy))
                w = max(0.0, min(1.0, w))
                h = max(0.0, min(1.0, h))
                lines.append(f"{cls_id} {cx:.6f} {cy:.6f} {w:.6f} {h:.6f}")
            label_path = out / "labels" / split_name / f"{stem}.txt"
            label_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    write_split(train_indices, "train")
    write_split(val_indices, "val")
    print(f"训练集: {len(train_indices)} 张 | 验证集: {len(val_indices)} 张")

    # 生成 data.yaml
    names_lines = "\n".join(f"  {i}: {name}" for i, name in enumerate(class_names))
    yaml_content = f"""path: {out.name}
train: images/train
val: images/val
names:
{names_lines}
"""
    (out / "data.yaml").write_text(yaml_content, encoding="utf-8")
    print(f"转换完成！数据集在 {out}/")
    print(f"类别定义已写入 {out / 'data.yaml'}")
    print("现在可以运行: python train.py --data dataset/data.yaml")


if __name__ == "__main__":
    main()
