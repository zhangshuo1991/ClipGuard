from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QStackedWidget,
    QTableView,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from ui.i18n import Translator


class ClipboardCard(QFrame):
    """单个剪贴板卡片，承载显示与交互信号。"""

    clicked = Signal(int)
    copyRequested = Signal(dict)
    deleteRequested = Signal(dict)
    favoriteToggled = Signal(dict, bool)
    restoreRequested = Signal(dict)

    def __init__(self, row: int, record: dict, translator: Translator, parent=None):
        super().__init__(parent)
        self.setObjectName("clipboardCard")
        self.setFrameShape(QFrame.NoFrame)
        self.setProperty("selected", False)
        self.row = row
        self.record = record
        self._translator = translator
        self._is_favorite = bool(record.get("is_favorite"))
        self._is_deleted = bool(record.get("is_deleted"))
        self._favorite_button = None
        self._copy_button = None
        self._delete_button = None
        self._restore_button = None
        self._build_ui()
        self._apply_translations()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        header = QWidget(self)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(8)

        category = QLabel(self.record.get("category", ""))
        category.setObjectName("cardCategory")
        header_layout.addWidget(category, 0, Qt.AlignLeft)

        types_display = ", ".join(self.record.get("types", [])) or self.record.get("types_display", "")
        if types_display:
            types_label = QLabel(types_display)
            types_label.setObjectName("cardTags")
            header_layout.addWidget(types_label, 0, Qt.AlignLeft)

        header_layout.addStretch(1)

        self._favorite_button = QToolButton(self)
        self._favorite_button.setObjectName("favoriteButton")
        self._favorite_button.setProperty("role", "favorite")
        self._favorite_button.setCursor(Qt.PointingHandCursor)
        self._favorite_button.setProperty("active", "true" if self._is_favorite else "false")
        self._favorite_button.setText("★" if self._is_favorite else "☆")
        self._favorite_button.clicked.connect(self._toggle_favorite)

        self._copy_button = QToolButton(self)
        self._copy_button.setCursor(Qt.PointingHandCursor)
        self._copy_button.clicked.connect(lambda: self.copyRequested.emit(self.record))

        self._delete_button = QToolButton(self)
        self._delete_button.setCursor(Qt.PointingHandCursor)
        self._delete_button.clicked.connect(lambda: self.deleteRequested.emit(self.record))

        if not self._is_deleted:
            header_layout.addWidget(self._favorite_button)
        else:
            self._restore_button = QToolButton(self)
            self._restore_button.setCursor(Qt.PointingHandCursor)
            self._restore_button.clicked.connect(lambda: self.restoreRequested.emit(self.record))
            header_layout.addWidget(self._restore_button)

        header_layout.addWidget(self._copy_button)
        header_layout.addWidget(self._delete_button)
        layout.addWidget(header)

        preview = QLabel(self.record.get("masked_preview", self.record.get("masked", "")) or "")
        preview.setObjectName("cardContent")
        preview.setWordWrap(True)
        layout.addWidget(preview)

        footer = QWidget(self)
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(0, 0, 0, 0)
        footer_layout.setSpacing(8)

        app = self.record.get("app", "Unknown")
        timestamp = self.record.get("timestamp_display", self.record.get("timestamp", "--"))
        footer_label = QLabel(f"{app} · {timestamp}")
        footer_label.setObjectName("cardMeta")
        footer_layout.addWidget(footer_label, 0, Qt.AlignLeft)

        footer_layout.addStretch(1)
        layout.addWidget(footer)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.row)
        super().mousePressEvent(event)

    def set_selected(self, selected: bool):
        self.setProperty("selected", "true" if selected else "false")
        self.style().unpolish(self)
        self.style().polish(self)

    def _toggle_favorite(self):
        self._is_favorite = not self._is_favorite
        self.record["is_favorite"] = self._is_favorite
        if self._favorite_button:
            self._favorite_button.setText("★" if self._is_favorite else "☆")
            self._favorite_button.setProperty("active", "true" if self._is_favorite else "false")
            self._favorite_button.style().unpolish(self._favorite_button)
            self._favorite_button.style().polish(self._favorite_button)
        self.favoriteToggled.emit(self.record, self._is_favorite)

    def set_translator(self, translator: Translator):
        self._translator = translator
        self._apply_translations()

    def _tr(self, key: str, **kwargs) -> str:
        return self._translator.tr(key, **kwargs)

    def _apply_translations(self):
        if self._copy_button:
            self._copy_button.setText(self._tr("card.copy"))
        if self._delete_button:
            key = "card.delete_permanent" if self._is_deleted else "card.delete"
            self._delete_button.setText(self._tr(key))
        if self._restore_button:
            self._restore_button.setText(self._tr("card.restore"))


