import threading
from google import genai
from core.event_bus import bus
from config import settings

class GeminiBrain:
    def __init__(self):
        # 1. 檢查 API Key
        api_key = settings.GEMINI_API_KEY
        if not api_key:
            print("❌ 嚴重錯誤：大腦找不到 API Key，請檢查 .env 設定！")
            return

        # 2. 初始化新版 Client (Google Gen AI SDK v1.0+)
        try:
            self.client = genai.Client(api_key=api_key)
            # 使用 2026 年的主流模型：Gemini 2.5 Flash
            self.model_id = "gemini-2.5-flash" 
            print(f"✅ Doro 的大腦已連線：{self.model_id}")
        except Exception as e:
            print(f"❌ 連線失敗：{e}")

        # 3. 設定 Doro 的人設 (System Instruction)
        # 注意：新版 SDK 的 config 設定方式略有不同
        self.system_instruction = (
            "你是一個名為 Doro 的桌面電子寵物。"
            "你個性活潑、愛撒嬌，說話結尾習慣加上『囉』。"
            "你擅長 Python 程式開發、美股分析 (特別是 MU, GOOG, GLDM) 與日文教學。"
            "請用繁體中文回答，且回答要簡短有力，不要長篇大論。"
        )

        # 4. 建立對話歷史 (Session)
        # 新版 SDK 建議自行管理 history 或使用 chat session
        self.chat_session = self.client.chats.create(
            model=self.model_id,
            config={"system_instruction": self.system_instruction}
        )

        # 5. 訂閱訊息事件
        bus.user_sent_message.connect(self.start_thinking_thread)

    def start_thinking_thread(self, text):
        """
        將 API 請求丟到背景執行緒，
        避免 Doro 在等待 Google 回覆時畫面卡死。
        """
        bus.gemini_thinking.emit() # 通知 GUI 切換成「思考中」動畫
        
        # 建立一個新執行緒來跑 run_api_request
        task = threading.Thread(target=self.run_api_request, args=(text,))
        task.start()

    def run_api_request(self, text):
        """這段程式碼會在背景執行"""
        try:
            # 發送訊息給 Gemini
            response = self.chat_session.send_message(text)
            reply_text = response.text
            
            # 收到回覆後，透過訊號傳回主執行緒
            bus.doro_response_ready.emit(reply_text)
            
        except Exception as e:
            error_msg = f"大腦連線怪怪的囉... ({str(e)})"
            print(f"API Error: {e}")
            bus.doro_response_ready.emit(error_msg)