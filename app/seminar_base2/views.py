from django.shortcuts import render, get_object_or_404
from django.views import View
# from markdownx.utils import markdownify
from .models import Seminar, File, Members, Manager
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
import re
from django.http import Http404, HttpResponse, FileResponse
from .lib.doc import Doc
from .lib.seminar import is_member, is_manager
from django.conf import settings
import mimetypes
from dotenv import load_dotenv
import os
from django.utils import timezone
import urllib.parse

load_dotenv()

# Create your views here.

# ホームページのビュー
class IndexView(View):
    def get(self, request):
        return render(request, 'index.html', {'edition': os.getenv('EDITION', None)})
    
# セミナーリストページのビュー
class SeminarListView(LoginRequiredMixin, View):
    def get(self, request):
        seminars = Seminar.objects.all().order_by('-id')
        
        for seminar in seminars:
            is_member(seminar, request.user)

        return render(request, 'seminar_list.html', {'seminars': seminars})
 
# 参加者認証ミックスイン
class MemberAuthorizationMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        
        # ログインしていない場合はログインページへリダイレクト
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        
        # 管理者は全てのセミナーにアクセス可能
        if request.user.is_superuser:
            return super().dispatch(request, *args, **kwargs)
        
        # セミナーIDをURLから取得して、参加者かどうかを確認
        seminar_id = kwargs.get('seminar_id')
        
        if seminar_id:
            seminar = get_object_or_404(Seminar, uuid=seminar_id)
            if not seminar.members_set.filter(user=request.user).exists() and not seminar.manager_set.filter(user=request.user).exists():
                raise PermissionDenied
            if not seminar.public:
                raise PermissionDenied
        
        return super().dispatch(request, *args, **kwargs) 

# マネージャー認証ミックスイン
class ManagerAuthorizationMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        
        # ログインしていない場合はログインページへリダイレクト
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        
        # 管理者は全てのセミナーにアクセス可能
        if request.user.is_superuser:
            return super().dispatch(request, *args, **kwargs)

        if not Manager.objects.filter(user=request.user).exists() or request.user.is_staff or request.user.is_superuser:
            raise PermissionDenied
        
        if 'seminar_id' in kwargs:
            seminar_id = kwargs['seminar_id']
            if not Manager.objects.filter(user=request.user, seminar__uuid=seminar_id).exists():
                raise PermissionDenied
            
            if not Seminar.objects.filter(uuid=seminar_id, public=True).exists():
                raise PermissionDenied

        return super().dispatch(request, *args, **kwargs)
    
# レクチャーリストページのビュー
class LectureListView(MemberAuthorizationMixin, View):
    def get(self, request, seminar_id):
        # seminar = get_object_or_404(Seminar, uuid=seminar_id)
        # lectures = seminar.lecture_set.all().order_by('id')
        # return render(request, 'lecture_list.html', {'seminar': seminar, 'lectures': lectures})
        seminar = get_object_or_404(Seminar, uuid=seminar_id)
        doc = Doc(seminar.content)
        lectures = doc.get_lecture_titles()
        return render(request, 'lecture_list.html', {'seminar': seminar, 'lectures': lectures})
    
# ドキュメントページのビュー
class DocumentView(MemberAuthorizationMixin, View):
    def get(self, request, seminar_id):
        # seminar = get_object_or_404(Seminar, uuid=seminar_id)
        # lecture = get_object_or_404(Lecture, uuid=lecture_id)
        # lecture.content = markdownify(lecture.content)
        # lecture.content = re.sub(r'<a','<a target="_blank" ', lecture.content)
        # contens = {
        #     'lecture': lecture,
        #     'seminar': seminar,
        #     'nextId': seminar.lecture_set.filter(id__gt=lecture.id).order_by('id').first() if seminar.lecture_set.filter(id__gt=lecture.id).exists() else None,
        #     'prevId': seminar.lecture_set.filter(id__lt=lecture.id).order_by('-id').first()
        # }
        # return render(request, 'document.html', contens)
        try:
            lec_id = int(request.GET.get('lec', 0))
        except (ValueError, TypeError):
            raise Http404("Invalid lecture ID")
        seminar = get_object_or_404(Seminar, uuid=seminar_id)
        doc = Doc(seminar.content)
        lecture = doc.get_lecture(lec_id)
        if not lecture:
            raise Http404("Lecture not found")
        lecture['content'] = re.sub(r'<a','<a target="_blank" ', lecture['content'])
        contents = {
            'lecture': lecture,
            'seminar': seminar,
            'nextId': lecture['next'],
            'prevId': lecture['prev']
        }
        if seminar.manage:
            member = Members.objects.filter(user=request.user, seminar=seminar).first()
            if member:
                member.progress = lec_id
                member.last_access = timezone.now()
                member.save()
        return render(request, 'document.html', contents)
        
        
    
