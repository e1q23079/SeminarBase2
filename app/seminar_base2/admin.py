from django.contrib import admin
from .models import Seminar, Members, User, File
from django.utils.safestring import mark_safe

# Register your models here.

# セミナーモデルの管理画面設定
class SeminarAdmin(admin.ModelAdmin):
    list_display = ('title', 'description')
admin.site.register(Seminar, SeminarAdmin)

# レクチャーモデルの管理画面設定
# class LectureAdmin(admin.ModelAdmin):
#     list_display = ('title',)
#     # セミナーでフィルタリングできるように設定
#     list_filter = ('seminar',)
# admin.site.register(Lecture, LectureAdmin)

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

# ファイルモデルの管理画面設定
class FileAdmin(admin.ModelAdmin):
    list_display = ('name', 'file_link', 'seminar', 'file_url')
    # セミナーでフィルタリングできるように設定
    list_filter = ('seminar',)
    # ファイルを直接表示するためのメソッド
    def file_link(self, obj):
        if obj.file:
            return mark_safe(f'<a href="/file/{obj.uuid}" target="_blank">ファイルを表示</a>')
        return "No File"
    file_link.short_description = "ファイルリンク"
    # ファイルのURLを表示するためのメソッド
    def file_url(self, obj):
        if obj.file:
            return f"/file/{obj.uuid}"
        return "No File"
    file_url.short_description = "ファイルURL"
admin.site.register(File, FileAdmin)

# 管理サイトのタイトルを変更
admin.site.site_header = "SeminarBase2 管理者サイト"
admin.site.site_title = "SeminarBase2"
admin.site.index_title = "管理画面"