class ClipboardCardView(QWidget):
    """支持列表/网格布局的卡片视图容器。"""

    cardClicked = Signal(int)
    cardCopyRequested = Signal(dict)
    cardDeleteRequested = Signal(dict)
    cardFavoriteToggled = Signal(dict, bool)
    cardRestoreRequested = Signal(dict)

    def __init__(self, translator: Translator, parent=None):
        super().__init__(parent)
        self._translator = translator
        self._mode = "list"
        self._cards = []

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.scroll = QScrollArea(self)
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.NoFrame)

        self.container = QWidget(self.scroll)
        self.grid = QGridLayout(self.container)
        self.grid.setContentsMargins(0, 0, 0, 0)
        self.grid.setHorizontalSpacing(16)
        self.grid.setVerticalSpacing(16)
        self.scroll.setWidget(self.container)
        layout.addWidget(self.scroll)

    def set_mode(self, mode: str):
        if mode not in ("list", "grid"):
            return
        if self._mode != mode:
            self._mode = mode
            self._reflow_cards()

    def set_records(self, records):
        for card in self._cards:
            card.setParent(None)
        self._cards = []
        while self.grid.count():
            item = self.grid.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        for row, record in enumerate(records):
            card = ClipboardCard(row, record, self._translator, self.container)
            card.clicked.connect(self.cardClicked)
            card.copyRequested.connect(self.cardCopyRequested)
            card.deleteRequested.connect(self.cardDeleteRequested)
            card.favoriteToggled.connect(self.cardFavoriteToggled)
            card.restoreRequested.connect(self.cardRestoreRequested)
            self._cards.append(card)

        self._reflow_cards()

    def highlight_row(self, row: int):
        for card in self._cards:
            card.set_selected(card.row == row)

    def set_translator(self, translator: Translator):
        self._translator = translator
        for card in self._cards:
            card.set_translator(translator)
        self._reflow_cards()

    def _reflow_cards(self):
        columns = 1 if self._mode == "list" else 2
        for idx, card in enumerate(self._cards):
            r = idx // columns
            c = idx % columns
            self.grid.addWidget(card, r, c)
        self.grid.setColumnStretch(columns, 1)


