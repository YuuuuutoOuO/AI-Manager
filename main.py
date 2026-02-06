import sys
import os
from PyQt6.QtWidgets import QApplication

# 確保 Python 找得到模組
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.window import PetWindow
from features.movement.controller import MovementController
from features.brain.gemini_client import GeminiBrain
from features.history.storage import HistoryLogger

def main():
    app = QApplication(sys.argv)
    
    # ★ 修正問題 2：防止關閉歷史視窗時導致 Doro 退出
    app.setQuitOnLastWindowClosed(False)
    
    # 1. 初始化大腦
    brain = GeminiBrain()
    
    # 2. ★ 修正問題 1：將 Logger 存入變數，確保它不會被回收
    # 我們可以將它設為全域或掛在 app 物件上
    app.history_logger = HistoryLogger()
    
    # 3. 初始化軀幹 (視窗)
    doro_window = PetWindow()
    
    # 4. 初始化移動
    move_ctrl = MovementController(doro_window)
    move_ctrl.start()
    
    doro_window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()