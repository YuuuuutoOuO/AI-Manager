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
        
        bus.drag_started.connect(self.stop)
        bus.drag_ended.connect(self.start)

    def start(self):
        if not self.timer.isActive():
            self.timer.start(settings.MOVE_INTERVAL)

    def stop(self):
        self.timer.stop()

    def decide_action(self):
        if random.random() < settings.IDLE_CHANCE:
            return

        # 決定方向
        direction = random.choice(["left", "right"])
        
        # ★ 重要：告訴 Event Bus 現在要面向哪邊
        bus.direction_changed.emit(direction)
        
        distance = random.randint(50, 150)
        current_pos = self.window.pos()
        target_x = current_pos.x()
        
        if direction == "left":
            target_x = max(0, current_pos.x() - distance)
        elif direction == "right":
            target_x = min(self.screen_geo.width() - self.window.width(), 
                           current_pos.x() + distance)

        if target_x != current_pos.x():
            self.animate_move(target_x, current_pos.y())

    def animate_move(self, target_x, target_y):
        self.anim = QPropertyAnimation(self.window, b"geometry")
        self.anim.setDuration(settings.ANIMATION_DURATION)
        self.anim.setStartValue(self.window.geometry())
        self.anim.setEndValue(QRect(target_x, target_y, 
                                    self.window.width(), self.window.height()))
        self.anim.start()