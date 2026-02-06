from PyQt6.QtCore import QObject, pyqtSignal

class EventBus(QObject):
    drag_started = pyqtSignal()
    drag_ended = pyqtSignal()
    direction_changed = pyqtSignal(str)

    user_sent_message = pyqtSignal(str)      # 使用者發送訊息 (打字或語音)
    gemini_thinking = pyqtSignal()           # 讓 Doro 知道現在要換成「思考中」動畫
    doro_response_ready = pyqtSignal(str)    # Gemini 回覆了

bus = EventBus()

bus = EventBus()
