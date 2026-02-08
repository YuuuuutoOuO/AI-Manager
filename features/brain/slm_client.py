import requests
import json

class LocalBrain:
    def __init__(self, model_name="gemma2:2b"):
        self.url = "http://localhost:11434/api/generate"
        self.model_name = model_name
        # 定義 Doro 的地端性格
        self.system_prompt = (
            "你是一隻名為 Doro 的可愛電子寵物。說話結尾要加『囉』。"
            "如果你不知道答案，或者主人詢問『即時股價、新聞、複雜程式碼』，"
            "請只回覆一個標籤：[NEED_GEMINI]"
        )

    def think(self, text):
        payload = {
            "model": self.model_name,
            "prompt": f"{self.system_prompt}\n主人：{text}\nDoro：",
            "stream": False
        }
        try:
            response = requests.post(self.url, json=payload, timeout=5)
            if response.status_code == 200:
                result = response.json().get("response", "")
                return True, result.strip()
            return False, "Ollama 連線失敗囉..."
        except Exception as e:
            return False, str(e)