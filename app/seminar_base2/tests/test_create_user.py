from io import StringIO
from unittest.mock import patch
from django.test import TestCase
from django.contrib.auth.models import User
from seminar_base2.management.commands.create_user import Command


class CreateUserCommandTest(TestCase):
    @patch('builtins.input')
    @patch('seminar_base2.management.commands.create_user.getpass')
    def test_create_user_success(self, mock_getpass, mock_input):
        """
        ユーザー作成コマンドのテスト（正常にユーザーが作成されるケース）
        """

        # input() のモック設定
        mock_input.side_effect = ['testuser', 'test@example.com']
        # getpass() のモック設定
        mock_getpass.side_effect = ['password123', 'password123']

        # コマンドの出力をキャプチャするための StringIO を作成
        out = StringIO()

        # コマンドのインスタンスを作成・実行
        command = Command(stdout=out)
        command.handle()

        # コマンドの出力を取得
        output = out.getvalue()
        self.assertIn('User "testuser" created successfully.', output)
        # ユーザが作成されたか確認
        self.assertTrue(User.objects.filter(username='testuser').exists())

    @patch('builtins.input')
    @patch('seminar_base2.management.commands.create_user.getpass')
    def test_create_user_username_empty(self, mock_getpass, mock_input):
        """
        ユーザー作成コマンドのテスト（ユーザー名が未入力）
        """

        # input() のモック設定
        mock_input.side_effect = ['', 'test@example.com']
        # getpass() のモック設定
        mock_getpass.side_effect = ['password123', 'password123']

        # コマンドのインスタンスを作成・実行
        out = StringIO()
        command = Command(stdout=out)
        command.handle()

        # コマンドの出力を取得
        output = out.getvalue()
        self.assertIn('Error: Username cannot be empty.', output)
        # ユーザが作成されたか確認
        self.assertFalse(User.objects.filter(username='testuser').exists())

    @patch('builtins.input')
    @patch('seminar_base2.management.commands.create_user.getpass')
    def test_create_user_password_empty(self, mock_getpass, mock_input):
        """
        ユーザー作成コマンドのテスト（パスワードが未入力）
        """

        # input() のモック設定
        mock_input.side_effect = ['testuser', 'test@example.com']
        # getpass() のモック設定
        mock_getpass.side_effect = ['', 'password123']

        # コマンドの出力をキャプチャするための StringIO を作成
        out = StringIO()

        # コマンドのインスタンスを作成・実行
        command = Command(stdout=out)
        command.handle()

        # コマンドの出力を取得
        output = out.getvalue()
        self.assertIn('Error: Password cannot be empty.', output)
        # ユーザが作成されたか確認
        self.assertFalse(User.objects.filter(username='testuser').exists())

    @patch('builtins.input')
    @patch('seminar_base2.management.commands.create_user.getpass')
    def test_create_user_password_mismatch(self, mock_getpass, mock_input):
        """
        ユーザー作成コマンドのテスト（パスワードが不一致）
        """

        # input() のモック設定
        mock_input.side_effect = ['testuser', 'test@example.com']
        # getpass() のモック設定
        mock_getpass.side_effect = ['password123', 'password456']

        # コマンドのインスタンスを作成・実行
        out = StringIO()
        command = Command(stdout=out)
        command.handle()

        # コマンドの出力を取得
        output = out.getvalue()
        self.assertIn('Error: Passwords do not match.', output)
        # ユーザが作成されたか確認
        self.assertFalse(User.objects.filter(username='testuser').exists())

    @patch('builtins.input')
    @patch('seminar_base2.management.commands.create_user.getpass')
    def test_create_user_username_exists(self, mock_getpass, mock_input):
        """
        ユーザー作成コマンドのテスト（ユーザー名が重複）
        """

        # 事前にユーザを作成
        User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123'
        )

        # input() のモック設定
        mock_input.side_effect = ['testuser', 'test@example.com']
        # getpass() のモック設定
        mock_getpass.side_effect = ['password123', 'password123']

        # コマンドのインスタンスを作成・実行
        out = StringIO()
        command = Command(stdout=out)
        command.handle()

        # コマンドの出力を取得
        output = out.getvalue()
        self.assertIn('Error: Username already exists.', output)
        # ユーザが重複して作成されていないか確認
        self.assertEqual(User.objects.filter(username='testuser').count(), 1)
