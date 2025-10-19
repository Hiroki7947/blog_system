from flask import Flask, render_template, request, redirect, url_for, flash, abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager, UserMixin, login_user, logout_user,
    login_required, current_user
)
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

# Flaskアプリの初期化
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET', 'dev-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# DBとログインマネージャの初期化
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# ------------------- モデル定義 -------------------
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    articles = db.relationship('Article', backref='author', lazy=True)
    comments = db.relationship('Comment', backref='author', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    body = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    comments = db.relationship('Comment', backref='article', lazy=True, cascade='all, delete-orphan')


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    article_id = db.Column(db.Integer, db.ForeignKey('article.id'), nullable=False)


# ------------------- ログイン管理 -------------------
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ------------------- フィルター -------------------
@app.template_filter('nl2br')
def nl2br(value):
    """改行を<br>に変換する"""
    return value.replace('\n', '<br>')


# ------------------- ルート -------------------
@app.route('/')
def index():
    articles = Article.query.order_by(Article.created_at.desc()).all()
    return render_template('index.html', articles=articles)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        if User.query.filter((User.username == username) | (User.email == email)).first():
            flash('ユーザー名またはメールアドレスが既に使用されています。', 'danger')
            return redirect(url_for('register'))

        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash('登録が完了しました。ログインしてください。', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        identifier = request.form['identifier']
        password = request.form['password']
        user = User.query.filter(
            (User.username == identifier) | (User.email == identifier)
        ).first()

        if user and user.check_password(password):
            login_user(user)
            flash('ログインしました。', 'success')
            return redirect(url_for('index'))
        flash('ユーザー名またはパスワードが正しくありません。', 'danger')

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('ログアウトしました。', 'info')
    return redirect(url_for('index'))


@app.route('/article/new', methods=['GET', 'POST'])
@login_required
def new_article():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        article = Article(title=title, body=body, author=current_user)
        db.session.add(article)
        db.session.commit()
        flash('記事を投稿しました。', 'success')
        return redirect(url_for('index'))
    return render_template('new_article.html')


@app.route('/article/<int:article_id>')
def view_article(article_id):
    article = Article.query.get_or_404(article_id)
    return render_template('view_article.html', article=article)


@app.route('/article/<int:article_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_article(article_id):
    article = Article.query.get_or_404(article_id)
    if article.user_id != current_user.id:
        abort(403)

    if request.method == 'POST':
        article.title = request.form['title']
        article.body = request.form['body']
        db.session.commit()
        flash('記事を更新しました。', 'success')
        return redirect(url_for('view_article', article_id=article.id))

    return render_template('edit_article.html', article=article)


@app.route('/article/<int:article_id>/comment', methods=['POST'])
@login_required
def add_comment(article_id):
    article = Article.query.get_or_404(article_id)
    body = request.form['body']
    if not body.strip():
        flash('コメントを入力してください。', 'danger')
        return redirect(url_for('view_article', article_id=article_id))

    comment = Comment(body=body, author=current_user, article=article)
    db.session.add(comment)
    db.session.commit()
    flash('コメントを投稿しました。', 'success')
    return redirect(url_for('view_article', article_id=article_id))


# ------------------- メイン -------------------
if __name__ == '__main__':
    with app.app_context():
        if not os.path.exists('blog.db'):
            db.create_all()
            print('✅ blog.db を作成しました。')
    app.run(debug=True)
