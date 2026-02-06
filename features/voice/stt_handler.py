from core.event_bus import bus

class VoiceAssistant:
    def __init__(self):
        self.is_active = False # 目前先擱置不啟用
        # bus.user_sent_message.connect(...) 

    def start_listening(self):
        """未來實作語音辨識邏輯"""
        # 辨識完後呼叫 bus.user_sent_message.emit(辨識結果)
        pass