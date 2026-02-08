import sys
import os
from PyQt6.QtWidgets import QApplication

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.window import PetWindow
from features.movement.controller import MovementController
from features.brain.brain_router import BrainRouter
from features.history.storage import HistoryLogger
from core.service_manager import ensure_ollama_running

def main():
    # 1. ★ 在建立視窗之前，先確保大腦 (Ollama) 已經醒來
    ensure_ollama_running()

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    
    # 初始化大腦路由器
    router = BrainRouter()
    app.router = router
    
    # 初始化歷史紀錄
    app.history_logger = HistoryLogger()
    
    # 初始化視窗與移動
    doro_window = PetWindow()
    move_ctrl = MovementController(doro_window)
    move_ctrl.start()
    
    doro_window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()