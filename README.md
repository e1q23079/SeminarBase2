# SeminarBase2

このアプリケーションは，資料の共有を行うウェブアプリケーションです。

## ウェブアプリケーションの起動
```bash
# コンテナビルド
docker compose build
# コンテナを起動
docker compose up -d
```

## ウェブアプリケーションのURLを確認する
```bash
sh docker-logs.sh
```

## ウェブアプリケーションの終了
```bash
# コンテナを終了
docker compose down
```

## 環境変数

- `SECRET_KEY`：シークレットキー
- `DEBUG`：デバッグモード
- `ALLOWED_HOSTS`：許可するホスト

### 開発環境
- `.env`：`./app/.env`
### 本番環境
- `.env`：`.env`

## 開発環境起動
```bash
# appディレクトリに移動
cd app
# 開発環境起動
python3 manage.py runserver
```