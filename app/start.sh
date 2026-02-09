#!/bin/sh
# データベースマイグレーションを適用
python3 manage.py migrate --noinput
# 静的ファイルを収集
python3 manage.py collectstatic --noinput
# アプリケーションを起動
gunicorn --workers 3 app.wsgi:application --bind 0.0.0.0:8000