# 印刷セミナー一覧
class PrintListView(LoginRequiredMixin, View):
    def get(self, request):
        seminars = Seminar.objects.all().order_by('-id')
        
        for seminar in seminars:
            seminar = is_member(seminar, request.user)

        return render(request, 'print_list.html', {'seminars': seminars})

# 印刷ページのビュー
class PrintView(MemberAuthorizationMixin, View):
    def get(self, request, seminar_id, lecture_id=None):
        
        seminar = get_object_or_404(Seminar, uuid=seminar_id)
        lec_query = request.GET.get('lec')
        if lec_query:
            try:
                lecture_id = int(lec_query)
            except ValueError:
                raise Http404("Invalid lecture ID")
        
        doc = Doc(seminar.content)
        
        # レクチャーのみを印刷
        if(lecture_id or lecture_id == 0):
            # lecture = get_object_or_404(Lecture, uuid=lecture_id)
            # lecture.content = markdownify(lecture.content)
            # lecture.content = re.sub(r'<a','<a target="_blank" ', lecture.content)
            # return render(request, 'print.html', {'lectures': [lecture], 'seminar': seminar, 'lec':True})
            lecture = doc.get_lecture(lecture_id)
            if not lecture:
                raise Http404("Lecture not found")
            lecture['content'] = re.sub(r'<a','<a target="_blank" ', lecture['content'])
            return render(request, 'print.html', {'lectures': [lecture], 'seminar': seminar, 'lec':True})
        else:
            # セミナー全体を印刷
            # lectures = seminar.lecture_set.all().order_by('id')
            # for lecture in lectures:
            #     lecture.content = markdownify(lecture.content)
            #     lecture.content = re.sub(r'<a','<a target="_blank" ', lecture.content)
            # return render(request, 'print.html', {'lectures': lectures, 'seminar': seminar, 'lec':False})
            lectures = doc.get_lectures()
            for lecture in lectures:
                lecture['content'] = re.sub(r'<a','<a target="_blank" ', lecture['content'])
            return render(request, 'print.html', {'lectures': lectures, 'seminar': seminar, 'lec':False})

# ファイル保護ビュー
class ProtectFileView(MemberAuthorizationMixin, View):
    def get(self, request, uuid):
        file = get_object_or_404(File, uuid=uuid)
        
        if not file.seminar.public or not file.seminar.members_set.filter(user=request.user).exists() and not request.user.is_superuser and not file.seminar.manager_set.filter(user=request.user).exists():
            raise PermissionDenied
        
        if settings.DEBUG:
            response = FileResponse(file.file.open(), content_type=mimetypes.guess_type(file.file.name)[0] or 'application/octet-stream')
        else:
            
            mime_type, _ = mimetypes.guess_type(file.file.name)
        
            response = HttpResponse()
            response['Content-Type'] = mime_type or 'application/octet-stream'
            response['X-Accel-Redirect'] = f'/protect/{file.file.name}'
        file_name = f'{file.name}{os.path.splitext(file.file.name)[1]}'
        encode_file_name = urllib.parse.quote(file_name)
        response['Content-Disposition'] = f'inline; filename*=UTF-8\'\'{encode_file_name}'
        return response

# マネージリストページのビュー
class ManagerListView(ManagerAuthorizationMixin, View):
    def get(self, request):
        seminars = Seminar.objects.filter(manage=True).order_by('-id')
        
        for seminar in seminars:
            seminar = is_manager(seminar, request.user)
            
        return render(request, 'manage_list.html', {'seminars': seminars})
    
# マネージャーページのビュー
class ManagerView(ManagerAuthorizationMixin, View):
    def get(self, request, seminar_id):
        seminar = get_object_or_404(Seminar, uuid=seminar_id)
        lecture = Doc(seminar.content)
        lecture_count = lecture.get_lecture_count()
        members = Members.objects.filter(seminar=seminar).order_by('-progress', '-last_access')
        if not seminar.manage:
            raise PermissionDenied
        return render(request, 'manager.html', {'seminar': seminar, 'members': members, 'lecture_count': lecture_count, 'update_time': timezone.now()})
