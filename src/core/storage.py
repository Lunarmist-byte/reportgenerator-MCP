import json
import os

CONFIG_FILE = "config.json"

def load_settings():
    if not os.path.exists(CONFIG_FILE):
        return {
            "openai_api_key": "",
            "gemini_api_key": "",
            "openrouter_api_key": "",
            "default_model": "openai"
        }
    with open(CONFIG_FILE, "r") as f:
        try:
            return json.load(f)
        except:
            return {}

def save_settings(settings):
    with open(CONFIG_FILE, "w") as f:
        json.dump(settings, f, indent=4)
