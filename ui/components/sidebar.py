from pathlib import Path

from PySide6.QtCore import Qt, Signal, QSize, QRectF, QPointF
from PySide6.QtGui import QColor, QFont, QIcon, QPainter, QPixmap, QPen
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import (
    QFrame,
    QLabel,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from ui.i18n import Translator


class SidebarWidget(QWidget):
    """侧边导航栏骨架，实现分区布局和信号声明，后续再接入真实数据。"""

    navigateRequested = Signal(str)
    contentFilterRequested = Signal(str)
    appFilterRequested = Signal(str)
    searchTextChanged = Signal(str)
    settingsRequested = Signal()

    def __init__(self, translator: Translator, parent=None):
        super().__init__(parent)
        self._translator = translator
        self.setObjectName("sidebar")
        self._nav_buttons = {}
        self._nav_label_keys = {}
        self._type_buttons = {}
        self._type_label_keys = {}
        self._app_buttons = {}
        self._app_label_keys = {}
        self._nav_counts = {}
        self._type_counts = {}
        self._app_counts = {}
        self._section_labels = []
        self._collapsed = False
        self._icon_cache = {}
        self._icon_dir = Path(__file__).resolve().parent.parent.parent / "assets" / "icons"
        self._button_layouts = {}
        self._title_label = None
        self._subtitle_label = None
        self._title_text = ""
        self._subtitle_text = ""
        self._search_container = None
        self.search_edit = None
        self._nav_icon_color = "#1d4ed8"
        self._nav_icon_map = {
            "/": self._load_icon_from_file("首页.svg", self._nav_icon_color),
            "/recent": self._load_icon_from_file("最近.svg", self._nav_icon_color),
            "/favorites": self._load_icon_from_file("收藏.svg", self._nav_icon_color),
            "/trash": self._load_icon_from_file("回收站.svg", self._nav_icon_color),
        }
        self._type_icon_map = {
            "type:text": self._make_chip_icon("T", "#1d4ed8", "#e0e7ff"),
            "type:image": self._make_chip_icon("图", "#0f766e", "#d1fae5"),
            "type:url": self._make_chip_icon("URL", "#b45309", "#fef3c7"),
            "type:code": self._make_chip_icon("{ }", "#7c3aed", "#ede9fe"),
        }
        self._app_icon_map = {}
        self._app_palette = [
            ("#2563eb", "#dbeafe"),
            ("#047857", "#d1fae5"),
            ("#b45309", "#fef3c7"),
            ("#7c3aed", "#ede9fe"),
            ("#db2777", "#fce7f3"),
            ("#0ea5e9", "#cffafe"),
        ]
        self._app_filter_names = []
        self._settings_icon = self._make_gear_icon("#ffffff")
        self._build_ui()
        self._update_button_layouts()
        self._refresh_button_texts()
        self._apply_translations()

    def _build_ui(self):
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        root_layout.addSpacing(16)

        scroll = QScrollArea(self)
        scroll.setObjectName("sidebarScroll")
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.viewport().setObjectName("sidebarScrollViewport")

        scroll_content = QWidget(scroll)
        scroll_content.setObjectName("sidebarScrollContent")
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(16, 0, 16, 16)
        scroll_layout.setSpacing(16)

        self._nav_section = self._build_button_section(
            "sidebar.section.navigation",
            [
                ("sidebar.nav.home", "/"),
                ("sidebar.nav.recent", "/recent"),
                ("sidebar.nav.favorites", "/favorites"),
                ("sidebar.nav.trash", "/trash"),
            ],
            self.navigateRequested,
            "nav",
        )
        scroll_layout.addWidget(self._nav_section)

        self._type_section = self._build_button_section(
            "sidebar.section.types",
            [
                ("sidebar.filter.text", "type:text"),
                ("sidebar.filter.image", "type:image"),
                ("sidebar.filter.url", "type:url"),
                ("sidebar.filter.code", "type:code"),
            ],
            self.contentFilterRequested,
            "filter",
        )
        scroll_layout.addWidget(self._type_section)

        self._app_section = self._build_button_section(
            "sidebar.section.apps",
            [],
            self.appFilterRequested,
            "filter",
        )
        scroll_layout.addWidget(self._app_section)
        scroll_layout.addStretch(1)

        scroll.setWidget(scroll_content)
        root_layout.addWidget(scroll, 1)

        footer = QWidget(self)
        footer.setObjectName("sidebarFooter")
        footer_layout = QVBoxLayout(footer)
        footer_layout.setContentsMargins(16, 12, 16, 16)
        footer_layout.setSpacing(8)

        settings_btn = QPushButton("", footer)
        settings_btn.setProperty("role", "footer")
        settings_btn.clicked.connect(self.settingsRequested)
        settings_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        settings_btn.setCursor(Qt.PointingHandCursor)
        settings_btn.setIcon(self._settings_icon)
        settings_btn.setIconSize(QSize(18, 18))

        footer_layout.addWidget(settings_btn)
        root_layout.addWidget(footer, 0)

    def _build_button_section(self, title_key, items, signal, role):
        section = QWidget(self)
        section.setProperty("sectionRole", role)
        layout = QVBoxLayout(section)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        label = QLabel(self._tr(title_key), section)
        label.setObjectName("sidebarSectionTitle")
        layout.addWidget(label)
        label.setProperty("textKey", title_key)
        self._section_labels.append(label)

        for text_key, payload in items:
            display_text = self._tr(text_key) if not text_key.startswith("app:") else text_key.split(":", 1)[1]
            btn = QPushButton(display_text, section)
            btn.setProperty("payload", payload)
            btn.setProperty("role", role)
            btn.setProperty("active", "false")
            btn.setCursor(Qt.PointingHandCursor)
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            btn.setProperty("textKey", text_key)
            label_text = display_text
            self._apply_icon(btn, payload, label_text)
            btn.clicked.connect(lambda checked=False, value=payload: signal.emit(value))
            layout.addWidget(btn)
            self._register_button(role, payload, btn, text_key, layout)

        return section

    def set_app_filter_items(self, app_names):
        normalized = []
        seen = set()
        for name in app_names:
            label = (name or "Unknown").strip()
            if not label:
                label = "Unknown"
            if label in seen:
                continue
            normalized.append(label)
            seen.add(label)

        if normalized == self._app_filter_names:
            return

        self._app_filter_names = normalized

        layout = self._app_section.layout()
        for payload, button in list(self._app_buttons.items()):
            layout.removeWidget(button)
            button.deleteLater()
            self._button_layouts.pop(button, None)
        self._app_buttons.clear()
        self._app_label_keys.clear()

        new_counts = {}
        for name in normalized:
            payload = f"app:{name}"
            btn = QPushButton(name, self._app_section)
            btn.setProperty("payload", payload)
            btn.setProperty("role", "filter")
            btn.setProperty("active", "false")
            btn.setCursor(Qt.PointingHandCursor)
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            label_key = f"app:{name}"
            btn.setProperty("textKey", label_key)
            self._apply_icon(btn, payload, name)
            btn.clicked.connect(lambda checked=False, value=payload: self.appFilterRequested.emit(value))
            layout.addWidget(btn)
            self._register_button("filter", payload, btn, label_key, layout)
            new_counts[payload] = self._app_counts.get(payload)

        self._app_counts = new_counts
        self._update_button_layouts()
        self._refresh_button_texts()

    def _register_button(self, role, payload, button, label_key, layout):
        self._button_layouts[button] = layout
        if role == "nav":
            self._nav_buttons[payload] = button
            self._nav_label_keys[payload] = label_key
        elif role == "filter":
            if payload.startswith("type:"):
                self._type_buttons[payload] = button
                self._type_label_keys[payload] = label_key
            elif payload.startswith("app:"):
                self._app_buttons[payload] = button
                self._app_label_keys[payload] = label_key

    def _refresh_button(self, button):
        button.style().unpolish(button)
        button.style().polish(button)

    def set_active_route(self, route: str):
        for key, btn in self._nav_buttons.items():
            btn.setProperty("active", "true" if key == route else "false")
            self._refresh_button(btn)

    def set_active_filters(self, type_filter=None, app_filter=None):
        active_type_key = f"type:{type_filter}" if type_filter else None
        active_app_key = f"app:{app_filter}" if app_filter else None
        for key, btn in self._type_buttons.items():
            btn.setProperty("active", "true" if key == active_type_key else "false")
            self._refresh_button(btn)
        for key, btn in self._app_buttons.items():
            btn.setProperty("active", "true" if key == active_app_key else "false")
            self._refresh_button(btn)

    def update_counts(self, nav_counts=None, type_counts=None, app_counts=None):
        if nav_counts is not None:
            self._nav_counts = dict(nav_counts)
        if type_counts is not None:
            self._type_counts = dict(type_counts)
        if app_counts is not None:
            self._app_counts = dict(app_counts)
        self._refresh_button_texts()

    def set_search_text(self, text: str):
        if not self.search_edit:
            return
        if self.search_edit.text() == text:
            return
        self.search_edit.blockSignals(True)
        self.search_edit.setText(text)
        self.search_edit.blockSignals(False)

    def reset_search(self):
        if self.search_edit:
            self.search_edit.clear()

    def nav_routes(self):
        return list(self._nav_buttons.keys())

    def type_filters(self):
        return list(self._type_buttons.keys())

    def app_filters(self):
        return list(self._app_buttons.keys())

    def resizeEvent(self, event):
        super().resizeEvent(event)
        collapsed = self.width() <= 120
        if collapsed != self._collapsed:
            self._collapsed = collapsed
            self._apply_collapse_state()
            self._refresh_button_texts()

    def _apply_icon(self, button: QPushButton, payload: str, label: str):
        icon = self._resolve_icon(payload)
        if icon is not None:
            button.setIcon(icon)
            button.setIconSize(QSize(24, 24))
        button.setToolTip(label)

    def _load_icon_from_file(self, filename: str, color: str | None = None) -> QIcon | None:
        if not filename:
            return None
        path = self._icon_dir / filename
        if not path.exists():
            return None
        cache_key = (str(path), color or "")
        icon = self._icon_cache.get(cache_key)
        if icon is None:
            renderer = QSvgRenderer(str(path))
            if not renderer.isValid():
                return None
            target_size = QSize(24, 24)
            glyph = QPixmap(target_size)
            glyph.fill(Qt.transparent)
            glyph_painter = QPainter(glyph)
            glyph_painter.setRenderHint(QPainter.Antialiasing)
            inset = 5
            renderer.render(glyph_painter, QRectF(inset, inset, target_size.width() - inset * 2, target_size.height() - inset * 2))
            if color:
                glyph_painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
                glyph_painter.fillRect(glyph.rect(), QColor(color))
            glyph_painter.end()

            pixmap = QPixmap(target_size)
            pixmap.fill(Qt.transparent)
            painter = QPainter(pixmap)
            painter.setRenderHint(QPainter.Antialiasing)
            painter.setPen(Qt.NoPen)
            painter.setBrush(QColor("#e0e8ff"))
            radius = 9
            painter.drawRoundedRect(QRectF(0, 0, target_size.width(), target_size.height()), radius, radius)
            painter.drawPixmap(0, 0, glyph)
            painter.end()
            icon = QIcon(pixmap)
            self._icon_cache[cache_key] = icon
        return icon

    def _make_chip_icon(self, text: str, foreground: str, background: str) -> QIcon:
        cache_key = ("chip", text, foreground, background)
        cached = self._icon_cache.get(cache_key)
        if cached:
            return cached
        size = 24
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(background))
        painter.drawRoundedRect(QRectF(0, 0, size, size), 8, 8)
        painter.setPen(QPen(QColor(foreground)))
        font = QFont(painter.font())
        font.setPointSize(10)
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(pixmap.rect(), Qt.AlignCenter, text)
        painter.end()
        icon = QIcon(pixmap)
        self._icon_cache[cache_key] = icon
        return icon

    def _make_gear_icon(self, foreground: str) -> QIcon:
        cache_key = ("gear", foreground)
        cached = self._icon_cache.get(cache_key)
        if cached:
            return cached
        size = 22
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        center = QPointF(size / 2, size / 2)
        outer_radius = size / 2 - 4
        inner_radius = outer_radius - 3
        tooth_length = 2.5
        painter.setPen(QPen(QColor(foreground), 2))
        painter.setBrush(Qt.NoBrush)
        painter.drawEllipse(center, outer_radius, outer_radius)
        for angle in range(0, 360, 45):
            painter.save()
            painter.translate(center)
            painter.rotate(angle)
            painter.drawLine(0, -outer_radius, 0, -outer_radius - tooth_length)
            painter.restore()
        painter.drawEllipse(center, inner_radius, inner_radius)
        painter.end()
        icon = QIcon(pixmap)
        self._icon_cache[cache_key] = icon
        return icon

    def _resolve_icon(self, payload: str) -> QIcon | None:
        if payload in self._nav_icon_map:
            return self._nav_icon_map[payload]
        if payload in self._type_icon_map:
            return self._type_icon_map[payload]
        if payload.startswith("app:"):
            name = payload.split(":", 1)[1]
            return self._icon_for_app(name)
        return None

    def _icon_for_app(self, name: str) -> QIcon:
        payload = f"app:{name}"
        icon = self._app_icon_map.get(payload)
        if icon is None:
            foreground, background = self._color_for_app(name)
            text = self._app_icon_text(name)
            icon = self._make_chip_icon(text, foreground, background)
            self._app_icon_map[payload] = icon
        return icon

    def _app_icon_text(self, name: str) -> str:
        if not name:
            return "?"
        trimmed = name.strip()
        if not trimmed:
            return "?"
        alnum = "".join(ch for ch in trimmed if ch.isalnum())
        if alnum:
            return alnum[:2].upper()
        return trimmed[:2]

    def _color_for_app(self, name: str) -> tuple[str, str]:
        if not self._app_palette:
            return "#1f2937", "#e5e7eb"
        total = sum(ord(ch) for ch in name)
        index = total % len(self._app_palette)
        return self._app_palette[index]

    def _refresh_button_texts(self):
        for key, btn in self._nav_buttons.items():
            base_key = self._nav_label_keys.get(key, "")
            count = self._nav_counts.get(key)
            self._apply_button_text(btn, base_key, count, key)
        for key, btn in self._type_buttons.items():
            base_key = self._type_label_keys.get(key, "")
            count = self._type_counts.get(key)
            self._apply_button_text(btn, base_key, count, key)
        for key, btn in self._app_buttons.items():
            base_key = self._app_label_keys.get(key, "")
            count = self._app_counts.get(key)
            self._apply_button_text(btn, base_key, count, key)

    def _apply_button_text(self, button: QPushButton, base_key: str, count, payload: str):
        if base_key and not base_key.startswith("app:"):
            base = self._tr(base_key)
        elif base_key and base_key.startswith("app:"):
            base = base_key.split(":", 1)[1]
        else:
            base = ""
        tooltip_base = base
        tooltip = f"{tooltip_base} ({count})" if isinstance(count, int) else tooltip_base
        button.setToolTip(tooltip)

        if self._collapsed:
            if self._resolve_icon(payload) is not None:
                button.setProperty("compact", "true")
                button.setText("")
            else:
                button.setProperty("compact", "true")
                button.setText(base[:1] if base else "")
        else:
            button.setProperty("compact", "false")
            display = base
            if isinstance(count, int):
                display = f"{display} ({count})"
            button.setText(display)
        self._refresh_button(button)

    def _apply_collapse_state(self):
        if self._search_container is not None:
            self._search_container.setVisible(not self._collapsed)
        if self._subtitle_label is not None:
            self._subtitle_label.setVisible(not self._collapsed)
        if self._title_label is not None:
            if self._collapsed:
                home_icon = self._nav_icon_map.get("/")
                pixmap = QPixmap()
                if home_icon:
                    pixmap = home_icon.pixmap(QSize(28, 28))
                self._title_label.setPixmap(pixmap)
                self._title_label.setText("")
            else:
                self._title_label.setPixmap(QPixmap())
                self._title_label.setText(self._title_text)
        for label in self._section_labels:
            label.setVisible(not self._collapsed)
        self._update_button_layouts()

    def _update_button_layouts(self):
        for button, layout in self._button_layouts.items():
            if self._collapsed:
                button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
                button.setMinimumSize(38, 38)
                button.setMaximumSize(38, 38)
                layout.setAlignment(button, Qt.AlignHCenter)
            else:
                button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
                button.setMinimumSize(0, 0)
                button.setMaximumSize(16777215, 16777215)
                layout.setAlignment(button, Qt.AlignLeft | Qt.AlignVCenter)
            self._refresh_button(button)

    def set_translator(self, translator: Translator):
        self._translator = translator
        self._apply_translations()

    def _tr(self, key: str, **kwargs) -> str:
        return self._translator.tr(key, **kwargs)

    def _apply_translations(self):
        for label in self._section_labels:
            key = label.property("textKey")
            if key:
                label.setText(self._tr(key))
        for key, btn in self._nav_buttons.items():
            text_key = self._nav_label_keys.get(key, "")
            if text_key:
                btn.setProperty("textKey", text_key)
        for key, btn in self._type_buttons.items():
            text_key = self._type_label_keys.get(key, "")
            btn.setProperty("textKey", text_key)
        for key, btn in self._app_buttons.items():
            text_key = self._app_label_keys.get(key, "")
            btn.setProperty("textKey", text_key)
        self._refresh_button_texts()
        # 更新底部按钮文字
        footer = self.findChild(QWidget, "sidebarFooter")
        if footer:
            button = footer.findChild(QPushButton)
            if button:
                button.setText(self._tr("sidebar.footer.settings"))
