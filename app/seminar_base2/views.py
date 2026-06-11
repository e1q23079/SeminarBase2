from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from .models import Seminar, File, Members, ResetRequest
from django.core.exceptions import PermissionDenied
from django.contrib.auth.mixins import LoginRequiredMixin
import re
from django.http import (
    Http404, HttpResponse, FileResponse
)
from .lib.doc import Doc
from .lib.authorization import MemberAuthorizationMixin
from .lib.login import LoginMemberRequiredMixin, LoginManagerRequiredMixin
from django.conf import settings
import mimetypes
from dotenv import load_dotenv
import os
from django.utils import timezone
import urllib.parse
from .forms import SettingForm

# 環境変数をロード
load_dotenv()


# ホームページのビュー
class IndexView(View):
    def get(self, request):
        # EDITION情報を取得
        edition = os.getenv('EDITION', None)
        # ホームページをレンダリング
        return render(request, 'index.html', {'edition': edition})


# セミナーリストページのビュー（ログインが必要）
class SeminarListView(LoginRequiredMixin, MemberAuthorizationMixin, View):
    def get(self, request):
        # セミナーを取得
        seminars = Seminar.objects.all().order_by('-id')
        # 公開セミナーのみを表示する（管理者・スタッフは除く）
        if not self.is_superuser_or_staff(request.user):
            seminars = seminars.filter(public=True)
        # アクセス権限を判定してセミナーオブジェクトに属性を追加
        for seminar in seminars:
            seminar.is_accessible = self.is_member_access(
                request.user,
                seminar
            )
        # セミナーリストページをレンダリング
        return render(request, 'seminar_list.html', {'seminars': seminars})


# レクチャーリストページのビュー（メンバー権限のアカウントが必要）
class LectureListView(LoginRequiredMixin, LoginMemberRequiredMixin, View):
    def get(self, request, seminar_id):
        # セミナーを取得
        seminar = get_object_or_404(Seminar, uuid=seminar_id)
        # ドキュメントを解析してレクチャーリストを取得
        doc = Doc(seminar.content)
        lectures = doc.get_lecture_titles()
        # レクチャーリストページをレンダリング
        return render(
            request,
            'lecture_list.html',
            {'seminar': seminar, 'lectures': lectures}
        )


# ドキュメントページのビュー（メンバー権限のアカウントが必要）
class DocumentView(LoginRequiredMixin, LoginMemberRequiredMixin, View):
    def get(self, request, seminar_id):
        # クエリパラメータからlecを取得
        try:
            lec_id = int(request.GET.get('lec', 0))
        except (ValueError, TypeError):
            raise Http404("Invalid lecture ID")
        # セミナーを取得
        seminar = get_object_or_404(Seminar, uuid=seminar_id)
        # ドキュメントを解析してレクチャーを取得
        doc = Doc(seminar.content)
        lecture = doc.get_lecture(lec_id)
        #  レクチャーが見つからない場合は404エラー
        if not lecture:
            raise Http404("Lecture not found")
        # レクチャーの内容をHTMLに変換してリンクにtarget="_blank"を追加
        lecture['content'] = re.sub(
            r'<a', '<a target="_blank" ', lecture['content']
        )
        # 進捗を更新（管理対象のセミナーのみ）
        maneger_mode = False
        if seminar.manage:
            # メンバーのみ
            member = Members.objects.filter(
                user=request.user,
                seminar=seminar
            ).first()
            if member:
                member.progress = lec_id
                member.last_access = timezone.now()
                member.save()
                maneger_mode = True
        # ドキュメントページをレンダリング
        contents = {
            'lecture': lecture,
            'seminar': seminar,
            'nextId': lecture['next'],
            'prevId': lecture['prev'],
            'manager_mode': maneger_mode
        }
        return render(request, 'document.html', contents)


# 印刷セミナー一覧（ログインが必要）
class PrintListView(LoginRequiredMixin, MemberAuthorizationMixin, View):
    def get(self, request):
        # セミナーを取得
        seminars = Seminar.objects.all().order_by('-id')
        # アクセス権限を判定してセミナーオブジェクトに属性を追加
        for seminar in seminars:
            seminar.is_accessible = self.is_member_access(
                request.user,
                seminar
            )
        # 印刷セミナー一覧ページをレンダリング
        return render(request, 'print_list.html', {'seminars': seminars})


