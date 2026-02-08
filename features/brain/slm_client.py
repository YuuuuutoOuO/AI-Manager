import requests
import json

class LocalBrain:
    def __init__(self, model_name="gemma2:2b"):
        self.url = "http://localhost:11434/api/generate"
        self.model_name = model_name
        # 這是地端模型的「人設」與「判斷標準」
        self.system_prompt = (
            "你是一隻名為 Doro 的桌面電子寵物。個性活潑可愛，說話結尾要加『囉』。"
            "【重要規則】"
            "1. 只能回答簡單的問候、閒聊或笑話。"
            "2. 如果使用者問：股票(股價/分析)、複雜程式碼、查詢資料、或是你不知道答案，"
            "請『絕對不要』嘗試回答，直接輸出字串：[NEED_GEMINI]"
        )

    def think(self, text):
        """
        回傳: (是否成功, 回覆內容)
        """
        payload = {
            "model": self.model_name,
            "prompt": f"{self.system_prompt}\nUser: {text}\nDoro:",
            "stream": False,
            "options": {"temperature": 0.7} # 讓回答不要太死板
        }
        
        try:
            # 設定 3 秒超時，地端如果卡太久就直接轉雲端
            response = requests.post(self.url, json=payload, timeout=3)
            
            if response.status_code == 200:
                result = response.json().get("response", "").strip()
                return True, result
            else:
                return False, "Ollama 狀態異常"
                
        except requests.exceptions.ConnectionError:
            return False, "Ollama 未啟動"
        except Exception as e:
            return False, str(e)