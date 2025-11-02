# ui/settings_dialog.py
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QButtonGroup,
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QGroupBox,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QRadioButton,
    QSpinBox,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from config import DEFAULT_CONFIG
from ui.i18n import Translator


class SettingsDialog(QDialog):
    """多分组设置面板，覆盖监控/存储/隐私/通知/界面/快捷键等配置。"""

    _TABS = [
        ("monitoring", "settings.tabs.monitoring"),
        ("storage", "settings.tabs.storage"),
        ("privacy", "settings.tabs.privacy"),
        ("notifications", "settings.tabs.notifications"),
        ("interface", "settings.tabs.interface"),
        ("shortcuts", "settings.tabs.shortcuts"),
    ]

    def __init__(self, config, translator: Translator, parent=None):
        super().__init__(parent)
        self._translator = translator
        self.setWindowTitle(self._tr("settings.title"))
        self.setObjectName("settingsDialog")
        self.resize(880, 580)
        self._config = DEFAULT_CONFIG.copy()
        if isinstance(config, dict):
            self._config.update({k: config.get(k) for k in DEFAULT_CONFIG})
        self._build_ui()
        self._load_values()

    # region UI 构建
    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        content = QHBoxLayout()
        content.setContentsMargins(0, 0, 0, 0)
        content.setSpacing(12)

        self.nav_list = QListWidget()
        self.nav_list.setObjectName("settingsNav")
        self.nav_list.setSpacing(4)
        self.nav_list.setFixedWidth(180)
        self.nav_list.setSelectionMode(QListWidget.SingleSelection)
        for tab_id, tab_key in self._TABS:
            item = QListWidgetItem(self._tr(tab_key))
            item.setData(Qt.UserRole, tab_id)
            self.nav_list.addItem(item)

        language_selector = QWidget()
        language_layout = QVBoxLayout(language_selector)
        language_layout.setContentsMargins(0, 12, 0, 0)
        language_layout.setSpacing(6)
        language_label = QLabel(self._tr("settings.interface.language"))
        language_label.setObjectName("languageSelectorLabel")
        self.language_combo = QComboBox()
        self.language_combo.setObjectName("languageSelectorCombo")
        self.language_combo.addItem(self._tr("settings.language.zh"), "zh-CN")
        self.language_combo.addItem(self._tr("settings.language.en"), "en-US")
        language_layout.addWidget(language_label)
        language_layout.addWidget(self.language_combo)

        nav_container = QWidget()
        nav_container_layout = QVBoxLayout(nav_container)
        nav_container_layout.setContentsMargins(0, 0, 0, 0)
        nav_container_layout.setSpacing(12)
        nav_container_layout.addWidget(self.nav_list)
        nav_container_layout.addWidget(language_selector)
        nav_container_layout.addStretch(1)

        self.stack = QStackedWidget()
        self.stack.addWidget(self._build_monitoring_page())
        self.stack.addWidget(self._build_storage_page())
        self.stack.addWidget(self._build_privacy_page())
        self.stack.addWidget(self._build_notifications_page())
        self.stack.addWidget(self._build_interface_page())
        self.stack.addWidget(self._build_shortcuts_page())

        self.nav_list.currentRowChanged.connect(self._on_tab_changed)
        self.nav_list.setCurrentRow(0)

        nav_container.setFixedWidth(200)
        content.addWidget(nav_container, 0, Qt.AlignTop)
        content.addWidget(self.stack, 1)
        layout.addLayout(content, 1)

        # 操作按钮（恢复默认）
        toolbar = QHBoxLayout()
        toolbar.setSpacing(8)
        self.reset_button = QPushButton(self._tr("settings.reset"))
        self.reset_button.clicked.connect(self._reset_to_default)
        toolbar.addStretch(1)
        toolbar.addWidget(self.reset_button)
        layout.addLayout(toolbar)

        # 底部确定/取消
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _build_monitoring_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(16)

        base_box = QGroupBox(self._tr("settings.monitoring.section"))
        base_layout = QVBoxLayout(base_box)
        self.enable_monitoring_checkbox = QCheckBox(self._tr("settings.monitoring.enable"))
        self.monitor_images_checkbox = QCheckBox(self._tr("settings.monitoring.images"))
        self.monitor_urls_checkbox = QCheckBox(self._tr("settings.monitoring.urls"))
        self.monitor_code_checkbox = QCheckBox(self._tr("settings.monitoring.code"))
        base_layout.addWidget(self.enable_monitoring_checkbox)
        base_layout.addWidget(self.monitor_images_checkbox)
        base_layout.addWidget(self.monitor_urls_checkbox)
        base_layout.addWidget(self.monitor_code_checkbox)

        interval_box = QGroupBox(self._tr("settings.monitoring.interval_section"))
        interval_layout = QHBoxLayout(interval_box)
        interval_layout.setContentsMargins(12, 12, 12, 12)
        interval_layout.addWidget(QLabel(self._tr("settings.monitoring.interval_label")), 0, Qt.AlignLeft)
        self.poll_interval_spin = QDoubleSpinBox()
        self.poll_interval_spin.setRange(0.2, 5.0)
        self.poll_interval_spin.setSingleStep(0.1)
        self.poll_interval_spin.setDecimals(1)
        self.poll_interval_spin.setSuffix(self._tr("settings.monitoring.interval_suffix"))
        interval_layout.addStretch(1)
        interval_layout.addWidget(self.poll_interval_spin)

        excluded_box = QGroupBox(self._tr("settings.monitoring.excluded.section"))
        excluded_layout = QVBoxLayout(excluded_box)
        excluded_layout.setSpacing(8)
        self.excluded_apps_list = QListWidget()
        excluded_layout.addWidget(self.excluded_apps_list)
        buttons_row = QHBoxLayout()
        buttons_row.setSpacing(8)
        add_btn = QPushButton(self._tr("settings.monitoring.excluded.add"))
        add_btn.clicked.connect(self._add_excluded_app)
        remove_btn = QPushButton(self._tr("settings.monitoring.excluded.remove"))
        remove_btn.clicked.connect(self._remove_selected_app)
        buttons_row.addWidget(add_btn)
        buttons_row.addWidget(remove_btn)
        buttons_row.addStretch(1)
        excluded_layout.addLayout(buttons_row)
        hint = QLabel(self._tr("settings.monitoring.excluded.hint"))
        hint.setWordWrap(True)
        hint.setStyleSheet("color: #64748b; font-size: 12px;")
        excluded_layout.addWidget(hint)

        layout.addWidget(base_box)
        layout.addWidget(interval_box)
        layout.addWidget(excluded_box)
        layout.addStretch(1)
        return page

    def _build_storage_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(16)

        storage_box = QGroupBox(self._tr("settings.storage.section"))
        storage_layout = QVBoxLayout(storage_box)
        max_items_row = QHBoxLayout()
        max_items_row.addWidget(QLabel(self._tr("settings.storage.max_items")))
        self.max_items_spin = QSpinBox()
        self.max_items_spin.setRange(50, 5000)
        self.max_items_spin.setSingleStep(50)
        max_items_row.addStretch(1)
        max_items_row.addWidget(self.max_items_spin)
        storage_layout.addLayout(max_items_row)

        self.auto_cleanup_checkbox = QCheckBox(self._tr("settings.storage.auto_cleanup"))
        self.auto_cleanup_checkbox.toggled.connect(self._toggle_cleanup_inputs)
        storage_layout.addWidget(self.auto_cleanup_checkbox)

        cleanup_row = QHBoxLayout()
        cleanup_row.addWidget(QLabel(self._tr("settings.storage.cleanup_days")))
        self.cleanup_days_spin = QSpinBox()
        self.cleanup_days_spin.setRange(1, 365)
        cleanup_row.addStretch(1)
        cleanup_row.addWidget(self.cleanup_days_spin)
        storage_layout.addLayout(cleanup_row)

        location_box = QGroupBox(self._tr("settings.storage.location.section"))
        location_layout = QVBoxLayout(location_box)
        self.storage_button_group = QButtonGroup(self)
        self.storage_local_radio = QRadioButton(self._tr("settings.storage.location.local"))
        self.storage_cloud_radio = QRadioButton(self._tr("settings.storage.location.cloud"))
        self.storage_button_group.addButton(self.storage_local_radio)
        self.storage_button_group.addButton(self.storage_cloud_radio)
        location_layout.addWidget(self.storage_local_radio)
        location_layout.addWidget(self.storage_cloud_radio)

        layout.addWidget(storage_box)
        layout.addWidget(location_box)
        layout.addStretch(1)
        return page

    def _build_privacy_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(16)

        privacy_box = QGroupBox(self._tr("settings.privacy.section"))
        privacy_layout = QVBoxLayout(privacy_box)
        self.save_raw_checkbox = QCheckBox(self._tr("settings.privacy.save_raw"))
        self.hide_passwords_checkbox = QCheckBox(self._tr("settings.privacy.hide_passwords"))
        self.hide_credit_cards_checkbox = QCheckBox(self._tr("settings.privacy.hide_cards"))
        self.encrypt_data_checkbox = QCheckBox(self._tr("settings.privacy.encrypt"))
        privacy_layout.addWidget(self.save_raw_checkbox)
        privacy_layout.addWidget(self.hide_passwords_checkbox)
        privacy_layout.addWidget(self.hide_credit_cards_checkbox)
        privacy_layout.addWidget(self.encrypt_data_checkbox)

        keywords_box = QGroupBox(self._tr("settings.privacy.keywords"))
        keywords_layout = QVBoxLayout(keywords_box)
        self.keywords_edit = QLineEdit()
        self.keywords_edit.setPlaceholderText(self._tr("settings.privacy.placeholder"))
        clear_btn = QPushButton(self._tr("settings.privacy.clear_keywords"))
        clear_btn.clicked.connect(self._clear_keywords)
        keywords_layout.addWidget(self.keywords_edit)
        keywords_layout.addWidget(clear_btn, alignment=Qt.AlignLeft)

        layout.addWidget(privacy_box)
        layout.addWidget(keywords_box)
        layout.addStretch(1)
        return page

    def _build_notifications_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(16)

        notify_box = QGroupBox(self._tr("settings.notifications.section"))
        notify_layout = QVBoxLayout(notify_box)
        self.show_notifications_checkbox = QCheckBox(self._tr("settings.notifications.show"))
        self.sound_enabled_checkbox = QCheckBox(self._tr("settings.notifications.sound"))
        notify_layout.addWidget(self.show_notifications_checkbox)
        notify_layout.addWidget(self.sound_enabled_checkbox)

        layout.addWidget(notify_box)
        layout.addStretch(1)
        return page

    def _build_interface_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(16)

        appearance_box = QGroupBox(self._tr("settings.interface.section"))
        appearance_layout = QVBoxLayout(appearance_box)
        theme_row = QHBoxLayout()
        theme_row.addWidget(QLabel(self._tr("settings.interface.theme")))
        self.theme_combo = QComboBox()
        self.theme_combo.addItem(self._tr("settings.interface.theme.light"), "light")
        self.theme_combo.addItem(self._tr("settings.interface.theme.dark"), "dark")
        theme_row.addStretch(1)
        theme_row.addWidget(self.theme_combo)
        appearance_layout.addLayout(theme_row)

        self.show_preview_checkbox = QCheckBox(self._tr("settings.interface.preview"))
        self.compact_mode_checkbox = QCheckBox(self._tr("settings.interface.compact"))
        appearance_layout.addWidget(self.show_preview_checkbox)
        appearance_layout.addWidget(self.compact_mode_checkbox)

        layout.addWidget(appearance_box)
        layout.addStretch(1)
        return page

    def _build_shortcuts_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(16)

        shortcuts_box = QGroupBox(self._tr("settings.shortcuts.section"))
        shortcuts_layout = QVBoxLayout(shortcuts_box)

        self.quick_paste_edit = QLineEdit()
        self.show_history_edit = QLineEdit()
        self.clear_all_edit = QLineEdit()

        shortcuts_layout.addLayout(self._form_row(self._tr("settings.shortcuts.quick_paste"), self.quick_paste_edit))
        shortcuts_layout.addLayout(self._form_row(self._tr("settings.shortcuts.history"), self.show_history_edit))
        shortcuts_layout.addLayout(self._form_row(self._tr("settings.shortcuts.clear_all"), self.clear_all_edit))

        hint = QLabel(self._tr("settings.shortcuts.hint"))
        hint.setWordWrap(True)
        hint.setStyleSheet("color: #64748b; font-size: 12px;")
        shortcuts_layout.addWidget(hint)

        layout.addWidget(shortcuts_box)
        layout.addStretch(1)
        return page

    # endregion

    # region 数据读写
    def _load_values(self):
        cfg = DEFAULT_CONFIG.copy()
        cfg.update({k: self._config.get(k, v) for k, v in DEFAULT_CONFIG.items()})
        self._config = cfg

        self.enable_monitoring_checkbox.setChecked(cfg["enable_monitoring"])
        self.monitor_images_checkbox.setChecked(cfg["monitor_images"])
        self.monitor_urls_checkbox.setChecked(cfg["monitor_urls"])
        self.monitor_code_checkbox.setChecked(cfg["monitor_code"])
        self.poll_interval_spin.setValue(float(cfg["poll_interval"]))

        self.excluded_apps_list.clear()
        for app in cfg.get("excluded_apps", []):
            self.excluded_apps_list.addItem(app)

        self.max_items_spin.setValue(int(cfg["max_items"]))
        self.auto_cleanup_checkbox.setChecked(bool(cfg["auto_cleanup"]))
        self.cleanup_days_spin.setValue(int(cfg["cleanup_days"]))
        self._toggle_cleanup_inputs(cfg["auto_cleanup"])

        location = cfg.get("storage_location", "local")
        if location == "cloud":
            self.storage_cloud_radio.setChecked(True)
        else:
            self.storage_local_radio.setChecked(True)

        self.save_raw_checkbox.setChecked(bool(cfg["save_raw_content"]))
        self.hide_passwords_checkbox.setChecked(bool(cfg["hide_passwords"]))
        self.hide_credit_cards_checkbox.setChecked(bool(cfg["hide_credit_cards"]))
        self.encrypt_data_checkbox.setChecked(bool(cfg["encrypt_data"]))
        keywords = cfg.get("custom_sensitive_keywords", [])
        self.keywords_edit.setText(", ".join(keywords))

        self.show_notifications_checkbox.setChecked(bool(cfg["show_notifications"]))
        self.sound_enabled_checkbox.setChecked(bool(cfg["sound_enabled"]))

        theme_index = self.theme_combo.findData(cfg["theme"])
        self.theme_combo.setCurrentIndex(theme_index if theme_index >= 0 else 0)

        lang_index = self.language_combo.findData(cfg["language"])
        self.language_combo.setCurrentIndex(lang_index if lang_index >= 0 else 0)

        self.show_preview_checkbox.setChecked(bool(cfg["show_preview"]))
        self.compact_mode_checkbox.setChecked(bool(cfg["compact_mode"]))

        self.quick_paste_edit.setText(cfg["quick_paste_key"])
        self.show_history_edit.setText(cfg["show_history_key"])
        self.clear_all_edit.setText(cfg["clear_all_key"])

    def export_config(self):
        excluded = [self.excluded_apps_list.item(i).text() for i in range(self.excluded_apps_list.count())]
        keywords = [kw.strip() for kw in self.keywords_edit.text().split(",") if kw.strip()]
        storage_location = "cloud" if self.storage_cloud_radio.isChecked() else "local"

        cfg = {
            "enable_monitoring": self.enable_monitoring_checkbox.isChecked(),
            "monitor_images": self.monitor_images_checkbox.isChecked(),
            "monitor_urls": self.monitor_urls_checkbox.isChecked(),
            "monitor_code": self.monitor_code_checkbox.isChecked(),
            "excluded_apps": excluded,
            "poll_interval": float(self.poll_interval_spin.value()),

            "save_raw_content": self.save_raw_checkbox.isChecked(),
            "max_items": int(self.max_items_spin.value()),
            "auto_cleanup": self.auto_cleanup_checkbox.isChecked(),
            "cleanup_days": int(self.cleanup_days_spin.value()),
            "storage_location": storage_location,

            "hide_passwords": self.hide_passwords_checkbox.isChecked(),
            "hide_credit_cards": self.hide_credit_cards_checkbox.isChecked(),
            "encrypt_data": self.encrypt_data_checkbox.isChecked(),
            "custom_sensitive_keywords": keywords,

            "show_notifications": self.show_notifications_checkbox.isChecked(),
            "sound_enabled": self.sound_enabled_checkbox.isChecked(),

            "theme": self.theme_combo.currentData(),
            "language": self.language_combo.currentData(),
            "show_preview": self.show_preview_checkbox.isChecked(),
            "compact_mode": self.compact_mode_checkbox.isChecked(),

            "quick_paste_key": self.quick_paste_edit.text().strip(),
            "show_history_key": self.show_history_edit.text().strip(),
            "clear_all_key": self.clear_all_edit.text().strip(),
        }
        self._config.update(cfg)
        return cfg

    # endregion

    # region 事件处理
    def _on_tab_changed(self, row: int):
        if 0 <= row < self.stack.count():
            self.stack.setCurrentIndex(row)

    def _toggle_cleanup_inputs(self, enabled: bool):
        self.cleanup_days_spin.setEnabled(bool(enabled))

    def _add_excluded_app(self):
        title = self._tr("settings.monitoring.excluded.add")
        prompt = self._tr("settings.monitoring.excluded.prompt")
        text, ok = QInputDialog.getText(self, title, prompt)
        if ok and text.strip():
            name = text.strip()
            existing = [self.excluded_apps_list.item(i).text() for i in range(self.excluded_apps_list.count())]
            if name not in existing:
                self.excluded_apps_list.addItem(name)

    def _remove_selected_app(self):
        for item in self.excluded_apps_list.selectedItems():
            row = self.excluded_apps_list.row(item)
            self.excluded_apps_list.takeItem(row)

    def _clear_keywords(self):
        self.keywords_edit.clear()

    def _reset_to_default(self):
        confirm = QMessageBox.question(
            self,
            self._tr("settings.reset.confirm.title"),
            self._tr("settings.reset.confirm.text"),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if confirm == QMessageBox.Yes:
            self._config = DEFAULT_CONFIG.copy()
            self._load_values()

    # endregion

    @staticmethod
    def _form_row(label_text: str, widget: QWidget):
        row = QHBoxLayout()
        row.addWidget(QLabel(label_text))
        row.addStretch(1)
        widget.setMinimumWidth(200)
        row.addWidget(widget)
        return row

    def _tr(self, key: str, **kwargs) -> str:
        return self._translator.tr(key, **kwargs)
