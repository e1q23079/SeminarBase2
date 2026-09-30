from django.test import TestCase
from ..models import NoSettingPermission
from django.contrib.auth.models import User


# 設定メニューページのビューのテスト
class SettingsMenuViewTests(TestCase):
    def setUp(self):
        '''
        テスト用アカウントを作成する
        '''
        # スーパーユーザーを作成
        self.superuser = User.objects.create_superuser(
            username='admin', password='adminpassword'
        )
        # スタッフユーザーを作成
        self.staffuser = User.objects.create_user(
            username='staffuser', password='staffpassword', is_staff=True
        )
        # 一般ユーザーを作成
        self.normaluser = User.objects.create_user(
            username='normaluser', password='normalpassword'
        )
        # 設定権限を制限されたユーザーを作成
        self.restricteduser = User.objects.create_user(
            username='restricteduser', password='restrictedpassword'
        )
        NoSettingPermission.objects.create(user=self.restricteduser)

    def test_settings_menu_view_not_login(self):
        '''
        設定メニューページのビューのテスト（ログインしていない場合）
        '''
        response = self.client.get('/settings')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response,
            '/accounts/login/?next=/settings'
        )

    def test_settings_menu_view_login_superuser(self):
        '''
        設定メニューページのビューのテスト（ログインしている場合，スーパーユーザー）
        '''
        self.client.login(username='admin', password='adminpassword')
        response = self.client.get('/settings')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'settings/menu.html')

    def test_settings_menu_view_login_staffuser(self):
        '''
        設定メニューページのビューのテスト（ログインしている場合，スタッフユーザー）
        '''
        self.client.login(username='staffuser', password='staffpassword')
        response = self.client.get('/settings')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'settings/menu.html')

    def test_settings_menu_view_login_normaluser(self):
        '''
        設定メニューページのビューのテスト（ログインしている場合，一般ユーザー）
        '''
        self.client.login(username='normaluser', password='normalpassword')
        response = self.client.get('/settings')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'settings/menu.html')

    def test_settings_menu_view_login_restricteduser(self):
        '''
        設定メニューページのビューのテスト（ログインしている場合，設定権限を制限されたユーザー）
        '''
        self.client.login(
            username='restricteduser',
            password='restrictedpassword'
        )
        response = self.client.get('/settings')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'no_available.html')


