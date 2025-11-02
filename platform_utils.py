# platform_utils.py
import subprocess
import sys
import ctypes


def _get_windows_process_name():
    try:
        import win32gui
        import win32process
        import psutil

        hwnd = win32gui.GetForegroundWindow()
        if not hwnd:
            return "Unknown"
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        return psutil.Process(pid).name()
    except ImportError:
        # 回退使用 ctypes 仅拿窗口标题
        user32 = ctypes.windll.user32
        hwnd = user32.GetForegroundWindow()
        if not hwnd:
            return "Unknown"
        length = user32.GetWindowTextLengthW(hwnd)
        if length == 0:
            return "Unknown"
        buffer = ctypes.create_unicode_buffer(length + 1)
        user32.GetWindowTextW(hwnd, buffer, length + 1)
        return buffer.value or "Unknown"
    except Exception:
        return "Unknown"


def _get_macos_app_name():
    try:
        from AppKit import NSWorkspace
        app = NSWorkspace.sharedWorkspace().activeApplication()
        name = app.get("NSApplicationName")
        if name:
            return name
    except ImportError:
        pass
    except Exception:
        pass

    # AppleScript 回退方案
    try:
        script = 'tell application "System Events" to get name of first process whose frontmost is true'
        output = subprocess.check_output(["osascript", "-e", script], text=True)
        result = output.strip()
        if result:
            return result
    except Exception:
        pass
    return "Unknown"


def get_active_app_name():
    if sys.platform == "win32":
        return _get_windows_process_name()
    if sys.platform == "darwin":
        return _get_macos_app_name()
    return "Unknown (Linux)"
