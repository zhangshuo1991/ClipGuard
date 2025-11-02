# ui/i18n.py
"""提供简单的翻译器，实现应用内中英文切换。"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict


TRANSLATIONS: Dict[str, Dict[str, str]] = {
    "zh-CN": {
        # Application
        "app.window_title": "ClipGuard - 剪贴板安全助手",
        "app.tray.tooltip": "ClipGuard - 剪贴板安全助手",
        "app.tray.menu.open": "打开主窗口",
        "app.tray.menu.quit": "退出",
        "app.tray.minimized": "应用已最小化到托盘，可通过图标恢复。",

        # Top bar
        "topbar.status.monitoring": "监控中",
        "topbar.status.paused": "已暂停",
        "topbar.toggle.pause": "暂停",
        "topbar.toggle.resume": "开始",
        "topbar.refresh": "刷新",
        "topbar.search.placeholder": "搜索剪贴板内容、来源应用…",
        "topbar.settings": "设置",

        # Sidebar
        "sidebar.section.navigation": "导航",
        "sidebar.section.types": "内容类型",
        "sidebar.section.apps": "来源应用",
        "sidebar.nav.home": "首页",
        "sidebar.nav.recent": "最近",
        "sidebar.nav.favorites": "收藏",
        "sidebar.nav.trash": "回收站",
        "sidebar.filter.text": "文本",
        "sidebar.filter.image": "图片",
        "sidebar.filter.url": "链接",
        "sidebar.filter.code": "代码",
        "sidebar.footer.settings": "设置",

        # Clipboard list
        "clipboard.title": "剪贴板历史",
        "clipboard.subtitle": "管理您的复制内容和来源应用",
        "clipboard.view.list": "列表视图",
        "clipboard.view.grid": "网格视图",
        "clipboard.restore": "恢复选中",
        "clipboard.delete": "删除选中",
        "clipboard.selection.count": "已选择 {count} 项",

        # Card actions
        "card.copy": "复制",
        "card.delete": "删除",
        "card.delete_permanent": "彻底删除",
        "card.restore": "恢复",

        # Table headers
        "table.column.time": "时间",
        "table.column.app": "来源应用",
        "table.column.category": "类型",
        "table.column.sensitive": "敏感类型",
        "table.column.masked": "内容（已脱敏）",

        # Detail panel
        "detail.group_title": "详情",
        "detail.masked_label": "脱敏内容:",
        "detail.raw_label": "原始内容:",
        "detail.time": "时间: {value}",
        "detail.source": "来源应用: {value}",
        "detail.category": "类型: {value}",
        "detail.sensitive": "敏感类型: {value}",
        "detail.masked_placeholder": "脱敏内容将在此显示",
        "detail.raw_placeholder_enabled": "刚刚捕获的数据会显示原始内容。",
        "detail.raw_placeholder_disabled": "已关闭保存原始内容。",

        # Actions
        "action.copy": "复制",
        "action.format": "格式化",
        "action.unformat": "还原",

        # Status messages
        "status.monitor.started": "剪贴板监控已启动",
        "status.monitor.paused": "剪贴板监控已暂停",
        "status.delete.none": "未选择可删除的记录",
        "status.delete.missing_id": "该记录缺少标识，无法删除",
        "status.delete.permanent": "已彻底删除记录",
        "status.delete.moved": "已移至回收站",
        "status.copy.none": "未找到可复制的记录",
        "status.copy.empty": "该记录没有可复制的文本",
        "status.copy.success": "已复制记录内容",
        "status.copy.masked_none": "当前没有可复制的脱敏内容",
        "status.copy.masked_success": "已复制脱敏内容",
        "status.copy.raw_none": "当前没有可复制的原始内容",
        "status.copy.raw_success": "已复制原始内容",
        "status.search.result": "搜索结果：{count} 条",
        "status.restore.none": "未选择可恢复的记录",
        "status.restore.missing_id": "该记录缺少标识，无法恢复",
        "status.restore.success": "记录已恢复",
        "status.record.new": "已捕获新的剪贴板内容",
        "status.worker.error": "剪贴板读取失败: {message}",
        "status.history.refreshed": "历史记录已刷新",
        "status.settings.saved": "设置已保存",
        "status.format.failed": "无法格式化该内容",
        "status.favorite.invalid": "该记录缺少标识，无法调整收藏状态",
        "status.favorite.added": "已加入收藏",
        "status.favorite.removed": "已取消收藏",

        # Settings dialog
        "settings.title": "设置",
        "settings.reset": "恢复默认",
        "settings.tabs.monitoring": "监控设置",
        "settings.tabs.storage": "存储设置",
        "settings.tabs.privacy": "隐私安全",
        "settings.tabs.notifications": "通知设置",
        "settings.tabs.interface": "界面设置",
        "settings.tabs.shortcuts": "快捷键",

        # Monitoring tab
        "settings.monitoring.section": "基础监控",
        "settings.monitoring.enable": "启用剪贴板监控",
        "settings.monitoring.images": "监控图片内容",
        "settings.monitoring.urls": "监控链接内容",
        "settings.monitoring.code": "监控代码片段",
        "settings.monitoring.interval_label": "剪贴板检测间隔",
        "settings.monitoring.interval_section": "轮询设置",
        "settings.monitoring.interval_suffix": " 秒",
        "settings.monitoring.excluded.section": "排除应用",
        "settings.monitoring.excluded.add": "添加应用",
        "settings.monitoring.excluded.remove": "移除选中",
        "settings.monitoring.excluded.hint": "提示：排除的应用复制内容将不会记录。",
        "settings.monitoring.excluded.prompt": "应用名称：",

        # Storage tab
        "settings.storage.section": "存储策略",
        "settings.storage.max_items": "最大保留条目数",
        "settings.storage.auto_cleanup": "启用自动清理",
        "settings.storage.cleanup_days": "清理时间（天）",
        "settings.storage.location.section": "存储位置",
        "settings.storage.location.local": "本地存储（仅当前设备）",
        "settings.storage.location.cloud": "云端同步（需要额外配置）",

        # Privacy tab
        "settings.privacy.section": "隐私控制",
        "settings.privacy.save_raw": "保存原始剪贴板内容（仅用于本地预览）",
        "settings.privacy.hide_passwords": "自动隐藏密码",
        "settings.privacy.hide_cards": "自动隐藏信用卡号",
        "settings.privacy.encrypt": "对存储的数据进行加密",
        "settings.privacy.keywords": "自定义敏感词",
        "settings.privacy.placeholder": "以逗号分隔，例如: 密码, 合同, 秘密",
        "settings.privacy.clear_keywords": "清空敏感词",

        # Notifications tab
        "settings.notifications.section": "通知提醒",
        "settings.notifications.show": "显示系统通知",
        "settings.notifications.sound": "通知时播放提示音",

        # Interface tab
        "settings.interface.section": "外观设置",
        "settings.interface.theme": "主题",
        "settings.interface.theme.light": "浅色",
        "settings.interface.theme.dark": "深色",
        "settings.interface.language": "界面语言",
        "settings.interface.preview": "列表中显示内容预览",
        "settings.interface.compact": "启用紧凑模式",

        # Language choices
        "settings.language.zh": "简体中文",
        "settings.language.en": "English",

        # Shortcuts tab
        "settings.shortcuts.section": "快捷键配置",
        "settings.shortcuts.quick_paste": "快速粘贴",
        "settings.shortcuts.history": "打开历史记录",
        "settings.shortcuts.clear_all": "清空所有记录",
        "settings.shortcuts.hint": "提示：快捷键需在系统中单独注册，本设置用于 UI 提示。",

        # Reset dialog
        "settings.reset.confirm.title": "恢复默认设置",
        "settings.reset.confirm.text": "确定要恢复默认设置吗？当前修改将丢失。",

        # Form helper
        "settings.form.placeholder.width": "200",
    },
    "en-US": {
        # Application
        "app.window_title": "ClipGuard - Clipboard Guardian",
        "app.tray.tooltip": "ClipGuard - Clipboard Guardian",
        "app.tray.menu.open": "Open Window",
        "app.tray.menu.quit": "Quit",
        "app.tray.minimized": "The app is hidden in the tray. Click the icon to restore.",

        # Top bar
        "topbar.status.monitoring": "Monitoring",
        "topbar.status.paused": "Paused",
        "topbar.toggle.pause": "Pause",
        "topbar.toggle.resume": "Start",
        "topbar.refresh": "Refresh",
        "topbar.search.placeholder": "Search clipboard content or source apps…",
        "topbar.settings": "Settings",

        # Sidebar
        "sidebar.section.navigation": "Navigation",
        "sidebar.section.types": "Content Types",
        "sidebar.section.apps": "Source Apps",
        "sidebar.nav.home": "Home",
        "sidebar.nav.recent": "Recent",
        "sidebar.nav.favorites": "Favorites",
        "sidebar.nav.trash": "Trash",
        "sidebar.filter.text": "Text",
        "sidebar.filter.image": "Images",
        "sidebar.filter.url": "Links",
        "sidebar.filter.code": "Code",
        "sidebar.footer.settings": "Settings",

        # Clipboard list
        "clipboard.title": "Clipboard History",
        "clipboard.subtitle": "Manage copied content and its origin apps",
        "clipboard.view.list": "List View",
        "clipboard.view.grid": "Grid View",
        "clipboard.restore": "Restore Selected",
        "clipboard.delete": "Delete Selected",
        "clipboard.selection.count": "Selected {count} item(s)",

        # Card actions
        "card.copy": "Copy",
        "card.delete": "Delete",
        "card.delete_permanent": "Delete Permanently",
        "card.restore": "Restore",

        # Table headers
        "table.column.time": "Time",
        "table.column.app": "Source App",
        "table.column.category": "Category",
        "table.column.sensitive": "Sensitive Types",
        "table.column.masked": "Masked Content",

        # Detail panel
        "detail.group_title": "Details",
        "detail.masked_label": "Masked Content:",
        "detail.raw_label": "Original Content:",
        "detail.time": "Time: {value}",
        "detail.source": "Source App: {value}",
        "detail.category": "Category: {value}",
        "detail.sensitive": "Sensitive Types: {value}",
        "detail.masked_placeholder": "Masked content appears here.",
        "detail.raw_placeholder_enabled": "Captured entries show the original content here.",
        "detail.raw_placeholder_disabled": "Saving original content is disabled.",

        # Actions
        "action.copy": "Copy",
        "action.format": "Format",
        "action.unformat": "Plain",

        # Status messages
        "status.monitor.started": "Clipboard monitoring is running",
        "status.monitor.paused": "Clipboard monitoring is paused",
        "status.delete.none": "No record selected for deletion",
        "status.delete.missing_id": "Record has no identifier and cannot be deleted",
        "status.delete.permanent": "Record permanently removed",
        "status.delete.moved": "Record moved to Trash",
        "status.copy.none": "No record found to copy",
        "status.copy.empty": "This record has no text to copy",
        "status.copy.success": "Record content copied",
        "status.copy.masked_none": "Masked content is empty",
        "status.copy.masked_success": "Masked content copied",
        "status.copy.raw_none": "Original content is empty",
        "status.copy.raw_success": "Original content copied",
        "status.search.result": "Search result: {count} item(s)",
        "status.restore.none": "No record selected for restore",
        "status.restore.missing_id": "Record has no identifier and cannot be restored",
        "status.restore.success": "Record restored",
        "status.record.new": "New clipboard entry captured",
        "status.worker.error": "Failed to read clipboard: {message}",
        "status.history.refreshed": "History refreshed",
        "status.settings.saved": "Settings saved",
        "status.format.failed": "Unable to format this content",
        "status.favorite.invalid": "Record has no identifier; cannot change favorite state",
        "status.favorite.added": "Added to favorites",
        "status.favorite.removed": "Removed from favorites",

        # Settings dialog
        "settings.title": "Settings",
        "settings.reset": "Restore Defaults",
        "settings.tabs.monitoring": "Monitoring",
        "settings.tabs.storage": "Storage",
        "settings.tabs.privacy": "Privacy & Security",
        "settings.tabs.notifications": "Notifications",
        "settings.tabs.interface": "Interface",
        "settings.tabs.shortcuts": "Shortcuts",

        # Monitoring tab
        "settings.monitoring.section": "Monitoring Basics",
        "settings.monitoring.enable": "Enable clipboard monitoring",
        "settings.monitoring.images": "Capture image content",
        "settings.monitoring.urls": "Capture link content",
        "settings.monitoring.code": "Capture code snippets",
        "settings.monitoring.interval_label": "Clipboard polling interval",
        "settings.monitoring.interval_section": "Polling Settings",
        "settings.monitoring.interval_suffix": " s",
        "settings.monitoring.excluded.section": "Excluded Apps",
        "settings.monitoring.excluded.add": "Add App",
        "settings.monitoring.excluded.remove": "Remove Selected",
        "settings.monitoring.excluded.hint": "Hint: entries copied from these apps are ignored.",
        "settings.monitoring.excluded.prompt": "Application name:",

        # Storage tab
        "settings.storage.section": "Storage Strategy",
        "settings.storage.max_items": "Maximum entries to keep",
        "settings.storage.auto_cleanup": "Enable automatic cleanup",
        "settings.storage.cleanup_days": "Cleanup interval (days)",
        "settings.storage.location.section": "Storage Location",
        "settings.storage.location.local": "Local only (this device)",
        "settings.storage.location.cloud": "Cloud sync (requires extra setup)",

        # Privacy tab
        "settings.privacy.section": "Privacy Controls",
        "settings.privacy.save_raw": "Save original clipboard content (local preview only)",
        "settings.privacy.hide_passwords": "Mask passwords automatically",
        "settings.privacy.hide_cards": "Mask credit card numbers",
        "settings.privacy.encrypt": "Encrypt stored entries",
        "settings.privacy.keywords": "Custom sensitive keywords",
        "settings.privacy.placeholder": "Comma separated, e.g. password, contract, secret",
        "settings.privacy.clear_keywords": "Clear keywords",

        # Notifications tab
        "settings.notifications.section": "Notifications",
        "settings.notifications.show": "Show system notifications",
        "settings.notifications.sound": "Play sound for notifications",

        # Interface tab
        "settings.interface.section": "Interface",
        "settings.interface.theme": "Theme",
        "settings.interface.theme.light": "Light",
        "settings.interface.theme.dark": "Dark",
        "settings.interface.language": "Language",
        "settings.interface.preview": "Show preview in list",
        "settings.interface.compact": "Enable compact mode",

        # Language choices
        "settings.language.zh": "Simplified Chinese",
        "settings.language.en": "English",

        # Shortcuts tab
        "settings.shortcuts.section": "Shortcut Configuration",
        "settings.shortcuts.quick_paste": "Quick paste",
        "settings.shortcuts.history": "Open history",
        "settings.shortcuts.clear_all": "Clear all records",
        "settings.shortcuts.hint": "Note: register shortcuts in the OS; these values are for UI hints.",

        # Reset dialog
        "settings.reset.confirm.title": "Restore Defaults",
        "settings.reset.confirm.text": "Restore default settings? Current changes will be lost.",

        # Form helper
        "settings.form.placeholder.width": "200",
    },
}

FALLBACK_LANGUAGE = "zh-CN"


@dataclass
class Translator:
    """轻量级翻译器，依赖预定义的字典完成文本切换。"""

    language_code: str = FALLBACK_LANGUAGE

    def __post_init__(self):
        self.set_language(self.language_code)

    def set_language(self, language_code: str) -> None:
        if language_code not in TRANSLATIONS:
            language_code = FALLBACK_LANGUAGE
        self.language_code = language_code
        self._catalog = TRANSLATIONS[language_code]

    def language(self) -> str:
        return self.language_code

    def tr(self, key: str, **kwargs) -> str:
        catalog = self._catalog
        text = catalog.get(key)
        if text is None:
            fallback = TRANSLATIONS.get(FALLBACK_LANGUAGE, {})
            text = fallback.get(key, key)
        if kwargs:
            try:
                text = text.format(**kwargs)
            except Exception:
                # 格式化失败时返回原文，避免界面崩溃
                pass
        return text

    @staticmethod
    def available_languages() -> Dict[str, str]:
        return {code: TRANSLATIONS[code].get("settings.language." + code.split("-")[0], code) for code in TRANSLATIONS}
