"""
啟動 ngrok 的腳本，自動從 .env 文件讀取 authtoken。
"""
import os
import subprocess
import sys
import time
from pathlib import Path
from dotenv import load_dotenv

def setup_ngrok():
    """
    從 .env 文件讀取 NGROK_AUTHTOKEN 並設置 ngrok。
    """
    # 加載環境變數
    env_path = Path(".") / ".env"
    load_dotenv(dotenv_path=env_path)
    
    # 獲取 ngrok authtoken
    authtoken = os.getenv("NGROK_AUTHTOKEN")
    
    if not authtoken or authtoken == "your_authtoken_here":
        print("請在 .env 文件中設置你的 NGROK_AUTHTOKEN")
        sys.exit(1)
    
    # 設置 ngrok authtoken
    subprocess.run(["ngrok", "config", "add-authtoken", authtoken])
    print("已成功設置 ngrok authtoken")

def start_ngrok_tunnel(port=8000):
    """
    啟動 ngrok 隧道，將特定端口暴露到公網。
    
    Args:
        port (int): 要暴露的本地端口，預設為 8000。
    """
    print(f"正在啟動 ngrok 隧道，將本地端口 {port} 暴露到公網...")
    
    # 啟動 ngrok 隧道
    process = subprocess.Popen(
        ["ngrok", "http", str(port)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True
    )
    
    # 等待隧道啟動
    time.sleep(3)
    
    # 獲取公網 URL
    try:
        tunnel_info = subprocess.check_output(["curl", "-s", "http://localhost:4040/api/tunnels"])
        print(f"ngrok 隧道已啟動。使用下面的 URL 來設置 LINE Webhook:\n{tunnel_info.decode('utf-8')}")
        print("\n保持這個終端窗口開啟，按 Ctrl+C 停止 ngrok")
        
        # 保持腳本運行
        process.wait()
    except subprocess.CalledProcessError:
        print("無法獲取 ngrok 隧道信息。請檢查 ngrok 是否正常運行。")
    except KeyboardInterrupt:
        print("\n正在停止 ngrok 隧道...")
        process.terminate()
        process.wait()
        print("ngrok 隧道已停止")

if __name__ == "__main__":
    # 設置 ngrok
    setup_ngrok()
    
    # 啟動隧道
    port = 8000
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    
    start_ngrok_tunnel(port) 