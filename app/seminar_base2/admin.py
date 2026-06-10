from django.contrib import admin
from .models import Seminar, Members, User, File, Manager, ResetRequest
from django.utils.safestring import mark_safe


# セミナーモデルの管理画面設定
class SeminarAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'seminar_link',
        'description',
        'is_public',
        'is_manage'
    )

    # セミナーURLを表示するためのメソッド
    def seminar_link(self, obj):
        if obj.uuid:
            return mark_safe(
                f'<a href="/lecture/{obj.uuid}" target="_blank">セミナーを表示</a>'
            )
        return "No Seminar"

    # 公開ステータス
    def is_public(self, obj):
        return "公開" if obj.public else "非公開"

    # 管理機能のステータス
    def is_manage(self, obj):
        return "有効" if obj.manage else "無効"

    is_public.short_description = "公開"
    is_manage.short_description = "管理機能"
    seminar_link.short_description = "セミナーURL"


admin.site.register(Seminar, SeminarAdmin)


# 参加者モデルの管理画面設定
class MembersAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name', 'seminar')
    fields = ('user', 'seminar')
    ordering = ('seminar__title', 'user__username')
    # ユーザー選択時にスタッフユーザーやスーパーユーザーを除外
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "user":
            kwargs["queryset"] = User.objects.filter(
                is_staff=False,
                is_superuser=False
            )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    # セミナーでフィルタリングできるように設定
    list_filter = ('seminar',)


admin.site.register(Members, MembersAdmin)


# マネージャーモデルの管理画面設定
class ManagerAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name', 'seminar')
    ordering = ('seminar__title', 'user__username')

    # ユーザー選択時にスタッフユーザーやスーパーユーザーを除外
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "user":
            kwargs["queryset"] = User.objects.filter(
                is_staff=False,
                is_superuser=False
            )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    # セミナーでフィルタリングできるように設定
    list_filter = ('seminar',)


admin.site.register(Manager, ManagerAdmin)


# ファイルモデルの管理画面設定
class FileAdmin(admin.ModelAdmin):
    list_display = ('name', 'file_link', 'seminar', 'file_url')
    # セミナーでフィルタリングできるように設定
    list_filter = ('seminar',)

    ordering = ('seminar__title', 'name')

    # ファイルを直接表示するためのメソッド
    def file_link(self, obj):
        if obj.file:
            return mark_safe(
                f'<a href="/file/{obj.uuid}" target="_blank">ファイルを表示</a>'
            )
        return "No File"
    file_link.short_description = "ファイルリンク"

    # ファイルのURLを表示するためのメソッド
    def file_url(self, obj):
        if obj.file:
            return f"/file/{obj.uuid}"
        return "No File"
    file_url.short_description = "ファイルURL"


admin.site.register(File, FileAdmin)


# 再設定要求モデルの管理画面設定
class ResetRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name')
    ordering = ('user__username',)


admin.site.register(ResetRequest, ResetRequestAdmin)

# 管理サイトのタイトルを変更
admin.site.site_header = "SeminarBase2 管理者サイト"
admin.site.site_title = "SeminarBase2"
admin.site.index_title = "管理画面"
