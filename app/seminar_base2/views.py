from django.shortcuts import render, get_object_or_404
from django.views import View
from .models import Seminar, File, Members
from django.contrib.auth.mixins import LoginRequiredMixin
import re
from django.http import Http404, HttpResponse, FileResponse
from .lib.doc import Doc
from .lib.authorization import MemberAuthorizationMixin
from .lib.login import LoginMemberRequiredMixin, LoginManagerRequiredMixin
from django.conf import settings
import mimetypes
from dotenv import load_dotenv
import os
from django.utils import timezone
import urllib.parse

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
        # ドキュメントページをレンダリング
        contents = {
            'lecture': lecture,
            'seminar': seminar,
            'nextId': lecture['next'],
            'prevId': lecture['prev']
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
        # ドキュメントを解析してレクチャー数を取得
        lecture = Doc(seminar.content)
        lecture_count = lecture.get_lecture_count()
        # メンバーを取得
        members = Members.objects.filter(
            seminar=seminar
        ).order_by('-progress', '-last_access')
        # マネージャーページをレンダリング
        return render(
            request,
            'manager.html',
            {
                'seminar': seminar,
                'members': members,
                'lecture_count': lecture_count,
                'update_time': timezone.now()
            }
        )
