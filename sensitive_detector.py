# sensitive_detector.py
import re

SENSITIVE_PATTERNS = {
    "ID_CARD": {
        "pattern": r"\b([1-9]\d{5}(18|19|20)\d{2}(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])\d{3}[\dXx])\b",
        "mask": lambda x: x[:6] + "********" + x[-4:] if len(x) == 18 else x
    },
    "BANK_CARD": {
        "pattern": r"\b(\d{16,19})\b",
        "mask": lambda x: x[:4] + " **** **** " + x[-4:]
    },
    "PHONE": {
        "pattern": r"\b(1[3-9]\d{9})\b",
        "mask": lambda x: x[:3] + "****" + x[-4:]
    },
    "EMAIL": {
        "pattern": r"\b([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,})\b",
        "mask": lambda x: re.sub(r"(?<=.).(?=.*@)", "*", x)
    },
    "IP_ADDRESS": {
        "pattern": r"\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b",
        "mask": lambda x: "*.*.*.*"
    }
}


def detect_and_mask(text, custom_keywords=None):
    masked = text
    found_types = set()

    # 内置规则
    for key, rule in SENSITIVE_PATTERNS.items():
        for match in re.finditer(rule["pattern"], text, re.IGNORECASE):
            original = match.group(1)
            masked = masked.replace(original, rule["mask"](original), 1)
            found_types.add(key)

    # 自定义关键词
    if custom_keywords:
        for kw in custom_keywords:
            if kw and kw in masked:
                masked = masked.replace(kw, "*" * len(kw))
                found_types.add("CUSTOM")

    return masked, len(found_types) > 0, list(found_types)