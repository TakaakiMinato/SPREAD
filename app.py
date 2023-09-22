from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pytz
from flask_login import UserMixin, LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os
from dotenv import load_dotenv

app = Flask(__name__)

load_dotenv()
db_user = os.environ.get("DB_USER")
db_password = os.environ.get("DB_PASSWORD")
db_host = os.environ.get("DB_HOST")
db_name = os.environ.get("DB_NAME")

#sqliteを使用する場合
#app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///spread.db"

#MYSQLを使用する場合
app.config["SQLALCHEMY_DATABASE_URI"] = f"mysql://{db_user}:{db_password}@{db_host}/{db_name}"

app.config["SECRET_KEY"] = os.urandom(24) 
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)

class Post(db.Model):
    __tablename__ = 'post'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), nullable=False)
    title = db.Column(db.String(50), nullable=False)
    body = db.Column(db.String(300), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now(pytz.timezone('Asia/Tokyo')))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True)
    password = db.Column(db.String(255))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()
        if check_password_hash(user.password, password):
            login_user(user)
            return redirect('/index')
    else:
        return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        with app.app_context():
            db.create_all()
            user = User(username=username, password=generate_password_hash(password, method='sha256'))
            db.session.add(user)
            db.session.commit()

        return redirect('/')

    else:
        return render_template('signup.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')

@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    if request.method == 'GET':
        posts = Post.query.all()
        username = current_user.username
        return render_template('index.html', posts=posts, username=username)

@app.route('/mypage', methods=['GET', 'POST'])
@login_required
def mypage():
    if request.method == 'GET':
      #  posts = Post.query.all()
        posts = Post.query.filter_by(username = current_user.username).all()

        return render_template('mypage.html', posts=posts)

@app.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        username = current_user.username
        title = request.form.get('title')
        body = request.form.get('body')

        with app.app_context():
            db.create_all()
            post = Post(username=username, title=title, body=body)
            db.session.add(post)
            db.session.commit()

        return redirect('/index')

    else:
        return render_template('create.html')



@app.route('/<int:id>/update', methods=['GET', 'POST'])
@login_required
def update(id):
    if request.method == 'GET':
        post = Post.query.get(id)
        return render_template('update.html', post=post)
    else:
        with app.app_context():
            post = Post.query.get(id)
            post.title = request.form.get('title')
            post.body = request.form.get('body')
            db.session.commit()
        return redirect('/mypage')

@app.route('/<int:id>/delete', methods=['GET'])
@login_required
def delete(id):
    with app.app_context():
        post = Post.query.get(id)
        db.session.delete(post)
        db.session.commit()
    return redirect('/mypage')