# 名前変更ページのビューのテスト
class SettingsNameViewTests(TestCase):
    def setUp(self):
        '''
        テスト用アカウントを作成する
        '''
        # スーパーユーザーを作成
        self.superuser = User.objects.create_superuser(
            username='admin', password='adminpassword'
        )
        # スタッフユーザーを作成
        self.staffuser = User.objects.create_user(
            username='staffuser', password='staffpassword', is_staff=True
        )
        # 一般ユーザーを作成
        self.normaluser = User.objects.create_user(
            username='normaluser', password='normalpassword'
        )
        # 設定権限を制限されたユーザーを作成
        self.restricteduser = User.objects.create_user(
            username='restricteduser', password='restrictedpassword'
        )
        NoSettingPermission.objects.create(user=self.restricteduser)

    def test_settings_name_view_not_login_get(self):
        '''
        名前変更ページのビューのテスト（ログインしていない場合：GETリクエスト）
        '''
        response = self.client.get('/settings/name')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response,
            '/accounts/login/?next=/settings/name'
        )

    def test_settings_name_view_not_login_post(self):
        '''
        名前変更ページのビューのテスト（ログインしていない場合：POSTリクエスト）
        '''
        response = self.client.post('/settings/name', {
            'first_name': 'Test',
            'last_name': 'User'
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response,
            '/accounts/login/?next=/settings/name'
        )

    def test_settings_name_view_login_superuser_get(self):
        '''
        名前変更ページのビューのテスト（ログインしている場合，スーパーユーザー：GETリクエスト）
        '''
        self.client.login(username='admin', password='adminpassword')
        response = self.client.get('/settings/name')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'settings/name.html')

    def test_settings_name_view_login_superuser_post(self):
        '''
        名前変更ページのビューのテスト（ログインしている場合，スーパーユーザー：POSTリクエスト）
        '''
        self.client.login(username='admin', password='adminpassword')
        response = self.client.post('/settings/name', {
            'first_name': 'Test',
            'last_name': 'User'
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'settings/complete.html')

    def test_settings_name_view_login_staffuser_get(self):
        '''
        名前変更ページのビューのテスト（ログインしている場合，スタッフユーザー：GETリクエスト）
        '''
        self.client.login(username='staffuser', password='staffpassword')
        response = self.client.get('/settings/name')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'settings/name.html')

    def test_settings_name_view_login_staffuser_post(self):
        '''
        名前変更ページのビューのテスト（ログインしている場合，スタッフユーザー：POSTリクエスト）
        '''
        self.client.login(username='staffuser', password='staffpassword')
        response = self.client.post('/settings/name', {
            'first_name': 'Test',
            'last_name': 'User'
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'settings/complete.html')

    def test_settings_name_view_login_normaluser_get(self):
        '''
        名前変更ページのビューのテスト（ログインしている場合，一般ユーザー：GETリクエスト）
        '''
        self.client.login(username='normaluser', password='normalpassword')
        response = self.client.get('/settings/name')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'settings/name.html')

    def test_settings_name_view_login_normaluser_post(self):
        '''
        名前変更ページのビューのテスト（ログインしている場合，一般ユーザー：POSTリクエスト）
        '''
        self.client.login(username='normaluser', password='normalpassword')
        response = self.client.post('/settings/name', {
            'first_name': 'Test',
            'last_name': 'User'
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'settings/complete.html')

    def test_settings_name_view_login_restricteduser_get(self):
        '''
        名前変更ページのビューのテスト（ログインしている場合，設定権限を制限されたユーザー：GETリクエスト）
        '''
        self.client.login(
            username='restricteduser',
            password='restrictedpassword'
        )
        response = self.client.get('/settings/name')
        self.assertEqual(response.status_code, 403)

    def test_settings_name_view_login_restricteduser_post(self):
        '''
        名前変更ページのビューのテスト（ログインしている場合，設定権限を制限されたユーザー：POSTリクエスト）
        '''
        self.client.login(
            username='restricteduser',
            password='restrictedpassword'
            )
        response = self.client.post('/settings/name', {
            'first_name': 'Test',
            'last_name': 'User'
        })
        self.assertEqual(response.status_code, 403)


# パスワード変更ページのビューのテスト
class SettingsPasswordViewTests(TestCase):
    def setUp(self):
        '''
        テスト用アカウントを作成する
        '''
        # スーパーユーザーを作成
        self.superuser = User.objects.create_superuser(
            username='admin', password='adminpassword'
        )
        # スタッフユーザーを作成
        self.staffuser = User.objects.create_user(
            username='staffuser', password='staffpassword', is_staff=True
        )
        # 一般ユーザーを作成
        self.normaluser = User.objects.create_user(
            username='normaluser', password='normalpassword'
        )
        # 設定権限を制限されたユーザーを作成
        self.restricteduser = User.objects.create_user(
            username='restricteduser', password='restrictedpassword'
        )
        NoSettingPermission.objects.create(user=self.restricteduser)
        # テストユーザーを作成
        self.testuser = User.objects.create_user(
            username='testuser', password='testpass'
        )

    def test_settings_password_view_not_login_get(self):
        '''
        パスワード変更ページのビューのテスト（ログインしていない場合：GETリクエスト）
        '''
        response = self.client.get('/settings/password')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response,
            '/accounts/login/?next=/settings/password'
        )

    def test_settings_password_view_not_login_post(self):
        '''
        パスワード変更ページのビューのテスト（ログインしていない場合：POSTリクエスト）
        '''
        response = self.client.post('/settings/password', {
            'old_password': 'oldpassword',
            'new_password1': 'new7pas8swo9rd',
            'new_password2': 'new7pas8swo9rd'
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response,
            '/accounts/login/?next=/settings/password'
        )

    def test_settings_password_view_login_superuser_get(self):
        '''
        パスワード変更ページのビューのテスト（ログインしている場合，スーパーユーザー：GETリクエスト）
        '''
        self.client.login(username='admin', password='adminpassword')
        response = self.client.get('/settings/password')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'settings/password.html')

    def test_settings_password_view_login_superuser_post(self):
        '''
        パスワード変更ページのビューのテスト（ログインしている場合，スーパーユーザー：POSTリクエスト）
        '''
        self.client.login(username='admin', password='adminpassword')
        response = self.client.post('/settings/password', {
            'old_password': 'adminpassword',
            'new_password1': 'new7pas8swo9rd',
            'new_password2': 'new7pas8swo9rd'
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'settings/complete.html')

    def test_settings_password_view_login_staffuser_get(self):
        '''
        パスワード変更ページのビューのテスト（ログインしている場合，スタッフユーザー：GETリクエスト）
        '''
        self.client.login(username='staffuser', password='staffpassword')
        response = self.client.get('/settings/password')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'settings/password.html')

    def test_settings_password_view_login_staffuser_post(self):
        '''
        パスワード変更ページのビューのテスト（ログインしている場合，スタッフユーザー：POSTリクエスト）
        '''
        self.client.login(username='staffuser', password='staffpassword')
        response = self.client.post('/settings/password', {
            'old_password': 'staffpassword',
            'new_password1': 'new7pas8swo9rd',
            'new_password2': 'new7pas8swo9rd'
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'settings/complete.html')

    def test_settings_password_view_login_normaluser_get(self):
        '''
        パスワード変更ページのビューのテスト（ログインしている場合，一般ユーザー：GETリクエスト）
        '''
        self.client.login(username='normaluser', password='normalpassword')
        response = self.client.get('/settings/password')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'settings/password.html')

    def test_settings_password_view_login_normaluser_post(self):
        '''
        パスワード変更ページのビューのテスト（ログインしている場合，一般ユーザー：POSTリクエスト）
        '''
        self.client.login(username='normaluser', password='normalpassword')
        response = self.client.post('/settings/password', {
            'old_password': 'normalpassword',
            'new_password1': 'new7pas8swo9rd',
            'new_password2': 'new7pas8swo9rd'
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'settings/complete.html')

    def test_settings_password_view_login_restricteduser_get(self):
        '''
        パスワード変更ページのビューのテスト（ログインしている場合，設定権限を制限されたユーザー：GETリクエスト）
        '''
        self.client.login(
            username='restricteduser',
            password='restrictedpassword'
        )
        response = self.client.get('/settings/password')
        self.assertEqual(response.status_code, 403)

    def test_settings_password_view_login_restricteduser_post(self):
        '''
        パスワード変更ページのビューのテスト（ログインしている場合，設定権限を制限されたユーザー：POSTリクエスト）
        '''
        self.client.login(
            username='restricteduser',
            password='restrictedpassword'
        )
        response = self.client.post('/settings/password', {
            'old_password': 'restrictedpassword',
            'new_password1': 'new7pas8swo9rd',
            'new_password2': 'new7pas8swo9rd'
        })
        self.assertEqual(response.status_code, 403)

    def test_settings_view_post_wrong_old_password(self):
        """
        古いパスワードが間違っている場合のテスト
        """
        self.client.login(username='testuser', password='testpass')

        # 古いパスワードが間違っている場合のテスト
        response = self.client.post('/settings/password', {
            'old_password': 'wrongpass',
            'new_password1': 'newtestpass',
            'new_password2': 'newtestpass',
            'first_name': 'Test',
            'last_name': 'User'
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'settings/password.html')

    def test_settings_view_post_password_mismatch(self):
        """
        パスワードの不一致をテスト
        """
        self.client.login(username='testuser', password='testpass')

        # パスワードの不一致をテスト
        response = self.client.post('/settings/password', {
            'old_password': 'testpass',
            'new_password1': 'newtestpass',
            'new_password2': 'differentpass',
            'first_name': 'Test',
            'last_name': 'User'
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'settings/password.html')
