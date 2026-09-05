"""灵眸-yolo - 桌面视觉检测程序

功能:
    - 加载训练好的 YOLOv8 模型（自动读取 models/best.pt）
    - 拖拽/选择图片，检测目标并画框标注、分类
    - 图片滚轮缩放 + 拖拽平移查看细节
    - 支持单张检测和整个文件夹批量检测
    - 保存标注结果（可选 JPG/PNG 格式、可选保存位置）
    - 置信度阈值滑条，随时调整检测灵敏度
    - 自动保存（按置信度阈值保存检测结果）
    - 批量检测后导出 CSV 目标统计报表
    - 检测耗时显示
    - 参数自动持久化（config.json），下次启动恢复
    - 浅色/深色主题切换
"""
import csv
import json
import sys
import time
from pathlib import Path

import cv2
import requests
from PySide6.QtCore import Qt, QThread, Signal, QRect
from PySide6.QtGui import (
    QImage, QPixmap, QWheelEvent, QMouseEvent, QAction,
)
from PySide6.QtWidgets import (
    QAbstractItemView, QApplication, QComboBox, QDoubleSpinBox, QFileDialog,
    QGroupBox,
    QHBoxLayout, QLabel, QLineEdit, QListWidget, QListWidgetItem,
    QMainWindow, QMessageBox, QPlainTextEdit, QPushButton, QScrollArea,
    QSlider, QSpinBox, QSplitter, QStatusBar, QVBoxLayout, QWidget,
)

BASE_DIR = Path(__file__).resolve().parent
MODEL_DIR = BASE_DIR / "models"
DEFAULT_MODEL = BASE_DIR / "yolov8n.pt"
DEFAULT_OUTPUT = BASE_DIR / "output"
CONFIG_PATH = BASE_DIR / "config.json"
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}

# ===================== 多语言 =====================

CUR_LANG = "zh"

TEXT = {
    "zh": {
        "brand_subtitle": "视见无界 / Beyond the Visible",
        "placeholder": "将图片拖到这里，或点击「选择图片」\n支持单张图片 / 整个文件夹批量检测",
        "model_none": "模型：未加载",
        "model_name": "● 模型：{name}",
        "model_fail": "● 模型：加载失败",
        "btn_open": "📷 选择图片",
        "btn_batch": "📂 批量检测",
        "btn_model": "🧠 选择模型",
        "btn_clear": "🗑 清空",
        "btn_camera": "📷 实时监测",
        "btn_theme": "🌓 主题",
        "btn_lang": "🌐 EN / 中文",
        "btn_ai": "🤖 AI 报告总结",
        "group_ai": "AI 分析",
        "ai_btn_hint": "仅批量检测用",
        "ai_hint": "点击顶部「🤖 AI 报告总结」，基于批量检测统计生成分析报告",
        "ai_placeholder": "批量检测完成后，在此生成 AI 分析报告…",
        "ai_requesting": "正在请求 DeepSeek，请稍候…\n（仅发送检测统计文本，不上传图片）",
        "ai_warn_no_summary": "请先执行一次「批量检测」生成统计数据，再进行 AI 总结",
        "ai_warn_no_key": "尚未配置 DeepSeek API Key。\n请打开 config.json，在 \"ai\" 段填入 api_key。",
        "ai_fail": "AI 调用失败：{msg}\n\n请检查 config.json 中的 api_key / base_url，以及网络连接。",
        "status_ai_start": "AI 正在分析批量检测数据...",
        "status_ai_ok": "AI 分析完成",
        "status_ai_fail": "AI 调用失败",
        "ai_saved": "✅ AI 报告已保存：{path}",
        "group_result": "检测结果",
        "group_detect": "检测设置",
        "label_conf": "置信度阈值:",
        "group_autosave": "自动保存（图片）",
        "btn_img_autosave": "🔴 自动保存检测结果",
        "label_conf_ge": "置信度 ≥",
        "label_conf_save": "才保存",
        "group_monitor": "实时监测",
        "btn_autosave": "🔴 自动保存监测结果",
        "label_conf_short": "置信",
        "label_stable": "稳定帧",
        "label_cool": "冷却秒",
        "group_save": "保存设置",
        "label_save_path": "保存位置:",
        "btn_browse": "浏览",
        "label_format": "输出格式:",
        "btn_save": "💾 保存结果",
        "status_ready": "就绪",
        "status_no_model_file": "未找到模型 yolov8n.pt，请点击「选择模型」手动加载",
        "status_loading_model": "正在加载模型：{name} ...",
        "status_model_loaded": "模型已加载：{path}",
        "status_model_fail": "模型加载失败：{msg}",
        "dlg_model_title": "选择模型文件",
        "dlg_model_filter": "模型文件 (*.pt)",
        "status_bad_type": "不支持的文件类型",
        "dlg_image_title": "选择图片",
        "dlg_image_filter": "图片文件 (*.jpg *.jpeg *.png *.bmp *.webp)",
        "dlg_folder_title": "选择文件夹",
        "warn_no_model": "尚未加载模型，请先训练或选择模型文件",
        "status_detecting": "正在检测：{name} ...",
        "result_no_target": "未检测到目标",
        "result_item": "{i}. {name}    置信度 {conf:.2f}",
        "result_conf_lb": "置信度",
        "status_done": "检测完成：{name}，共 {n} 个目标    耗时 {ms}ms",
        "status_fail": "检测失败：{msg}",
        "status_batch_run": "批量检测中...",
        "status_batch_progress": "批量检测：{cur}/{total}  {name}    (耗时 {ms}ms)",
        "status_batch_done": "批量检测完成，保存 {n} 张到 {dir}，总耗时 {sec}s，报表：{report}",
        "dlg_batch_title": "批量检测完成",
        "dlg_batch_msg": "共保存 {n} 张标注图到：\n{dir}\n\n目标统计报表已导出到：\n{report}\n\n总耗时：{sec} 秒\n（报表为 CSV 格式，双击可用 Excel 打开）",
        "status_batch_fail": "批量检测失败：{msg}",
        "warn_no_model_cam": "尚未加载模型，请先加载后再启动实时监测",
        "status_cam_start": "实时监测已启动",
        "status_cam_stop": "实时监测已停止",
        "status_cam_saved": "已自动保存监测画面：{path}（{n} 个目标）",
        "status_cam_error": "摄像头错误：{msg}",
        "status_autosave_on": "自动保存已开启",
        "status_autosave_off": "自动保存已关闭",
        "dlg_note_title": "提示",
        "dlg_no_result": "当前没有可保存的检测结果",
        "status_saved": "已保存：{path}",
        "status_autosaved": "已自动保存：{path}",
        "dlg_savepos_title": "选择保存位置",
        "status_cleared": "已清空",
        "err_no_result": "未返回检测结果",
        "err_cam_open": "无法打开摄像头",
        "csv_title": "【批量检测统计报表】",
        "csv_summary": "图片总数: {total}    目标总数: {objs}",
        "csv_summary_zero": "图片总数: 0",
        "csv_class_total": "各类目标累计: {sum}",
        "csv_col_image": "图片",
        "csv_col_targets": "目标总数",
    },
    "en": {
        "brand_subtitle": "视见无界 / Beyond the Visible",
        "placeholder": "Drag an image here, or click \"Select Image\"\nSingle image / batch folder detection",
        "model_none": "Model: not loaded",
        "model_name": "● Model: {name}",
        "model_fail": "● Model: load failed",
        "btn_open": "📷 Select Image",
        "btn_batch": "📂 Batch Detect",
        "btn_model": "🧠 Select Model",
        "btn_clear": "🗑 Clear",
        "btn_camera": "📷 Live Monitor",
        "btn_theme": "🌓 Theme",
        "btn_lang": "🌐 中文 / EN",
        "btn_ai": "🤖 AI Report",
        "group_ai": "AI Analysis",
        "ai_btn_hint": "batch only",
        "ai_hint": "Click \"🤖 AI Report\" to generate an analysis report from batch stats",
        "ai_placeholder": "Click after batch detection to generate the AI report…",
        "ai_requesting": "Requesting DeepSeek, please wait…\n(only sends detection stats text, no images)",
        "ai_warn_no_summary": "Please run a batch detection first to generate stats before the AI summary",
        "ai_warn_no_key": "DeepSeek API key not set.\nOpen config.json and fill in the \"ai\".api_key field.",
        "ai_fail": "AI call failed: {msg}\n\nCheck api_key / base_url in config.json and network connection.",
        "status_ai_start": "AI is analyzing batch detection data...",
        "status_ai_ok": "AI analysis done",
        "status_ai_fail": "AI call failed",
        "ai_saved": "✅ AI report saved: {path}",
        "group_result": "Detection Results",
        "group_detect": "Detection Settings",
        "label_conf": "Confidence:",
        "group_autosave": "Auto-save (Images)",
        "btn_img_autosave": "🔴 Auto-save results",
        "label_conf_ge": "Conf ≥",
        "label_conf_save": "to save",
        "group_monitor": "Live Monitor",
        "btn_autosave": "🔴 Auto-save monitor",
        "label_conf_short": "Conf",
        "label_stable": "Frames",
        "label_cool": "Cooldown",
        "group_save": "Save Settings",
        "label_save_path": "Save to:",
        "btn_browse": "Browse",
        "label_format": "Format:",
        "btn_save": "💾 Save Result",
        "status_ready": "Ready",
        "status_no_model_file": "Model yolov8n.pt not found. Click \"Select Model\" to load manually",
        "status_loading_model": "Loading model: {name} ...",
        "status_model_loaded": "Model loaded: {path}",
        "status_model_fail": "Model load failed: {msg}",
        "dlg_model_title": "Select model file",
        "dlg_model_filter": "Model files (*.pt)",
        "status_bad_type": "Unsupported file type",
        "dlg_image_title": "Select image",
        "dlg_image_filter": "Image files (*.jpg *.jpeg *.png *.bmp *.webp)",
        "dlg_folder_title": "Select folder",
        "warn_no_model": "No model loaded. Please train or select a model file first",
        "status_detecting": "Detecting: {name} ...",
        "result_no_target": "No targets detected",
        "result_item": "{i}. {name}    conf {conf:.2f}",
        "result_conf_lb": "Conf",
        "status_done": "Done: {name}, {n} targets    {ms}ms",
        "status_fail": "Detect failed: {msg}",
        "status_batch_run": "Batch detecting...",
        "status_batch_progress": "Batch: {cur}/{total}  {name}    ({ms}ms)",
        "status_batch_done": "Batch done, saved {n} images to {dir}, total {sec}s, report: {report}",
        "dlg_batch_title": "Batch Detection Done",
        "dlg_batch_msg": "Saved {n} annotated images to:\n{dir}\n\nReport exported to:\n{report}\n\nTotal time: {sec} s\n(CSV report, open with Excel)",
        "status_batch_fail": "Batch detect failed: {msg}",
        "warn_no_model_cam": "No model loaded. Please load a model before starting live monitor",
        "status_cam_start": "Live monitor started",
        "status_cam_stop": "Live monitor stopped",
        "status_cam_saved": "Auto-saved: {path} ({n} targets)",
        "status_cam_error": "Camera error: {msg}",
        "status_autosave_on": "Auto-save enabled",
        "status_autosave_off": "Auto-save disabled",
        "dlg_note_title": "Notice",
        "dlg_no_result": "No result to save",
        "status_saved": "Saved: {path}",
        "status_autosaved": "Auto-saved: {path}",
        "dlg_savepos_title": "Select save location",
        "status_cleared": "Cleared",
        "err_no_result": "No detection results returned",
        "err_cam_open": "Cannot open camera",
        "csv_title": "[Batch Detection Report]",
        "csv_summary": "Total images: {total}    Total targets: {objs}",
        "csv_summary_zero": "Total images: 0",
        "csv_class_total": "Class totals: {sum}",
        "csv_col_image": "Image",
        "csv_col_targets": "Targets",
    },
}


