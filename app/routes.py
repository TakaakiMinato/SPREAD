from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from app import app, db, login_manager
from app.models import User, Post, Setting
from datetime import datetime
import openai
import json
from sqlalchemy import desc



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
            if user.first_login:
                user.first_login = False
                db.session.commit()
                return redirect('/setting')
            else:
                return redirect('/index')
    else:
        return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User(username=username, password=generate_password_hash(password, method='sha256'))
        db.session.add(user)
        db.session.commit()
        return redirect('/')
    else:
        return render_template('signup.html')

@app.route('/setting', methods=['GET', 'POST'])
@login_required
def setting():
    if request.method == 'POST':
        user_id = current_user.id
        price = request.form.get('price')
        number = request.form.get('number')
        setting = Setting(user_id=user_id, price=price, number=number)
        db.session.add(setting)
        db.session.commit()
        return redirect('/index')
    else:
        return render_template('setting.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')

@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    if request.method == 'POST':
        username = current_user.username
        body = request.form.get('body')
        user_id = current_user.id
        post = Post(user_id=user_id,  username=username, body=body)
        db.session.add(post)
        db.session.commit()
        return redirect('/index')

    elif request.method == 'GET':
        posts = Post.query.all()
        username = current_user.username
        setting = Setting.query.filter_by(user_id = current_user.id).first()
        
        def generate_prompt(comment, duration):
            return """私は禁煙{}日目です。私は今、{}と考えています。
            禁煙継続を応援するコメントを生成してください
            """.format(
                duration, comment
            )

        comment = "まだ投稿はしていません。ユーザーに投稿を推薦するように促すコメントの生成を促してください"
        if Post.query.filter_by(user_id=current_user.id).first():
            comment = Post.query.filter_by(user_id=current_user.id).order_by(desc(Post.id)).first().body
        start_at = Setting.query.filter_by(user_id=current_user.id).first().start_at
        current_date = datetime.now().date()
        duration = (start_at.date() - current_date).days
     
       # response = openai.Completion.create(
       #     model="text-davinci-003",
       #     prompt=generate_prompt(comment, duration),
       #     max_tokens=100,
       #     temperature=1.0
       # )
       # generated_text = response.choices[0].text
       
        generated_text="禁煙頑張ってください"

        return render_template('index.html', generated_text=generated_text, setting=setting, posts=posts, username=username)

@app.route('/mypage', methods=['GET', 'POST'])
@login_required
def mypage():
    if request.method == 'GET':
        posts = Post.query.filter_by(username = current_user.username).all()
        return render_template('mypage.html', posts=posts)

@app.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        username = current_user.username
        title = request.form.get('title')
        body = request.form.get('body')
        user_id = current_user.id
        post = Post(user_id=user_id,  username=username, title=title, body=body)
        db.session.add(post)
        db.session.commit()
        return redirect('/index')
    else:
        return render_template('create.html')


@app.route('/delete-posts', methods=['POST'])
@login_required
def delete_selected_posts():
    data = request.get_json()
    post_ids = data.get('postIds', [])

    try:
        for post_id in post_ids:
            post = Post.query.get(post_id)
            if post:
                db.session.delete(post)
        db.session.commit()
        response = {'message': f'{len(post_ids)} 件の投稿が削除されました'}
    except Exception as e:
        db.session.rollback()
        response = {'error': '削除中にエラーが発生しました'}

    return jsonify(response)

