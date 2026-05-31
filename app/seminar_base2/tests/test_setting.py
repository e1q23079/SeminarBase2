from django.test import TestCase
from ..models import ResetRequest
from django.contrib.auth.models import User


class SettingViewTest(TestCase):
    """
    SettingViewのテストケース
    """
    def setUp(self):
        """
        テストのセットアップ
        """
        # テストユーザーを作成
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass'
        )
        # 再設定要求を作成
        ResetRequest.objects.create(user=self.user)

    def test_setting_view_not_login_get(self):
        """
        ログインしていない場合はリダイレクトされることを確認（GETリクエスト）
        """
        response = self.client.get('/setting')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)

    def test_setting_view_not_login_post(self):
        """
        ログインしていない場合はリダイレクトされることを確認（POSTリクエスト）
        """
        response = self.client.post('/setting', {
            'old_password': 'testpass',
            'new_password1': 'newtestpass',
            'new_password2': 'newtestpass',
            'first_name': 'Test',
            'last_name': 'User'
        })
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)

    def test_setting_view_login(self):
        """
        ログインしている場合は設定ページにアクセスできることを確認（GETリクエスト）
        """
        # テストユーザーを作成してログイン
        self.client.login(username='testuser', password='testpass')

        # 設定ページにアクセスして200 OKが返ることを確認
        response = self.client.get('/setting')
        self.assertEqual(response.status_code, 200)

    def test_setting_view_post_success(self):
        """
        設定を更新するPOSTリクエストのテスト
        """
        # テストユーザーを作成してログイン
        self.client.login(username='testuser', password='testpass')

        # 設定ページにPOSTリクエストを送信してリダイレクトされることを確認
        response = self.client.post('/setting', {
            'old_password': 'testpass',
            'new_password1': 'newtestpass',
            'new_password2': 'newtestpass',
            'first_name': 'Test',
            'last_name': 'User'
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/setting/complete')

    def test_setting_view_post_wrong_old_password(self):
        """
        古いパスワードが間違っている場合のテスト
        """
        self.client.login(username='testuser', password='testpass')

        # 古いパスワードが間違っている場合のテスト
        response = self.client.post('/setting', {
            'old_password': 'wrongpass',
            'new_password1': 'newtestpass',
            'new_password2': 'newtestpass',
            'first_name': 'Test',
            'last_name': 'User'
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'setting.html')

    def test_setting_view_post_password_mismatch(self):
        """
        パスワードの不一致をテスト
        """
        self.client.login(username='testuser', password='testpass')

        # パスワードの不一致をテスト
        response = self.client.post('/setting', {
            'old_password': 'testpass',
            'new_password1': 'newtestpass',
            'new_password2': 'differentpass',
            'first_name': 'Test',
            'last_name': 'User'
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'setting.html')

    # def test_complete_view_not_setting(self):
    #     """
    #     設定完了ページに直接アクセスした場合は404が返ることを確認
    #     """
    #     response = self.client.get('/setting/complete')
    #     self.assertEqual(response.status_code, 404)

    def test_complete_view_setting(self):
        """
        設定完了ページにアクセスできることを確認
        """
        self.client.login(username='testuser', password='testpass')

        # 設定ページにPOSTリクエストを送信してリダイレクトされることを確認
        response = self.client.post('/setting', {
            'old_password': 'testpass',
            'new_password1': 'newtestpass',
            'new_password2': 'newtestpass',
            'first_name': 'Test',
            'last_name': 'User'
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/setting/complete')

        # # 設定完了ページにアクセスして200 OKが返ることを確認
        # response = self.client.get('/setting/complete')
        # self.assertEqual(response.status_code, 200)

        # # 再読み込みすると404が返ることを確認
        # response = self.client.get('/setting/complete')
        # self.assertEqual(response.status_code, 404)

    def test_setting_view_no_reset_request_user(self):
        """
        再設定要求がないユーザーが設定ページにアクセスした場合のテスト
        """
        # テストユーザーを作成
        User.objects.create_user(
            username='testuser2',
            password='testpass'
        )

        self.client.login(username='testuser2', password='testpass')

        # 設定ページにアクセスして403 Forbiddenが返ることを確認
        response = self.client.get('/setting')
        self.assertEqual(response.status_code, 403)

        response = self.client.post('/setting', {
            'old_password': 'testpass',
            'new_password1': 'newtestpass',
            'new_password2': 'newtestpass',
            'first_name': 'Test',
            'last_name': 'User'
        })
        self.assertEqual(response.status_code, 403)

    def test_setting_view_no_reset_request(self):
        """
        設定完了後，再設定要求が存在しないことを確認
        """
        # テストユーザーを作成
        test_user = User.objects.create_user(
            username='testuser2',
            password='testpass'
        )

        # 再設定要求を作成
        ResetRequest.objects.create(user=test_user)

        self.client.login(username='testuser2', password='testpass')

        # 設定ページにPOSTリクエストを送信してリダイレクトされることを確認
        response = self.client.post('/setting', {
            'old_password': 'testpass',
            'new_password1': 'newtestpass',
            'new_password2': 'newtestpass',
            'first_name': 'Test',
            'last_name': 'User'
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/setting/complete')

        # 再設定要求が存在しないことを確認
        reset_request_exists = ResetRequest.objects.filter(
            user=test_user
        ).exists()
        self.assertFalse(reset_request_exists)