def tr(key):
    d = TEXT[CUR_LANG]
    return d.get(key, TEXT["zh"].get(key, key))


# ===================== 主题样式 =====================

LIGHT_QSS = """
QMainWindow, QWidget {
    background: #f5f5f7;
    color: #1f1f23;
    font-family: "Microsoft YaHei", "Segoe UI", sans-serif;
    font-size: 13px;
}
QLabel#brand_title {
    font-size: 23px;
    font-weight: 800;
    color: #111111;
    letter-spacing: 2px;
}
QLabel#brand_subtitle {
    font-size: 11px;
    color: #9a9aa0;
    letter-spacing: 1px;
}
QLabel#model_label {
    background: #ffffff;
    border: 1px solid #e2e2e6;
    border-radius: 14px;
    padding: 5px 14px;
    color: #111111;
}
QGroupBox {
    border: 1px solid #e6e6ea;
    border-radius: 10px;
    margin-top: 10px;
    padding-top: 8px;
    background: #ffffff;
    font-weight: bold;
    color: #3a3a40;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 6px;
    color: #2A5DB0;
}
QPushButton {
    background: #ffffff;
    border: 1px solid #ddddE2;
    border-radius: 8px;
    padding: 6px 16px;
    min-height: 24px;
    color: #33333a;
    font-weight: 500;
}
QPushButton:hover {
    background: #f2f2f4;
    border-color: #c9c9cf;
}
QPushButton:pressed {
    background: #e8e8ec;
}
QPushButton:disabled {
    background: #f1f1f3;
    color: #c6c6cb;
    border-color: #e8e8eb;
}
QPushButton[class="primary"] {
    background: #2A5DB0;
    border: 1px solid #2A5DB0;
    color: #ffffff;
}
QPushButton[class="primary"]:hover {
    background: #24509c;
    border-color: #24509c;
}
QPushButton[class="primary"]:pressed {
    background: #1f4586;
}
QPushButton[class="danger"] {
    background: #ffffff;
    border: 1px solid #f2d8d0;
    color: #d0402a;
}
QPushButton[class="danger"]:hover {
    background: #fdf4f1;
    border-color: #e9b8ab;
}
QPushButton[class="toggle"]:checked {
    background: #2A5DB0;
    border: 1px solid #2A5DB0;
    color: #ffffff;
}
QPushButton[class="camera"]:checked {
    background: #e53935;
    border: 1px solid #e53935;
    color: #ffffff;
}
QLineEdit {
    border: 1px solid #e0e0e4;
    border-radius: 8px;
    padding: 5px 10px;
    background: #ffffff;
    color: #1f1f23;
}
QLineEdit:focus {
    border-color: #2A5DB0;
}
QSpinBox {
    border: 1px solid #e0e0e4;
    border-radius: 8px;
    padding: 3px 8px;
    background: #ffffff;
    color: #1f1f23;
}
QDoubleSpinBox {
    border: 1px solid #e0e0e4;
    border-radius: 8px;
    padding: 3px 8px;
    background: #ffffff;
    color: #1f1f23;
}
QComboBox {
    border: 1px solid #e0e0e4;
    border-radius: 8px;
    padding: 4px 10px;
    background: #ffffff;
    color: #1f1f23;
}
QComboBox::drop-down {
    border: none;
    width: 22px;
}
QComboBox QAbstractItemView {
    background: #ffffff;
    border: 1px solid #e0e0e4;
    selection-background-color: #2A5DB0;
    selection-color: #ffffff;
}
QListWidget {
    border: 1px solid #ececef;
    border-radius: 10px;
    background: #fafafb;
    padding: 3px;
}
QListWidget::item {
    padding: 7px 8px;
    border-radius: 6px;
    margin: 1px 2px;
}
QListWidget::item:hover {
    background: #f2f2f4;
}
QListWidget::item:selected {
    background: #2A5DB0;
    color: #ffffff;
}
QSlider::groove:horizontal {
    height: 6px;
    background: #e6e6ea;
    border-radius: 3px;
}
QSlider::sub-page:horizontal {
    background: #2A5DB0;
    border-radius: 3px;
}
QSlider::handle:horizontal {
    width: 18px;
    height: 18px;
    margin: -6px 0;
    background: #ffffff;
    border: 3px solid #2A5DB0;
    border-radius: 9px;
}
QScrollArea {
    border: 1px solid #e8e8ec;
    border-radius: 14px;
    background: #ececee;
}
QStatusBar {
    background: #ffffff;
    border-top: 1px solid #ececef;
    color: #8c8c92;
}
QRadioButton {
    color: #3a3a40;
    spacing: 6px;
}
QRadioButton::indicator {
    width: 16px;
    height: 16px;
    border-radius: 8px;
    border: 2px solid #d0d0d4;
    background: #ffffff;
}
QRadioButton::indicator:checked {
    background: #2A5DB0;
    border: 2px solid #2A5DB0;
}
"""

