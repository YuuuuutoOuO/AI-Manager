import sys
import os
from PyQt6.QtWidgets import QApplication

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.window import PetWindow
from features.movement.controller import MovementController
from features.brain.gemini_client import GeminiBrain
from features.voice.stt_handler import VoiceAssistant

def main():
    app = QApplication(sys.argv)
    
    # 1. 初始化大腦 (Gemini)
    brain = GeminiBrain()
    
    # 2. 初始化語音助手 (預留，暫不啟用)
    voice = VoiceAssistant()
    
    # 3. 初始化軀幹 (視窗)
    doro_window = PetWindow()
    
    # 4. 初始化移動
    move_ctrl = MovementController(doro_window)
    move_ctrl.start()
    
    doro_window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()