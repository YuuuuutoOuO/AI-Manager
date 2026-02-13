import sys
import os
from PyQt6.QtWidgets import QApplication

# 1. 環境路徑修正：確保 Python 能找到專案內的所有資料夾
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 2. 匯入核心與功能模組
from core.window import PetWindow
from core.service_manager import ensure_ollama_running
from core.config_manager import user_config
from features.movement.controller import MovementController
from features.brain.brain_router import BrainRouter
from features.history.storage import HistoryLogger
from features.idle.idle_controller import IdleTalkController

def main():
    # --- A. 系統預備階段 ---
    # 在 GUI 啟動前，先確保地端 Ollama 服務與模型 (gemma2:2b) 已就緒
    # 這部分會處理路徑偵測與背景喚醒
    ensure_ollama_running()

    # --- B. 應用程式初始化 ---
    app = QApplication(sys.argv)
    
    # 核心設定：防止關閉歷史紀錄或設定視窗時，導致整隻 Doro 結束執行
    app.setQuitOnLastWindowClosed(False)
    
    # --- C. 背景邏輯模組 (掛載於 app 以防止被回收) ---
    
    # 1. 大腦路由器：管理地端與雲端 AI 的呼叫邏輯
    app.router = BrainRouter()
    
    # 2. 歷史紀錄器：負責將對話內容儲存至 chat_history.json
    app.history_logger = HistoryLogger()
    
    # 3. 閒聊控制器：負責處理隨機對話 (10-30秒)
    # 它會自動讀取 user_config.json 來決定初始狀態是否開啟
    app.idle_ctrl = IdleTalkController()
    
    # --- D. 視覺與運動模組 ---
    
    # 1. 建立 Doro 的主視窗 (包含右鍵選單與氣泡)
    doro_window = PetWindow()
    app.doro_window = doro_window
    
    # 2. 建立走路控制器：負責處理 Doro 在螢幕上的隨機移動
    move_ctrl = MovementController(doro_window)
    app.move_ctrl = move_ctrl
    move_ctrl.start()
    
    # --- E. 正式運行 ---
    # 顯示 Doro！
    doro_window.show()
    
    print("✨ Doro 已經成功喚醒囉！")
    sys.exit(app.exec())

if __name__ == "__main__":
    main()