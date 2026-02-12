from django.shortcuts import render, get_object_or_404
from django.views import View
from markdownx.utils import markdownify
from .models import Seminar, Lecture
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
import re

# Create your views here.

# ホームページのビュー
class IndexView(View):
    def get(self, request):
        return render(request, 'index.html')
    
# セミナーリストページのビュー
class SeminarListView(LoginRequiredMixin, View):
    def get(self, request):
        seminars = Seminar.objects.all()
        return render(request, 'seminar_list.html', {'seminars': seminars})
 
# 参加者認証ミックスイン
class MemberAuthorizationMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        
        if request.user.is_superuser:
            return super().dispatch(request, *args, **kwargs)
        
        seminar_id = kwargs.get('seminar_id')
        
        if seminar_id:
            seminar = get_object_or_404(Seminar, uuid=seminar_id)
            if not seminar.members_set.filter(user=request.user).exists():
                raise PermissionDenied
        
        return super().dispatch(request, *args, **kwargs) 
    
# レクチャーリストページのビュー
class LectureListView(MemberAuthorizationMixin, View):
    def get(self, request, seminar_id):
        seminar = get_object_or_404(Seminar, uuid=seminar_id)
        lectures = seminar.lecture_set.all().order_by('id')
        return render(request, 'lecture_list.html', {'seminar': seminar, 'lectures': lectures})
    
# ドキュメントページのビュー
class DocumentView(MemberAuthorizationMixin, View):
    def get(self, request, seminar_id, lecture_id):
        seminar = get_object_or_404(Seminar, uuid=seminar_id)
        lecture = get_object_or_404(Lecture, uuid=lecture_id)
        lecture.content = markdownify(lecture.content)
        lecture.content = re.sub(r'<a','<a target="_blank" ', lecture.content)
        contens = {
            'lecture': lecture,
            'seminar': seminar,
            'nextId': seminar.lecture_set.filter(id__gt=lecture.id).order_by('id').first() if seminar.lecture_set.filter(id__gt=lecture.id).exists() else None,
            'prevId': seminar.lecture_set.filter(id__lt=lecture.id).order_by('-id').first()
        }
        return render(request, 'document.html', contens)
    
# 印刷セミナー一覧
class PrintListView(LoginRequiredMixin, View):
    def get(self, request):
        seminars = Seminar.objects.all()
        return render(request, 'print_list.html', {'seminars': seminars})

# 印刷ページのビュー
class PrintView(MemberAuthorizationMixin, View):
    def get(self, request, seminar_id, lecture_id=None):
        
        seminar = get_object_or_404(Seminar, uuid=seminar_id)
        
        # レクチャーのみを印刷
        if(lecture_id):
            lecture = get_object_or_404(Lecture, uuid=lecture_id)
            lecture.content = markdownify(lecture.content)
            lecture.content = re.sub(r'<a','<a target="_blank" ', lecture.content)
            return render(request, 'print.html', {'lectures': [lecture], 'seminar': seminar, 'lec':True})
        else:
            # セミナー全体を印刷
            lectures = seminar.lecture_set.all().order_by('id')
            for lecture in lectures:
                lecture.content = markdownify(lecture.content)
                lecture.content = re.sub(r'<a','<a target="_blank" ', lecture.content)
            return render(request, 'print.html', {'lectures': lectures, 'seminar': seminar, 'lec':False})