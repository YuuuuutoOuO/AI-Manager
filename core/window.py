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
        
        # 1. 視窗屬性設定 (無邊框、最上層、不顯示在工具列)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | 
                            Qt.WindowType.WindowStaysOnTopHint | 
                            Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.resize(settings.WINDOW_SIZE, settings.WINDOW_SIZE)

        # 2. 載入左右兩張 GIF 素材
        self.movie_left = QMovie(settings.GIF_PATH_LEFT)
        self.movie_right = QMovie(settings.GIF_PATH_RIGHT)
        
        # 檢查素材是否讀取成功
        if not self.movie_left.isValid() or not self.movie_right.isValid():
             print("⚠️ 警告：找不到 GIF 素材，請確認 assets 資料夾內是否有 doro_left.gif 和 doro_right.gif")

        # 3. 初始化顯示元件
        self.label = QLabel(self)
        self.label.setScaledContents(True)
        self.label.resize(settings.WINDOW_SIZE, settings.WINDOW_SIZE)
        
        # 預設起始方向 (向左)
        self.current_direction = "left"
        self.label.setMovie(self.movie_left)
        self.movie_left.start()
        
        # 4. 初始化功能元件 (聊天氣泡 & 歷史視窗)
        self.chat_bubble = ChatBubble()
        self.history_window = None # 延遲載入，等要用再建立
        
        # 5. 訂閱事件訊號
        bus.direction_changed.connect(self.update_direction)
        bus.doro_response_ready.connect(self.display_reply)
        
        # 6. ★ 關鍵修復：初始化拖曳變數
        self.is_dragging = False
        self.drag_pos = QPoint()

    # --- 互動事件 1：滑鼠按下 (準備拖曳) ---
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_dragging = True
            # 記錄滑鼠點擊位置相對於視窗左上角的距離
            self.drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
            
            # 通知走路模組暫停 (這樣你抓著他的時候他不會亂跑)
            bus.drag_started.emit()

    # --- 互動事件 2：滑鼠移動 (正在拖曳) ---
    def mouseMoveEvent(self, event):
        # 確保是左鍵按住且處於拖曳狀態
        if event.buttons() == Qt.MouseButton.LeftButton and self.is_dragging:
            # 移動 Doro 視窗
            self.move(event.globalPosition().toPoint() - self.drag_pos)
            event.accept()

    # --- 互動事件 3：滑鼠放開 (結束拖曳) ---
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_dragging = False
            bus.drag_ended.emit() # 通知走路模組可以繼續走了

    # --- 互動事件 4：滑鼠雙擊 (開啟對話框) ---
    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            input_box = TextInputBox(self)
            # 讓輸入框出現在 Doro 下方一點點
            input_box.move(self.pos().x(), self.pos().y() + self.height() + 10)
            input_box.show()

    # --- 互動事件 5：右鍵選單 ---
    def contextMenuEvent(self, event):
        menu = QMenu(self)
        
        # 選項：歷史紀錄
        history_action = QAction("📜 查看回憶 (歷史紀錄)", self)
        history_action.triggered.connect(self.open_history)
        menu.addAction(history_action)
        
        menu.addSeparator()
        
        # 選項：關閉程式
        quit_action = QAction("👋 讓 Doro 去睡覺 (關閉)", self)
        quit_action.triggered.connect(QApplication.instance().quit)
        menu.addAction(quit_action)
        
        menu.exec(event.globalPos())

    # --- 系統事件：視窗移動時 (讓氣泡跟隨) ---
    def moveEvent(self, event):
        # 如果氣泡正在顯示，強制它跟著 Doro 移動
        if self.chat_bubble.isVisible():
            self.chat_bubble.move(self.pos().x(), self.pos().y() - self.chat_bubble.height() - 10)
        
        super().moveEvent(event)

    # --- 功能實作區域 ---
    
    @pyqtSlot(str)
    def update_direction(self, new_direction):
        """接收訊號並切換 GIF 方向"""
        if new_direction == self.current_direction:
            return
            
        # print(f"DEBUG: Doro 轉向 -> {new_direction}")
        self.current_direction = new_direction
        self.label.movie().stop()
        
        if new_direction == "left":
            self.label.setMovie(self.movie_left)
            self.movie_left.start()
        elif new_direction == "right":
            self.label.setMovie(self.movie_right)
            self.movie_right.start()

    def display_reply(self, text):
        """顯示對話氣泡"""
        self.chat_bubble.show_text(text, self.pos().x(), self.pos().y())

    def open_history(self):
        """開啟歷史紀錄視窗"""
        if self.history_window is None:
            self.history_window = HistoryWindow()
        
        self.history_window.load_data()
        self.history_window.show()
        self.history_window.raise_()
        self.history_window.activateWindow()