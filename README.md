# Gift Image Creator (Streamlit)

## セットアップ

1.  **仮想環境の作成と有効化**:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

2.  **依存ライブラリのインストール**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **APIキーの設定**:
    `.env.example` を `.env` にリネームし、Google APIキーを設定してください。
    ```bash
    cp .env.example .env
    # .envファイルを開いてAPIキーを編集
    ```

## 実行方法

以下のコマンドでアプリを起動します。

```bash
# 仮想環境が有効になっていない場合は有効化してください
# source venv/bin/activate

streamlit run app.py
```

ブラウザが自動的に開き、アプリが表示されます。

## Streamlit Cloudへのデプロイ

### 前提条件
- GitHubアカウント
- Streamlit Cloudアカウント（[https://streamlit.io/cloud](https://streamlit.io/cloud)で無料登録可能）
- リポジトリ名: `selectable-gift-image-creator`

### デプロイ手順

1. **GitHubにリポジトリを作成・プッシュ**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/selectable-gift-image-creator.git
   git push -u origin main
   ```

2. **Streamlit Cloudでアプリをデプロイ**
   - [Streamlit Cloud](https://share.streamlit.io/)にログイン
   - "New app" をクリック
   - リポジトリ: `selectable-gift-image-creator` を選択
   - Branch: `main` を選択
   - Main file path: `app.py` を指定

3. **環境変数の設定**
   - Streamlit Cloudのアプリ設定画面で "Secrets" タブを開く
   - 以下の形式でシークレットを追加:
     ```toml
     GOOGLE_API_KEY = "your-google-api-key-here"
     ```
   - または、アプリのサイドバーから直接APIキーを入力することも可能です

4. **デプロイ完了**
   - デプロイが完了すると、自動的にアプリのURLが生成されます
   - 例: `https://YOUR_APP_NAME.streamlit.app`

### 注意事項
- `.env`ファイルはGitHubにコミットしないでください（`.gitignore`に追加推奨）
- APIキーは必ずStreamlit CloudのSecrets機能を使用してください
- `templates/`フォルダ内の画像ファイルもリポジトリに含める必要があります
