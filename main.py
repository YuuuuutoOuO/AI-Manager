import sys
import os
from PyQt6.QtWidgets import QApplication

# 確保 Python 找得到模組
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.window import PetWindow
from features.movement.controller import MovementController
from features.brain.gemini_client import GeminiBrain
from features.history.storage import HistoryLogger
from features.brain.brain_router import BrainRouter

def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    
    # ★ 核心改動：初始化指揮官
    # 指揮官會自動初始化 LocalBrain 和 GeminiBrain
    app.router = BrainRouter() 
    
    app.history_logger = HistoryLogger()
    doro_window = PetWindow()
    move_ctrl = MovementController(doro_window)
    move_ctrl.start()
    
    doro_window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()