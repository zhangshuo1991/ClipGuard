from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QWidget,
)

from ui.i18n import Translator


class TopBarWidget(QWidget):
    """顶部工具栏骨架，包含状态显示、操作按钮与搜索框。"""

    startMonitorRequested = Signal()
    stopMonitorRequested = Signal()
    refreshRequested = Signal()
    settingsRequested = Signal()
    searchTextChanged = Signal(str)

    def __init__(self, translator: Translator, parent=None):
        super().__init__(parent)
        self._translator = translator
        self.setObjectName("topbar")
        self._monitoring = True
        self._build_ui()
        self._apply_translations()

    def _build_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(16)

        status_container = QWidget(self)
        status_layout = QHBoxLayout(status_container)
        status_layout.setContentsMargins(0, 0, 0, 0)
        status_layout.setSpacing(8)

        self.status_indicator = QLabel("\u25CF", status_container)
        self.status_indicator.setObjectName("topbarStatusDot")
        self.status_label = QLabel("", status_container)
        status_layout.addWidget(self.status_indicator)
        status_layout.addWidget(self.status_label)

        self.toggle_button = QPushButton("", status_container)
        self.toggle_button.setProperty("role", "monitorToggle")
        self.toggle_button.setCursor(Qt.PointingHandCursor)
        self.toggle_button.clicked.connect(self._toggle_monitoring)
        status_layout.addWidget(self.toggle_button)
        layout.addWidget(status_container, 0, Qt.AlignLeft)

        actions_container = QWidget(self)
        actions_layout = QHBoxLayout(actions_container)
        actions_layout.setContentsMargins(0, 0, 0, 0)
        actions_layout.setSpacing(8)

        self.refresh_button = QPushButton("", actions_container)
        self.refresh_button.setProperty("role", "secondary")
        self.refresh_button.setCursor(Qt.PointingHandCursor)
        self.refresh_button.clicked.connect(self.refreshRequested)
        actions_layout.addWidget(self.refresh_button)

        layout.addWidget(actions_container, 0, Qt.AlignLeft)

        search_edit = QLineEdit(self)
        search_edit.setObjectName("topbarSearch")
        search_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        search_edit.textChanged.connect(self.searchTextChanged)
        layout.addWidget(search_edit, 1)
        self.search_edit = search_edit

        trailing_container = QWidget(self)
        trailing_layout = QHBoxLayout(trailing_container)
        trailing_layout.setContentsMargins(0, 0, 0, 0)
        trailing_layout.setSpacing(8)

        self.settings_button = QPushButton("", trailing_container)
        self.settings_button.setProperty("role", "iconOnly")
        self.settings_button.setCursor(Qt.PointingHandCursor)
        self.settings_button.clicked.connect(self.settingsRequested)

        trailing_layout.addWidget(self.settings_button)
        layout.addWidget(trailing_container, 0, Qt.AlignRight)

    def set_monitoring(self, monitoring: bool):
        self._monitoring = monitoring
        self.status_label.setText(
            self._tr("topbar.status.monitoring" if monitoring else "topbar.status.paused")
        )
        self.status_indicator.setProperty("status", "on" if monitoring else "off")
        self.status_indicator.style().unpolish(self.status_indicator)
        self.status_indicator.style().polish(self.status_indicator)
        self.toggle_button.setText(
            self._tr("topbar.toggle.pause" if monitoring else "topbar.toggle.resume")
        )
        self.toggle_button.style().unpolish(self.toggle_button)
        self.toggle_button.style().polish(self.toggle_button)

    def _toggle_monitoring(self):
        if self._monitoring:
            self.stopMonitorRequested.emit()
        else:
            self.startMonitorRequested.emit()

    def set_search_text(self, text: str):
        if self.search_edit.text() == text:
            return
        self.search_edit.blockSignals(True)
        self.search_edit.setText(text)
        self.search_edit.blockSignals(False)

    def set_translator(self, translator: Translator):
        self._translator = translator
        self._apply_translations()

    def _tr(self, key: str, **kwargs) -> str:
        return self._translator.tr(key, **kwargs)

    def _apply_translations(self):
        self.status_label.setText(
            self._tr("topbar.status.monitoring" if self._monitoring else "topbar.status.paused")
        )
        self.toggle_button.setText(
            self._tr("topbar.toggle.pause" if self._monitoring else "topbar.toggle.resume")
        )
        self.refresh_button.setText(self._tr("topbar.refresh"))
        self.search_edit.setPlaceholderText(self._tr("topbar.search.placeholder"))
        self.settings_button.setText(self._tr("topbar.settings"))
        # 刷新样式以防止属性未更新
        self.status_indicator.style().unpolish(self.status_indicator)
        self.status_indicator.style().polish(self.status_indicator)
        self.toggle_button.style().unpolish(self.toggle_button)
        self.toggle_button.style().polish(self.toggle_button)
