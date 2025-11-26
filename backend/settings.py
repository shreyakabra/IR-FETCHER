import os
from pathlib import Path
from typing import Dict
from dotenv import dotenv_values

BASE_DIR = Path(__file__).resolve().parents[1]
ENV_PATH = BASE_DIR / ".env"

SETTING_KEYS = {
    "openai_api_key": "OPENAI_API_KEY",
    "tavily_api_key": "TAVILY_API_KEY",
    "google_api_key": "GOOGLE_API_KEY",
    "google_cse_id": "GOOGLE_CSE_ID",
    "default_provider": "DEFAULT_PROVIDER",
}

def load_settings_status():
    result = {}
    for field, env_key in SETTING_KEYS.items():
        value = os.getenv(env_key)
        if not value:
            result[field] = None
        else:
            if len(value) <= 6:
                result[field] = "*" * len(value)
            else:
                result[field] = value[:3] + "..." + value[-2:]
    return result

def update_settings_env(updates: Dict[str, str]):
    if not updates:
        return

    existing = {}
    if ENV_PATH.exists():
        existing = dotenv_values(ENV_PATH) or {}

    for field, env_key in SETTING_KEYS.items():
        if field in updates and updates[field] is not None:
            value = updates[field].strip()
            existing[env_key] = value
            os.environ[env_key] = value

    lines = [f"{key}={value}\n" for key, value in existing.items()]
    with ENV_PATH.open("w", encoding="utf-8") as f:
        f.writelines(lines)

