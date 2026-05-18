# nginxの公式イメージをベースに使用
FROM nginx:latest
# カスタムnginx設定ファイルをコピー
COPY defalt.conf /etc/nginx/conf.d/defalt.conf
# SSL証明書をコピー
COPY ssl/nginx.crt /etc/nginx/ssl/nginx.crt
COPY ssl/nginx.key /etc/nginx/ssl/nginx.key