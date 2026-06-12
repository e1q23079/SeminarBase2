from django.contrib import admin
from .models import Seminar, Members, User, File, Manager, ResetRequest
from django.contrib.auth.admin import UserAdmin
from django.utils.safestring import mark_safe

admin.site.unregister(User)  # デフォルトのUserモデルをアンレジスターしてカスタムUserAdminを登録


# カスタムユーザーモデルの管理画面設定
class CustomUserAdmin(UserAdmin):
    search_fields = ('username', 'email', 'first_name', 'last_name')


admin.site.register(User, CustomUserAdmin)


# 参加者モデルの管理画面設定（インライン表示用）
class MembersInline(admin.TabularInline):
    model = Members
    extra = 0
    autocomplete_fields = ['user']
    fields = ('user', 'full_name')
    readonly_fields = ('full_name',)

    @admin.display(description='名前')
    # フルネームを表示するためのメソッド
    def full_name(self, obj):
        return f"{obj.user.last_name} {obj.user.first_name}"


# マネージャーモデルの管理画面設定（インライン表示用）
class ManagerInline(admin.TabularInline):
    model = Manager
    extra = 0
    autocomplete_fields = ['user']
    fields = ('user', 'full_name')
    readonly_fields = ('full_name',)

    @admin.display(description='名前')
    # フルネームを表示するためのメソッド
    def full_name(self, obj):
        return f"{obj.user.last_name} {obj.user.first_name}"


# ファイルモデルの管理画面設定（インライン表示用）
class FileInline(admin.TabularInline):
    model = File
    extra = 0
    fields = ('name', 'file', 'file_link', 'file_url')
    readonly_fields = ('file_link', 'file_url')

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


# セミナーモデルの管理画面設定
class SeminarAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'seminar_link',
        'description',
        'is_public',
        'is_manage'
    )

    search_fields = ('title', 'description')

    inlines = [FileInline, MembersInline, ManagerInline]

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

    autocomplete_fields = ['user', 'seminar']

    ordering = ('seminar__title', 'user__username')

    # ユーザー選択時にスタッフユーザーやスーパーユーザーを除外
    # 検索利用のため、コメントアウトしておく
    # def formfield_for_foreignkey(self, db_field, request, **kwargs):
    #     if db_field.name == "user":
    #         kwargs["queryset"] = User.objects.filter(
    #             is_staff=False,
    #             is_superuser=False
    #         ).order_by('username')
    #     return super().formfield_for_foreignkey(db_field, request, **kwargs)

    # セミナーでフィルタリングできるように設定
    list_filter = ('seminar',)


admin.site.register(Members, MembersAdmin)


# マネージャーモデルの管理画面設定
class ManagerAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name', 'seminar')
    fields = ('user', 'seminar')

    autocomplete_fields = ['user', 'seminar']

    ordering = ('seminar__title', 'user__username')

    # ユーザー選択時にスタッフユーザーやスーパーユーザーを除外
    # 検索利用のため、コメントアウトしておく
    # def formfield_for_foreignkey(self, db_field, request, **kwargs):
    #     if db_field.name == "user":
    #         kwargs["queryset"] = User.objects.filter(
    #             is_staff=False,
    #             is_superuser=False
    #         ).order_by('username')
    #     return super().formfield_for_foreignkey(db_field, request, **kwargs)

    # セミナーでフィルタリングできるように設定
    list_filter = ('seminar',)


admin.site.register(Manager, ManagerAdmin)


# ファイルモデルの管理画面設定
class FileAdmin(admin.ModelAdmin):
    list_display = ('name', 'file_link', 'seminar', 'file_url')
    # セミナーでフィルタリングできるように設定
    list_filter = ('seminar',)

    autocomplete_fields = ['seminar']

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

    autocomplete_fields = ['user']

    ordering = ('user__username',)


admin.site.register(ResetRequest, ResetRequestAdmin)

# 管理サイトのタイトルを変更
admin.site.site_header = "SeminarBase2 管理者サイト"
admin.site.site_title = "SeminarBase2"
admin.site.index_title = "管理画面"
