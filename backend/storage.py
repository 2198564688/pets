import json
import os
from appdirs import user_data_dir

APP_NAME = "CyberZombie"
APP_AUTHOR = "CyberZombie"

DATA_DIR = user_data_dir(APP_NAME, APP_AUTHOR)
SETTINGS_PATH = os.path.join(DATA_DIR, "settings.json")

DEFAULT_DATA = {
    "config": {
        "scale": 1.0,
        "fps": 15,
        "position": {"x": 100, "y": 200},
        "always_on_top": True,
        "auto_hide": False,
        "state": "IDLE"
    },
    "memos": [],
    "stats": {
        "total_uptime": 0,
        "errors_caught": 0
    }
}

def ensure_dir():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

def load():
    ensure_dir()
    if not os.path.exists(SETTINGS_PATH):
        save(DEFAULT_DATA)
        return DEFAULT_DATA.copy()
    try:
        with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        # 合并默认值，防止新增字段缺失
        merged = DEFAULT_DATA.copy()
        merged.update(data)
        if "config" in data:
            merged["config"] = {**DEFAULT_DATA["config"], **data["config"]}
        return merged
    except Exception:
        return DEFAULT_DATA.copy()

def save(data):
    ensure_dir()
    with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
