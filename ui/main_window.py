# ui/main_window.py
import json
import sys
from collections import Counter
from datetime import datetime, timedelta
from pathlib import Path

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMenu,
    QPlainTextEdit,
    QPushButton,
    QSplitter,
    QSplitterHandle,
    QStatusBar,
    QStyle,
    QSystemTrayIcon,
    QVBoxLayout,
    QWidget,
)

from config import load_config, save_config
from core.clipboard_worker import ClipboardWorker
from database import delete_permanently, get_all_records, get_records, init_db, set_deleted, set_favorite
from ui.models import ClipHistoryModel
from ui.settings_dialog import SettingsDialog
from ui.components import ClipboardListWidget, SidebarWidget, TopBarWidget
from ui.i18n import Translator
from ui.styles import load_stylesheet


class GripSplitterHandle(QSplitterHandle):
    """自定义 Splitter 手柄，展示拖动提示图标。"""

    def __init__(self, orientation, parent):
        super().__init__(orientation, parent)
        self._icon = QLabel("⋮" if orientation == Qt.Horizontal else "⋯", self)
        self._icon.setObjectName("splitterHandleIcon")
        self._icon.setAlignment(Qt.AlignCenter)

    def resizeEvent(self, event):  # noqa: N802
        super().resizeEvent(event)
        self._icon.setGeometry(0, 0, self.width(), self.height())


class GripSplitter(QSplitter):
    """带图标提示的 Splitter。"""

    def __init__(self, orientation, parent=None):
        super().__init__(orientation, parent)
        self.setHandleWidth(12)

    def createHandle(self):  # noqa: D401
        return GripSplitterHandle(self.orientation(), self)


