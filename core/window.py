from PyQt6.QtWidgets import QWidget, QLabel, QMenu, QApplication
from PyQt6.QtCore import Qt, QPoint, pyqtSlot, QTimer
from PyQt6.QtGui import QMovie, QAction

from config import settings
from core.config_manager import user_config
from core.event_bus import bus
from features.chat_ui.input_dialog import TextInputBox
from features.chat_ui.chat_bubble import ChatBubble
from features.history.viewer import HistoryWindow

class PetWindow(QWidget):
    def __init__(self):
        super().__init__()
        
        # 1. 視窗屬性設定
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | 
                            Qt.WindowType.WindowStaysOnTopHint | 
                            Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.resize(settings.WINDOW_SIZE, settings.WINDOW_SIZE)

        # 讀取持久化設定
        self.idle_talk_enabled = user_config.get("idle_talk_enabled")
        self.movement_enabled = user_config.get("movement_enabled")
        self.gemini_enabled = user_config.get("gemini_enabled")

        # 啟動時同步設定狀態給各個控制器
        QTimer.singleShot(1000, self.sync_initial_settings)
        
        # 2. 載入 GIF 素材
        self.movie_left = QMovie(settings.GIF_PATH_LEFT)
        self.movie_right = QMovie(settings.GIF_PATH_RIGHT)
        
        if not self.movie_left.isValid() or not self.movie_right.isValid():
             print("⚠️ 警告：找不到 GIF 素材")

        # 3. 初始化顯示元件
        self.label = QLabel(self)
        self.label.setScaledContents(True)
        self.label.resize(settings.WINDOW_SIZE, settings.WINDOW_SIZE)
        
        self.current_direction = "left"
        self.label.setMovie(self.movie_left)
        self.movie_left.start()
        
        # 4. 初始化功能元件
        self.chat_bubble = ChatBubble()
        self.history_window = None 
        
        # 5. 訂閱事件
        bus.direction_changed.connect(self.update_direction)
        bus.doro_response_ready.connect(self.display_reply)
        
        self.is_dragging = False
        self.drag_pos = QPoint()

    def sync_initial_settings(self):
        """確保啟動時控制器拿到正確的開關狀態"""
        bus.idle_talk_toggled.emit(self.idle_talk_enabled)
        bus.movement_toggled.emit(self.movement_enabled)

    # --- 互動事件 ---
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_dragging = True
            self.drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            bus.drag_started.emit()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and self.is_dragging:
            self.move(event.globalPosition().toPoint() - self.drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_dragging = False
            bus.drag_ended.emit()

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            input_box = TextInputBox(self)
            input_box.move(self.pos().x(), self.pos().y() + self.height() + 10)
            input_box.show()

    # --- 右鍵選單 ---
    def contextMenuEvent(self, event):
        menu = QMenu(self)
        settings_menu = menu.addMenu("🔧 設定")
        
        # 1. 閒聊開關
        idle_action = QAction("開啟閒聊模式", self, checkable=True)
        idle_action.setChecked(self.idle_talk_enabled)
        idle_action.triggered.connect(self.toggle_idle_talk)
        settings_menu.addAction(idle_action)

        # 2. 移動開關
        move_action = QAction("啟用隨機移動", self, checkable=True)
        move_action.setChecked(self.movement_enabled)
        move_action.triggered.connect(self.toggle_movement)
        settings_menu.addAction(move_action)

        # 3. ★ 新增：Gemini 備援開關
        gemini_action = QAction("啟用雲端 Gemini 備援", self, checkable=True)
        gemini_action.setChecked(self.gemini_enabled)
        gemini_action.triggered.connect(self.toggle_gemini)
        settings_menu.addAction(gemini_action)

        menu.addSeparator()

        # 4. ★ 新增：記憶總結功能
        summary_action = QAction("🧠 讓 Doro 重新認識我 (總結記憶)", self)
        summary_action.triggered.connect(self.request_summary)
        menu.addAction(summary_action)

        history_action = QAction("📜 查看回憶 (歷史紀錄)", self)
        history_action.triggered.connect(self.open_history)
        menu.addAction(history_action)
        
        menu.addSeparator()
        quit_action = QAction("👋 讓 Doro 去睡覺 (關閉)", self)
        quit_action.triggered.connect(QApplication.instance().quit)
        menu.addAction(quit_action)
        
        menu.exec(event.globalPos())

    # --- 邏輯處理 ---
    def toggle_idle_talk(self, checked):
        self.idle_talk_enabled = checked
        user_config.set("idle_talk_enabled", checked)
        bus.idle_talk_toggled.emit(checked)

    def toggle_movement(self, checked):
        self.movement_enabled = checked
        user_config.set("movement_enabled", checked)
        bus.movement_toggled.emit(checked)

    def toggle_gemini(self, checked):
        """控制是否允許使用 Gemini 雲端大腦"""
        self.gemini_enabled = checked
        user_config.set("gemini_enabled", checked)
        print(f"🌐 Gemini 備援模式: {'開啟' if checked else '關閉'}")

    def request_summary(self):
        """觸發大腦去讀歷史紀錄做總結"""
        bus.user_sent_message.emit("[SYSTEM_REQUEST_SUMMARY]")

    def moveEvent(self, event):
        if self.chat_bubble.isVisible():
            self.chat_bubble.move(self.pos().x(), self.pos().y() - self.chat_bubble.height() - 10)
        super().moveEvent(event)

    @pyqtSlot(str)
    def update_direction(self, new_direction):
        if new_direction == self.current_direction: return
        self.current_direction = new_direction
        self.label.movie().stop()
        self.label.setMovie(self.movie_left if new_direction == "left" else self.movie_right)
        self.label.movie().start()

    def display_reply(self, text):
        self.chat_bubble.show_text(text, self.pos().x(), self.pos().y())

    def open_history(self):
        if self.history_window is None: self.history_window = HistoryWindow()
        self.history_window.load_data()
        self.history_window.show()