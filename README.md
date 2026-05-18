# SeminarBase2

このアプリケーションは，資料の共有を行うウェブアプリケーションです。

## ウェブアプリケーションの起動
### Cloudflare版
```bash
docker compose -f docker-compose.cloudflare.yml up -d --build
```

#### ウェブアプリケーションのURLを確認する
```bash
sh cloudflare_logs.sh
```

### Nginx版
```bash
# コンテナビルド
docker compose build
# コンテナを起動
docker compose up -d
```

## スクリプトで起動する
### Cloudflare版
```bash
sh start_cloudflare.sh
```
### Nginx版
```bash
sh start.sh
```


#### SSL
- `infra/ssl/nginx.crt`
- `infra/ssl/nginx.key`

#### migrate
```bash
# コンテナの中に入る
docker container exec -it SeminarBase2_web bash
# migrate
python3 manage.py migrate
```

## ウェブアプリケーションの終了
```bash
# コンテナを終了
docker compose down --remove-orphans
```

## 環境変数

- `SECRET_KEY`：シークレットキー
- `DEBUG`：デバッグモード
- `ALLOWED_HOSTS`：許可するホスト
- `CSRF_TRUSTED_ORIGINS`: CSRF保護で信頼するオリジン
- `EDITION`：バージョン

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