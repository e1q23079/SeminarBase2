from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from getpass import getpass

User = get_user_model()


class Command(BaseCommand):
    """
    Djangoの管理コマンドで新しいユーザーを作成するためのコマンドクラス
    """
    help = '新規ユーザーを作成するコマンド'

    def handle(self, *args, **kwargs):

        self.stdout.write(self.style.SUCCESS('Creating a new user...'))

        # ユーザ情報の入力

        self.stdout.write('ユーザー名: ', ending='')
        username = input()
        # ユーザ名が空でないかのチェック
        if not username:
            self.stdout.write(
                self.style.ERROR('Error: Username cannot be empty.')
            )
            return

        self.stdout.write('メールアドレス: ', ending='')

        email = input()

        password = getpass()
        # パスワードが空でないかのチェック
        if not password:
            self.stdout.write(
                self.style.ERROR('Error: Password cannot be empty.')
            )
            return
        password_confirm = getpass()

        # パスワードの確認
        if password != password_confirm:
            self.stdout.write(
                self.style.ERROR('Error: Passwords do not match.')
            )
            return

        # ユーザ名の重複チェック
        if User.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.ERROR('Error: Username already exists.')
            )
            return

        # ユーザの作成
        User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        self.stdout.write(f'User "{username}" created successfully.')
