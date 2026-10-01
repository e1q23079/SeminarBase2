# Raspberry Pi セットアップ

## Dockerの実行設定
スワップ領域の状態を確認
```bash
sudo swapon --show
free -h
```

スワップ用ファイルの作成
```bash
sudo fallocate -l 2G /swapfile
```
権限の設定
```bash
sudo chmod 600 /swapfile
```

ファイルをスワップ形式に初期化&有効化
```bash
sudo mkswap /swapfile
sudo swapon /swapfile
```

設定を永続化
```bash
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```
