import os
import re
from typing import Optional

_FILE_EXT_CATEGORIES = {
    # 图片
    "png": "Image",
    "jpg": "Image",
    "jpeg": "Image",
    "gif": "Image",
    "bmp": "Image",
    "webp": "Image",
    "tif": "Image",
    "tiff": "Image",
    "svg": "Image",
    "heic": "Image",
    "heif": "Image",
    "psd": "Image",
    "ai": "Image",
    "eps": "Image",
    # 代码
    "py": "Code",
    "pyw": "Code",
    "ipynb": "Code",
    "js": "Code",
    "jsx": "Code",
    "ts": "Code",
    "tsx": "Code",
    "java": "Code",
    "c": "Code",
    "cpp": "Code",
    "cc": "Code",
    "h": "Code",
    "hpp": "Code",
    "cs": "Code",
    "go": "Code",
    "rs": "Code",
    "swift": "Code",
    "kt": "Code",
    "kts": "Code",
    "php": "Code",
    "rb": "Code",
    "pl": "Code",
    "sh": "Code",
    "bash": "Code",
    "ps1": "Code",
    "sql": "Code",
    "json": "Code",
    "yaml": "Code",
    "yml": "Code",
    "xml": "Code",
    "css": "Code",
    "scss": "Code",
    "less": "Code",
    # 文档
    "txt": "Document",
    "md": "Document",
    "doc": "Document",
    "docx": "Document",
    "rtf": "Document",
    "odt": "Document",
    "pdf": "Document",
    "tex": "Document",
    "epub": "Document",
    # 表格
    "xls": "Spreadsheet",
    "xlsx": "Spreadsheet",
    "xlsm": "Spreadsheet",
    "ods": "Spreadsheet",
    "csv": "Spreadsheet",
    # 演示
    "ppt": "Presentation",
    "pptx": "Presentation",
    "odp": "Presentation",
    "key": "Presentation",
    # 压缩包
    "zip": "Archive",
    "rar": "Archive",
    "7z": "Archive",
    "tar": "Archive",
    "gz": "Archive",
    "tgz": "Archive",
    "bz2": "Archive",
    "xz": "Archive",
    "lz": "Archive",
    "cab": "Archive",
    "iso": "Archive",
    # 音频
    "mp3": "Audio",
    "wav": "Audio",
    "flac": "Audio",
    "aac": "Audio",
    "ogg": "Audio",
    "m4a": "Audio",
    "aiff": "Audio",
    # 视频
    "mp4": "Video",
    "mov": "Video",
    "avi": "Video",
    "mkv": "Video",
    "wmv": "Video",
    "flv": "Video",
    "webm": "Video",
    "mts": "Video",
    # 可执行文件
    "exe": "Executable",
    "msi": "Executable",
    "apk": "Executable",
    "app": "Executable",
    "dmg": "Executable",
    "pkg": "Executable",
    "deb": "Executable",
    "rpm": "Executable",
    "bat": "Executable",
    # 字体
    "ttf": "Font",
    "otf": "Font",
    "woff": "Font",
    "woff2": "Font",
}

_BUSINESS_KEYWORDS_ZH = ["合同", "发票", "报价", "客户", "交易"]
_BUSINESS_KEYWORDS_EN = [
    "contract",
    "invoice",
    "quotation",
    "quote",
    "client",
    "customer",
    "transaction",
    "agreement",
    "proposal",
]

_CODE_LINE_START_PATTERN = re.compile(
    r"^\s*(def|class|import|from|for|while|if|elif|else|try|except|with|return|lambda|"
    r"package|using|public|private|protected|interface|enum|namespace)\b",
    re.IGNORECASE | re.MULTILINE,
)
_CODE_ASSIGN_CALL_PATTERN = re.compile(r"=\s*[^=]+\([^)]*\)")
_CODE_KEYWORD_PATTERN = re.compile(
    r"\b(function|console\.log|System\.out\.println|print\s*\(|async\s+def|await|var\s+\w+|let\s+\w+|const\s+\w+)\b"
)


def _looks_like_code(text: str) -> bool:
    if _CODE_LINE_START_PATTERN.search(text):
        return True
    if _CODE_ASSIGN_CALL_PATTERN.search(text):
        return True
    if _CODE_KEYWORD_PATTERN.search(text):
        return True
    structural_hits = 0
    for line in text.splitlines() or [text]:
        if re.search(r"[{}\[\]]", line):
            structural_hits += 1
        if ";" in line or "->" in line:
            structural_hits += 1
    return structural_hits >= 2


def _category_from_extension(text: str) -> Optional[str]:
    tokens = re.split(r'[\s"\'<>]+', text)
    for token in tokens:
        token = token.strip('.,;:!?()[]{}\'"')
        if not token:
            continue
        name, ext = os.path.splitext(token)
        if not ext:
            continue
        if not name or re.search(r"[^\w\-.]", name):
            continue
        category = _FILE_EXT_CATEGORIES.get(ext.lstrip(".").lower())
        if category:
            return category
    return None


def classify_content(text):
    if text.strip() == "":
        return "Text"
    ext_category = _category_from_extension(text)
    if ext_category:
        return ext_category
    sample = (text or "").strip()
    if not sample:
        return "Text"

    if _looks_like_code(sample):
        return "Code"
    sample_lower = sample.lower()

    if re.search(r'(http|https)://', sample):
        return "URL"
    elif re.search(r'^\s*def\s+|\s*class\s+|import\s+|from\s+.*import', sample):
        return "Code"
    elif re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', sample):
        return "Email"
    elif re.search(r'1[3-9]\d{9}', sample):
        return "Phone"
    elif re.search(r'\d{17}[\dXx]', sample):
        return "ID"
    elif any(kw in sample for kw in _BUSINESS_KEYWORDS_ZH) or any(
        kw in sample_lower for kw in _BUSINESS_KEYWORDS_EN
    ):
        return "Business"
    else:
        return "Text"
