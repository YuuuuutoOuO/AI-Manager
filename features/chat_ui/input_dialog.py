from PyQt6.QtWidgets import QLineEdit, QDialog, QVBoxLayout
from PyQt6.QtCore import Qt
from core.event_bus import bus

class TextInputBox(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        
        self.setStyleSheet("""
            QDialog { background-color: white; border: 2px solid #66ccff; border-radius: 10px; }
            QLineEdit { border: none; font-size: 14px; background: transparent; color: black; }
        """)

        layout = QVBoxLayout()
        self.input_field = QLineEdit(self)
        self.input_field.setPlaceholderText("想跟 Doro 說什麼囉？")
        # 綁定訊號
        self.input_field.returnPressed.connect(self.send_message)
        self.input_field.setAttribute(Qt.WidgetAttribute.WA_InputMethodEnabled, True)
        
        layout.addWidget(self.input_field)
        self.setLayout(layout)
        self.resize(250, 50)
        self.is_processing = False

    def send_message(self):
        if self.is_processing: return
        
        text = self.input_field.text().strip()
        if text:
            self.is_processing = True
            # ★ 關鍵保險：立刻斷開連接，防止 IME 造成的第二次觸發
            try:
                self.input_field.returnPressed.disconnect(self.send_message)
            except: pass 
            
            bus.user_sent_message.emit(text)
            self.input_field.clear()
            self.close()

    def focusOutEvent(self, event):
        self.close() # 點擊旁邊自動關閉

    def showEvent(self, event):
        self.input_field.setFocus()
        self.is_processing = False
        super().showEvent(event)