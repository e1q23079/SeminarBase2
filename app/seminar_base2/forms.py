from django import forms
from django.contrib.auth.forms import PasswordChangeForm


class SettingForm(PasswordChangeForm):
    """
    ユーザー設定フォーム
    """
    # 名前のフィールドを追加
    first_name = forms.CharField(
        label='名前',
        max_length=150,
        required=False
    )
    # 姓のフィールドを追加
    last_name = forms.CharField(
        label='姓',
        max_length=150,
        required=False
    )

    def save(self, commit=True):
        # パスワードを保存
        user = super().save()
        # 名前を保存
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
        return user
