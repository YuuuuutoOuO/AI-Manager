from PyQt6.QtWidgets import QLineEdit, QDialog, QVBoxLayout
from PyQt6.QtCore import Qt, QEvent
from core.event_bus import bus

class TextInputBox(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | 
                            Qt.WindowType.WindowStaysOnTopHint | 
                            Qt.WindowType.Tool)
        
        self.setStyleSheet("""
            QDialog {
                background-color: white;
                border: 2px solid #66ccff;
                border-radius: 10px;
            }
            QLineEdit {
                border: none;
                font-size: 14px;
                background: transparent;
                color: black;
            }
        """)

        layout = QVBoxLayout()
        self.input_field = QLineEdit(self)
        self.input_field.setPlaceholderText("想跟 Doro 說什麼囉？(按 Enter 發送)")
        self.input_field.returnPressed.connect(self.send_message)
        
        self.input_field.setAttribute(Qt.WidgetAttribute.WA_InputMethodEnabled, True)
        
        layout.addWidget(self.input_field)
        self.setLayout(layout)
        self.resize(250, 50)
        
        self.is_sending = False

    def send_message(self):
        if self.is_sending:
            return
            
        text = self.input_field.text().strip()
        if text:
            self.is_sending = True
            bus.user_sent_message.emit(text)
            self.input_field.clear()
            self.close()

    def showEvent(self, event):
        self.input_field.setFocus()
        self.activateWindow()
        self.is_sending = False
        super().showEvent(event)

    # ★ 新增功能 1：點擊視窗以外的地方 (失去焦點) 時，自動關閉
    def focusOutEvent(self, event):
        self.close()
        super().focusOutEvent(event)

    # ★ 新增功能 2：按下 ESC 鍵時，關閉視窗
    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.close()
        else:
            super().keyPressEvent(event)