import threading
from core.event_bus import bus
from features.brain.slm_client import LocalBrain
from features.brain.gemini_client import GeminiBrain

class BrainRouter:
    def __init__(self):
        self.local_brain = LocalBrain()
        self.cloud_brain = GeminiBrain()
        
        # 訂閱使用者訊息
        bus.user_sent_message.connect(self.dispatch)

    def dispatch(self, text):
        # 啟動執行緒，避免 GUI 卡死
        task = threading.Thread(target=self.logic_process, args=(text,))
        task.start()

    def logic_process(self, text):
        bus.gemini_thinking.emit() # 讓 Doro 進入思考動畫
        
        # 第一步：先問地端 SLM
        success, local_reply = self.local_brain.think(text)
        
        # 第二步：判定是否需要交給雲端 Gemini
        if not success or "[NEED_GEMINI]" in local_reply:
            print("🤖 地端無法處理，交給雲端 Gemini 囉！")
            # 這裡我們手動觸發 cloud_brain 的邏輯，但不要重複觸發 thread
            self.cloud_brain.run_api_request(text)
        else:
            print("🏠 地端已處理回覆。")
            bus.doro_response_ready.emit(local_reply)