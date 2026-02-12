from django.contrib import admin
from .models import Seminar, Lecture, Members, User

# Register your models here.

# セミナーモデルの管理画面設定
class SeminarAdmin(admin.ModelAdmin):
    list_display = ('title', 'description')
admin.site.register(Seminar, SeminarAdmin)

# レクチャーモデルの管理画面設定
class LectureAdmin(admin.ModelAdmin):
    list_display = ('title',)
    # セミナーでフィルタリングできるように設定
    list_filter = ('seminar',)
admin.site.register(Lecture, LectureAdmin)

# 参加者モデルの管理画面設定
class MembersAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name', 'seminar')
    
    # ユーザー選択時にスタッフユーザーやスーパーユーザーを除外
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "user":
            kwargs["queryset"] = User.objects.filter(is_staff=False, is_superuser=False)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
    # セミナーでフィルタリングできるように設定
    list_filter = ('seminar',)
admin.site.register(Members, MembersAdmin)

# 管理サイトのタイトルを変更
admin.site.site_header = "SeminarBase2 管理者サイト"
admin.site.site_title = "SeminarBase2"
admin.site.index_title = "管理画面"