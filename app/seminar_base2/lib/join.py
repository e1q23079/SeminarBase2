from datetime import datetime, timedelta


def get_join_valid_until(now: datetime) -> datetime:
    """
    参加受付コードの有効期限を取得する関数
    """
    # 有効期限は1分後
    valid_until = now + timedelta(minutes=1)
    return valid_until


def is_join_valid(join_issued_at: datetime, now: datetime) -> bool:
    """
    参加受付コードが有効かどうかを判定する関数
    """
    # 有効期限は1分後
    valid_until = join_issued_at + timedelta(minutes=1)
    return now <= valid_until
