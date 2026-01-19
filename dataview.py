import sqlite3
import csv

# DB接続
conn = sqlite3.connect("window_log.db")
cursor = conn.cursor()

# データを取得
# 変更点1: LIMIT 10 を削除（すべて取得するため）
# 変更点2: DESC(降順) を ASC(昇順) に変更（古い順＝時系列順に並べるため）
cursor.execute("SELECT * FROM active_window_logs ORDER BY id ASC")
rows = cursor.fetchall()

# カラム名（ヘッダー）を取得
headers = [description[0] for description in cursor.description]

# CSVファイルへの書き出し
output_file = "exported_logs.csv"

# WindowsのExcelで開くことを想定して 'utf-8-sig' に設定しています（文字化け防止）
with open(output_file, 'w', newline='', encoding='utf-8-sig') as f:
    writer = csv.writer(f)
    
    # ヘッダーを書き込み
    writer.writerow(headers)
    
    # 全データをまとめて書き込み
    writer.writerows(rows)

print(f"完了: {len(rows)} 件のデータを {output_file} にエクスポートしました。")

conn.close()