DARK_QSS = """
QMainWindow, QWidget {
    background: #17171a;
    color: #e3e3e8;
    font-family: "Microsoft YaHei", "Segoe UI", sans-serif;
    font-size: 13px;
}
QLabel#brand_title {
    font-size: 23px;
    font-weight: 800;
    color: #f2f2f5;
    letter-spacing: 2px;
}
QLabel#brand_subtitle {
    font-size: 11px;
    color: #7c7c85;
    letter-spacing: 1px;
}
QLabel#model_label {
    background: #222226;
    border: 1px solid #3a3a41;
    border-radius: 14px;
    padding: 5px 14px;
    color: #e8e8ec;
}
QGroupBox {
    border: 1px solid #2c2c33;
    border-radius: 10px;
    margin-top: 10px;
    padding-top: 8px;
    background: #1f1f24;
    font-weight: bold;
    color: #d5d5db;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 6px;
    color: #7FA6E0;
}
QPushButton {
    background: #2a2a30;
    border: 1px solid #3a3a42;
    border-radius: 8px;
    padding: 6px 16px;
    min-height: 24px;
    color: #e3e3e8;
    font-weight: 500;
}
QPushButton:hover {
    background: #34343c;
    border-color: #4a4a53;
}
QPushButton:pressed {
    background: #1f1f24;
}
QPushButton:disabled {
    background: #202025;
    color: #6f6f78;
    border-color: #2c2c33;
}
QPushButton[class="primary"] {
    background: #7FA6E0;
    border: 1px solid #7FA6E0;
    color: #111114;
}
QPushButton[class="primary"]:hover {
    background: #95b6e6;
    border-color: #95b6e6;
}
QPushButton[class="primary"]:pressed {
    background: #6a8fd0;
}
QPushButton[class="danger"] {
    background: #2a2a30;
    color: #ff8f80;
    border: 1px solid #ff8f80;
}
QPushButton[class="danger"]:hover {
    background: #382124;
    border-color: #ff8f80;
}
QPushButton[class="toggle"]:checked {
    background: #7FA6E0;
    border: 1px solid #7FA6E0;
    color: #111114;
}
QPushButton[class="camera"]:checked {
    background: #e53935;
    border: 1px solid #e53935;
    color: #ffffff;
}
QLineEdit {
    border: 1px solid #3a3a42;
    border-radius: 8px;
    padding: 5px 10px;
    background: #1f1f24;
    color: #e3e3e8;
}
QLineEdit:focus {
    border-color: #7FA6E0;
}
QSpinBox {
    border: 1px solid #3a3a42;
    border-radius: 8px;
    padding: 3px 8px;
    background: #1f1f24;
    color: #e3e3e8;
}
QDoubleSpinBox {
    border: 1px solid #3a3a42;
    border-radius: 8px;
    padding: 3px 8px;
    background: #1f1f24;
    color: #e3e3e8;
}
QComboBox {
    border: 1px solid #3a3a42;
    border-radius: 8px;
    padding: 4px 10px;
    background: #1f1f24;
    color: #e3e3e8;
}
QComboBox::drop-down {
    border: none;
    width: 22px;
}
QComboBox QAbstractItemView {
    background: #1f1f24;
    border: 1px solid #3a3a42;
    color: #e3e3e8;
    selection-background-color: #7FA6E0;
    selection-color: #111114;
}
QListWidget {
    border: 1px solid #2c2c33;
    border-radius: 10px;
    background: #141418;
    padding: 3px;
}
QListWidget::item {
    padding: 7px 8px;
    border-radius: 6px;
    margin: 1px 2px;
}
QListWidget::item:hover {
    background: #24242a;
}
QListWidget::item:selected {
    background: #7FA6E0;
    color: #111114;
}
QSlider::groove:horizontal {
    height: 6px;
    background: #33333b;
    border-radius: 3px;
}
QSlider::sub-page:horizontal {
    background: #7FA6E0;
    border-radius: 3px;
}
QSlider::handle:horizontal {
    width: 18px;
    height: 18px;
    margin: -6px 0;
    background: #e3e3e8;
    border: 3px solid #7FA6E0;
    border-radius: 9px;
}
QScrollArea {
    border: 1px solid #2c2c33;
    border-radius: 14px;
    background: #101014;
}
QStatusBar {
    background: #141418;
    border-top: 1px solid #2c2c33;
    color: #8f8f99;
}
QRadioButton {
    color: #d5d5db;
    spacing: 6px;
}
QRadioButton::indicator {
    width: 16px;
    height: 16px;
    border-radius: 8px;
    border: 2px solid #4a4a53;
    background: #1f1f24;
}
QRadioButton::indicator:checked {
    background: #7FA6E0;
    border: 2px solid #7FA6E0;
}
"""

PLACEHOLDER_STYLE_LIGHT = (
    "border: 2px dashed #c6c6cc; border-radius: 14px; "
    "background: #fafafb; color: #9a9aa0; font-size: 15px;"
)
PLACEHOLDER_STYLE_DARK = (
    "border: 2px dashed #4a4a53; border-radius: 14px; "
    "background: #101014; color: #6f6f78; font-size: 15px;"
)


# ===================== 工作线程 =====================

class ModelLoadWorker(QThread):
    loaded = Signal(object, str)
    failed = Signal(str)

    def __init__(self, path):
        super().__init__()
        self.path = str(path)

    def run(self):
        try:
            from ultralytics import YOLO
            model = YOLO(self.path)
            self.loaded.emit(model, self.path)
        except Exception as e:
            self.failed.emit(str(e))


class DetectWorker(QThread):
    done = Signal(object, object, str, float)   # (annotated, detections, path, elapsed_ms)
    failed = Signal(str)

    def __init__(self, model, image_path, conf):
        super().__init__()
        self.model = model
        self.image_path = str(image_path)
        self.conf = conf

    def run(self):
        t0 = time.perf_counter()
        try:
            results = self.model.predict(self.image_path, conf=self.conf, verbose=False)
            elapsed = (time.perf_counter() - t0) * 1000
            if not results:
                self.failed.emit(tr("err_no_result"))
                return
            r = results[0]
            annotated = r.plot()
            detections = []
            names = r.names
            if r.boxes is not None:
                for box in r.boxes:
                    cls_id = int(box.cls[0])
                    conf = float(box.conf[0])
                    detections.append((names[cls_id], conf))
            self.done.emit(annotated, detections, self.image_path, elapsed)
        except Exception as e:
            self.failed.emit(str(e))


