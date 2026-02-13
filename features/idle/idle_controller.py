# features/idle/idle_controller.py
import random
from PyQt6.QtCore import QTimer
from core.event_bus import bus
from core.config_manager import user_config

class IdleTalkController:
    def __init__(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.trigger_talk)
        bus.idle_talk_toggled.connect(self.handle_toggle)
        
        # 啟動時自動檢查設定
        if user_config.get("idle_talk_enabled"):
            self.start_random_timer()
        
    def handle_toggle(self, enabled):
        if enabled:
            print("📢 Doro 閒聊模式已開啟囉！")
            self.start_random_timer()
        else:
            print("🔇 Doro 進入靜音模式囉。")
            self.timer.stop()
            
    def start_random_timer(self):
        # 10 到 30 秒隨機觸發一次 (毫秒計)
        interval = random.randint(10, 30) * 1000
        self.timer.start(interval)
        
    def trigger_talk(self):
        # 這裡發送一個隱藏指令給 BrainRouter
        # Doro 會針對 Python、日文或股市隨機噴點幹話
        bus.user_sent_message.emit("隨機說一句幹話、笑話，或是關於 Python/日文/股市的吐槽囉\n" \
                                    "[目前無網路，無法使用雲端資料，請讓 Doro 發揮想像力！]")
        
        # 說完後，重新開始下一個循環的隨機計時
        self.start_random_timer()