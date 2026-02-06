from PyQt6.QtWidgets import QLabel, QWidget, QVBoxLayout
from PyQt6.QtCore import Qt, QTimer

class ChatBubble(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.layout = QVBoxLayout()
        self.label = QLabel("")
        self.label.setStyleSheet("""
            background-color: rgba(255, 255, 255, 230);
            border-radius: 10px;
            padding: 8px;
            border: 1px solid #ccc;
            color: #333;
            font-size: 14px;
        """)
        self.label.setWordWrap(True)
        self.layout.addWidget(self.label)
        self.setLayout(self.layout)
        self.hide()

    def show_text(self, text, x, y):
        self.label.setText(text)
        self.adjustSize()
        # 顯示在 Doro 上方
        self.move(x, y - self.height() - 10)
        self.show()
        # 10秒後自動消失
        QTimer.singleShot(10000, self.hide)