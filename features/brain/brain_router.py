import threading
import json
import os
from core.event_bus import bus
from core.config_manager import user_config
from config import settings
from features.brain.slm_client import LocalBrain
from features.brain.gemini_client import GeminiBrain

class BrainRouter:
    def __init__(self):
        # 初始化兩個大腦
        self.local_brain = LocalBrain(model_name="gemma2:2b")
        self.cloud_brain = GeminiBrain()
        self.history_file = os.path.join(settings.BASE_DIR, "chat_history.json")
        
        # 訂閱訊號
        bus.user_sent_message.connect(self.dispatch)
        print("🧠 大腦路由器已啟動：具備記憶總結與 Gemini 開關功能")

    def dispatch(self, text):
        # 啟動背景執行緒，防止 GUI 卡死
        task = threading.Thread(target=self.logic_process, args=(text,), daemon=True)
        task.start()

    def logic_process(self, text):
        # 發送思考中訊號
        bus.gemini_thinking.emit() 

        # --- A. 處理記憶總結請求 (來自右鍵選單) ---
        if text == "[SYSTEM_REQUEST_SUMMARY]":
            self.handle_memory_summary()
            return

        # --- B. 處理一般對話邏輯 ---
        # 1. 注入長期記憶
        memory = user_config.get("doro_memory", "主人是一位開發 Python 專案且正在學習日文的工程師。")
        final_prompt = f"【Doro 的長期記憶：{memory}】\n\n主人現在說：{text}"

        # 2. 優先嘗試地端 (Ollama)
        print(f"🏠 地端嘗試處理: {text}")
        success, local_reply = self.local_brain.think(final_prompt)
        
        # 3. 判斷是否需要 Fallback 轉雲端
        gemini_allowed = user_config.get("gemini_enabled", True)
        needs_cloud = False

        if not success:
            print("⚠️ 地端通訊失敗 -> 切換雲端")
            needs_cloud = True
        elif "[NEED_GEMINI]" in local_reply:
            print("🔄 地端判斷能力不足 -> 切換雲端")
            needs_cloud = True
        elif len(local_reply) < 2:
            print("⚠️ 地端回覆內容過空 -> 切換雲端")
            needs_cloud = True

        # 4. 執行分流與回覆
        if needs_cloud:
            if gemini_allowed:
                print("🚀 正在請求雲端 Gemini 支援...")
                self.cloud_brain.run_api_request(final_prompt)
            else:
                print("🔒 Gemini 已停用，回傳地端初步結果。")
                clean_reply = local_reply.replace("[NEED_GEMINI]", "").strip()
                bus.doro_response_ready.emit(clean_reply if clean_reply else "Doro 現在斷網了，也聯絡不上 Gemini 囉...")
        else:
            print("✅ 地端成功處理回覆")
            bus.doro_response_ready.emit(local_reply)

    def handle_memory_summary(self):
        """讀取歷史紀錄並分析主人特徵"""
        print("🧠 Doro 正在回憶過去的點點滴滴...")
        
        if not os.path.exists(self.history_file):
            bus.doro_response_ready.emit("主人，我們還沒聊過天，Doro 沒辦法總結回憶囉！")
            return

        try:
            with open(self.history_file, "r", encoding="utf-8") as f:
                history = json.load(f)
            
            # 取最後 50 條對話作為背景資料
            recent_chats = history[-50:]
            chat_context = "\n".join([f"{m['role']}: {m['text']}" for m in recent_chats])
            
            summary_prompt = (
                "請根據以下對話紀錄，分析『主人』的性格與近況 (例如：正在學日文、開發 Python 專案、關注股市等)。"
                "請用一段話 (50字內) 總結，這將成為你的長期記憶：\n\n" + chat_context
            )
            
            # 使用 Gemini 進行高品質總結
            response = self.cloud_brain.chat_session.send_message(summary_prompt)
            new_memory = response.text.strip()
            
            # 儲存記憶到設定檔
            user_config.set("doro_memory", new_memory)
            bus.doro_response_ready.emit(f"Doro 已經重新認識主人囉！我知道主人：{new_memory}")
            print(f"✨ 新記憶已儲存: {new_memory}")

        except Exception as e:
            print(f"❌ 記憶總結失敗: {e}")
            bus.doro_response_ready.emit("Doro 剛才頭痛了一下，沒辦法完成記憶總結囉...")