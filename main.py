import sys
import os
from PyQt6.QtWidgets import QApplication

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.window import PetWindow
from features.movement.controller import MovementController
# from features.brain.gemini_client import GeminiBrain  <-- 這一行刪掉
from features.brain.brain_router import BrainRouter   # <-- 改用這個
from features.history.storage import HistoryLogger

def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    
    # ★ 初始化大腦路由器 (它會自動管理 Ollama 和 Gemini)
    router = BrainRouter()
    
    # 為了防止被 GC 回收，掛在 app 上
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