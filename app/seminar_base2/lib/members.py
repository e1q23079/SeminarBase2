from ..models import Seminar, Members


def get_last_request_time(seminar: Seminar):
    '''
    ユーザーのセミナーへの最後のリクエスト時間を取得する関数
    '''
    last_request_update_member = Members.objects.filter(
        seminar=seminar
    ).order_by(
        '-last_request'
    ).first()
    # 対象者が存在しない場合はNoneを返す
    if not last_request_update_member:
        return None
    return last_request_update_member.last_request
