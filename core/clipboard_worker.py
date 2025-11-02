# core/clipboard_worker.py
from __future__ import annotations

import threading
from datetime import datetime

from PySide6.QtCore import QThread, Signal

from clipboard_monitor import get_clipboard_text
from platform_utils import get_active_app_name
from classifier import classify_content
from sensitive_detector import detect_and_mask
from database import add_record


class ClipboardWorker(QThread):
    """后台线程轮询剪贴板并输出处理结果。"""

    record_ready = Signal(dict)
    error = Signal(str)

    def __init__(self, config_provider, interval=0.8, parent=None):
        super().__init__(parent)
        self._config_provider = config_provider
        self._interval = max(0.1, float(interval))
        self._stop_event = threading.Event()
        self._last_text = ""
        self._error_reported = False
        self._duplicate_logged = False
        self._blank_logged = False
        self._ignore_lock = threading.Lock()
        self._ignore_once: list[str] = []

    def run(self):
        print(f"[调试] ClipboardWorker 启动，轮询间隔：{self._interval}s")
        self._stop_event.clear()
        while not self._stop_event.is_set():
            try:
                text = get_clipboard_text()
                if text and text.strip():
                    if self._should_ignore(text):
                        print("[调试] 忽略来自应用内部的复制内容")
                        self._last_text = text
                        self._duplicate_logged = False
                        self._blank_logged = False
                        continue
                    if text != self._last_text:
                        preview = text.replace("\n", " ")[:60]
                        print(f"[调试] 捕获到新的剪贴板文本（长度 {len(text)}）：{preview!r}")
                        self._handle_clipboard_text(text)
                        self._last_text = text
                        self._duplicate_logged = False
                        self._blank_logged = False
                    else:
                        if not self._duplicate_logged:
                            print("[调试] 剪贴板内容未变化，跳过处理")
                            self._duplicate_logged = True
                else:
                    if not self._blank_logged:
                        print("[调试] 当前剪贴板为空或仅为空白字符，跳过")
                        self._blank_logged = True
                if self._error_reported:
                    self._error_reported = False
            except Exception as exc:
                print(f"[调试] 读取剪贴板时出现异常：{exc}")
                if not self._error_reported:
                    self.error.emit(str(exc))
                    self._error_reported = True
            if self._stop_event.wait(self._interval):
                break

    def stop(self):
        self._stop_event.set()
        self.wait()

    def update_interval(self, interval):
        self._interval = max(0.1, float(interval))

    def reset_last_seen(self):
        self._last_text = ""

    def ignore_text_once(self, text: str):
        if not text:
            return
        with self._ignore_lock:
            self._ignore_once.append(text)

    def _should_ignore(self, text: str) -> bool:
        with self._ignore_lock:
            for idx, value in enumerate(self._ignore_once):
                if value == text:
                    self._ignore_once.pop(idx)
                    return True
        return False

    def _handle_clipboard_text(self, text):
        config = self._config_provider()
        custom_kw = config.get("custom_sensitive_keywords", [])
        masked, has_sensitive, types = detect_and_mask(text, custom_kw)
        app_name = get_active_app_name()
        category = classify_content(text)
        timestamp = datetime.now().isoformat()
        print(f"[调试] 分类结果：category={category}, app={app_name}, has_sensitive={has_sensitive}, types={types}")
        record_id = add_record(masked, app_name, category, types, has_sensitive, timestamp=timestamp)
        payload = {
            "id": record_id,
            "timestamp": timestamp,
            "app": app_name or "Unknown",
            "category": category,
            "types": types or [],
            "masked": masked,
            "raw": text if config.get("save_raw_content") else "",
            "has_sensitive": has_sensitive,
            "is_favorite": False,
            "is_deleted": False,
        }
        self.record_ready.emit(payload)