class ClipGuardWindow(QMainWindow):
    RECENT_WINDOW_HOURS = 24

    def __init__(self):
        super().__init__()
        self.resize(1080, 640)
        self._asset_base = None
        self._app_icon = self._load_icon([
            ("assets", "icons", "app-icon-32.png", 32),
            ("assets", "icons", "app-icon-64.png", 64),
            ("assets", "icons", "app-icon-128.png", 128),
        ])
        if not self._app_icon.isNull():
            self.setWindowIcon(self._app_icon)
        self._tray_qicon = self._load_icon([
            ("assets", "icons", "tray.png", 24),
            ("assets", "icons", "tray@2x.png", 48),
        ])

        init_db()
        self.config = load_config()
        self.translator = Translator(self.config.get("language", "zh-CN"))
        self._filters = {
            "search": "",
            "type": None,
            "app": None,
        }
        self._active_record = None
        self._current_route = "/"
        self._masked_original_text = ""
        self._raw_original_text = ""
        self._masked_formatted = False
        self._raw_formatted = False
        self._all_records = self._load_initial_records()
        self.model = ClipHistoryModel(list(self._all_records), translator=self.translator)

        self._build_ui()
        self._connect_components()
        self._apply_styles()
        self._setup_worker()
        self._update_actions()
        self._tray_icon = None
        self._tray_menu = None
        self._quit_requested = False
        self._setup_tray_icon()
        self._apply_language(self.translator.language(), initial=True)

    def _asset_path(self, *parts: str) -> Path:
        if self._asset_base is None:
            base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parents[1]))
            self._asset_base = base
        return self._asset_base.joinpath(*parts)

    def _load_icon(self, specs) -> QIcon:
        icon = QIcon()
        found = False
        for *segments, size in specs:
            path = self._asset_path(*segments)
            if path.exists():
                icon.addFile(str(path), QSize(size, size))
                found = True
        return icon if found else QIcon()

    def _build_ui(self):
        central = QWidget(self)
        central_layout = QVBoxLayout(central)
        central_layout.setContentsMargins(0, 0, 0, 0)
        central_layout.setSpacing(0)

        self.topbar = TopBarWidget(self.translator, self)
        central_layout.addWidget(self.topbar, 0)

        self.main_splitter = GripSplitter(Qt.Horizontal, central)
        self.main_splitter.setObjectName("mainSplitter")
        self.main_splitter.setChildrenCollapsible(False)

        self.sidebar = SidebarWidget(self.translator, self.main_splitter)
        self.sidebar.setMinimumWidth(96)
        self.sidebar.setMaximumWidth(360)
        self.main_splitter.addWidget(self.sidebar)

        content_frame = QWidget(self.main_splitter)
        content_layout = QVBoxLayout(content_frame)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        self.content_splitter = GripSplitter(Qt.Horizontal, content_frame)
        self.content_splitter.setObjectName("contentSplitter")
        self.content_splitter.setChildrenCollapsible(False)

        self.clipboard_list = ClipboardListWidget(self.translator, self.content_splitter)
        self.clipboard_list.setMinimumWidth(320)
        self.content_splitter.addWidget(self.clipboard_list)

        self.detail_group = QGroupBox("", self.content_splitter)
        self.detail_group.setObjectName("detailPane")
        self.detail_group.setMinimumWidth(320)
        detail_layout = QVBoxLayout(self.detail_group)
        detail_layout.setContentsMargins(16, 16, 16, 16)
        detail_layout.setSpacing(12)

        self.detail_timestamp = QLabel("", self.detail_group)
        self.detail_source = QLabel("", self.detail_group)
        self.detail_category = QLabel("", self.detail_group)
        self.detail_sensitive = QLabel("", self.detail_group)

        detail_layout.addWidget(self.detail_timestamp)
        detail_layout.addWidget(self.detail_source)
        detail_layout.addWidget(self.detail_category)
        detail_layout.addWidget(self.detail_sensitive)

        masked_header = QHBoxLayout()
        masked_header.setContentsMargins(0, 0, 0, 0)
        self.detail_masked_label = QLabel("", self.detail_group)
        masked_header.addWidget(self.detail_masked_label)
        masked_header.addStretch(1)
        self.format_masked_button = QPushButton("", self.detail_group)
        self.format_masked_button.setCursor(Qt.PointingHandCursor)
        self.format_masked_button.clicked.connect(self._toggle_masked_format)
        self.format_masked_button.setEnabled(False)
        masked_header.addWidget(self.format_masked_button)
        self.copy_masked_button = QPushButton("", self.detail_group)
        self.copy_masked_button.setCursor(Qt.PointingHandCursor)
        self.copy_masked_button.clicked.connect(self._copy_masked_detail)
        self.copy_masked_button.setEnabled(False)
        masked_header.addWidget(self.copy_masked_button)
        detail_layout.addLayout(masked_header)

        self.masked_edit = QPlainTextEdit()
        self.masked_edit.setReadOnly(True)
        detail_layout.addWidget(self.masked_edit, stretch=1)

        raw_header = QHBoxLayout()
        raw_header.setContentsMargins(0, 0, 0, 0)
        self.detail_raw_label = QLabel("", self.detail_group)
        raw_header.addWidget(self.detail_raw_label)
        raw_header.addStretch(1)
        self.format_raw_button = QPushButton("", self.detail_group)
        self.format_raw_button.setCursor(Qt.PointingHandCursor)
        self.format_raw_button.clicked.connect(self._toggle_raw_format)
        self.format_raw_button.setEnabled(False)
        raw_header.addWidget(self.format_raw_button)
        self.copy_raw_button = QPushButton("", self.detail_group)
        self.copy_raw_button.setCursor(Qt.PointingHandCursor)
        self.copy_raw_button.clicked.connect(self._copy_raw_detail)
        self.copy_raw_button.setEnabled(False)
        raw_header.addWidget(self.copy_raw_button)
        detail_layout.addLayout(raw_header)

        self.raw_edit = QPlainTextEdit()
        self.raw_edit.setReadOnly(True)
        detail_layout.addWidget(self.raw_edit, stretch=1)

        self.content_splitter.addWidget(self.detail_group)
        self.content_splitter.setStretchFactor(0, 2)
        self.content_splitter.setStretchFactor(1, 3)
        self.content_splitter.setSizes([560, 520])

        content_layout.addWidget(self.content_splitter, 1)
        self.main_splitter.addWidget(content_frame)
        self.main_splitter.setStretchFactor(0, 0)
        self.main_splitter.setStretchFactor(1, 1)
        self.main_splitter.setSizes([120, 960])

        central_layout.addWidget(self.main_splitter, 1)

        self.setCentralWidget(central)
        self.setStatusBar(QStatusBar(self))

        self.clipboard_list.set_model(self.model)

    def _apply_styles(self):
        self.setStyleSheet(load_stylesheet())

    def _connect_components(self):
        self.clipboard_list.selectionChanged.connect(self._show_record)
        self.clipboard_list.viewModeChanged.connect(self._on_view_mode_changed)
        self.clipboard_list.deleteSelectedRequested.connect(self._on_delete_selected_items)
        self.clipboard_list.restoreSelectedRequested.connect(self._on_restore_selected_items)
        self.clipboard_list.copyRequested.connect(self._on_copy_requested)
        self.clipboard_list.favoriteToggled.connect(self._on_favorite_toggled)

        self.topbar.startMonitorRequested.connect(self.start_monitoring)
        self.topbar.stopMonitorRequested.connect(self.stop_monitoring)
        self.topbar.refreshRequested.connect(self._refresh_history)
        self.topbar.settingsRequested.connect(self._open_settings)
        self.topbar.searchTextChanged.connect(self._on_search_text_changed)

        self.sidebar.navigateRequested.connect(self._on_sidebar_navigate)
        self.sidebar.contentFilterRequested.connect(self._on_sidebar_content_filter)
        self.sidebar.appFilterRequested.connect(self._on_sidebar_app_filter)
        self.sidebar.searchTextChanged.connect(self._on_sidebar_search)
        self.sidebar.settingsRequested.connect(self._open_settings)

        self.sidebar.set_active_route(self._current_route)
        self._update_app_filters()
        self.sidebar.set_active_filters(self._filters["type"], self._filters["app"])
        self._apply_filters(initial=True)

    def _on_view_mode_changed(self, mode: str):
        print(f"[调试] 切换列表视图模式: {mode}")

    def _on_delete_selected_items(self, record=None):
        target = record or self._active_record
        if not target:
            self._show_status("status.delete.none", 2000)
            return
        record_id = target.get("id")
        if record_id is None:
            self._show_status("status.delete.missing_id", 2000)
            return
        if self._current_route == "/trash":
            delete_permanently(record_id)
            self._all_records = [item for item in self._all_records if item.get("id") != record_id]
            if self._active_record and self._active_record.get("id") == record_id:
                self._active_record = None
            self._apply_filters()
            self._show_status("status.delete.permanent", 2000)
            return
        set_deleted(record_id, True)
        for item in self._all_records:
            if item.get("id") == record_id:
                item["is_deleted"] = True
        if self._active_record and self._active_record.get("id") == record_id:
            self._active_record = None
        self._apply_filters()
        self._show_status("status.delete.moved", 2000)

    def _on_copy_requested(self, record: dict):
        if not record:
            self._show_status("status.copy.none", 2000)
            return
        text = record.get("raw") or record.get("masked") or record.get("masked_preview") or ""
        if not text:
            self._show_status("status.copy.empty", 2000)
            return
        if self._copy_to_clipboard(text):
            self._active_record = record
            self._focus_record(record)
            self._show_status("status.copy.success", 2000)

    def _copy_masked_detail(self):
        text = self.masked_edit.toPlainText()
        if not text:
            self._show_status("status.copy.masked_none", 2000)
            return
        if self._copy_to_clipboard(text):
            self._show_status("status.copy.masked_success", 2000)

    def _copy_raw_detail(self):
        text = self.raw_edit.toPlainText()
        if not text:
            self._show_status("status.copy.raw_none", 2000)
            return
        if self._copy_to_clipboard(text):
            self._show_status("status.copy.raw_success", 2000)

    def _copy_to_clipboard(self, text: str) -> bool:
        if not text:
            return False
        if hasattr(self, "worker") and hasattr(self.worker, "ignore_text_once"):
            self.worker.ignore_text_once(text)
        QApplication.clipboard().setText(text)
        return True

    def _on_search_text_changed(self, text: str):
        self._filters["search"] = text or ""
        self._apply_filters()
        self.sidebar.set_search_text(text or "")

    def _on_sidebar_navigate(self, route: str):
        if route not in {"/", "/recent", "/favorites", "/trash"}:
            return
        if route == self._current_route:
            return
        self._current_route = route
        self.sidebar.set_active_route(route)
        self._apply_filters()

    def _on_sidebar_content_filter(self, key: str):
        _, value = key.split(":", 1)
        current = self._filters.get("type")
        self._filters["type"] = None if current == value else value
        self.sidebar.set_active_filters(self._filters["type"], self._filters["app"])
        self._apply_filters()

    def _on_sidebar_app_filter(self, key: str):
        _, value = key.split(":", 1)
        current = self._filters.get("app")
        self._filters["app"] = None if current == value else value
        self.sidebar.set_active_filters(self._filters["type"], self._filters["app"])
        self._apply_filters()

    def _on_sidebar_search(self, text: str):
        self._filters["search"] = text or ""
        self._apply_filters()
        self.topbar.set_search_text(text or "")

    def _on_favorite_toggled(self, record: dict, is_favorite: bool):
        record_id = record.get("id")
        if record_id is None:
            self._show_status("status.favorite.invalid", 2000)
            return
        set_favorite(record_id, is_favorite)
        for item in self._all_records:
            if item.get("id") == record_id:
                item["is_favorite"] = is_favorite
        if self._active_record and self._active_record.get("id") == record_id:
            self._active_record["is_favorite"] = is_favorite
        self._apply_filters()
        self._show_status("status.favorite.added" if is_favorite else "status.favorite.removed", 2000)

    def _apply_filters(self, initial: bool = False):
        active_id = self._active_record.get("id") if self._active_record else None
        search_text = (self._filters.get("search") or "").strip()
        search_lower = search_text.lower()
        self.clipboard_list.set_trash_mode(self._current_route == "/trash")

        if search_text:
            records_source = self._fetch_records(search_text, limit=400)
        else:
            records_source = self._all_records

        if self._current_route == "/trash":
            base_records = [rec for rec in records_source if rec.get("is_deleted")]
        else:
            base_records = [rec for rec in records_source if not rec.get("is_deleted")]
            if self._current_route == "/favorites":
                base_records = [rec for rec in base_records if rec.get("is_favorite")]
            elif self._current_route == "/recent":
                threshold = datetime.now() - timedelta(hours=self.RECENT_WINDOW_HOURS)
                base_records = [rec for rec in base_records if self._is_recent(rec, threshold)]

        self._update_app_filters(base_records)
        type_filter = self._filters.get("type")
        app_filter = self._filters.get("app")

        def matches(record):
            record_type = self._type_key(record.get("category"))
            if type_filter and record_type != type_filter:
                return False
            if app_filter and record.get("app") != app_filter:
                return False
            if search_text:
                haystacks = [
                    record.get("masked", ""),
                    record.get("masked_preview", ""),
                    record.get("app", ""),
                    record.get("category", ""),
                    record.get("types_display", ""),
                    record.get("raw", ""),
                ]
                joined = "\n".join(filter(None, haystacks)).lower()
                if search_lower and search_lower not in joined:
                    return False
            return True

        filtered = [rec for rec in base_records if matches(rec)]
        self.model.set_records(filtered)

        if filtered:
            target_index = 0
            if active_id is not None:
                for idx, rec in enumerate(filtered):
                    if rec.get("id") == active_id:
                        target_index = idx
                        break
            if 0 <= target_index < len(filtered):
                self.clipboard_list.select_row(target_index)
        else:
            self.clipboard_list.update_selection_info(0)
            self._show_record(None)

        self.sidebar.set_active_route(self._current_route)
        self.sidebar.set_active_filters(type_filter, app_filter)
        self._update_sidebar_counts()

        if not initial and search_text:
            self._show_status("status.search.result", 2000, count=len(filtered))

    def _on_restore_selected_items(self, record=None):
        target = record or self._active_record
        if not target:
            self._show_status("status.restore.none", 2000)
            return
        record_id = target.get("id")
        if record_id is None:
            self._show_status("status.restore.missing_id", 2000)
            return
        set_deleted(record_id, False)
        for item in self._all_records:
            if item.get("id") == record_id:
                item["is_deleted"] = False
        if self._current_route == "/trash":
            self._active_record = None
        else:
            self._active_record = target
        self._apply_filters()
        self._show_status("status.restore.success", 2000)

    @staticmethod
    def _is_recent(record, threshold: datetime) -> bool:
        ts = record.get("timestamp")
        if not ts:
            return False
        try:
            dt = datetime.fromisoformat(ts)
        except ValueError:
            return False
        return dt >= threshold

    def _focus_record(self, record: dict):
        if not record:
            return
        record_id = record.get("id")
        if record_id is None:
            return
        for idx in range(self.model.rowCount()):
            candidate = self.model.record_at(idx)
            if candidate and candidate.get("id") == record_id:
                self.clipboard_list.select_row(idx)
                break

    def _update_app_filters(self, records=None):
        if not hasattr(self, "sidebar"):
            return
        source = records if records is not None else self._all_records
        frequency = Counter()
        for rec in source:
            name = (rec.get("app") or "Unknown").strip()
            if not name:
                name = "Unknown"
            frequency[name] += 1
        if frequency:
            sorted_names = [
                item[0]
                for item in sorted(
                    frequency.items(),
                    key=lambda item: (-item[1], item[0].casefold()),
                )
            ]
        else:
            sorted_names = []
        previous_app = self._filters.get("app")
        self.sidebar.set_app_filter_items(sorted_names)
        if previous_app and previous_app not in sorted_names:
            self._filters["app"] = None

    def _update_sidebar_counts(self):
        active_records = [rec for rec in self._all_records if not rec.get("is_deleted")]
        threshold = datetime.now() - timedelta(hours=self.RECENT_WINDOW_HOURS)
        recent_records = [rec for rec in active_records if self._is_recent(rec, threshold)]
        favorites = [rec for rec in active_records if rec.get("is_favorite")]
        trash = [rec for rec in self._all_records if rec.get("is_deleted")]

        nav_counts = {
            "/": len(active_records),
            "/recent": len(recent_records),
            "/favorites": len(favorites),
            "/trash": len(trash),
        }

        type_counts = {key: 0 for key in self.sidebar.type_filters()}
        for rec in active_records:
            category_key = self._type_key(rec.get("category"))
            payload = f"type:{category_key}"
            if payload in type_counts:
                type_counts[payload] += 1

        app_counts = {key: 0 for key in self.sidebar.app_filters()}
        for rec in active_records:
            app_name = rec.get("app") or "Unknown"
            payload = f"app:{app_name}"
            if payload in app_counts:
                app_counts[payload] += 1

        self.sidebar.update_counts(nav_counts=nav_counts, type_counts=type_counts, app_counts=app_counts)

    @staticmethod
    def _type_key(category):
        mapping = {
            "business": "text",
            "email": "text",
            "phone": "text",
            "id": "text",
            "text": "text",
            "note": "text",
            "url": "url",
            "link": "url",
            "website": "url",
            "code": "code",
            "snippet": "code",
            "script": "code",
            "image": "image",
            "picture": "image",
            "screenshot": "image",
        }
        key = (category or "").strip().lower()
        return mapping.get(key, "text")

    def _setup_worker(self):
        interval = self.config.get("poll_interval", 0.8)
        self.worker = ClipboardWorker(lambda: self.config, interval=interval)
        self.worker.record_ready.connect(self._on_record_ready)
        self.worker.error.connect(self._on_worker_error)
        self._monitoring = False
        if self.config.get("enable_monitoring", True):
            self.start_monitoring()
        else:
            self._update_actions()
            self._show_status("status.monitor.paused", 3000)

    def _load_initial_records(self):
        rows = get_all_records(limit=200)
        return [self._record_from_row(row) for row in rows]

    def _record_from_row(self, row):
        return self._prepare_record({
            "id": row[0],
            "masked": row[1],
            "app": row[2],
            "category": row[3],
            "types": row[4],
            "has_sensitive": row[5],
            "timestamp": row[6],
            "is_favorite": row[7],
            "is_deleted": row[8],
            "raw": "",
        })

    def _fetch_records(self, search_text: str | None = None, limit: int = 200):
        rows = get_records(limit=limit, search=search_text)
        return [self._record_from_row(row) for row in rows]

    def start_monitoring(self):
        if self._monitoring:
            return
        if not self.worker.isRunning():
            self.worker.start()
        self._monitoring = True
        if not self.config.get("enable_monitoring", True):
            self.config["enable_monitoring"] = True
            save_config(self.config)
        self._show_status("status.monitor.started", 3000)
        self._update_actions()

    def stop_monitoring(self):
        if not self._monitoring:
            return
        if self.worker.isRunning():
            self.worker.stop()
            self.worker.reset_last_seen()
        self._monitoring = False
        if self.config.get("enable_monitoring", True):
            self.config["enable_monitoring"] = False
            save_config(self.config)
        self._show_status("status.monitor.paused", 3000)
        self._update_actions()

    def closeEvent(self, event):
        if self._quit_requested or not self._tray_icon or not self._tray_icon.isVisible():
            self.stop_monitoring()
            if self._tray_icon:
                self._tray_icon.hide()
            event.accept()
            super().closeEvent(event)
            return

        event.ignore()
        self.hide()
        print("[调试] 窗口已隐藏到系统托盘")
        if QSystemTrayIcon.supportsMessages():
            self._tray_icon.showMessage(
                "ClipGuard",
                self._tr("app.tray.minimized"),
                QSystemTrayIcon.MessageIcon.Information,
                3000,
            )

    def _refresh_history(self):
        self._active_record = None
        self._all_records = self._load_initial_records()
        self._apply_filters()
        self._show_status("status.history.refreshed", 2000)

    def _open_settings(self):
        dialog = SettingsDialog(self.config, translator=self.translator, parent=self)
        if dialog.exec() == QDialog.Accepted:
            new_config = dialog.export_config()
            previous_language = self.config.get("language", self.translator.language())
            self.config.update(new_config)
            save_config(self.config)
            self.worker.update_interval(self.config.get("poll_interval", 0.8))
            self.worker.reset_last_seen()
            should_monitor = self.config.get("enable_monitoring", True)
            if should_monitor and not self._monitoring:
                self.start_monitoring()
            elif not should_monitor and self._monitoring:
                self.stop_monitoring()
            new_language = self.config.get("language", previous_language)
            if new_language != self.translator.language():
                self._apply_language(new_language)
            else:
                self._apply_detail_translations()
            self._show_status("status.settings.saved", 3000)

    def _show_record(self, record):
        if not record:
            self._active_record = None
            self.clipboard_list.update_selection_info(0)
            self.detail_timestamp.setText(self._tr("detail.time", value="--:--:--"))
            self.detail_source.setText(self._tr("detail.source", value="--"))
            self.detail_category.setText(self._tr("detail.category", value="--"))
            self.detail_sensitive.setText(self._tr("detail.sensitive", value="--"))
            self._masked_original_text = ""
            self._raw_original_text = ""
            self._masked_formatted = False
            self._raw_formatted = False
            self._update_masked_display()
            self._update_raw_display()
            return

        self._active_record = record
        self.detail_timestamp.setText(self._tr("detail.time", value=record.get("timestamp_full", "--")))
        source_app = record.get("app") or "Unknown"
        self.detail_source.setText(self._tr("detail.source", value=source_app))
        category = record.get("category", "--") or "--"
        self.detail_category.setText(self._tr("detail.category", value=category))
        types = record.get("types_display") or "--"
        self.detail_sensitive.setText(self._tr("detail.sensitive", value=types if types else "--"))
        self._masked_original_text = record.get("masked", "") or ""
        self._raw_original_text = record.get("raw", "") or ""
        self._masked_formatted = False
        self._raw_formatted = False
        self._update_masked_display()
        self._update_raw_display()

    def _on_record_ready(self, payload):
        record = self._prepare_record(payload)
        self._all_records.insert(0, record)
        self._active_record = record
        self._apply_filters()
        self._show_status("status.record.new", 2000)

    def _on_worker_error(self, message):
        self._show_status("status.worker.error", 5000, message=message)

    def _update_actions(self):
        if hasattr(self, "topbar"):
            self.topbar.set_monitoring(self._monitoring)

    def _setup_tray_icon(self):
        if not QSystemTrayIcon.isSystemTrayAvailable():
            print("[警告] 当前系统未检测到托盘支持，关闭窗口将结束程序。")
            return

        icon = self._tray_qicon if not self._tray_qicon.isNull() else self.windowIcon()
        if icon.isNull():
            icon = self._app_icon
        if icon.isNull():
            icon = self.style().standardIcon(QStyle.SP_DesktopIcon)

        tray = QSystemTrayIcon(icon, self)
        menu = QMenu(self)
        restore_action = menu.addAction("")
        restore_action.triggered.connect(self._restore_from_tray)
        menu.addSeparator()
        quit_action = menu.addAction("")
        quit_action.triggered.connect(self._quit_from_tray)
        self._tray_icon = tray
        self._tray_menu = menu
        self._update_tray_translations()
        tray.setContextMenu(menu)
        tray.activated.connect(self._on_tray_activated)
        tray.show()

    def _restore_from_tray(self):
        if self.isHidden():
            self.show()
        self.setWindowState(self.windowState() & ~Qt.WindowMinimized)
        self.activateWindow()
        if self._tray_icon and self._tray_icon.isVisible():
            self._tray_icon.setToolTip(self._tr("app.tray.tooltip"))

    def _quit_from_tray(self):
        self._quit_requested = True
        if self._tray_icon:
            self._tray_icon.hide()
        self.close()
        app = QApplication.instance()
        if app is not None:
            app.quit()

    def _on_tray_activated(self, reason):
        if reason in (QSystemTrayIcon.Trigger, QSystemTrayIcon.DoubleClick):
            self._restore_from_tray()

    def _prepare_record(self, base):
        record = dict(base)
        masked = record.get("masked") or record.get("masked_content") or ""
        record["masked"] = masked
        record["masked_preview"] = masked[:200]
        types = record.get("types", [])
        if isinstance(types, str):
            types = [t for t in types.split(",") if t]
        record["types"] = types
        record["types_display"] = ", ".join(types)
        timestamp = record.get("timestamp") or ""
        record["timestamp"] = timestamp
        record["timestamp_full"] = timestamp
        record["timestamp_display"] = self._fmt_time_short(timestamp)
        record["app"] = record.get("app") or "Unknown"
        record["has_sensitive"] = bool(record.get("has_sensitive"))
        record.setdefault("raw", "")
        record["category"] = record.get("category") or "Text"
        record["category"] = record["category"]
        record["is_favorite"] = bool(record.get("is_favorite"))
        record["is_deleted"] = bool(record.get("is_deleted"))
        return record

    def _apply_language(self, language_code: str, initial: bool = False):
        self.translator.set_language(language_code)
        self.setWindowTitle(self._tr("app.window_title"))
        self.topbar.set_translator(self.translator)
        self.sidebar.set_translator(self.translator)
        self.clipboard_list.set_translator(self.translator)
        self.model.set_translator(self.translator)
        self._apply_detail_translations()
        self._update_sidebar_counts()
        self._update_actions()
        self._update_tray_translations()
        if self._active_record:
            self._show_record(self._active_record)
        else:
            self._show_record(None)
        if initial and not self._monitoring:
            self._show_status("status.monitor.paused", 3000)

    def _apply_detail_translations(self):
        self.detail_group.setTitle(self._tr("detail.group_title"))
        self.detail_masked_label.setText(self._tr("detail.masked_label"))
        self.detail_raw_label.setText(self._tr("detail.raw_label"))
        self.copy_masked_button.setText(self._tr("action.copy"))
        self.copy_raw_button.setText(self._tr("action.copy"))
        self.masked_edit.setPlaceholderText(self._tr("detail.masked_placeholder"))
        placeholder_raw = (
            self._tr("detail.raw_placeholder_enabled")
            if self.config.get("save_raw_content")
            else self._tr("detail.raw_placeholder_disabled")
        )
        self.raw_edit.setPlaceholderText(placeholder_raw)
        self._update_format_button_state("masked")
        self._update_format_button_state("raw")

    def _update_masked_display(self):
        text = self._masked_original_text or ""
        display = text
        if self._masked_formatted and text:
            formatted = self._format_text(text)
            if formatted is None:
                self._masked_formatted = False
                self._show_status("status.format.failed", 2000)
                display = text
            else:
                display = formatted
        self.masked_edit.blockSignals(True)
        self.masked_edit.setPlainText(display)
        if not display:
            self.masked_edit.clear()
            self.masked_edit.setPlaceholderText(self._tr("detail.masked_placeholder"))
        self.masked_edit.blockSignals(False)
        self.copy_masked_button.setEnabled(bool(display))
        self.format_masked_button.setEnabled(bool(text))
        self._update_format_button_state("masked")

    def _update_raw_display(self):
        text = self._raw_original_text or ""
        display = text
        if self._raw_formatted and text:
            formatted = self._format_text(text)
            if formatted is None:
                self._raw_formatted = False
                self._show_status("status.format.failed", 2000)
                display = text
            else:
                display = formatted
        self.raw_edit.blockSignals(True)
        self.raw_edit.setPlainText(display)
        if not display:
            self.raw_edit.clear()
        placeholder_raw = (
            self._tr("detail.raw_placeholder_enabled")
            if self.config.get("save_raw_content")
            else self._tr("detail.raw_placeholder_disabled")
        )
        self.raw_edit.setPlaceholderText(placeholder_raw)
        self.raw_edit.blockSignals(False)
        self.copy_raw_button.setEnabled(bool(display))
        self.format_raw_button.setEnabled(bool(text))
        self._update_format_button_state("raw")

    def _update_format_button_state(self, target: str):
        if target == "masked":
            button = self.format_masked_button
            formatted = self._masked_formatted
        else:
            button = self.format_raw_button
            formatted = self._raw_formatted
        text_key = "action.unformat" if formatted else "action.format"
        button.setText(self._tr(text_key))

    def _toggle_masked_format(self):
        if not self._masked_original_text:
            return
        self._masked_formatted = not self._masked_formatted
        self._update_masked_display()

    def _toggle_raw_format(self):
        if not self._raw_original_text:
            return
        self._raw_formatted = not self._raw_formatted
        self._update_raw_display()

    def _format_text(self, text: str) -> str | None:
        if not text:
            return None
        try:
            parsed = json.loads(text)
            return json.dumps(parsed, ensure_ascii=False, indent=2)
        except (TypeError, ValueError):
            pass
        return self._format_code_like(text)

    @staticmethod
    def _format_code_like(text: str) -> str | None:
        lines = text.splitlines()
        if len(lines) <= 1:
            return None
        indent = 0
        formatted_lines = []
        for line in lines:
            raw = line.rstrip()
            stripped = raw.strip()
            if not stripped:
                formatted_lines.append("")
                continue
            if stripped[0] in "})]":
                indent = max(indent - 1, 0)
            formatted_lines.append("    " * indent + stripped)
            delta = (
                stripped.count("{")
                + stripped.count("(")
                + stripped.count("[")
                - stripped.count("}")
                - stripped.count(")")
                - stripped.count("]")
            )
            if stripped.endswith(":") and not stripped.endswith("?:"):
                delta = max(delta, 1)
            indent = max(indent + delta, 0)
        candidate = "\n".join(formatted_lines)
        return candidate if candidate != text else None

    def _update_tray_translations(self):
        if self._tray_icon:
            self._tray_icon.setToolTip(self._tr("app.tray.tooltip"))
        if not self._tray_menu:
            return
        actions = [action for action in self._tray_menu.actions() if not action.isSeparator()]
        if actions:
            actions[0].setText(self._tr("app.tray.menu.open"))
        if len(actions) > 1:
            actions[-1].setText(self._tr("app.tray.menu.quit"))

    def _tr(self, key: str, **kwargs) -> str:
        return self.translator.tr(key, **kwargs)

    def _show_status(self, key: str, duration: int = 2000, **kwargs):
        self.statusBar().showMessage(self._tr(key, **kwargs), duration)

    @staticmethod
    def _fmt_time_short(timestamp):
        if not timestamp:
            return "--:--:--"
        try:
            dt = datetime.fromisoformat(timestamp)
            return dt.strftime("%H:%M:%S")
        except ValueError:
            return timestamp

def run_app():
    app = QApplication.instance() or QApplication([])
    window = ClipGuardWindow()
    window.show()
    return app.exec()
