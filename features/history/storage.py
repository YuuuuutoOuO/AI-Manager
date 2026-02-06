import json
import os
import datetime
from core.event_bus import bus
from config import settings

class HistoryLogger:
    def __init__(self):
        self.log_file = os.path.join(settings.BASE_DIR, "chat_history.json")
        
        # 確保訊號正確連接
        bus.user_sent_message.connect(self.on_user_msg)
        bus.doro_response_ready.connect(self.on_doro_msg)
        print(f"DEBUG: 歷史紀錄器已啟動，儲存路徑：{self.log_file}")

    def on_user_msg(self, text):
        self.log("You", text)

    def on_doro_msg(self, text):
        self.log("Doro", text)

    def log(self, role, text):
        entry = {
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "role": role,
            "text": text
        }
        
        history = self.load_history()
        history.append(entry)
        
        try:
            with open(self.log_file, "w", encoding="utf-8") as f:
                json.dump(history, f, ensure_ascii=False, indent=2)
            # print(f"DEBUG: 已紀錄 {role} 的訊息") # 成功後可註解
        except Exception as e:
            print(f"❌ 紀錄儲存失敗: {e}")

    def load_history(self):
        if not os.path.exists(self.log_file):
            return []
        try:
            with open(self.log_file, "r", encoding="utf-8") as f:
                content = f.read()
                if not content: return []
                return json.loads(content)
        except Exception as e:
            print(f"讀取紀錄錯誤: {e}")
            return []