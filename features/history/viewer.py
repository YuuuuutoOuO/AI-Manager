from PyQt6.QtWidgets import QDialog, QVBoxLayout, QTextBrowser, QPushButton
from PyQt6.QtCore import Qt
from features.history.storage import HistoryLogger

class HistoryWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("與 Doro 的回憶")
        self.resize(400, 500)
        
        self.setStyleSheet("""
            QDialog { background-color: #2b2b2b; } /* 視窗背景改深灰，比較護眼 */
            QTextBrowser { 
                background-color: white; 
                border-radius: 5px; 
                padding: 10px;
                font-size: 14px;
                color: black; /* ★ 強制預設字體為黑色 */
            }
            QPushButton {
                background-color: #66ccff;
                color: white;
                border-radius: 5px;
                padding: 8px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #5bbce6; }
        """)

        layout = QVBoxLayout()
        
        self.text_browser = QTextBrowser()
        layout.addWidget(self.text_browser)
        
        refresh_btn = QPushButton("重新整理")
        refresh_btn.clicked.connect(self.load_data)
        layout.addWidget(refresh_btn)
        
        self.setLayout(layout)
        self.logger = HistoryLogger()
        self.load_data()

    def load_data(self):
        data = self.logger.load_history()
        html = "<body style='color: black;'>" # ★ 設定全體預設黑字
        for msg in data:
            role_color = "blue" if msg['role'] == "You" else "#e60073"
            role_name = "主人" if msg['role'] == "You" else "Doro"
            
            html += f"<div style='margin-bottom: 10px;'>"
            html += f"<div style='color: gray; font-size: 11px;'>{msg['timestamp']}</div>"
            html += f"<div style='color: {role_color}; font-weight: bold;'>{role_name}: "
            html += f"<span style='color: black; font-weight: normal;'>{msg['text']}</span></div>"
            html += "</div><hr style='border: 0.5px solid #eee;'>"
            
        html += "</body>"
        self.text_browser.setHtml(html)
        self.text_browser.moveCursor(self.text_browser.textCursor().MoveOperation.End)