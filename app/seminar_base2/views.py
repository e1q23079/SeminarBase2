from django.shortcuts import render, get_object_or_404
from django.views import View
from markdownx.utils import markdownify
from .models import Seminar, Lecture
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone

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
    
# レクチャーリストページのビュー
class LectureListView(LoginRequiredMixin, View):
    def get(self, request, seminar_id):
        seminar = get_object_or_404(Seminar, uuid=seminar_id)
        lectures = seminar.lecture_set.all().order_by('id')
        return render(request, 'lecture_list.html', {'seminar': seminar, 'lectures': lectures})
    
# ドキュメントページのビュー
class DocumentView(LoginRequiredMixin, View):
    def get(self, request, seminar_id, lecture_id):
        seminar = get_object_or_404(Seminar, uuid=seminar_id)
        lecture = get_object_or_404(Lecture, uuid=lecture_id)
        lecture.content = markdownify(lecture.content)
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
class PrintView(LoginRequiredMixin, View):
    def get(self, request, seminar_id, lecture_id=None):
        
        seminar = get_object_or_404(Seminar, uuid=seminar_id)
        
        # レクチャーのみを印刷
        if(lecture_id):
            lecture = get_object_or_404(Lecture, uuid=lecture_id)
            lecture.content = markdownify(lecture.content)
            return render(request, 'print.html', {'lectures': [lecture], 'seminar': seminar})
        else:
            # セミナー全体を印刷
            lectures = seminar.lecture_set.all().order_by('id')
            for lecture in lectures:
                lecture.content = markdownify(lecture.content)
            return render(request, 'print.html', {'lectures': lectures, 'seminar': seminar})