# features/brain/memory_manager.py
import json
import os
from config import settings
from core.config_manager import user_config

class MemoryManager:
    def __init__(self):
        self.history_file = os.path.join(settings.BASE_DIR, "chat_history.json")

    def generate_summary_prompt(self):
        """從歷史紀錄中產生給 AI 的總結請求"""
        if not os.path.exists(self.history_file):
            return "目前沒有歷史紀錄，請用初始人格與主人互動。"
        
        try:
            with open(self.history_file, "r", encoding="utf-8") as f:
                history = json.load(f)
            
            # 取最後 50 條對話來分析主人
            recent_chats = history[-50:]
            chat_context = ""
            for msg in recent_chats:
                chat_context += f"{msg['role']}: {msg['text']}\n"
            
            prompt = (
                "你是一個記憶分析專家。請根據以下對話紀錄，總結『主人』的特徵、愛好、"
                "目前正在學習的東西以及關注的股票。請用一段話描述，這段話將成為 Doro 的長期記憶。\n\n"
                f"對話紀錄：\n{chat_context}"
            )
            return prompt
        except Exception as e:
            print(f"⚠️ 記憶管理器錯誤：{e}")
            return "無法解析歷史紀錄。"