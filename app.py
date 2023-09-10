from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pytz

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///spread.db"
db = SQLAlchemy(app)

class Post(db.Model):
    __tablename__ = 'post'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    body = db.Column(db.String(300), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now(pytz.timezone('Asia/Tokyo')))

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        posts = Post.query.all()
        return render_template('index.html', posts=posts)

@app.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        title = request.form.get('title')
        body = request.form.get('body')

        with app.app_context():
            db.create_all()
            post = Post(title=title, body=body)
            db.session.add(post)
            db.session.commit()

        return redirect('/')

    else:
        return render_template('create.html')


@app.route('/<int:id>/update', methods=['GET', 'POST'])
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
        return redirect('/')

@app.route('/<int:id>/delete', methods=['GET'])
def delete(id):
    with app.app_context():
        post = Post.query.get(id)
        db.session.delete(post)
        db.session.commit()
    return redirect('/')

'''
    if request.method == 'GETT':
        title = request.form.get('title')
        body = request.form.get('body')

        with app.app_context():
            db.create_all()
            post = Post(title=title, body=body)
            db.session.add(post)
            db.session.commit()

        return redirect('/')

    else:
        return render_template('create.html')

'''