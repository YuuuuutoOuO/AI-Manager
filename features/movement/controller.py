import random
from PyQt6.QtCore import QTimer, QPropertyAnimation, QRect
from PyQt6.QtWidgets import QApplication

from config import settings
from core.event_bus import bus

class MovementController:
    def __init__(self, window):
        self.window = window
        self.timer = QTimer()
        self.timer.timeout.connect(self.decide_action)
        self.screen_geo = QApplication.primaryScreen().availableGeometry()
        
        # 狀態控制
        self.is_moving_allowed = True
        self.anim = None

        # 訂閱事件
        bus.movement_toggled.connect(self.update_permission)
        bus.drag_started.connect(self.stop)
        bus.drag_ended.connect(self.start)

    def update_permission(self, enabled):
        """根據設定開關移動計時器"""
        self.is_moving_allowed = enabled
        if not enabled:
            self.stop()
        else:
            self.start()

    def start(self):
        if self.is_moving_allowed and not self.timer.isActive():
            self.timer.start(settings.MOVE_INTERVAL)

    def stop(self):
        self.timer.stop()
        if self.anim and self.anim.state() == QPropertyAnimation.State.Running:
            self.anim.stop()

    def decide_action(self):
        if not self.is_moving_allowed: return
        
        # 隨機機率原地發呆
        if random.random() < settings.IDLE_CHANCE:
            return

        # 1. 決定隨機位移量 (X 與 Y 軸)
        dist_x = random.randint(50, 150)
        dist_y = random.randint(30, 100)
        
        # 隨機正負方向
        dir_x = random.choice([-1, 1])
        dir_y = random.choice([-1, 1])

        current_pos = self.window.pos()
        
        # 2. 計算目標位置並處理邊界限制
        target_x = current_pos.x() + (dist_x * dir_x)
        target_y = current_pos.y() + (dist_y * dir_y)

        # 螢幕邊界檢查 (留下一些緩衝空間)
        target_x = max(10, min(target_x, self.screen_geo.width() - self.window.width() - 10))
        target_y = max(10, min(target_y, self.screen_geo.height() - self.window.height() - 10))

        # 3. 根據 X 軸位移決定面向方向 (Y 軸位移不影響 GIF)
        if target_x < current_pos.x():
            bus.direction_changed.emit("left")
        elif target_x > current_pos.x():
            bus.direction_changed.emit("right")

        # 4. 執行 2D 動畫移動
        if target_x != current_pos.x() or target_y != current_pos.y():
            self.animate_move(target_x, target_y)

    def animate_move(self, target_x, target_y):
        self.anim = QPropertyAnimation(self.window, b"geometry")
        self.anim.setDuration(settings.ANIMATION_DURATION)
        self.anim.setStartValue(self.window.geometry())
        self.anim.setEndValue(QRect(target_x, target_y, 
                                    self.window.width(), self.window.height()))
        self.anim.start()