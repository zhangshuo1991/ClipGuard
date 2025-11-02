# main.py
import sys

try:
    from PySide6.QtWidgets import QApplication
except ImportError:
    print("未检测到 PySide6。请先运行 `pip install PySide6` 后再启动程序。")
    sys.exit(1)

from ui.main_window import ClipGuardWindow


def main():
    if sys.platform == "darwin":
        try:
            import AppKit  # noqa: F401
        except ImportError:
            print("[警告] 建议安装 pyobjc-framework-AppKit，以便准确识别当前前台应用。")
    app = QApplication.instance() or QApplication(sys.argv)
    window = ClipGuardWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
