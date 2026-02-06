import os
from dotenv import load_dotenv

# 取得專案根目錄
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# --- 載入 .env 檔案 ---
load_dotenv(os.path.join(BASE_DIR, ".env"))

# --- 核心設定 ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# --- 視窗與路徑設定 (維持原樣) ---
PET_SIZE = 128
WINDOW_SIZE = 128
GIF_PATH_LEFT = os.path.join(BASE_DIR, "assets", "doro_left.gif")
GIF_PATH_RIGHT = os.path.join(BASE_DIR, "assets", "doro_right.gif")

# --- 行為設定 ---
MOVE_INTERVAL = 3000
ANIMATION_DURATION = 1500
IDLE_CHANCE = 0.6