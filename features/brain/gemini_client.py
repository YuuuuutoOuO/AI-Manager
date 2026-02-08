import threading
from google import genai
from core.event_bus import bus
from config import settings

class GeminiBrain:
    def __init__(self):
        """
        初始化 Doro 的雲端大腦 (Gemini 2.5)
        """
        # 1. 取得 API Key
        api_key = settings.GEMINI_API_KEY
        if not api_key:
            print("❌ 錯誤：Gemini API Key 缺失，請檢查 .env 檔案")
            return

        # 2. 初始化 Google Gen AI Client
        try:
            self.client = genai.Client(api_key=api_key)
            self.model_id = "gemini-2.5-flash"  # 使用 2026 年主流的 2.5 版本
            print(f"✅ Doro 雲端大腦已就緒: {self.model_id}")
        except Exception as e:
            print(f"❌ Gemini Client 初始化失敗: {e}")
            return

        # 3. 定義 Doro 的人格特質 (System Instruction)
        self.system_instruction = (
            "你是一個名為 Doro 的桌面電子寵物助理。"
            "你的個性活潑、可愛且愛撒嬌，說話結尾喜歡加上『囉』。"
            "你非常擅長 Python 程式開發、日文學習（特別是 JLPT N5 內容）以及美股分析。"
            "當主人提到股票（如 MU, GOOG, GLDM）時，請展現你的專業。"
            "回答請保持簡短，像是在聊天氣泡中說話一樣。"
        )

        # 4. 建立對話 Session
        self.chat_session = self.client.chats.create(
            model=self.model_id,
            config={
                "system_instruction": self.system_instruction,
                "temperature": 0.7, # 增加一點點隨機性，讓說話不呆板
            }
        )

        # 5. 訂閱訊息事件
        # 當 Event Bus 收到使用者訊息時，觸發思考流程
        bus.user_sent_message.connect(self.handle_incoming_message)

    def handle_incoming_message(self, text):
        """
        處理來自使用者（打字或語音）的訊息
        """
        # 啟動背景執行緒處理 API 請求，避免阻塞 GUI 視窗
        thinking_thread = threading.Thread(
            target=self.process_with_gemini, 
            args=(text,),
            daemon=True # 確保主程式關閉時，此執行緒也會跟著關閉
        )
        thinking_thread.start()

    def process_with_gemini(self, text):
        """
        這部分在背景執行緒運作，負責與 Google 伺服器通訊
        """
        # 發送「思考中」訊號，讓 GUI 可以換成思考動畫
        bus.gemini_thinking.emit()

        try:
            # 取得目前的股票即時資訊 (如果有實作 stock_tool，可以在這裡先抓取數據)
            # 這裡示範直接發送訊息
            response = self.chat_session.send_message(text)
            
            # 取得回覆文字
            reply_text = response.text
            
            # 透過 Event Bus 發送回覆，由 GUI 的氣泡模組接收顯示
            bus.doro_response_ready.emit(reply_text)

        except Exception as e:
            error_msg = f"哎呀，我的大腦連線好像有點不穩囉... ({str(e)})"
            print(f"Gemini API 請求錯誤: {e}")
            bus.doro_response_ready.emit(error_msg)

# 在 main.py 中實例化：
# brain = GeminiBrain()