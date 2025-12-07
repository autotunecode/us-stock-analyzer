# US Stock Analysis App

米国株式分析アプリケーション - Streamlitで構築された株式スクリーニングと分析ツール

## 🔒 パスワード認証

このアプリケーションはパスワード保護されています。アクセスするには正しいパスワードを入力する必要があります。

### パスワードの変更方法

1. `.streamlit/secrets.toml` ファイルを開きます
2. `app_password` の値を変更します：

```toml
[passwords]
app_password = "your_new_password_here"
```

3. ファイルを保存します
4. アプリケーションを再起動します（ブラウザをリフレッシュ）

**デフォルトパスワード**: `StockAnalyzer2024`

⚠️ **セキュリティ注意**: `.streamlit/secrets.toml` ファイルは `.gitignore` に含まれており、Gitリポジトリにコミットされません。

## 📊 機能

### 1. 単一銘柄分析
- リアルタイム株価データ
- ファンダメンタル指標（PER、PBR、ROE）
- テクニカル分析（RSI、MACD、移動平均線）
- インタラクティブなチャート

### 2. 株式スクリーナー
複数の条件で銘柄をフィルタリング：
- **PER** (Price to Earnings Ratio)
- **PBR** (Price to Book Ratio)
- **ROE** (Return on Equity)
- **RSI** (Relative Strength Index)
- **MACD** (Moving Average Convergence Divergence)
- **時価総額** (Market Cap)
- **セクター** (Sector)

## 🚀 セットアップ

### 必要要件
- Python 3.8以上
- pip

### インストール

1. リポジトリをクローン：
```bash
git clone <repository-url>
cd us-stock-analyzer
```

2. 仮想環境を作成（推奨）：
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. 依存関係をインストール：
```bash
pip install -r requirements.txt
```

4. パスワードを設定：
   - `.streamlit/secrets.toml` ファイルが自動的に作成されます
   - 必要に応じてパスワードを変更してください

### 実行

```bash
streamlit run app.py
```

アプリケーションは `http://localhost:8501` で起動します。

## 📦 依存関係

- streamlit
- yfinance
- pandas
- plotly

## 🔧 設定

### パスワード設定
`.streamlit/secrets.toml`:
```toml
[passwords]
app_password = "your_password"
```

## 📝 使用方法

1. アプリケーションにアクセス
2. パスワードを入力
3. サイドバーから分析モードを選択：
   - **Single Stock Analysis**: 特定の銘柄を詳細分析
   - **Stock Screener**: 複数銘柄をフィルタリング
4. パラメータを設定して分析を実行

## 🛡️ セキュリティ

- パスワードは `.streamlit/secrets.toml` に保存されます
- このファイルは `.gitignore` に含まれており、バージョン管理されません
- パスワードはセッション中のみメモリに保持されます

## 📄 ライセンス

このプロジェクトは個人使用のために作成されています。

## 🤝 貢献

プルリクエストを歓迎します。大きな変更の場合は、まずissueを開いて変更内容を議論してください。
