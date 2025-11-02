"""集中定义应用的基础样式，帮助 PySide6 布局贴近 React 设计稿。"""

BASE_STYLESHEET = """
QMainWindow {
    background: #f8fafc;
    color: #0f172a;
    font-family: "Helvetica Neue", "PingFang SC", "Microsoft YaHei", sans-serif;
    font-size: 14px;
}

QWidget#topbar {
    background: #ffffff;
    border-bottom: 1px solid #e2e8f0;
}

#topbar QPushButton {
    border: 1px solid transparent;
    border-radius: 6px;
    padding: 6px 12px;
    background: transparent;
    color: #334155;
}

#topbar QPushButton:hover {
    background: #f1f5f9;
    color: #1d4ed8;
}

#topbar QPushButton:pressed {
    background: #e2e8f0;
}

#topbar QPushButton[role="monitorToggle"] {
    color: #2563eb;
    border-color: rgba(37, 99, 235, 0.2);
    background: rgba(37, 99, 235, 0.08);
}

#topbar QLabel#topbarStatusDot {
    font-size: 20px;
    color: #22c55e;
}

#topbar QLabel#topbarStatusDot[status="off"] {
    color: #ef4444;
}

#topbar QLineEdit#topbarSearch {
    border-radius: 8px;
    border: 1px solid #cbd5e1;
    padding: 6px 12px;
    background: #f8fafc;
}

#topbar QLineEdit#topbarSearch:focus {
    border-color: #2563eb;
    background: #ffffff;
}

QWidget#sidebar {
    background: #edf2ff;
    border-right: 1px solid #c7d2fe;
}

#sidebar QWidget#sidebarFooter {
    border-top: 1px solid rgba(29, 78, 216, 0.08);
}

#sidebar QScrollArea#sidebarScroll {
    background: transparent;
    border: none;
}

#sidebar QWidget#sidebarScrollViewport {
    background: transparent;
}

#sidebar QWidget#sidebarScrollContent {
    background: transparent;
}

#sidebar QLabel#sidebarSectionTitle {
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    color: #94a3b8;
    letter-spacing: 1.2px;
}

#sidebar QPushButton {
    text-align: left;
    border: 1px solid transparent;
    border-radius: 12px;
    padding: 10px 14px;
    background: transparent;
    color: #1f2937;
}

#sidebar QPushButton::icon {
    margin-left: 2px;
    margin-right: 12px;
}

#sidebar QPushButton[compact="true"] {
    padding: 4px;
    border-radius: 10px;
    min-width: 38px;
    min-height: 38px;
    max-width: 38px;
    max-height: 38px;
    border: 1px solid transparent;
}

#sidebar QPushButton[compact="true"]::icon {
    margin: 0;
}

#sidebar QPushButton:hover {
    background: rgba(37, 99, 235, 0.12);
}

#sidebar QPushButton[compact="true"]:hover {
    background: rgba(37, 99, 235, 0.18);
}

#sidebar QPushButton[role="nav"][active="true"],
#sidebar QPushButton[role="filter"][active="true"] {
    background: #dbeafe;
    border: 1px solid #bfdbfe;
    color: #1d4ed8;
    font-weight: 600;
}

#sidebar QPushButton[role="nav"][active="true"][compact="true"],
#sidebar QPushButton[role="filter"][active="true"][compact="true"] {
    background: rgba(37, 99, 235, 0.2);
    border-color: rgba(37, 99, 235, 0.35);
    color: #1d4ed8;
}

#sidebar QPushButton[role="footer"] {
    border: none;
    border-radius: 12px;
    padding: 10px 16px;
    background: #2563eb;
    color: #ffffff;
    font-weight: 600;
}

#sidebar QPushButton[role="footer"]:hover {
    background: #1d4ed8;
}

#sidebar QPushButton[role="footer"]:pressed {
    background: #1e40af;
}

QWidget#clipboardList {
    background: transparent;
}

#clipboardList QWidget#clipboardHeader {
    background: transparent;
}

#clipboardList QLabel#clipboardTitle {
    font-size: 20px;
    font-weight: 600;
    color: #0f172a;
}

#clipboardList QLabel#clipboardSubtitle {
    font-size: 13px;
    color: #64748b;
}

#clipboardList QPushButton {
    border-radius: 8px;
    padding: 6px 12px;
    border: 1px solid #cbd5f5;
    background: #ffffff;
    color: #1e293b;
}

#clipboardList QPushButton:hover {
    background: #f1f5f9;
}

#clipboardList QPushButton[role="switcher"] {
    border-color: #cbd5f5;
}

#clipboardList QPushButton[role="danger"] {
    border-color: #fca5a5;
    background: #fee2e2;
    color: #b91c1c;
}

#clipboardList QPushButton[role="danger"]:hover {
    background: #fecaca;
}

QFrame#clipboardCard {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 16px;
}

QFrame#clipboardCard:hover {
    border-color: #93c5fd;
}

QFrame#clipboardCard[selected="true"] {
    border-color: #3b82f6;
}

#clipboardCard QLabel#cardCategory {
    font-size: 13px;
    font-weight: 600;
    color: #2563eb;
}

#clipboardCard QLabel#cardTags {
    font-size: 12px;
    color: #64748b;
    background: #f1f5f9;
    padding: 2px 8px;
    border-radius: 999px;
}

#clipboardCard QLabel#cardContent {
    font-size: 14px;
    color: #1e293b;
    line-height: 1.5;
}

#clipboardCard QLabel#cardMeta {
    font-size: 12px;
    color: #94a3b8;
}

#clipboardCard QToolButton {
    border: none;
    border-radius: 6px;
    padding: 4px 8px;
    background: #f8fafc;
    color: #475569;
}

#clipboardCard QToolButton:hover {
    background: #e2e8f0;
    color: #1e293b;
}

#clipboardCard QToolButton[role="favorite"] {
    font-size: 16px;
    padding: 2px 6px;
    background: transparent;
    color: #facc15;
}

#clipboardCard QToolButton[role="favorite"][active="true"] {
    color: #f59e0b;
}


QGroupBox#detailPane {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 16px;
    margin-top: 0px;
    padding-top: 16px;
}

QGroupBox#detailPane > QLabel {
    font-size: 13px;
    color: #475569;
}

QPlainTextEdit {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 12px;
    font-family: "JetBrains Mono", "Menlo", "Consolas", "Courier New";
    font-size: 13px;
    color: #0f172a;
}

QPlainTextEdit:disabled {
    color: #94a3b8;
}

QTableView {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 16px;
    gridline-color: #e2e8f0;
    selection-background-color: rgba(59, 130, 246, 0.12);
    selection-color: #1e293b;
    alternate-background-color: #f8fafc;
}

QHeaderView::section {
    background: #f1f5f9;
    border: none;
    border-right: 1px solid #e2e8f0;
    padding: 8px;
    font-weight: 600;
    color: #475569;
}

QScrollBar:vertical {
    border: none;
    background: transparent;
    width: 10px;
    margin: 4px 0;
}

QScrollBar::handle:vertical {
    background: rgba(148, 163, 184, 0.6);
    border-radius: 4px;
}

QScrollBar::handle:vertical:hover {
    background: rgba(71, 85, 105, 0.7);
}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {
    height: 0;
}

QStatusBar {
    background: #ffffff;
    border-top: 1px solid #e2e8f0;
    padding: 4px 12px;
    color: #475569;
}

QDialog#settingsDialog {
    background: #ffffff;
}

QListWidget#settingsNav {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 8px;
}

QListWidget#settingsNav::item {
    border-radius: 8px;
    padding: 6px 12px;
    margin: 2px 0;
    color: #334155;
}

QListWidget#settingsNav::item:selected {
    background: #eff6ff;
    color: #1d4ed8;
    font-weight: 600;
}

QSplitter#mainSplitter::handle,
QSplitter#contentSplitter::handle {
    background: #e2e8f0;
    margin: 0;
}

QSplitter#mainSplitter::handle:horizontal:hover,
QSplitter#contentSplitter::handle:horizontal:hover {
    background: #dbeafe;
}

QLabel#splitterHandleIcon {
    font-size: 16px;
    color: #94a3b8;
}
"""


def load_stylesheet() -> str:
    """返回全局基础样式，供主窗口应用。"""
    return BASE_STYLESHEET
