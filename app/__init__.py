from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from flask_migrate import Migrate
from flask_login import LoginManager
import openai
import os

app = Flask(__name__)

# ここに必要な設定を追加
app.config["SECRET_KEY"] = os.urandom(24)
#開発環境
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://admin:M19970616@localhost/spread_db"
#本番環境
#app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://admin:M19970616@spread-rds.cltnutjgc2rp.ap-northeast-1.rds.amazonaws.com/spread_db"
app.config["SESSION_TYPE"] = "filesystem"

db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager()
#login_manager.login_view = "login"
login_manager.init_app(app)
Session(app)

# 他の拡張機能を初期化する場合、ここで初期化
openai.api_key = os.getenv("OPENAI_API_KEY")

from app import routes, models
