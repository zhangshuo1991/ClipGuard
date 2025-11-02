"""根据基础 PNG 生成 macOS icns 与应用内所需多尺寸图标。

运行方式：
    python tools/generate_app_icons.py
"""

from __future__ import annotations

import io
import struct
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
ASSETS_DIR = ROOT / "assets"
BASE_IMAGE = ASSETS_DIR / "app-icon-1024.png"
ICONSET_DIR = ASSETS_DIR / "clipguard.iconset"
ICNS_PATH = ASSETS_DIR / "clipguard.icns"
APP_ICON_EXPORTS = {
    ASSETS_DIR / "icons" / "app-icon-32.png": 32,
    ASSETS_DIR / "icons" / "app-icon-64.png": 64,
    ASSETS_DIR / "icons" / "app-icon-128.png": 128,
}
TRAY_ICON_EXPORTS = {
    ASSETS_DIR / "icons" / "tray.png": 24,
    ASSETS_DIR / "icons" / "tray@2x.png": 48,
}

# icns 类型映射：type code -> 目标像素
ICNS_ENTRIES = [
    ("icp4", 16),   # 16x16
    ("ic11", 32),   # 16x16 @2x
    ("icp5", 32),   # 32x32
    ("ic12", 64),   # 32x32 @2x
    ("icp6", 64),   # 64x64
    ("ic07", 128),  # 128x128
    ("ic13", 256),  # 128x128 @2x
    ("ic08", 256),  # 256x256
    ("ic14", 512),  # 256x256 @2x
    ("ic09", 512),  # 512x512
    ("ic10", 1024), # 512x512 @2x
]

ICONSET_SPECS = [
    ("icon_16x16.png", 16),
    ("icon_16x16@2x.png", 32),
    ("icon_32x32.png", 32),
    ("icon_32x32@2x.png", 64),
    ("icon_128x128.png", 128),
    ("icon_128x128@2x.png", 256),
    ("icon_256x256.png", 256),
    ("icon_256x256@2x.png", 512),
    ("icon_512x512.png", 512),
    ("icon_512x512@2x.png", 1024),
]


def ensure_base_image() -> Image.Image:
    if not BASE_IMAGE.exists():
        raise FileNotFoundError(f"未找到基础图标：{BASE_IMAGE}")
    return Image.open(BASE_IMAGE).convert("RGBA")


def resize_icon(base: Image.Image, size: int) -> Image.Image:
    if base.width == size and base.height == size:
        return base.copy()
    return base.resize((size, size), Image.LANCZOS)


def export_iconset(base: Image.Image) -> dict[int, bytes]:
    ICONSET_DIR.mkdir(parents=True, exist_ok=True)
    generated: dict[int, bytes] = {}
    for name, size in ICONSET_SPECS:
        img = resize_icon(base, size)
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        ICONSET_DIR.joinpath(name).write_bytes(buffer.getvalue())
        generated[size] = buffer.getvalue()
        print(f"[iconset] {name} -> {size}px")
    return generated


def export_png_variants(base: Image.Image, targets: dict[Path, int]) -> None:
    for path, size in targets.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        img = resize_icon(base, size)
        img.save(path, format="PNG")
        print(f"[export] {path.relative_to(ROOT)} -> {size}px")


def build_icns(png_cache: dict[int, bytes]) -> None:
    chunks: list[bytes] = []
    total_size = 8  # header
    for type_code, size in ICNS_ENTRIES:
        data = png_cache.get(size)
        if data is None:
            raise ValueError(f"缺少 {size}px 图标数据，无法写入 {type_code}")
        chunk = type_code.encode("ascii") + struct.pack(">I", len(data) + 8) + data
        chunks.append(chunk)
        total_size += len(chunk)

    with ICNS_PATH.open("wb") as fp:
        fp.write(b"icns")
        fp.write(struct.pack(">I", total_size))
        for chunk in chunks:
            fp.write(chunk)
    print(f"[icns] 写入 {ICNS_PATH.relative_to(ROOT)} ({total_size} bytes)")


def main() -> None:
    base = ensure_base_image()
    png_cache = export_iconset(base)
    export_png_variants(base, APP_ICON_EXPORTS)
    export_png_variants(base, TRAY_ICON_EXPORTS)
    build_icns(png_cache)


if __name__ == "__main__":
    main()
