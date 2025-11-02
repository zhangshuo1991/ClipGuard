# build.py
import runpy
import sys
from pathlib import Path

import PyInstaller.__main__

ICON_BASE = Path("assets/app-icon-1024.png")
ICNS_PATH = Path("assets/clipguard.icns")

if ICON_BASE.exists() and (not ICNS_PATH.exists() or ICON_BASE.stat().st_mtime > ICNS_PATH.stat().st_mtime):
    print("[build] 检测到图标资源更新，重新生成 icns 与多尺寸 PNG …")
    runpy.run_path(str(Path("tools/generate_app_icons.py")), run_name="__main__")

opts = [
    'main.py',
    '--name=ClipGuard',
    '--windowed',
    '--onefile',
    '--icon=assets/clipguard.icns',
    '--exclude-module=matplotlib',
    '--exclude-module=numpy',
]

# 平台特定优化
if sys.platform == "darwin":
    opts.extend(['--add-binary=/System/Library/Frameworks/Tk.framework/Tk:tk',
                 '--add-binary=/System/Library/Frameworks/Tcl.framework/Tcl:tcl'])

PyInstaller.__main__.run(opts)
