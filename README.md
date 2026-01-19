# acti-window-logger

# RiNgo-Tools: 自動日報生成ツール 🍎

**RiNgo-Tools** は、Windows PCのアクティブウィンドウ履歴を自動で記録し、そのログデータを元に Azure OpenAI (GPT) を使用して「業務日報」を自動生成するツールセットです。

## 🚀 特徴

1. **自動ロギング**: 作業中のアプリケーション名とウィンドウタイトルをバックグラウンドで監視・記録します。
2. **プライバシー配慮**: ウィンドウが切り替わったタイミングやタイトルが変化した時のみログを保存するため、データ量を抑制します。
3. **AIによる日報生成**: Azure OpenAI API を利用し、ログデータを解析して「業務サマリ」「タイムライン」「振り返り」を含むMarkdown形式の日報を作成します。
4. **CSVエクスポート**: 記録された生データをCSVとして出力し、Excel等で分析することも可能です。

## 📂 ファイル構成

本ツールの動作に必要なファイル構成は以下の通りです。

```text
.
├── window_logger.py      # 常駐してウィンドウ情報を記録するスクリプト
├── generate_report.py    # ログを読み込み、AIで日報を生成するスクリプト
├── dataview.py           # DBの内容をCSV出力するツール
├── window_log.db         # ログ保存用データベース（初回実行時に自動生成）
├── .env                  # APIキー設定ファイル（作成が必要）
└── llm/
    └── prompt.txt        # AIへの命令書（プロンプトテンプレート）

```

> 
> **注意**: `generate_report.py` は `llm/prompt.txt` を読み込みます 。配布されている `prompt.txt` は `llm` フォルダを作成してその中に入れてください。
> 
> 

## 🛠️ 必要要件 (Requirements)

* OS: Windows (win32 APIを使用するため) 


* Python 3.x
* Azure OpenAI Service の利用環境

### 依存ライブラリのインストール

以下のコマンドで必要なライブラリをインストールしてください。

```bash
pip install pywin32 psutil openai python-dotenv

```

※ `requirements.txt` に記載されている `cx_Freeze` 等は、exe化する場合にのみ必要です 。

## ⚙️ 設定 (Configuration)

プロジェクトのルートディレクトリに `.env` ファイルを作成し、Azure OpenAI の接続情報を記述してください。

```ini
AZURE_OPENAI_API_KEY=your_api_key_here
AZURE_OPENAI_API_VERSION=2023-05-15
AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=your_deployment_name

```

## 📖 使い方 (Usage)

### 1. ログの記録開始

業務を開始する際に、以下のコマンドでロガーを起動します。

```bash
python window_logger.py

```

* 実行中はリアルタイムでウィンドウの切り替えを監視し、`window_log.db` に保存します 。


* 終了する際は、ターミナルで `Ctrl + C` を押してください。

### 2. 日報の生成

業務終了後、以下のコマンドを実行して日報を作成します。

```bash
python generate_report.py

```

* データベースからログを読み込み、Azure OpenAI に送信します。
* 実行完了後、同じディレクトリに `[RiNgo-Tools]日次業務レポート_yyyymmdd.md` というファイルが生成されます 。



### 3. 生データの確認 (オプション)

データベースの中身をCSVで確認したい場合は、以下を実行します。

```bash
python dataview.py

```

* 
`exported_logs.csv` が出力されます 。



## 🤖 プロンプトのカスタマイズ

`llm/prompt.txt` を編集することで、日報の出力フォーマットやAIのキャラ付けを変更できます。デフォルトでは「プロジェクトマネージャー補佐」として振る舞い、業務のグルーピングや時間の要約を行うよう設定されています 。

## ⚠️ 免責事項

* 本ツールは `win32gui` を使用してウィンドウタイトルを取得します。機密情報がタイトルに含まれるアプリケーションの使用にはご注意ください。
* ログデータはローカルの `window_log.db` (SQLite) に保存されますが、レポート生成時には Azure OpenAI へテキストデータとして送信されます。会社のセキュリティポリシーに従ってご利用ください。