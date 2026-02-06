import google.generativeai as genai
from core.event_bus import bus
from config import settings  # 改從 settings 讀取

class GeminiBrain:
    def __init__(self):
        # 從設定檔中取得 API Key
        api_key = settings.GEMINI_API_KEY
        
        if not api_key:
            print("警告：未偵測到 GEMINI_API_KEY，請檢查 .env 檔案！")
            return

        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        
        # 設定 Doro 的個性 (System Instruction)
        self.chat = self.model.start_chat(history=[])
        self.system_prompt = "你是一個名為 Doro 的桌面電子寵物。你很可愛、愛撒嬌，說話結尾會加『囉』。你也很聰明，會幫助主人處理程式開發、美股分析與日文學習的問題。"

        # 訂閱訊息事件
        bus.user_sent_message.connect(self.ask_gemini)

    def ask_gemini(self, text):
        bus.gemini_thinking.emit() # 告訴大家 Doro 正在思考
        
        try:
            # 將系統指令與使用者問題結合
            full_prompt = f"{self.system_prompt}\n主人說：{text}"
            response = self.chat.send_message(full_prompt)
            
            # 發送回覆訊號
            bus.doro_response_ready.emit(response.text)
        except Exception as e:
            bus.doro_response_ready.emit(f"哎呀，我的大腦打結了囉... ({str(e)})")