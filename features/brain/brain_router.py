import threading
from core.event_bus import bus
from features.brain.slm_client import LocalBrain
from features.brain.gemini_client import GeminiBrain

class BrainRouter:
    def __init__(self):
        # 初始化兩個大腦
        self.local_brain = LocalBrain(model_name="gemma2:2b") # 確保你有 ollama run gemma2:2b
        self.cloud_brain = GeminiBrain()
        
        # ★ 這是全家唯一聽使用者說話的耳朵
        bus.user_sent_message.connect(self.dispatch)
        print("🧠 大腦路由器已啟動：Ollama 優先 -> Gemini 備援")

    def dispatch(self, text):
        # 啟動執行緒，避免 GUI 卡死
        task = threading.Thread(target=self.logic_process, args=(text,), daemon=True)
        task.start()

    def logic_process(self, text):
        # 1. 發送思考訊號 (讓 Doro 切換動畫)
        bus.gemini_thinking.emit() 
        
        # 2. 優先嘗試地端 (Ollama)
        print(f"🏠 地端嘗試處理: {text}")
        success, local_reply = self.local_brain.think(text)
        
        # 3. 判斷是否需要切換雲端 (Fallback Logic)
        needs_cloud = False
        
        if not success:
            print(f"⚠️ 地端失敗 ({local_reply}) -> 切換雲端")
            needs_cloud = True
        elif "[NEED_GEMINI]" in local_reply:
            print("🔄 地端判斷無法回答 -> 切換雲端")
            needs_cloud = True
        elif len(local_reply) < 2:
            print("⚠️ 地端回覆太短 -> 切換雲端")
            needs_cloud = True

        # 4. 執行分流
        if needs_cloud:
            # 呼叫 Gemini (它裡面包含了 StockTool 股票查詢邏輯)
            self.cloud_brain.run_api_request(text)
        else:
            print("✅ 地端成功回覆")
            # 發送訊號給 UI 顯示氣泡
            bus.doro_response_ready.emit(local_reply)