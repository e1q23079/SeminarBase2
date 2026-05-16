from ..models import Seminar, File
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from ..lib.authorization import (
    MemberAuthorizationMixin,
    ManagerAuthorizationMixin
)


class LoginMemberRequiredMixin(MemberAuthorizationMixin):
    """
    メンバー権限を要求するミックスイン
    """
    def dispatch(self, request, *args, **kwargs):
        # セミナーIDを取得
        seminar_id = kwargs.get('seminar_id')
        file_uuid = kwargs.get('uuid')
        if seminar_id:
            seminar = get_object_or_404(Seminar, uuid=seminar_id)
            # 参加者アクセス権限がある場合はリクエストを処理する
            if self.is_member_access(request.user, seminar):
                return super().dispatch(request, *args, **kwargs)
        elif file_uuid:
            # ファイルUUIDがある場合はセミナーを取得
            file = get_object_or_404(File, uuid=file_uuid)
            # 参加者アクセス権限がある場合はリクエストを処理する
            if self.is_member_access(request.user, file.seminar):
                return super().dispatch(request, *args, **kwargs)
        # それ以外はアクセス拒否する
        raise PermissionDenied


class LoginManagerRequiredMixin(ManagerAuthorizationMixin):
    """
    マネージャー権限を要求するミックスイン
    """
    def dispatch(self, request, *args, **kwargs):
        # セミナーIDを取得
        seminar_id = kwargs.get('seminar_id')
        if seminar_id:
            seminar = get_object_or_404(Seminar, uuid=seminar_id)
            # マネージャーアクセス権限がある場合はリクエストを処理する
            if self.is_manager_access(request.user, seminar):
                return super().dispatch(request, *args, **kwargs)
        else:
            # マネージャーアクセス権限がある場合はリクエストを処理する
            if self.is_manager_access(request.user):
                return super().dispatch(request, *args, **kwargs)
        # それ以外はアクセス拒否する
        raise PermissionDenied
