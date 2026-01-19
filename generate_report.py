import os
import sqlite3
import csv
import io
from datetime import datetime
from dotenv import load_dotenv
from openai import AzureOpenAI

# .envファイルの読み込み
load_dotenv()

# --- 設定 ---
DB_NAME = "window_log.db"
PROMPT_FILE = "llm/prompt.txt"

# Azure OpenAI クライアントの設定
client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)

def get_logs_as_csv():
    """DBからログを取得してCSV文字列として返す"""
    if not os.path.exists(DB_NAME):
        print(f"エラー: データベース {DB_NAME} が見つかりません。")
        return ""

    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        # 時系列順(ASC)ですべて取得
        cursor.execute("SELECT id, user_name, window_title, app_name, timestamp FROM active_window_logs ORDER BY id ASC")
        rows = cursor.fetchall()

        # カラム名取得
        headers = [description[0] for description in cursor.description]
        conn.close()

        if not rows:
            return ""

        # CSVをメモリ上の文字列バッファに書き込む
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(headers)
        writer.writerows(rows)
        
        return output.getvalue()

    except Exception as e:
        print(f"DB読み込みエラー: {e}")
        return ""

def generate_report_content(csv_data):
    """Azure OpenAIにCSVデータを渡して日報を生成する"""
    if not csv_data:
        return "ログデータがありませんでした。"

    # プロンプトファイルの読み込み
    try:
        with open(PROMPT_FILE, "r", encoding="utf-8") as f:
            prompt_template = f.read()
    except FileNotFoundError:
        print(f"エラー: {PROMPT_FILE} が見つかりません。")
        return None

    # {{DATA}} を CSVデータに置換
    full_prompt = prompt_template.replace("{{DATA}}", csv_data)

    print("Azure OpenAI にリクエストを送信中...")
    
    try:
        response = client.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
            messages=[
                {"role": "system", "content": "あなたは優秀な日報作成アシスタントです。"},
                {"role": "user", "content": full_prompt}
            ],
            temperature=0.7,
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Azure OpenAI API エラー: {e}")
        return None

def main():
    # 1. DBからCSVデータ作成
    csv_logs = get_logs_as_csv()
    if not csv_logs:
        print("ログデータが存在しないため、処理を終了します。")
        return

    # 2. Azure OpenAI で日報生成
    report_markdown = generate_report_content(csv_logs)
    
    if report_markdown:
        # ファイル名を生成: [RiNgo-Tools]日次業務レポート_yyyyMMdd.md
        today_str = datetime.now().strftime("%Y%m%d")
        output_filename = f"[RiNgo-Tools]日次業務レポート_{today_str}.md"

        try:
            with open(output_filename, "w", encoding="utf-8") as f:
                f.write(report_markdown)
            print(f"レポート保存完了: {output_filename}")
        except Exception as e:
            print(f"ファイル保存エラー: {e}")

if __name__ == "__main__":
    main()