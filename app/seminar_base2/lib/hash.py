import hashlib


def generate_hash(timestamp):
    '''
    タイムスタンプからSHA-256ハッシュを生成する関数
    '''
    return hashlib.sha256(str(timestamp).encode()).hexdigest()
