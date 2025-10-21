# 📝 Flask Blog System

Flask を使用して構築されたシンプルかつモダンなデザインのブログシステムです。  
ユーザー登録・ログイン・記事投稿・編集・コメント機能など、  
基本的なブログ機能を備えた学習・個人利用向けのアプリケーションです。

---

## 🚀 主な機能

- 🔐 **ユーザー認証**
  - 新規登録 / ログイン / ログアウト  
  - `Flask-Login` によるセッション管理  

- 📰 **記事管理**
  - 記事の新規投稿  
  - 投稿者本人による記事編集  
  - 記事詳細ページの閲覧  

- 💬 **コメント機能**
  - ログインユーザーが記事にコメントを投稿可能  

- 🎨 **モダンなUI**
  - Bootstrap + カスタムCSSによる柔らかいデザイン  
  - レスポンシブ対応（PC / モバイル両方OK）  

---

## 🧱 使用技術

| カテゴリ | 使用技術 |
|-----------|-----------|
| バックエンド | Flask, Flask-Login, Flask-SQLAlchemy |
| データベース | SQLite |
| フロントエンド | HTML, Bootstrap 5, CSS (カスタムスタイル) |
| テンプレートエンジン | Jinja2 |
| 認証 | Werkzeug のパスワードハッシュ |

---


## ⚙️ セットアップ手順

### 1. 仮想環境の作成と有効化と起動
```bash
python3 -m venv venv
source venv/bin/activate  # macOS / Linux
# または
venv\Scripts\activate     # Windows

依存パッケージのインストール
pip install flask flask_sqlalchemy flask_login

アプリケーションの起動
python flask_blog_app.py

ブラウザで以下にアクセス：
👉 http://127.0.0.1:5000

