from PyQt6.QtWidgets import QWidget, QLabel, QMenu, QApplication
from PyQt6.QtCore import Qt, QPoint, pyqtSlot
from PyQt6.QtGui import QMovie, QAction
from config import settings
from core.event_bus import bus
from features.chat_ui.input_dialog import TextInputBox
from features.chat_ui.chat_bubble import ChatBubble
from features.history.viewer import HistoryWindow

class PetWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | 
                            Qt.WindowType.WindowStaysOnTopHint | 
                            Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.resize(settings.WINDOW_SIZE, settings.WINDOW_SIZE)
        # 初始化聊天 UI
        self.chat_bubble = ChatBubble()
        bus.doro_response_ready.connect(self.display_reply)
        # 預載歷史視窗 (先不顯示)
        self.history_window = None

        # 1. 預先載入左右兩個 Movie 物件
        self.movie_left = QMovie(settings.GIF_PATH_LEFT)
        self.movie_right = QMovie(settings.GIF_PATH_RIGHT)

        # 檢查素材是否讀取成功
        if not self.movie_left.isValid() or not self.movie_right.isValid():
             print("錯誤：找不到 GIF 素材，請確認 assets 資料夾內是否有 doro_left.gif 和 doro_right.gif")

        # 2. 初始化 Label 並設定預設方向 (向左)
        self.label = QLabel(self)
        self.label.setScaledContents(True)
        self.label.resize(settings.WINDOW_SIZE, settings.WINDOW_SIZE)
        
        # 初始狀態：設定為向左並開始播放
        self.current_direction = "left"
        self.label.setMovie(self.movie_left)
        self.movie_left.start()

        # 3. 訂閱方向改變的訊號
        # 當 bus 發出 direction_changed 訊號時，執行 self.update_direction
        bus.direction_changed.connect(self.update_direction)

        # 拖曳相關變數
        self.is_dragging = False
        self.drag_pos = QPoint()

    # ★ 新增 Slot 函式：接收訊號並切換圖片
    @pyqtSlot(str)
    def update_direction(self, new_direction):
        # 如果方向沒變，就什麼都不做 (避免重複重新載入動畫)
        if new_direction == self.current_direction:
            return

        print(f"Doro 轉向：{new_direction}")
        self.current_direction = new_direction
        
        # 停止當前動畫
        self.label.movie().stop()

        # 切換到新的 Movie
        if new_direction == "left":
            self.label.setMovie(self.movie_left)
            self.movie_left.start()
        elif new_direction == "right":
            self.label.setMovie(self.movie_right)
            self.movie_right.start()

    def mouseDoubleClickEvent(self, event):
        """雙擊 Doro 彈出輸入框"""
        if event.button() == Qt.MouseButton.LeftButton:
            input_box = TextInputBox(self)
            # 讓輸入框出現在 Doro 旁邊
            input_box.move(self.pos().x(), self.pos().y() + self.height() + 5)
            input_box.show()

    def display_reply(self, text):
        """顯示 Doro 的回覆氣泡"""
        self.chat_bubble.show_text(text, self.pos().x(), self.pos().y())
        
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_dragging = True
            self.drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
            bus.drag_started.emit()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and self.is_dragging:
            self.move(event.globalPosition().toPoint() - self.drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        self.is_dragging = False
        bus.drag_ended.emit()

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        
        history_action = QAction("📜 查看回憶 (歷史紀錄)", self)
        history_action.triggered.connect(self.open_history)
        menu.addAction(history_action)
        
        menu.addSeparator()
        
        # 2. 修正：點擊這裡才真正關閉整個應用程式
        quit_action = QAction("👋 讓 Doro 去睡覺 (關閉)", self)
        quit_action.triggered.connect(QApplication.instance().quit) # 強制結束 app
        menu.addAction(quit_action)
        
        menu.exec(event.globalPos())

    def open_history(self):
        if self.history_window is None:
            self.history_window = HistoryWindow()
        
        self.history_window.load_data() # 先刷新資料再顯示
        self.history_window.show()
        self.history_window.raise_()      # 確保視窗在最前面
        self.history_window.activateWindow()