import subprocess
import requests
import time
import os
import sys

def get_ollama_path():
    """
    動態尋找 ollama.exe 的絕對路徑
    """
    # 1. 嘗試用 'where' 指令找 (這是最準的)
    try:
        result = subprocess.run("where ollama", shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout.splitlines()[0].strip()
    except:
        pass

    # 2. 嘗試預設的安裝路徑 (Windows 預設位置)
    local_app_data = os.environ.get("LOCALAPPDATA", "")
    default_path = os.path.join(local_app_data, "Programs", "Ollama", "ollama.exe")
    if os.path.exists(default_path):
        return default_path

    # 3. 最後一搏：直接回傳指令名稱
    return "ollama"

def ensure_ollama_running():
    ollama_url = "http://localhost:11434"
    model_name = "gemma2:2b"
    
    # 取得絕對路徑
    exe_path = get_ollama_path()
    print(f"🔍 偵測到 Ollama 路徑: {exe_path}")

    # 1. 啟動伺服器
    if not is_ollama_ready(ollama_url):
        print("🔄 正在背景喚醒地端大腦...")
        
        # 針對 Windows 的隱藏視窗設定
        creationflags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
        
        try:
            # 使用絕對路徑啟動，避開 PATH 找不到的問題
            subprocess.Popen(
                [exe_path, "serve"], 
                creationflags=creationflags,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            
            # 等待伺服器就緒
            for _ in range(15):
                if is_ollama_ready(ollama_url):
                    print(" ✅ 伺服器已啟動！")
                    break
                time.sleep(1)
                print(".", end="", flush=True)
        except Exception as e:
            print(f"\n❌ 無法啟動 Ollama: {e}")
            return

    # 2. 檢查並下載模型 (使用絕對路徑)
    check_and_pull_model(exe_path, model_name)

def check_and_pull_model(exe_path, model_name):
    print(f"📦 正在檢查模型 {model_name}...")
    try:
        # 使用絕對路徑執行 list
        result = subprocess.run(
            [exe_path, "list"], 
            capture_output=True, 
            text=True, 
            encoding='utf-8',
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
        )
        
        if model_name not in result.stdout:
            print(f"🚀 正在為 Doro 安裝大腦 ({model_name})...")
            # 使用 Popen 執行 pull，這樣不會卡住主程式太久
            subprocess.run([exe_path, "pull", model_name])
            print(f"✨ 安裝完成！")
        else:
            print(f"✅ 模型已就緒。")
    except Exception as e:
        print(f"⚠️ 模型檢查失敗: {e}")

def is_ollama_ready(url):
    try:
        return requests.get(url, timeout=1).status_code == 200
    except:
        return False