# 印刷ページのビュー（メンバー権限のアカウントが必要）
class PrintView(LoginRequiredMixin, LoginMemberRequiredMixin, View):
    def get(self, request, seminar_id, lecture_id=None):
        # クエリパラメータからlecを取得
        lec_query = request.GET.get('lec')
        if lec_query:
            try:
                lecture_id = int(lec_query)
            except ValueError:
                raise Http404("Invalid lecture ID")
        # セミナーを取得
        seminar = get_object_or_404(Seminar, uuid=seminar_id)
        # ドキュメントを解析してレクチャーを取得
        doc = Doc(seminar.content)

        if lecture_id or lecture_id == 0:
            # レクチャーのみを印刷
            lecture = doc.get_lecture(lecture_id)
            # レクチャーが見つからない場合は404エラー
            if not lecture:
                raise Http404("Lecture not found")
            # レクチャーの内容をHTMLに変換してリンクにtarget="_blank"を追加
            lecture['content'] = re.sub(
                r'<a', '<a target="_blank" ', lecture['content']
            )
            # ドキュメントページをレンダリング
            return render(
                request,
                'print.html',
                {'lectures': [lecture], 'seminar': seminar, 'lec': True}
            )
        else:
            # セミナー全体を印刷
            lectures = doc.get_lectures()
            # レクチャーの内容をHTMLに変換してリンクにtarget="_blank"を追加
            for lecture in lectures:
                lecture['content'] = re.sub(
                    r'<a', '<a target="_blank" ', lecture['content']
                )
            # ドキュメントページをレンダリング
            return render(
                request,
                'print.html',
                {'lectures': lectures, 'seminar': seminar, 'lec': False}
            )


# ファイル保護ビュー
class ProtectFileView(LoginRequiredMixin, LoginMemberRequiredMixin, View):
    def get(self, request, uuid):
        # ファイルを取得
        file = get_object_or_404(File, uuid=uuid)
        # ファイルをレスポンスとして返す（開発環境と本番環境で処理を分ける）
        if settings.DEBUG:
            # 開発環境ではFileResponseを使用して直接ファイルを返す
            response = FileResponse(
                file.file.open(),
                content_type=mimetypes.guess_type(file.file.name)[0] or 'application/octet-stream'  # noqa: E501
            )
        else:
            # 本番環境ではX-Accel-Redirectを使用してNginxにファイルの配信を任せる
            mime_type, _ = mimetypes.guess_type(file.file.name)
            response = HttpResponse()
            response['Content-Type'] = mime_type or 'application/octet-stream'
            response['X-Accel-Redirect'] = f'/protect/{file.file.name}'
        file_name = f'{file.name}{os.path.splitext(file.file.name)[1]}'
        encode_file_name = urllib.parse.quote(file_name)
        response['Content-Disposition'] = f'inline; filename*=UTF-8\'\'{encode_file_name}'  # noqa: E501
        return response


# マネージリストページのビュー（マネージャー権限のアカウントが必要）
class ManagerListView(LoginRequiredMixin, LoginManagerRequiredMixin, View):
    def get(self, request):
        # 管理対象のセミナーを取得
        seminars = Seminar.objects.filter(manage=True).order_by('-id')
        # アクセス権限を判定してセミナーオブジェクトに属性を追加
        for seminar in seminars:
            seminar.is_accessible = self.is_manager_access(
                request.user,
                seminar
            )
        # マネージリストページをレンダリング
        return render(request, 'manage_list.html', {'seminars': seminars})


# マネージャーページのビュー（マネージャー権限のアカウントが必要）
class ManagerView(LoginRequiredMixin, LoginManagerRequiredMixin, View):
    def get(self, request, seminar_id):
        # セミナーを取得
        seminar = get_object_or_404(Seminar, uuid=seminar_id)
        # 管理モードでない場合は404エラー
        if not seminar.manage:
            raise Http404("This seminar is not in management mode.")
        # マネージャーページをレンダリング
        return render(request, 'manager.html', {'seminar': seminar})


