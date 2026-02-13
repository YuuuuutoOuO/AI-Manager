import json
import os
from config import settings

class ConfigManager:
    def __init__(self):
        self.config_file = os.path.join(settings.BASE_DIR, "user_config.json")
        self.defaults = {
            "idle_talk_enabled": False,
            "movement_enabled": True,
            "gemini_enabled": True, # ★ 新增：預設開啟 Gemini
            "ollama_model": "gemma2:2b",
            "doro_memory": "主人是一個喜歡技術的人。" # 儲存記憶
        }
        self.config = self.load_config()

    def load_config(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    return {**self.defaults, **json.load(f)}
            except:
                return self.defaults
        return self.defaults

    def get(self, key, default=None):
        """
        取得設定值。
        如果 key 不存在，優先回傳傳入的 default；
        如果沒傳 default，則使用 self.defaults 裡的預設值。
        """
        if key in self.config:
            return self.config[key]
        return default if default is not None else self.defaults.get(key)

    def set(self, key, value):
        self.config[key] = value
        self.save_config()

    def save_config(self):
        with open(self.config_file, "w", encoding="utf-8") as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)

# ★ 這是最重要的：建立單例供全域使用
user_config = ConfigManager()