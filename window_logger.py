import time
import sqlite3
import os
import win32gui
import win32process
import psutil
from datetime import datetime, timezone, timedelta

# --- 設定 ---
DB_NAME = "window_log.db"
POLLING_INTERVAL = 0.5  # 監視間隔(秒)
JST = timezone(timedelta(hours=9), 'JST') # 日本標準時

def init_db():
    """データベースとテーブルの初期化"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS active_window_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_name TEXT,
            window_title TEXT,
            app_name TEXT,
            timestamp TEXT
        )
    ''')
    conn.commit()
    conn.close()

def get_active_window_info():
    """現在のアクティブウィンドウの情報を取得する"""
    try:
        hwnd = win32gui.GetForegroundWindow()
        if hwnd == 0:
            return None, None, None

        window_title = win32gui.GetWindowText(hwnd)
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        
        try:
            process = psutil.Process(pid)
            app_name = process.name()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            app_name = "Unknown"

        return hwnd, window_title, app_name

    except Exception as e:
        # print(f"Error: {e}") # エラーログがうるさい場合はコメントアウト
        return None, None, None

def save_log(user_name, window_title, app_name):
    """DBへログを保存"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    current_time = datetime.now(JST).strftime('%Y-%m-%d %H:%M:%S')
    
    cursor.execute('''
        INSERT INTO active_window_logs (user_name, window_title, app_name, timestamp)
        VALUES (?, ?, ?, ?)
    ''', (user_name, window_title, app_name, current_time))
    
    conn.commit()
    conn.close()
    print(f"[{current_time}] Logged: {app_name} - {window_title[:40]}...")

def main():
    print("詳細監視を開始します（タイトル変更も検知）... (停止: Ctrl+C)")
    init_db()
    
    last_hwnd = None
    last_title = None # 前回のタイトルを記憶する変数を追加
    
    current_user = os.getlogin()

    try:
        while True:
            current_hwnd, window_title, app_name = get_active_window_info()

            # ハンドルが取得でき、かつタイトルが空でない場合
            if current_hwnd is not None and window_title:
                
                # 条件変更: 
                # 1. アクティブなウィンドウ(アプリ)自体が切り替わった場合 (current_hwnd != last_hwnd)
                #    または
                # 2. 同じウィンドウだが、タイトルが変わった場合 (window_title != last_title)
                if (current_hwnd != last_hwnd) or (window_title != last_title):
                    
                    save_log(current_user, window_title, app_name)
                    
                    # 状態を更新
                    last_hwnd = current_hwnd
                    last_title = window_title

            time.sleep(POLLING_INTERVAL)

    except KeyboardInterrupt:
        print("\n監視を終了しました。")

if __name__ == "__main__":
    main()