# マネージャー進捗確認ページのビュー（マネージャー権限のアカウントが必要）
class ManagerProgressView(LoginRequiredMixin, LoginManagerRequiredMixin, View):
    def get(self, request, seminar_id):
        # セミナーを取得
        seminar = get_object_or_404(Seminar, uuid=seminar_id)
        # 管理モードでない場合は404エラー
        if not seminar.manage:
            raise Http404("This seminar is not in management mode.")
        # ドキュメントを解析してレクチャー数を取得
        lecture = Doc(seminar.content)
        lecture_count = lecture.get_lecture_count()
        # メンバーを取得
        members = Members.objects.filter(
            seminar=seminar
        ).order_by('-progress', '-last_access')
        # マネージャー進捗確認ページをレンダリング
        return render(
            request,
            'manager_progress.html',
            {
                'seminar': seminar,
                'members': members,
                'lecture_count': lecture_count,
                'update_time': timezone.now()
            }
        )


# マネージャーリクエスト確認ページのビュー（マネージャー権限のアカウントが必要）
class ManagerRequestView(LoginRequiredMixin, LoginManagerRequiredMixin, View):
    def get(self, request, seminar_id):
        # セミナーを取得
        seminar = get_object_or_404(Seminar, uuid=seminar_id)
        # 管理モードでない場合は404エラー
        if not seminar.manage:
            raise Http404("This seminar is not in management mode.")
        # メンバーを取得
        members = Members.objects.filter(
            seminar=seminar
        ).order_by('-request', 'last_request')
        # マネージャーリクエスト確認ページをレンダリング
        return render(
            request,
            'manager_request.html',
            {
                'seminar': seminar,
                'members': members,
                'update_time': timezone.now()
            }
        )


# マネージャーリクエスト解除ページのビュー（マネージャー権限のアカウントが必要）
class ManagerRequestResetView(
    LoginRequiredMixin,
    LoginManagerRequiredMixin,
    View
):
    def post(self, request, seminar_id, username):
        # セミナーを取得
        seminar = get_object_or_404(Seminar, uuid=seminar_id)
        # 管理モードでない場合は404エラー
        if not seminar.manage:
            raise Http404("This seminar is not in management mode.")
        # メンバーを取得
        member = get_object_or_404(
            Members,
            user__username=username,
            seminar=seminar
        )
        if member.request:
            member.request = False
            member.last_request = None
            member.save()
        # マネージャーリクエスト確認ページにリダイレクト
        return redirect('manager_request', seminar_id=seminar.uuid)


# マネージャーリクエストリアルタイム確認ページのビュー（マネージャー権限のアカウントが必要）
class ManagerRequestRealtimeView(
    LoginRequiredMixin,
    LoginManagerRequiredMixin,
    View
):
    def get(self, request, seminar_id):
        # セミナーを取得
        seminar = get_object_or_404(Seminar, uuid=seminar_id)
        # 管理モードでない場合は404エラー
        if not seminar.manage:
            raise Http404("This seminar is not in management mode.")
        # マネージャーリクエストリアルタイム確認ページをレンダリング
        return render(
            request,
            'manager_request_realtime.html',
            {
                'seminar': seminar
            }
        )


# 名前・パスワード設定ページのビュー
class SettingView(LoginRequiredMixin, View):
    def dispatch(self, request, *args, **kwargs):
        # ログインしていない場合はアクセスを許可
        if not request.user.is_authenticated:
            return super().dispatch(request, *args, **kwargs)
        # 再設定要求が存在しない場合はアクセスを拒否
        reset_request = ResetRequest.objects.filter(user=request.user).exists()
        if not reset_request:
            raise PermissionDenied()
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        # 名前・パスワード設定ページをレンダリング
        return render(request, 'setting.html')

    def post(self, request):
        # フォームからデータを取得
        form = SettingForm(user=request.user, data=request.POST)
        if form.is_valid():
            # データが有効な場合は保存して成功メッセージを表示
            form.save()
            return redirect('setting_complete')
        else:
            # データが無効な場合はエラーメッセージを表示
            return render(request, 'setting.html', {'form': form})


# 完了ページのビュー
class CompleteView(View):
    def get(self, request):
        # 完了ページをレンダリング
        return render(request, 'setting_complete.html')
