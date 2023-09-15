#!/usr/bin/python3

import sys
import logging

# Apacheログの設定
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0, '/var/www/SPREAD')

# Flaskアプリケーションのインポート
from app import app as application  # "your_app" はあなたの Flask アプリケーションの名前

# オプション: 仮想環境の有効化 (必要に応じて)
# activate_this = '/path/to/your/venv/bin/activate_this.py'
# with open(activate_this) as file_:
#     exec(file_.read(), dict(__file__=activate_this))

# アプリケーションの実行
if __name__ == '__main__':
    application.run()
