# clipboard_monitor.py
import sys
import time

try:
    import pyperclip
except ImportError:  # noqa: F401
    pyperclip = None

_error_reported = False

def get_clipboard_text():
    if sys.platform == "win32":
        import win32clipboard
        try:
            win32clipboard.OpenClipboard()
            data = win32clipboard.GetClipboardData(win32clipboard.CF_UNICODETEXT)
            win32clipboard.CloseClipboard()
            return data
        except:
            return ""
    else:
        if pyperclip is None:
            raise RuntimeError("缺少依赖 pyperclip，请运行 `pip install pyperclip` 后重试。")
        return pyperclip.paste()

def monitor_clipboard(callback, interval=0.8, stop_event=None):
    global _error_reported
    last = ""
    while True:
        if stop_event is not None and stop_event.is_set():
            break
        try:
            current = get_clipboard_text()
            if current != last and current.strip():
                callback(current)
                last = current
            if _error_reported:
                _error_reported = False
        except Exception as e:
            if not _error_reported:
                print(f"[错误] 读取剪贴板失败: {e}")
                print("      请确认已安装依赖，并授予系统剪贴板访问权限。")
                _error_reported = True
        if stop_event is not None:
            if stop_event.wait(interval):
                break
        else:
            time.sleep(interval)
