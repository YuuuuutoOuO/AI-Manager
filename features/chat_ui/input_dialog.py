from PyQt6.QtWidgets import QLineEdit, QDialog, QVBoxLayout
from PyQt6.QtCore import Qt
from core.event_bus import bus

class TextInputBox(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 設定視窗屬性
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | 
                            Qt.WindowType.WindowStaysOnTopHint | 
                            Qt.WindowType.Tool)
        
        # 設定樣式
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
        
        # 1. 綁定訊號
        self.input_field.returnPressed.connect(self.send_message)
        
        # 2. 啟用輸入法支援
        self.input_field.setAttribute(Qt.WidgetAttribute.WA_InputMethodEnabled, True)
        
        layout.addWidget(self.input_field)
        self.setLayout(layout)
        
        self.resize(250, 50)
        
        # 3. 初始化防手抖旗標
        self.has_sent = False

    def send_message(self):
        # ★ 終極防護：如果已經送過了，直接把這個請求丟掉
        if self.has_sent:
            return
            
        text = self.input_field.text().strip()
        if text:
            # 1. 立刻鎖定
            self.has_sent = True
            
            # 2. ★ 物理斷開訊號 (最保險的做法)
            try:
                self.input_field.returnPressed.disconnect()
            except:
                pass

            # 3. 發送訊息
            bus.user_sent_message.emit(text)
            
            # 4. 清空並關閉
            self.input_field.clear()
            self.close()

    def showEvent(self, event):
        """每次視窗打開時，重置狀態"""
        self.input_field.setFocus()
        self.has_sent = False  # 重置為可以發送
        
        # 重新綁定訊號 (因為上面 disconnect 掉了)
        try:
            self.input_field.returnPressed.disconnect()
        except:
            pass
        self.input_field.returnPressed.connect(self.send_message)
        
        super().showEvent(event)

    def focusOutEvent(self, event):
        self.close()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.close()
        else:
            super().keyPressEvent(event)