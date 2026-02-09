# nginxの公式イメージをベースに使用
FROM python:latest
# 作業ディレクトリを設定
WORKDIR /app
# pipを最新バージョンにアップグレード
RUN pip install --upgrade pip
# コンテナにrequirements.txtをコピー
COPY requirements.txt /app/
# 依存関係をインストール
RUN pip install --no-cache-dir -r requirements.txt
# アプリケーションコードをコンテナにコピー
COPY . /app/
# コンテナ起動時に実行されるコマンドを指定
CMD [ "sh", "start.sh" ]