class ClipboardListWidget(QWidget):
    """内容列表骨架，当前默认使用表格视图，后续逐步替换为卡片视图。"""

    selectionChanged = Signal(dict)
    viewModeChanged = Signal(str)
    deleteSelectedRequested = Signal(dict)
    copyRequested = Signal(dict)
    favoriteToggled = Signal(dict, bool)
    restoreSelectedRequested = Signal(dict)

    def __init__(self, translator: Translator, parent=None):
        super().__init__(parent)
        self.setObjectName("clipboardList")
        self._translator = translator
        self._model = None
        self._selection_model = None
        self._current_mode = "list"
        self._model_connections = []
        self._trash_mode = False
        self._selection_count = 0
        self._title_label = None
        self._subtitle_label = None
        self._build_ui()
        self._apply_translations()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        header = QWidget(self)
        header.setObjectName("clipboardHeader")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(12)

        title_group = QWidget(header)
        title_layout = QVBoxLayout(title_group)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(2)

        self._title_label = QLabel("", title_group)
        self._title_label.setObjectName("clipboardTitle")
        self._subtitle_label = QLabel("", title_group)
        self._subtitle_label.setObjectName("clipboardSubtitle")

        title_layout.addWidget(self._title_label)
        title_layout.addWidget(self._subtitle_label)
        header_layout.addWidget(title_group, 1)

        controls = QWidget(header)
        controls.setObjectName("clipboardControls")
        controls_layout = QHBoxLayout(controls)
        controls_layout.setContentsMargins(0, 0, 0, 0)
        controls_layout.setSpacing(8)

        self.view_mode_button = QPushButton("", controls)
        self.view_mode_button.setProperty("role", "switcher")
        self.view_mode_button.setCursor(Qt.PointingHandCursor)
        self.view_mode_button.clicked.connect(self._toggle_view_mode)
        controls_layout.addWidget(self.view_mode_button)

        self.selection_info = QLabel("", controls)
        controls_layout.addWidget(self.selection_info)

        self.restore_button = QPushButton("", controls)
        self.restore_button.setProperty("role", "secondary")
        self.restore_button.setCursor(Qt.PointingHandCursor)
        self.restore_button.clicked.connect(self._restore_current_selection)
        self.restore_button.setVisible(False)
        controls_layout.addWidget(self.restore_button)

        self.delete_button = QPushButton("", controls)
        self.delete_button.setProperty("role", "danger")
        self.delete_button.setCursor(Qt.PointingHandCursor)
        self.delete_button.clicked.connect(self._delete_current_selection)
        self.delete_button.setVisible(False)
        controls_layout.addWidget(self.delete_button)

        header_layout.addWidget(controls, 0, Qt.AlignRight)
        layout.addWidget(header, 0)

        self._view_stack = QStackedWidget(self)

        table_container = QWidget(self)
        table_layout = QVBoxLayout(table_container)
        table_layout.setContentsMargins(0, 0, 0, 0)
        table_layout.setSpacing(0)

        self.table_view = QTableView(table_container)
        self.table_view.setSelectionBehavior(QTableView.SelectRows)
        self.table_view.setSelectionMode(QTableView.SingleSelection)
        self.table_view.setAlternatingRowColors(True)
        self.table_view.clicked.connect(self._emit_current_selection)
        table_layout.addWidget(self.table_view)
        self._view_stack.addWidget(table_container)

        self.card_view = ClipboardCardView(self._translator, self)
        self.card_view.cardClicked.connect(self._on_card_clicked)
        self.card_view.cardCopyRequested.connect(self.copyRequested)
        self.card_view.cardDeleteRequested.connect(self._on_card_delete)
        self.card_view.cardFavoriteToggled.connect(self.favoriteToggled)
        self.card_view.cardRestoreRequested.connect(self._on_card_restore)
        self._view_stack.addWidget(self.card_view)

        layout.addWidget(self._view_stack, 1)

    def set_model(self, model):
        if self._model:
            for signal, handler in self._model_connections:
                try:
                    signal.disconnect(handler)
                except (TypeError, RuntimeError):
                    pass
            self._model_connections = []

        self._model = model
        if self._selection_model:
            try:
                self._selection_model.currentRowChanged.disconnect(self._handle_current_changed)
            except (TypeError, RuntimeError):
                pass
        self.table_view.setModel(model)
        self._selection_model = self.table_view.selectionModel()
        if self._selection_model:
            self._selection_model.currentRowChanged.connect(self._handle_current_changed)
        if model.rowCount() > 0:
            self.table_view.selectRow(0)
            self.update_selection_info(1)
        else:
            self.update_selection_info(0)
        self._apply_trash_controls()
        self._refresh_cards()
        self._model_connections = [
            (model.modelReset, self._refresh_cards),
            (model.rowsInserted, self._refresh_cards),
            (model.rowsRemoved, self._refresh_cards),
            (model.dataChanged, self._refresh_cards),
        ]
        for signal, handler in self._model_connections:
            signal.connect(handler)

    def select_first_row(self):
        self.select_row(0)

    def select_row(self, row: int):
        if not self._model:
            return
        if row < 0 or row >= self._model.rowCount():
            return
        self.table_view.selectRow(row)
        self.update_selection_info(1)
        self.card_view.highlight_row(row)
        self._emit_current_selection(self.table_view.currentIndex())

    def update_selection_info(self, count: int):
        self._selection_count = count
        self.selection_info.setVisible(count > 0)
        self.selection_info.setText(self._tr("clipboard.selection.count", count=count) if count else "")
        self.delete_button.setVisible(count > 0)
        if self._trash_mode:
            self.restore_button.setVisible(count > 0)
        else:
            self.restore_button.setVisible(False)
        if count == 0:
            self.card_view.highlight_row(-1)

    def _toggle_view_mode(self):
        current_index = self._view_stack.currentIndex()
        new_index = 1 - current_index
        self._view_stack.setCurrentIndex(new_index)
        self._current_mode = "grid" if new_index == 1 else "list"
        self.card_view.set_mode(self._current_mode)
        self._update_view_mode_button_text()
        self.viewModeChanged.emit(self._current_mode)
        if self.table_view.currentIndex().isValid():
            row = self.table_view.currentIndex().row()
            self.card_view.highlight_row(row)

    def _handle_current_changed(self, current, _previous):
        self._emit_current_selection(current)

    def _emit_current_selection(self, index=None):
        if not self._model:
            return
        if index is None:
            index = self.table_view.currentIndex()
        if not index.isValid():
            self.update_selection_info(0)
            return
        record = self._model.record_at(index.row())
        if record:
            self.update_selection_info(1)
            self.selectionChanged.emit(record)
            self.card_view.highlight_row(index.row())

    def _refresh_cards(self, *args):
        if not self._model:
            return
        records = [self._model.record_at(i) for i in range(self._model.rowCount())]
        self.card_view.set_mode(self._current_mode)
        self.card_view.set_records(records)
        if self.table_view.currentIndex().isValid():
            self.card_view.highlight_row(self.table_view.currentIndex().row())

    def _on_card_clicked(self, row: int):
        self.select_row(row)

    def _on_card_delete(self, record: dict):
        self.deleteSelectedRequested.emit(record)

    def _on_card_restore(self, record: dict):
        self.restoreSelectedRequested.emit(record)

    def _apply_trash_controls(self):
        self.restore_button.setVisible(self._trash_mode and self.selection_info.isVisible())

    def set_trash_mode(self, enabled: bool):
        self._trash_mode = enabled
        self._apply_trash_controls()
        self._update_view_mode_button_text()

    def _restore_current_selection(self):
        record = self._current_record()
        if record:
            self.restoreSelectedRequested.emit(record)

    def _delete_current_selection(self):
        record = self._current_record()
        if record:
            self.deleteSelectedRequested.emit(record)

    def _current_record(self):
        if not self._model or not self.table_view.currentIndex().isValid():
            return None
        return self._model.record_at(self.table_view.currentIndex().row())

    def _update_view_mode_button_text(self):
        key = "clipboard.view.grid" if self._current_mode == "grid" else "clipboard.view.list"
        self.view_mode_button.setText(self._tr(key))

    def set_translator(self, translator: Translator):
        self._translator = translator
        self.card_view.set_translator(translator)
        self._apply_translations()
        if self._selection_count:
            self.selection_info.setText(self._tr("clipboard.selection.count", count=self._selection_count))

    def _apply_translations(self):
        self._title_label.setText(self._tr("clipboard.title"))
        self._subtitle_label.setText(self._tr("clipboard.subtitle"))
        self.restore_button.setText(self._tr("clipboard.restore"))
        self.delete_button.setText(self._tr("clipboard.delete"))
        self._update_view_mode_button_text()

    def _tr(self, key: str, **kwargs) -> str:
        return self._translator.tr(key, **kwargs)
