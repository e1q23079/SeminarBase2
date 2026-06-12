from django.views import View
from django.http import Http404
from django.utils import timezone
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Seminar, Members

from .lib.members import get_last_request_time
from .lib.hash import generate_hash
from .lib.login import LoginMemberRequiredMixin, LoginManagerRequiredMixin


class RequestHashView(LoginRequiredMixin, LoginManagerRequiredMixin, View):
    '''
    リクエストハッシュのビュー
    '''
    def get(self, request, *args, **kwargs):
        seminar_id = kwargs.get('seminar_id')
        # セミナーIDに対応するセミナーを取得する
        seminar = Seminar.objects.filter(uuid=seminar_id).first()
        if not seminar:
            return JsonResponse(
                {
                    'status': 'error',
                    'message': 'セミナーが見つかりませんでした'
                },
                status=404
            )
        # 管理モードでない場合は404エラー
        if not seminar.manage:
            raise Http404("This seminar is not in management mode.")
        # セミナーの最後のリクエスト時間を取得する
        last_request_time = get_last_request_time(seminar)
        # タイムスタンプからハッシュを生成する
        hash_value = generate_hash(last_request_time)
        # リクエスト人数
        request_count = Members.objects.filter(
            seminar=seminar,
            request=True
        ).count()
        # 時間
        now_time = timezone.localtime()
        format_time = now_time.strftime('%Y-%m-%d %H:%M:%S')
        return JsonResponse(
            {
                'status': 'success',
                'hash': hash_value,
                'time': format_time,
                'request_count': request_count
            }
        )


class RequestView(LoginRequiredMixin, LoginMemberRequiredMixin, View):
    '''
    リクエストのビュー
    '''
    def post(self, request, *args, **kwargs):
        seminar_id = kwargs.get('seminar_id')
        # セミナーIDに対応するセミナーを取得する
        seminar = Seminar.objects.filter(uuid=seminar_id).first()
        if not seminar:
            return JsonResponse(
                {
                    'status': 'error',
                    'message': 'セミナーが見つかりませんでした'
                },
                status=404
            )
        # 管理モードでない場合は403エラー
        if not seminar.manage:
            return JsonResponse(
                {
                    'status': 'error',
                    'message': 'このセミナーは管理モードではありません'
                },
                status=403
            )
        # 参加者を取得する
        member = Members.objects.filter(
            seminar=seminar,
            user=request.user
        ).first()
        # 参加者が見つからない場合は404エラー
        if not member:
            return JsonResponse(
                {
                    'status': 'error',
                    'message': 'セミナーの参加者が見つかりませんでした'
                },
                status=404
            )
        # 参加者のリクエスト状態を更新する
        member.request = True
        member.last_request = timezone.now()
        member.save()
        return JsonResponse({'status': 'success', 'message': 'リクエストが送信されました'})