class BatchWorker(QThread):
    progress = Signal(int, int, str, float)   # (cur, total, name, elapsed_ms)
    done = Signal(int, str, str, float)        # 加 total_elapsed
    report_ready = Signal(dict)                # 批量统计结果，供 AI 报告使用
    failed = Signal(str)

    def __init__(self, model, folder, output_dir, ext, conf,
                 auto_enabled=False, auto_conf=0.5):
        super().__init__()
        self.model = model
        self.folder = folder
        self.output_dir = output_dir
        self.ext = ext
        self.conf = conf
        self.auto_enabled = auto_enabled
        self.auto_conf = auto_conf

    def run(self):
        t0 = time.perf_counter()
        try:
            images = [p for p in Path(self.folder).iterdir()
                      if p.is_file() and p.suffix.lower() in IMAGE_EXTS]
            total = len(images)
            count = 0
            rows = []
            class_total = {}

            for i, img in enumerate(images):
                name = img.name
                img_t0 = time.perf_counter()
                result = self.model.predict(str(img), conf=self.conf, verbose=False)
                img_elapsed = (time.perf_counter() - img_t0) * 1000
                per_class = {}
                target_num = 0
                if result and result[0].boxes is not None:
                    r = result[0]
                    names = r.names
                    max_conf = 0.0
                    for box in r.boxes:
                        cls_name = names[int(box.cls[0])]
                        per_class[cls_name] = per_class.get(cls_name, 0) + 1
                        target_num += 1
                        max_conf = max(max_conf, float(box.conf[0]))
                    annotated = r.plot()
                    do_save = True
                    if self.auto_enabled:
                        do_save = max_conf >= self.auto_conf
                    if do_save:
                        out = Path(self.output_dir) / f"{img.stem}_detected.{self.ext}"
                        cv2.imwrite(str(out), annotated)
                        count += 1

                for cls_name, n in per_class.items():
                    class_total[cls_name] = class_total.get(cls_name, 0) + n

                row = {
                    tr("csv_col_image"): name,
                    tr("csv_col_targets"): target_num,
                    "_dir": self.output_dir,
                }
                row.update(per_class)
                rows.append(row)

                self.progress.emit(i + 1, total, name, img_elapsed)

            report_path = self._write_report(rows, class_total)
            total_elapsed = (time.perf_counter() - t0) * 1000
            self.report_ready.emit({
                "rows": rows, "class_total": class_total, "total": total,
                "col_image": tr("csv_col_image"),
                "col_targets": tr("csv_col_targets"),
                "folder_name": Path(self.folder).name,
                "out_dir": str(self.output_dir),
            })
            self.done.emit(count, str(self.output_dir), str(report_path), total_elapsed)
        except Exception as e:
            self.failed.emit(str(e))

    @staticmethod
    def _write_report(rows, class_total):
        total = len(rows)
        fixed = [tr("csv_col_image"), tr("csv_col_targets")]
        hidden = "_dir"
        dynamic = []
        for row in rows:
            for k in row:
                if k not in fixed and k != hidden and k not in dynamic:
                    dynamic.append(k)
        headers = fixed + sorted(dynamic)

        if not rows:
            raise RuntimeError(tr("err_no_result"))
        report = Path(rows[0]["_dir"]) / "目标统计报表.csv"

        with report.open("w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow([tr("csv_title")])
            if total:
                objs = sum(r.get(tr("csv_col_targets"), 0) for r in rows)
                writer.writerow([tr("csv_summary").format(total=total, objs=objs)])
            else:
                writer.writerow([tr("csv_summary_zero")])
            if class_total:
                summary = "     ".join(f"{k}: {v}" for k, v in
                                       sorted(class_total.items(), key=lambda x: -x[1]))
                writer.writerow([tr("csv_class_total").format(sum=summary)])
            writer.writerow([])
            writer.writerow(headers)
            for row in rows:
                writer.writerow([row.get(h, 0) if h != tr("csv_col_image") else row.get(h, "")
                                 for h in headers])
        return report


class AISummaryWorker(QThread):
    """后台线程：调用 DeepSeek API 生成批量检测报告总结（只传文本，不传图片）。"""
    done = Signal(str)
    failed = Signal(str)

    def __init__(self, api_key, base_url, model, summary_text):
        super().__init__()
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        self.summary_text = summary_text

    def run(self):
        try:
            result = self._call()
        except Exception as e:
            self.failed.emit(str(e))
            return
        self.done.emit(result)

    def _call(self):
        # 本模块按 OpenAI 兼容的 Chat Completions 协议调用，默认指向 DeepSeek。
        # 其它厂商只要提供 OpenAI 兼容接口，改 config.json 中 "ai".base_url / api_key / model 即可接入，无需改代码。
        url = (self.base_url or "").strip()
        if not url or "chat/completions" not in url:
            url = "https://api.deepseek.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        system = (
            "你是一名数据处理助手。用户会提供一批图片的目标检测统计结果（图片数量、目标总数、"
            "各类目标数量等）。请你输出一份简洁、客观的统计总结：描述各类目标的分布与数量构成，"
            "可提出通用性观察；不得做任何“合格/不合格”之类的质量判定。"
            "要求：严格基于提供的数据，不得编造任何数字或结论；用中文、分小点输出。"
        )
        payload = {
            "model": self.model or "deepseek-v4-flash",
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": self.summary_text},
            ],
            "temperature": 0.3,
            "stream": False,
        }
        resp = requests.post(url, headers=headers, json=payload, timeout=90)
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]


class CameraWorker(QThread):
    frame_ready = Signal(object)    # annotated BGR image
    saved = Signal(str, int)        # (saved_path, target_count)
    failed = Signal(str)

    def __init__(self, model, camera_index=0, conf=0.5):
        super().__init__()
        self.model = model
        self.index = camera_index
        self.conf = conf
        self.autosave = False
        self.stable_frames_need = 6
        self.cool_seconds = 3
        self.save_dir = ""
        self.save_ext = "jpg"
        self._running = True
        self._stable = 0
        self._last_save = 0.0

    def set_params(self, conf=None, autosave=None, stable_frames=None,
                   cool_seconds=None, save_dir=None, save_ext=None):
        if conf is not None:
            self.conf = conf
        if autosave is not None:
            self.autosave = autosave
            self._stable = 0
            self._last_save = 0.0
        if stable_frames is not None:
            self.stable_frames_need = stable_frames
        if cool_seconds is not None:
            self.cool_seconds = cool_seconds
        if save_dir is not None:
            self.save_dir = save_dir
        if save_ext is not None:
            self.save_ext = save_ext

    def stop(self):
        self._running = False

    def run(self):
        cap = cv2.VideoCapture(self.index)
        if not cap.isOpened():
            self.failed.emit(tr("err_cam_open"))
            return
        while self._running:
            ok, frame = cap.read()
            if not ok:
                continue
            h, w = frame.shape[:2]
            if w > 640:
                scale = 640 / w
                frame = cv2.resize(frame, (640, int(h * scale)))
            try:
                results = self.model.track(
                    frame, conf=self.conf, persist=True, verbose=False)
            except Exception:
                results = self.model.predict(frame, conf=self.conf, verbose=False)
            if not results:
                continue
            r = results[0]
            annotated = r.plot()
            max_conf = 0.0
            count = 0
            if r.boxes is not None and len(r.boxes):
                count = len(r.boxes)
                max_conf = float(r.boxes.conf.max())

            if self.autosave:
                if max_conf >= self.conf:
                    self._stable += 1
                else:
                    self._stable = 0
                now = time.time()
                if (self._stable >= self.stable_frames_need
                        and now - self._last_save >= self.cool_seconds
                        and self.save_dir):
                    ts = time.strftime("%Y%m%d_%H%M%S")
                    out = Path(self.save_dir) / f"monitor_{ts}.{self.save_ext}"
                    cv2.imwrite(str(out), annotated)
                    self._last_save = now
                    self._stable = 0
                    self.saved.emit(str(out), count)

            self.frame_ready.emit(annotated)
        cap.release()


# ===================== 可缩放图片预览 =====================

