from django.test import TestCase
from django.contrib.auth.models import User
from seminar_base2.models import ResetRequest


class SettingRequestMiddlewareTest(TestCase):
    """
    SettingRequestMiddlewareのテストケース
    """
    def test_middleware_redirect(self):
        """
        再設定要求が存在する場合は設定ページにリダイレクトされることを確認
        """
        # テストユーザーを作成してログイン
        user = User.objects.create_user(
            username='testuser',
            password='testpass'
        )
        self.client.login(username='testuser', password='testpass')
        # 再設定要求を作成
        ResetRequest.objects.create(user=user)
        # 任意のページにアクセスして設定ページにリダイレクトされることを確認
        response = self.client.get('/some-page')
        self.assertRedirects(response, '/setting')

    def test_middleware_excluded_paths(self):
        """
        除外ページへのアクセスは許可されることを確認
        """
        # テストユーザーを作成してログイン
        user = User.objects.create_user(
            username='testuser',
            password='testpass'
        )
        self.client.login(username='testuser', password='testpass')
        # 再設定要求を作成
        ResetRequest.objects.create(user=user)
        # 除外ページにアクセスして200 OKが返ることを確認
        response = self.client.get('/setting')
        self.assertEqual(response.status_code, 200)
        response = self.client.post('/accounts/logout/')
        self.assertEqual(response.status_code, 200)

    def test_middleware_no_redirect(self):
        """
        再設定要求が存在しない場合は通常通りアクセスできることを確認
        """
        # テストユーザーを作成してログイン
        User.objects.create_user(
            username='testuser',
            password='testpass'
        )
        self.client.login(username='testuser', password='testpass')
        # 任意のページにアクセスして200 OKが返ることを確認
        response = self.client.get('/seminar')
        self.assertEqual(response.status_code, 200)
