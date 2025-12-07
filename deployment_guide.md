# US Stock Analyzerアプリのデプロイ手順書

このガイドでは、US Stock AnalyzerアプリをStreamlit Community Cloudで無料デプロイする手順を説明します。

## 📋 前提条件

- GitHubアカウント
- US Stock Analyzerアプリのコード（ローカル環境）
- インターネット接続

## 🚀 デプロイ手順

### ステップ1: GitHubリポジトリの作成とコードのプッシュ

#### 1.1 GitHubで新規リポジトリを作成

1. [GitHub](https://github.com)にログイン
2. 右上の「+」→「New repository」をクリック
3. リポジトリ情報を入力：
   - **Repository name**: `us-stock-analyzer`（任意の名前）
   - **Description**: `US Stock Analysis App with Streamlit`（任意）
   - **Public/Private**: どちらでも可（無料プランではPublicを推奨）
   - **Initialize this repository with**: 何もチェックしない
4. 「Create repository」をクリック

#### 1.2 ローカルリポジトリの初期化とプッシュ

ターミナル（PowerShell）で以下のコマンドを実行：

```powershell
# プロジェクトディレクトリに移動
cd c:\Users\mkdel\Desktop\dev\us-stock-analyzer

# Gitリポジトリを初期化（まだの場合）
git init

# すべてのファイルをステージング
git add .

# 初回コミット
git commit -m "Initial commit: US Stock Analyzer app"

# GitHubリポジトリをリモートとして追加
# ⚠️ 以下のURLは自分のGitHubユーザー名とリポジトリ名に置き換えてください
git remote add origin https://github.com/YOUR_USERNAME/us-stock-analyzer.git

# メインブランチにプッシュ
git branch -M main
git push -u origin main
```

> [!IMPORTANT]
> `.streamlit/secrets.toml`ファイルは`.gitignore`で除外されているため、GitHubにはプッシュされません。これはセキュリティ上重要です。

---

### ステップ2: Streamlit Community Cloudでアプリをデプロイ

#### 2.1 Streamlit Community Cloudにアクセス

1. [share.streamlit.io](https://share.streamlit.io)にアクセス
2. 「Sign in with GitHub」をクリック
3. GitHubアカウントでサインイン
4. 必要に応じてStreamlitへのアクセス権限を承認

#### 2.2 新しいアプリをデプロイ

1. ダッシュボードで「New app」ボタンをクリック
2. デプロイ設定を入力：
   - **Repository**: `YOUR_USERNAME/us-stock-analyzer`を選択
   - **Branch**: `main`を選択
   - **Main file path**: `app.py`を入力
   - **App URL** (optional): カスタムURLを設定（例：`us-stock-analyzer`）
3. 「Deploy!」ボタンをクリック

デプロイが開始されます。初回は数分かかる場合があります。

---

### ステップ3: Secretsの設定（パスワード認証）

デプロイ後、パスワード認証を機能させるためにSecretsを設定します。

#### 3.1 Secrets設定画面へのアクセス方法

**方法1: ダッシュボードから**

1. [share.streamlit.io](https://share.streamlit.io)のダッシュボードに移動
2. デプロイしたアプリを見つける
3. アプリの右側にある「⚙️」（歯車アイコン）または「⋮」メニューをクリック
4. 「Settings」を選択

**方法2: URLから直接アクセス**

```
https://your-app-name.streamlit.app/~/settings
```

#### 3.2 Secretsを追加

1. 設定画面で「**Secrets**」タブを選択
2. テキストエリアに以下の内容を貼り付け：

```toml
[passwords]
app_password = "your_secure_password_here"
```

3. `your_secure_password_here`を任意のパスワードに変更
4. 「Save」ボタンをクリック

> [!TIP]
> 強力なパスワードを使用することをお勧めします。例：`StockAnalyzer2024!Secure`

#### 3.3 アプリを再起動

1. 設定画面またはアプリ画面で「**Reboot app**」をクリック
2. アプリが再起動されるまで待機（数秒）

---

### ステップ4: デプロイの確認

#### 4.1 アプリにアクセス

1. ブラウザで生成されたURLにアクセス（例：`https://your-app-name.streamlit.app`）
2. パスワード入力画面が表示されることを確認
3. Secretsで設定したパスワードを入力
4. ログイン成功後、アプリが正常に動作することを確認

#### 4.2 機能テスト

以下の機能が正常に動作することを確認：

- ✅ パスワード認証
- ✅ Single Stock Analysis（銘柄分析）
- ✅ Stock Screener（銘柄スクリーニング）
- ✅ チャート表示（価格、RSI、MACD）

---

## 🔄 アプリの更新方法

コードを変更した場合、以下の手順で自動的にデプロイが更新されます：

```powershell
# 変更をコミット
git add .
git commit -m "Update: description of changes"

# GitHubにプッシュ
git push origin main
```

Streamlit Community Cloudが自動的に変更を検出し、アプリを再デプロイします。

---

## 🔐 パスワードの変更方法

### オンライン（デプロイ済みアプリ）

1. Streamlit Community Cloudのダッシュボードにアクセス
2. アプリの「Settings」→「Secrets」を開く
3. `app_password`の値を変更
4. 「Save」をクリック
5. 「Reboot app」でアプリを再起動

### ローカル環境

1. `.streamlit/secrets.toml`ファイルを開く
2. `app_password`の値を変更
3. ファイルを保存
4. Streamlitアプリを再起動（`Ctrl+C`で停止後、`streamlit run app.py`で再起動）

---

## 🛠️ トラブルシューティング

### エラー: "Secrets file not found" または "st.secrets has no key 'passwords'"

**原因**: Secretsが設定されていない

**解決方法**:

1. アプリの設定画面を開く（`https://your-app-name.streamlit.app/~/settings`）
2. 「Secrets」タブを選択
3. パスワード設定を追加：

   ```toml
   [passwords]
   app_password = "your_password"
   ```

4. 保存してアプリを再起動

### エラー: "Module not found"

**原因**: `requirements.txt`に必要なパッケージが記載されていない

**解決方法**:

1. `requirements.txt`を確認
2. 不足しているパッケージを追加
3. GitHubにプッシュして再デプロイ

### アプリが起動しない

**原因**: コードにエラーがある可能性

**解決方法**:

1. Streamlit Community Cloudのログを確認
2. ローカル環境で`streamlit run app.py`を実行してエラーを確認
3. エラーを修正してGitHubにプッシュ

### Secretsタブが見つからない

**原因**: UI変更または権限の問題

**解決方法**:

1. URLから直接アクセス：`https://your-app-name.streamlit.app/~/settings`
2. ブラウザのキャッシュをクリアして再読み込み
3. 別のブラウザで試す

---

## 📊 リソース制限

Streamlit Community Cloudの無料プランには以下の制限があります：

- **アプリ数**: 最大3つ
- **リソース**: 1GB RAM、1 CPU
- **ストレージ**: 限定的
- **スリープ**: 一定時間アクセスがないとスリープ状態になる可能性

これらの制限は個人使用や小規模プロジェクトには十分です。

---

## 🔗 参考リンク

- [Streamlit Community Cloud公式ドキュメント](https://docs.streamlit.io/streamlit-community-cloud)
- [Streamlit Secrets管理](https://docs.streamlit.io/streamlit-community-cloud/deploy-your-app/secrets-management)
- [GitHub公式ドキュメント](https://docs.github.com)

---

## ✅ チェックリスト

デプロイ完了前に以下を確認：

- [ ] GitHubリポジトリが作成されている
- [ ] コードがGitHubにプッシュされている
- [ ] `.streamlit/secrets.toml`が`.gitignore`に含まれている
- [ ] Streamlit Community Cloudでアプリがデプロイされている
- [ ] Secretsが正しく設定されている
- [ ] パスワード認証が動作している
- [ ] すべての機能が正常に動作している

おめでとうございます！🎉 アプリが正常にデプロイされました。