class ZoomableImage(QLabel):
    """支持滚轮缩放 + 拖拽平移的图片标签"""
    clicked = Signal()
    file_dropped = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setAlignment(Qt.AlignCenter)
        self.setMinimumSize(480, 360)
        self._original_pixmap = None
        self._scale = 1.0
        self._pan_start = None
        self._is_placeholder = True

    def set_placeholder(self, text):
        self._is_placeholder = True
        self._original_pixmap = None
        self._scale = 1.0
        self.setText(text)

    def set_pixmap(self, pixmap):
        self._is_placeholder = False
        self._original_pixmap = pixmap
        self._scale = 1.0
        self._apply_scale()

    def _apply_scale(self):
        if self._original_pixmap is None:
            return
        if self._scale == 1.0:
            self.setPixmap(self._original_pixmap)
            return
        w = int(self._original_pixmap.width() * self._scale)
        h = int(self._original_pixmap.height() * self._scale)
        if w < 10 or h < 10:
            return
        self.setPixmap(self._original_pixmap.scaled(
            w, h, Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def wheelEvent(self, event: QWheelEvent):
        if self._original_pixmap is None:
            return
        delta = event.angleDelta().y()
        factor = 1.15 if delta > 0 else 1 / 1.15
        new_scale = self._scale * factor
        if 0.05 <= new_scale <= 8.0:
            self._scale = new_scale
            self._apply_scale()
        event.accept()

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton and self._original_pixmap is not None:
            self._pan_start = event.position().toPoint()
            self.setCursor(Qt.ClosedHandCursor)
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        if self._pan_start is not None and self.parent() is not None:
            delta = self._pan_start - event.position().toPoint()
            self._pan_start = event.position().toPoint()
            sb_h = self.parent().horizontalScrollBar()
            sb_v = self.parent().verticalScrollBar()
            if sb_h:
                sb_h.setValue(sb_h.value() + delta.x())
            if sb_v:
                sb_v.setValue(sb_v.value() + delta.y())
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self._pan_start = None
            self.setCursor(Qt.ArrowCursor)
            if self._original_pixmap is None:
                self.clicked.emit()
        event.accept()

    def mouseDoubleClickEvent(self, event):
        if self._original_pixmap is not None:
            self._scale = 1.0
            self._apply_scale()
        event.accept()

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        if urls:
            self.file_dropped.emit(urls[0].toLocalFile())


# ===================== 主窗口 =====================

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("灵眸-yolo")
        self.resize(1280, 780)

        self.model = None
        self.model_path = None
        self.current_path = None
        self.current_annotated = None
        self._last_detections = None
        self.conf_threshold = 0.25
        self.dark_mode = False
        self.lang = "zh"
        self._i18n_widgets = []
        self.model_worker = None
        self.detect_worker = None
        self.batch_worker = None
        self._model_failed = False
        self.camera_worker = None
        self.camera_on = False
        self.auto_conf = 0.5
        self.auto_stable = 6
        self.auto_cool = 3
        self.auto_img_enabled = False
        self.auto_img_conf = 0.5

        self.ai_enabled = False
        self.ai_api_key = ""
        self.ai_base_url = "https://api.deepseek.com/v1/chat/completions"
        self.ai_model = "deepseek-v4-flash"
        self.last_batch_summary = None
        self.ai_worker = None

        self._load_config()
        global CUR_LANG
        CUR_LANG = self.lang
        self._init_ui()
        self._apply_theme()
        self._load_default_model()

    # ========== 多语言 ==========

    def _tr(self, key):
        return tr(key)

    def _register(self, widget, key):
        self._i18n_widgets.append((widget, key))

    def _apply_language(self):
        for widget, key in self._i18n_widgets:
            try:
                if isinstance(widget, QGroupBox):
                    widget.setTitle(tr(key))
                else:
                    widget.setText(tr(key))
            except Exception:
                pass
        self.brand_subtitle.setText(tr("brand_subtitle"))
        if self.model is not None:
            self.model_label.setText(tr("model_name").format(name=self.model_path.name))
        elif self._model_failed:
            self.model_label.setText(tr("model_fail"))
        else:
            self.model_label.setText(tr("model_none"))
        if self.preview_image._is_placeholder:
            self.preview_image.setText(tr("placeholder"))
        if self._last_detections is not None:
            self.result_list.clear()
            if self._last_detections:
                for i, (name, conf) in enumerate(self._last_detections, 1):
                    self.result_list.addItem(
                        QListWidgetItem(tr("result_item").format(i=i, name=name, conf=conf)))
            else:
                self.result_list.addItem(tr("result_no_target"))
        self.status.showMessage(tr("status_ready"))

    def _toggle_lang(self):
        self.lang = "en" if self.lang == "zh" else "zh"
        global CUR_LANG
        CUR_LANG = self.lang
        self._apply_language()
        self._save_config()

    # ========== 配置持久化 ==========

    def _load_config(self):
        try:
            if CONFIG_PATH.exists():
                cfg = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
                self.conf_threshold = float(cfg.get("conf_threshold", 0.25))
                self._saved_output = cfg.get("save_path", str(DEFAULT_OUTPUT))
                self._saved_fmt = cfg.get("save_format", "jpg")
                self.dark_mode = bool(cfg.get("dark_mode", False))
                self.auto_conf = float(cfg.get("auto_conf", 0.5))
                self.auto_stable = int(cfg.get("auto_stable", 6))
                self.auto_cool = int(cfg.get("auto_cool", 3))
                self.auto_img_enabled = bool(cfg.get("auto_img_enabled", False))
                self.auto_img_conf = float(cfg.get("auto_img_conf", 0.5))
                self.lang = cfg.get("lang", "zh")
                if self.lang not in ("zh", "en"):
                    self.lang = "zh"
                ai = cfg.get("ai", {}) or {}
                self.ai_enabled = bool(ai.get("enabled", False))
                self.ai_api_key = ai.get("api_key", "").strip()
                self.ai_base_url = ai.get("base_url",
                                         "https://api.deepseek.com/v1/chat/completions").strip()
                self.ai_model = ai.get("model", "deepseek-v4-flash").strip()
            else:
                self._saved_output = str(DEFAULT_OUTPUT)
                self._saved_fmt = "jpg"
        except Exception:
            self._saved_output = str(DEFAULT_OUTPUT)
            self._saved_fmt = "jpg"

    def _save_config(self):
        cfg = {
            "conf_threshold": self.conf_threshold,
            "save_path": self.save_path_edit.text().strip(),
            "save_format": self.fmt_combo.currentData(),
            "dark_mode": self.dark_mode,
            "auto_conf": self.auto_conf,
            "auto_stable": self.auto_stable,
            "auto_cool": self.auto_cool,
            "auto_img_enabled": self.auto_img_enabled,
            "auto_img_conf": self.auto_img_conf,
            "lang": self.lang,
            "ai": {
                "enabled": self.ai_enabled,
                "api_key": self.ai_api_key,
                "base_url": self.ai_base_url,
                "model": self.ai_model,
            },
        }
        try:
            CONFIG_PATH.write_text(json.dumps(cfg, ensure_ascii=False, indent=2),
                                   encoding="utf-8")
        except Exception:
            pass

    # ========== 主题 ==========
    def _apply_theme(self):
        if self.dark_mode:
            self.setStyleSheet(DARK_QSS)
        else:
            self.setStyleSheet(LIGHT_QSS)
        self._update_placeholder_style()
        self._refresh_model_badge()

    def _apply_model_badge(self, color):
        if self.dark_mode:
            bg, bd = "#222226", "#3a3a41"
        else:
            bg, bd = "#ffffff", "#e2e2e6"
        self.model_label.setStyleSheet(
            f"color:{color}; background:{bg}; border:1px solid {bd};"
            f"border-radius:14px; padding:5px 14px; font-weight:500;")

    def _refresh_model_badge(self):
        if self._model_failed:
            color = "#dc2626" if not self.dark_mode else "#f38ba8"
        elif self.model is not None:
            color = "#111111" if not self.dark_mode else "#f2f2f5"
        else:
            color = "#94a3b8" if not self.dark_mode else "#a6adc8"
        self._apply_model_badge(color)

    def _update_placeholder_style(self):
        if self._is_placeholder():
            self.preview_image.setStyleSheet(
                PLACEHOLDER_STYLE_DARK if self.dark_mode else PLACEHOLDER_STYLE_LIGHT)

    def _is_placeholder(self):
        return self.preview_image._is_placeholder

    def _toggle_theme(self):
        self.dark_mode = not self.dark_mode
        self._apply_theme()
        self._save_config()

    # ========== UI 搭建 ==========

    def _init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(10)

        # 顶部品牌栏
        header = QHBoxLayout()
        header.setSpacing(10)
        brand_box = QVBoxLayout()
        brand_box.setSpacing(2)
        self.brand_title = QLabel("灵眸-yolo")
        self.brand_title.setObjectName("brand_title")
        self.brand_subtitle = QLabel(tr("brand_subtitle"))
        self.brand_subtitle.setObjectName("brand_subtitle")
        brand_box.addWidget(self.brand_title)
        brand_box.addWidget(self.brand_subtitle)
        header.addLayout(brand_box)
        header.addStretch()
        self.model_label = QLabel(tr("model_none"))
        self.model_label.setObjectName("model_label")
        header.addWidget(self.model_label)
        root.addLayout(header)

        # 顶部工具条
        top = QHBoxLayout()
        top.setSpacing(8)
        self.btn_open = QPushButton(tr("btn_open"))
        self.btn_batch = QPushButton(tr("btn_batch"))
        self.btn_ai = QPushButton(tr("btn_ai"))
        self.btn_model = QPushButton(tr("btn_model"))
        self.btn_clear = QPushButton(tr("btn_clear"))
        self.btn_camera = QPushButton(tr("btn_camera"))
        self.btn_theme = QPushButton(tr("btn_theme"))
        self.btn_lang = QPushButton(tr("btn_lang"))
        self.btn_open.setProperty("class", "primary")
        self.btn_clear.setProperty("class", "danger")
        self.btn_camera.setProperty("class", "camera")
        self.btn_camera.setCheckable(True)
        self.btn_ai.setEnabled(False)
        self._register(self.btn_open, "btn_open")
        self._register(self.btn_batch, "btn_batch")
        self._register(self.btn_ai, "btn_ai")
        self._register(self.btn_model, "btn_model")
        self._register(self.btn_clear, "btn_clear")
        self._register(self.btn_camera, "btn_camera")
        self._register(self.btn_theme, "btn_theme")
        self._register(self.btn_lang, "btn_lang")
        for b in (self.btn_open, self.btn_batch,
                  self.btn_model,
                  self.btn_clear, self.btn_camera, self.btn_theme, self.btn_lang):
            top.addWidget(b)
        # AI 按钮单独加容器，下方显示小字提示
        ai_box = QVBoxLayout()
        ai_box.setContentsMargins(0, 0, 0, 0)
        ai_box.setSpacing(0)
        ai_box.addWidget(self.btn_ai)
        self.ai_btn_hint_lbl = QLabel(tr("ai_btn_hint"))
        self.ai_btn_hint_lbl.setAlignment(Qt.AlignCenter)
        self.ai_btn_hint_lbl.setStyleSheet("color: #888; font-size: 11px;")
        ai_box.addWidget(self.ai_btn_hint_lbl)
        ai_wrap = QWidget()
        ai_wrap.setLayout(ai_box)
        top.addWidget(ai_wrap)
        top.addStretch()
        root.addLayout(top)
        # 注册小字提示，使其随中英文切换而更新
        self._register(self.ai_btn_hint_lbl, "ai_btn_hint")

        # 主区域
        splitter = QSplitter(Qt.Horizontal)

        # 左侧：可缩放预览
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(False)
        self.scroll_area.setAlignment(Qt.AlignCenter)
        self.preview_image = ZoomableImage()
        self.preview_image.setText(tr("placeholder"))
        self.preview_image.setWordWrap(True)
        self.preview_image.file_dropped.connect(self._on_file_dropped)
        self.preview_image.clicked.connect(self._open_image_dialog)
        self.scroll_area.setWidget(self.preview_image)
        splitter.addWidget(self.scroll_area)

        # 右侧面板
        right = QWidget()
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(8)

        result_group = QGroupBox(tr("group_result"))
        result_layout = QVBoxLayout(result_group)
        self.result_list = QListWidget()
        self.result_list.setMinimumWidth(280)
        self.result_list.setMinimumHeight(140)
        self.result_list.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        result_layout.addWidget(self.result_list)
        right_layout.addWidget(result_group)

        # 检测设置
        detect_group = QGroupBox(tr("group_detect"))
        detect_layout = QVBoxLayout(detect_group)
        conf_row = QHBoxLayout()
        self.conf_lbl = QLabel(tr("label_conf"))
        conf_row.addWidget(self.conf_lbl)
        self.conf_label = QLabel(f"{self.conf_threshold:.2f}")
        self.conf_label.setMinimumWidth(40)
        conf_row.addWidget(self.conf_label)
        conf_row.addStretch()
        detect_layout.addLayout(conf_row)
        self.conf_slider = QSlider(Qt.Horizontal)
        self.conf_slider.setRange(5, 95)
        self.conf_slider.setValue(int(self.conf_threshold * 100))
        detect_layout.addWidget(self.conf_slider)
        right_layout.addWidget(detect_group)

        # 自动保存（图片检测）
        autosave_group = QGroupBox(tr("group_autosave"))
        autosave_group.setCheckable(True)
        autosave_layout = QVBoxLayout(autosave_group)
        autosave_content = QWidget()
        autosave_content_layout = QVBoxLayout(autosave_content)
        autosave_content_layout.setContentsMargins(0, 0, 0, 0)
        autosave_content_layout.setSpacing(6)

        self.img_autosave_btn = QPushButton(tr("btn_img_autosave"))
        self.img_autosave_btn.setProperty("class", "toggle")
        self.img_autosave_btn.setCheckable(True)
        self.img_autosave_btn.setChecked(self.auto_img_enabled)
        autosave_content_layout.addWidget(self.img_autosave_btn)

        img_conf_row = QHBoxLayout()
        self.img_conf_ge_label = QLabel(tr("label_conf_ge"))
        img_conf_row.addWidget(self.img_conf_ge_label)
        self.img_auto_conf_spin = QDoubleSpinBox()
        self.img_auto_conf_spin.setRange(0.05, 0.95)
        self.img_auto_conf_spin.setSingleStep(0.05)
        self.img_auto_conf_spin.setDecimals(2)
        self.img_auto_conf_spin.setValue(self.auto_img_conf)
        img_conf_row.addWidget(self.img_auto_conf_spin)
        self.img_conf_save_label = QLabel(tr("label_conf_save"))
        img_conf_row.addWidget(self.img_conf_save_label)
        img_conf_row.addStretch()
        autosave_content_layout.addLayout(img_conf_row)

        autosave_layout.addWidget(autosave_content)
        autosave_group.toggled.connect(autosave_content.setVisible)
        autosave_group.setChecked(False)

        right_layout.addWidget(autosave_group)

        # 实时监测
        monitor_group = QGroupBox(tr("group_monitor"))
        monitor_group.setCheckable(True)
        monitor_layout = QVBoxLayout(monitor_group)
        monitor_content = QWidget()
        monitor_content_layout = QVBoxLayout(monitor_content)
        monitor_content_layout.setContentsMargins(0, 0, 0, 0)
        monitor_content_layout.setSpacing(6)

        self.autosave_btn = QPushButton(tr("btn_autosave"))
        self.autosave_btn.setProperty("class", "toggle")
        self.autosave_btn.setCheckable(True)
        monitor_content_layout.addWidget(self.autosave_btn)

        auto_params_row = QHBoxLayout()
        auto_params_row.setSpacing(6)
        self.auto_conf_lbl = QLabel(tr("label_conf_short"))
        auto_params_row.addWidget(self.auto_conf_lbl)
        self.auto_conf_spin = QDoubleSpinBox()
        self.auto_conf_spin.setRange(0.05, 0.95)
        self.auto_conf_spin.setSingleStep(0.05)
        self.auto_conf_spin.setDecimals(2)
        self.auto_conf_spin.setValue(self.auto_conf)
        self.auto_conf_spin.setFixedWidth(56)
        auto_params_row.addWidget(self.auto_conf_spin)
        self.auto_stable_lbl = QLabel(tr("label_stable"))
        auto_params_row.addWidget(self.auto_stable_lbl)
        self.auto_stable_spin = QSpinBox()
        self.auto_stable_spin.setRange(1, 60)
        self.auto_stable_spin.setValue(self.auto_stable)
        self.auto_stable_spin.setFixedWidth(46)
        auto_params_row.addWidget(self.auto_stable_spin)
        self.auto_cool_lbl = QLabel(tr("label_cool"))
        auto_params_row.addWidget(self.auto_cool_lbl)
        self.auto_cool_spin = QSpinBox()
        self.auto_cool_spin.setRange(1, 60)
        self.auto_cool_spin.setValue(self.auto_cool)
        self.auto_cool_spin.setFixedWidth(46)
        auto_params_row.addWidget(self.auto_cool_spin)
        auto_params_row.addStretch()
        monitor_content_layout.addLayout(auto_params_row)

        monitor_layout.addWidget(monitor_content)
        monitor_group.toggled.connect(monitor_content.setVisible)
        monitor_group.setChecked(False)

        right_layout.addWidget(monitor_group)

        ai_group = QGroupBox(tr("group_ai"))
        ai_layout = QVBoxLayout(ai_group)
        self._register(ai_group, "group_ai")
        self.ai_hint_lbl = QLabel(tr("ai_hint"))
        self.ai_hint_lbl.setWordWrap(True)
        self.ai_hint_lbl.setStyleSheet("font-size:11px; color:#9a9aa0;")
        self._register(self.ai_hint_lbl, "ai_hint")
        ai_layout.addWidget(self.ai_hint_lbl)
        self.ai_text = QPlainTextEdit()
        self.ai_text.setReadOnly(True)
        self.ai_text.setPlaceholderText(tr("ai_placeholder"))
        self.ai_text.setMinimumHeight(150)
        ai_layout.addWidget(self.ai_text)
        right_layout.addWidget(ai_group)

        save_group = QGroupBox(tr("group_save"))
        save_layout = QVBoxLayout(save_group)

        path_row = QHBoxLayout()
        self.save_path_lbl = QLabel(tr("label_save_path"))
        path_row.addWidget(self.save_path_lbl)
        self.save_path_edit = QLineEdit(self._saved_output)
        self.btn_browse = QPushButton(tr("btn_browse"))
        path_row.addWidget(self.save_path_edit)
        path_row.addWidget(self.btn_browse)
        save_layout.addLayout(path_row)

        fmt_row = QHBoxLayout()
        self.fmt_lbl = QLabel(tr("label_format"))
        fmt_row.addWidget(self.fmt_lbl)
        self.fmt_combo = QComboBox()
        self.fmt_combo.addItem("JPG", "jpg")
        self.fmt_combo.addItem("PNG", "png")
        self.fmt_combo.addItem("BMP", "bmp")
        self.fmt_combo.addItem("WEBP", "webp")
        self.fmt_combo.addItem("TIFF", "tif")
        idx = self.fmt_combo.findData(self._saved_fmt)
        if idx >= 0:
            self.fmt_combo.setCurrentIndex(idx)
        fmt_row.addWidget(self.fmt_combo)
        fmt_row.addStretch()
        save_layout.addLayout(fmt_row)

        self.btn_save = QPushButton(tr("btn_save"))
        self.btn_save.setProperty("class", "primary")
        save_layout.addWidget(self.btn_save)
        right_layout.addWidget(save_group)
        right_layout.addStretch(1)

        right_scroll = QScrollArea()
        right_scroll.setWidgetResizable(True)
        right_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        right_scroll.setMinimumWidth(360)
        right_scroll.setMaximumWidth(560)
        right_scroll.setWidget(right)
        splitter.addWidget(right_scroll)
        splitter.setStretchFactor(0, 5)
        splitter.setStretchFactor(1, 4)
        splitter.setSizes([740, 540])
        root.addWidget(splitter, 1)

        self._register(result_group, "group_result")
        self._register(detect_group, "group_detect")
        self._register(autosave_group, "group_autosave")
        self._register(monitor_group, "group_monitor")
        self._register(save_group, "group_save")

        # 右侧面板内的标签与按钮
        self._register(self.conf_lbl, "label_conf")
        self._register(self.img_autosave_btn, "btn_img_autosave")
        self._register(self.img_conf_ge_label, "label_conf_ge")
        self._register(self.img_conf_save_label, "label_conf_save")
        self._register(self.autosave_btn, "btn_autosave")
        self._register(self.auto_conf_lbl, "label_conf_short")
        self._register(self.auto_stable_lbl, "label_stable")
        self._register(self.auto_cool_lbl, "label_cool")
        self._register(self.save_path_lbl, "label_save_path")
        self._register(self.btn_browse, "btn_browse")
        self._register(self.fmt_lbl, "label_format")
        self._register(self.btn_save, "btn_save")

        self.status = QStatusBar()
        self.setStatusBar(self.status)
        self.status.showMessage(tr("status_ready"))

        self.btn_open.clicked.connect(self._open_image_dialog)
        self.btn_batch.clicked.connect(self._open_folder_dialog)
        self.btn_ai.clicked.connect(self._run_ai_summary)
        self.btn_model.clicked.connect(self._select_model)
        self.btn_clear.clicked.connect(self._clear)
        self.btn_browse.clicked.connect(self._browse_save_path)
        self.btn_save.clicked.connect(self._save_result)
        self.btn_theme.clicked.connect(self._toggle_theme)
        self.btn_lang.clicked.connect(self._toggle_lang)
        self.btn_camera.clicked.connect(self._toggle_camera)
        self.autosave_btn.toggled.connect(self._on_autosave_toggled)
        self.auto_conf_spin.valueChanged.connect(self._on_auto_conf_changed)
        self.auto_stable_spin.valueChanged.connect(self._on_auto_stable_changed)
        self.auto_cool_spin.valueChanged.connect(self._on_auto_cool_changed)
        self.img_autosave_btn.toggled.connect(self._on_img_autosave_toggled)
        self.img_auto_conf_spin.valueChanged.connect(self._on_img_auto_conf_changed)
        self.conf_slider.valueChanged.connect(self._on_conf_changed)

    # ========== 设置回调 ==========

    def _on_conf_changed(self, value):
        self.conf_threshold = value / 100.0
        self.conf_label.setText(f"{self.conf_threshold:.2f}")
        self._save_config()

    # ========== 模型 ==========

    def _load_default_model(self):
        if DEFAULT_MODEL.exists():
            self._load_model_async(DEFAULT_MODEL)
        else:
            self.status.showMessage(tr("status_no_model_file"))

    def _load_model_async(self, path):
        self.status.showMessage(tr("status_loading_model").format(name=path.name))
        self.model_worker = ModelLoadWorker(path)
        self.model_worker.loaded.connect(self._on_model_loaded)
        self.model_worker.failed.connect(self._on_model_failed)
        self.model_worker.start()

    def _on_model_loaded(self, model, path):
        self.model = model
        self.model_path = Path(path)
        self._model_failed = False
        self.model_label.setText(tr("model_name").format(name=self.model_path.name))
        self._refresh_model_badge()
        self.status.showMessage(tr("status_model_loaded").format(path=self.model_path))

    def _on_model_failed(self, msg):
        self.model = None
        self._model_failed = True
        self.model_label.setText(tr("model_fail"))
        self._refresh_model_badge()
        self.status.showMessage(tr("status_model_fail").format(msg=msg))

    def _select_model(self):
        path, _ = QFileDialog.getOpenFileName(
            self, tr("dlg_model_title"), str(MODEL_DIR), tr("dlg_model_filter"))
        if path:
            self._load_model_async(Path(path))

    # ========== 输入 ==========

    def _on_file_dropped(self, path):
        p = Path(path)
        if p.is_dir():
            self._run_batch(p)
        elif p.is_file() and p.suffix.lower() in IMAGE_EXTS:
            self._detect_single(p)
        else:
            self.status.showMessage(tr("status_bad_type"))

    def _open_image_dialog(self):
        path, _ = QFileDialog.getOpenFileName(
            self, tr("dlg_image_title"), str(BASE_DIR), tr("dlg_image_filter"))
        if path:
            self._detect_single(Path(path))

    def _open_folder_dialog(self):
        folder = QFileDialog.getExistingDirectory(self, tr("dlg_folder_title"), str(BASE_DIR))
        if folder:
            self._run_batch(Path(folder))

    # ========== 检测 ==========

    def _detect_single(self, path):
        if self.model is None:
            QMessageBox.warning(self, tr("dlg_note_title"), tr("warn_no_model"))
            return
        self.current_path = path
        self.status.showMessage(tr("status_detecting").format(name=path.name))
        self._set_busy(True)
        self.detect_worker = DetectWorker(self.model, path, self.conf_threshold)
        self.detect_worker.done.connect(self._on_detect_done)
        self.detect_worker.failed.connect(self._on_detect_failed)
        self.detect_worker.start()

    def _on_detect_done(self, annotated, detections, path, elapsed):
        self.current_annotated = annotated
        self._last_detections = detections
        self.result_list.clear()
        if detections:
            for i, (name, conf) in enumerate(detections, 1):
                self.result_list.addItem(
                    QListWidgetItem(tr("result_item").format(i=i, name=name, conf=conf)))
        else:
            self.result_list.addItem(tr("result_no_target"))
        self._show_numpy(annotated)
        if self.auto_img_enabled and detections:
            max_conf = max(c for _, c in detections)
            if max_conf >= self.auto_img_conf:
                self._auto_save_annotated(annotated)
        self.status.showMessage(
            tr("status_done").format(
                name=Path(path).name, n=len(detections), ms=elapsed))
        self._set_busy(False)

    def _on_detect_failed(self, msg):
        self.status.showMessage(tr("status_fail").format(msg=msg))
        self._set_busy(False)

    def _run_batch(self, folder):
        if self.model is None:
            QMessageBox.warning(self, tr("dlg_note_title"), tr("warn_no_model"))
            return
        out_dir = Path(self.save_path_edit.text().strip() or str(DEFAULT_OUTPUT))
        out_dir.mkdir(parents=True, exist_ok=True)
        ext = self.fmt_combo.currentData()
        self.status.showMessage(tr("status_batch_run"))
        self._set_busy(True)
        self.batch_worker = BatchWorker(
            self.model, folder, out_dir, ext, self.conf_threshold,
            auto_enabled=self.auto_img_enabled, auto_conf=self.auto_img_conf)
        self.batch_worker.progress.connect(self._on_batch_progress)
        self.batch_worker.report_ready.connect(self._on_batch_report)
        self.batch_worker.done.connect(self._on_batch_done)
        self.batch_worker.failed.connect(self._on_batch_failed)
        self.batch_worker.start()

    def _on_batch_report(self, summary):
        self.last_batch_summary = summary
        self.btn_ai.setEnabled(True)

    def _build_ai_prompt(self, summary):
        total = summary.get("total", 0)
        class_total = summary.get("class_total", {})
        rows = summary.get("rows", [])
        col_image = summary.get("col_image", "图片")
        col_targets = summary.get("col_targets", "目标总数")
        total_targets = sum(r.get(col_targets, 0) for r in rows)

        lines = [
            "【批量目标检测统计结果】",
            f"检测图片总数：{total}，目标总数：{total_targets}",
        ]
        if class_total:
            dist = "、".join(f"{k}: {v}" for k, v in
                             sorted(class_total.items(), key=lambda x: -x[1]))
            lines.append(f"各类目标累计：{dist}")
        lines.append("请基于以上数据，输出一份简洁客观的批量目标检测统计总结："
                     "描述各类目标的分布与数量构成，可提出通用性观察；"
                     "严格基于提供的数据，不得编造任何数字或结论。")
        return "\n".join(lines)

    def _run_ai_summary(self):
        if self.last_batch_summary is None:
            QMessageBox.warning(self, tr("dlg_note_title"), tr("ai_warn_no_summary"))
            return
        if not self.ai_api_key:
            QMessageBox.warning(self, tr("dlg_note_title"), tr("ai_warn_no_key"))
            return
        prompt = self._build_ai_prompt(self.last_batch_summary)
        self.ai_text.setPlainText(tr("ai_requesting"))
        self.status.showMessage(tr("status_ai_start"))
        self._set_busy(True)
        self.ai_worker = AISummaryWorker(
            self.ai_api_key, self.ai_base_url, self.ai_model, prompt)
        self.ai_worker.done.connect(self._on_ai_done)
        self.ai_worker.failed.connect(self._on_ai_failed)
        self.ai_worker.start()

    def _on_ai_done(self, result):
        self.ai_text.setPlainText(result)
        try:
            saved = self._save_ai_report(result)
            self.status.showMessage(tr("ai_saved").format(path=saved))
        except Exception:
            self.status.showMessage(tr("status_ai_ok"))
        self._set_busy(False)

    def _save_ai_report(self, result):
        summary = self.last_batch_summary or {}
        folder_name = summary.get("folder_name") or "batch"
        safe = "".join(c for c in folder_name if c not in '\\/:*?"<>|').strip() or "batch"
        ts = time.strftime("%Y%m%d_%H%M%S")
        out = Path(summary.get("out_dir") or str(DEFAULT_OUTPUT))
        path = out / f"AI报告_{safe}_{ts}.txt"
        with path.open("w", encoding="utf-8-sig") as f:
            f.write(result)
        return path

    def _on_ai_failed(self, msg):
        self.ai_text.setPlainText(tr("ai_fail").format(msg=msg))
        self._set_busy(False)
        self.status.showMessage(tr("status_ai_fail"))

    def _on_batch_progress(self, cur, total, name, elapsed):
        self.status.showMessage(
            tr("status_batch_progress").format(cur=cur, total=total, name=name, ms=elapsed))

    def _on_batch_done(self, count, out_dir, report_path, total_elapsed):
        sec = total_elapsed / 1000
        self.status.showMessage(
            tr("status_batch_done").format(
                n=count, dir=out_dir, sec=sec, report=report_path))
        QMessageBox.information(
            self, tr("dlg_batch_title"),
            tr("dlg_batch_msg").format(
                n=count, dir=out_dir, report=report_path, sec=sec))
        self._set_busy(False)

    def _on_batch_failed(self, msg):
        self.status.showMessage(tr("status_batch_fail").format(msg=msg))
        self._set_busy(False)

    # ========== 实时监测 ==========

    def _toggle_camera(self):
        if self.camera_on:
            self._stop_camera()
        else:
            self._start_camera()

    def _set_camera_busy(self, busy):
        for b in (self.btn_open, self.btn_batch, self.btn_model, self.btn_save):
            b.setEnabled(not busy)

    def _start_camera(self):
        if self.model is None:
            QMessageBox.warning(self, tr("dlg_note_title"), tr("warn_no_model_cam"))
            self.btn_camera.setChecked(False)
            return
        out_dir = Path(self.save_path_edit.text().strip() or str(DEFAULT_OUTPUT))
        out_dir.mkdir(parents=True, exist_ok=True)
        ext = self.fmt_combo.currentData()
        self.camera_worker = CameraWorker(self.model, 0, self.auto_conf)
        self.camera_worker.autosave = self.autosave_btn.isChecked()
        self.camera_worker.stable_frames_need = self.auto_stable
        self.camera_worker.cool_seconds = self.auto_cool
        self.camera_worker.save_dir = str(out_dir)
        self.camera_worker.save_ext = ext
        self.camera_worker.frame_ready.connect(self._on_camera_frame)
        self.camera_worker.saved.connect(self._on_camera_saved)
        self.camera_worker.failed.connect(self._on_camera_failed)
        self.camera_worker.start()
        self.camera_on = True
        self.btn_camera.setChecked(True)
        self._set_camera_busy(True)
        self.status.showMessage(tr("status_cam_start"))

    def _stop_camera(self):
        if self.camera_worker is not None:
            self.camera_worker.stop()
            self.camera_worker.wait(2000)
        self.camera_worker = None
        self.camera_on = False
        self.btn_camera.setChecked(False)
        self._set_camera_busy(False)
        self.status.showMessage(tr("status_cam_stop"))

    def _on_camera_frame(self, annotated):
        self._show_numpy(annotated)

    def _on_camera_saved(self, path, count):
        self.status.showMessage(tr("status_cam_saved").format(path=path, n=count))

    def _on_camera_failed(self, msg):
        self.camera_worker = None
        self.camera_on = False
        self.btn_camera.setChecked(False)
        self._set_camera_busy(False)
        self.status.showMessage(tr("status_cam_error").format(msg=msg))

    def _on_autosave_toggled(self, checked):
        if self.camera_worker is not None:
            self.camera_worker.set_params(autosave=checked)
        self.status.showMessage(tr("status_autosave_on") if checked else tr("status_autosave_off"))

    def _on_auto_conf_changed(self, value):
        self.auto_conf = value
        if self.camera_worker is not None:
            self.camera_worker.set_params(conf=value)
        self._save_config()

    def _on_auto_stable_changed(self, value):
        self.auto_stable = value
        if self.camera_worker is not None:
            self.camera_worker.set_params(stable_frames=value)
        self._save_config()

    def _on_auto_cool_changed(self, value):
        self.auto_cool = value
        if self.camera_worker is not None:
            self.camera_worker.set_params(cool_seconds=value)
        self._save_config()

    def _on_img_autosave_toggled(self, checked):
        self.auto_img_enabled = checked
        self._save_config()
        self.status.showMessage(tr("status_autosave_on") if checked else tr("status_autosave_off"))

    def _on_img_auto_conf_changed(self, value):
        self.auto_img_conf = value
        self._save_config()

    # ========== 显示与保存 ==========

    def _show_numpy(self, bgr):
        rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        qimg = QImage(rgb.data, w, h, ch * w, QImage.Format_RGB888).copy()
        pixmap = QPixmap.fromImage(qimg)
        # 缩放到滚动区域可用宽度
        avail_w = self.scroll_area.viewport().width() - 20
        if pixmap.width() > avail_w:
            pixmap = pixmap.scaledToWidth(avail_w, Qt.SmoothTransformation)
        self.preview_image.set_pixmap(pixmap)
        self.preview_image.resize(pixmap.size())
        self._update_placeholder_style()

    def _save_result(self):
        if self.current_annotated is None:
            QMessageBox.information(self, tr("dlg_note_title"), tr("dlg_no_result"))
            return
        out_dir = Path(self.save_path_edit.text().strip() or str(DEFAULT_OUTPUT))
        out_dir.mkdir(parents=True, exist_ok=True)
        ext = self.fmt_combo.currentData()
        src = Path(self.current_path)
        out = out_dir / f"{src.stem}_detected.{ext}"
        cv2.imwrite(str(out), self.current_annotated)
        self.status.showMessage(tr("status_saved").format(path=out))
        self._save_config()

    def _auto_save_annotated(self, annotated):
        out_dir = Path(self.save_path_edit.text().strip() or str(DEFAULT_OUTPUT))
        out_dir.mkdir(parents=True, exist_ok=True)
        ext = self.fmt_combo.currentData()
        src = Path(self.current_path)
        out = out_dir / f"{src.stem}_detected.{ext}"
        cv2.imwrite(str(out), annotated)
        self.status.showMessage(tr("status_autosaved").format(path=out))

    def _browse_save_path(self):
        folder = QFileDialog.getExistingDirectory(
            self, tr("dlg_savepos_title"), str(self.save_path_edit.text() or str(DEFAULT_OUTPUT)))
        if folder:
            self.save_path_edit.setText(folder)
            self._save_config()

    def _clear(self):
        self.current_path = None
        self.current_annotated = None
        self._last_detections = None
        self.result_list.clear()
        self.preview_image.set_placeholder(tr("placeholder"))
        self.preview_image.setWordWrap(True)
        self.preview_image.resize(self.scroll_area.viewport().size() - QRect(0, 0, 4, 4).size())
        self._update_placeholder_style()
        self.status.showMessage(tr("status_cleared"))

    def _set_busy(self, busy):
        for b in (self.btn_open, self.btn_batch, self.btn_save, self.btn_camera):
            b.setEnabled(not busy)
        # AI 按钮仅在已有批量结果时可用；忙碌期间也禁用
        if self.last_batch_summary is not None:
            self.btn_ai.setEnabled(not busy)

    def closeEvent(self, event):
        self._save_config()
        if self.camera_worker is not None and self.camera_worker.isRunning():
            self.camera_worker.stop()
            self.camera_worker.wait(2000)
        for w in (self.model_worker, self.detect_worker, self.batch_worker, self.ai_worker):
            if w is not None and w.isRunning():
                w.wait(2000)
        event.accept()


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    win = MainWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()