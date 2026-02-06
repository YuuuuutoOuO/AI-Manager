from PyQt6.QtWidgets import QLineEdit, QDialog, QVBoxLayout
from PyQt6.QtCore import Qt
from core.event_bus import bus

class TextInputBox(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Popup)
        self.setModal(True)
        
        layout = QVBoxLayout()
        self.input_field = QLineEdit(self)
        self.input_field.setPlaceholderText("想跟 Doro 說什麼囉？")
        self.input_field.returnPressed.connect(self.send_message)
        layout.addWidget(self.input_field)
        self.setLayout(layout)

    def send_message(self):
        text = self.input_field.text().strip()
        if text:
            bus.user_sent_message.emit(text)
            self.input_field.clear()
        self.close()