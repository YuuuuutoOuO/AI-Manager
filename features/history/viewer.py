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
        html = ""
        for msg in data:
            time = msg['timestamp']
            role = msg['role']
            content = msg['text']
            
            if role == "You":
                role_display = "主人"
                # 主人標籤用藍色
                role_html = f"<span style='color:blue; font-weight:bold;'>{role_display}:</span>"
            else:
                role_display = "Doro"
                # Doro 標籤用桃紅色
                role_html = f"<span style='color:#e60073; font-weight:bold;'>{role_display}:</span>"
                
            # ★ 關鍵修正：將 {content} 包在黑色的 span 裡面
            html += f"<p style='color:gray; font-size:10px; margin-bottom:2px;'>{time}</p>"
            html += f"<p style='margin-top:0;'>{role_html} <span style='color:black;'>{content}</span></p>"
            html += "<hr>"
            
        self.text_browser.setHtml(html)
        self.text_browser.moveCursor(self.text_browser.textCursor().MoveOperation.End)