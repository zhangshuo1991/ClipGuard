# config.py
import os
import json

CONFIG_PATH = os.path.expanduser("~/.clipguard/config.json")

DEFAULT_CONFIG = {
    # 剪贴板监控
    "enable_monitoring": True,
    "monitor_images": True,
    "monitor_urls": True,
    "monitor_code": True,
    "excluded_apps": [],
    "poll_interval": 0.8,  # 剪贴板轮询间隔（秒）

    # 数据与存储
    "save_raw_content": False,
    "max_items": 1000,
    "auto_cleanup": False,
    "cleanup_days": 30,
    "storage_location": "local",

    # 隐私与安全
    "hide_passwords": True,
    "hide_credit_cards": True,
    "encrypt_data": False,
    "custom_sensitive_keywords": [],

    # 通知提示
    "show_notifications": True,
    "sound_enabled": False,

    # 界面外观
    "theme": "light",
    "language": "zh-CN",
    "show_preview": True,
    "compact_mode": False,

    # 快捷键
    "quick_paste_key": "Ctrl+Shift+V",
    "show_history_key": "Ctrl+Shift+H",
    "clear_all_key": "Ctrl+Shift+Delete",
}


def load_config():
    cfg = DEFAULT_CONFIG.copy()
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, dict):
                    cfg.update({k: v for k, v in data.items() if k in DEFAULT_CONFIG})
        except Exception:
            pass
    return cfg


def save_config(cfg):
    payload = DEFAULT_CONFIG.copy()
    payload.update({k: v for k, v in cfg.items() if k in DEFAULT_CONFIG})
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
