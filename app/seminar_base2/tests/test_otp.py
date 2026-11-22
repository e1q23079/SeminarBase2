import pyotp
from django.test import TestCase
from ..models import OneTimePassword, NoSettingPermission
from django.contrib.auth.models import User


# ワンタイムパスワード設定メニューのビューのテスト
class OneTimePasswordMenuViewTests(TestCase):
    def setUp(self):
        '''
        テスト用アカウントを作成する
        '''
        self.user = User.objects.create_user(
            username='testuser', password='testpassword'
        )

    def test_one_time_password_menu_view_not_login(self):
        '''
        ワンタイムパスワード設定メニューのビューのテスト（ログインしていない場合）
        '''
        response = self.client.get('/settings/otp')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response,
            '/accounts/login/?next=/settings/otp'
        )

    def test_one_time_password_menu_view_login(self):
        '''
        ワンタイムパスワード設定メニューのビューのテスト（ログインしている場合）
        '''
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get('/settings/otp')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'settings/otp/otp_menu.html')

    def test_one_time_password_menu_view_login_no_setting_permission(self):
        '''
        ワンタイムパスワード設定メニューのビューのテスト（ログインしている場合，設定権限がない）
        '''
        NoSettingPermission.objects.create(user=self.user)
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get('/settings/otp')
        self.assertEqual(response.status_code, 403)

    def test_one_time_password_menu_view_login_no_setting_permission_2(self):
        '''
        ワンタイムパスワード設定メニューのビューのテスト（ログインしている場合，設定権限がない）
        '''
        NoSettingPermission.objects.create(user=self.user)
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get('/settings/otp')
        self.assertEqual(response.status_code, 403)


# ワンタイムパスワードシークレットキーを取得するためのビューのテスト
class OneTimePasswordGetSecretKeyViewTests(TestCase):
    def setUp(self):
        '''
        テスト用アカウントを作成する
        '''
        self.user = User.objects.create_user(
            username='testuser', password='testpassword'
        )

    def test_one_time_password_get_secret_key_view_not_login(self):
        '''
        ワンタイムパスワードシークレットキーを取得するためのビューのテスト（ログインしていない場合）
        '''
        response = self.client.get('/settings/otp/get/secret_key')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response,
            '/accounts/login/?next=/settings/otp/get/secret_key'
        )

    def test_one_time_password_get_secret_key_view_login(self):
        '''
        ワンタイムパスワードシークレットキーを取得するためのビューのテスト（ログインしている場合）
        '''
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get('/settings/otp/get/secret_key')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            'settings/otp/otp_show_secret_key.html'
        )

    def test_one_time_password_get_secret_key_view_login_no_setting_permission(self):  # noqa: E501
        '''
        ワンタイムパスワードシークレットキーを取得するためのビューのテスト（ログインしている場合，設定権限がない）
        '''
        NoSettingPermission.objects.create(user=self.user)
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get('/settings/otp/get/secret_key')
        self.assertEqual(response.status_code, 403)


# ワンタイムパスワードを有効にするためのビューのテスト
class OneTimePasswordEnableViewTests(TestCase):
    def setUp(self):
        '''
        テスト用アカウントを作成する
        '''
        self.user = User.objects.create_user(
            username='testuser', password='testpassword'
        )

    def test_one_time_password_enable_view_not_login(self):
        '''
        ワンタイムパスワードを有効にするためのビューのテスト（ログインしていない場合）
        '''
        response = self.client.get('/settings/otp/enable')
        self.assertEqual(response.status_code, 302)

        response = self.client.post('/settings/otp/enable', {
            'otp_code': '123456'
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response,
            '/accounts/login/?next=/settings/otp/enable'
        )

    def test_one_time_password_enable_view_login(self):
        '''
        ワンタイムパスワードを有効にするためのビューのテスト（ログインしている場合）
        '''
        self.client.login(username='testuser', password='testpassword')
        # シークレットキーを取得していない
        response = self.client.get('/settings/otp/enable')
        self.assertEqual(response.status_code, 403)

        response = self.client.post('/settings/otp/enable', {
            'otp_code': '123456'
        })
        self.assertEqual(response.status_code, 403)
        self.client.logout()

        self.client.login(username='testuser', password='testpassword')
        # シークレットキーを取得する
        self.client.get('/settings/otp/get/secret_key')

        response = self.client.get('/settings/otp/enable')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'settings/otp/otp_setting.html')

        response = self.client.post('/settings/otp/enable', {
            'otp_code': '123456'
        })
        self.assertEqual(response.status_code, 200)
        # ワンタイムパスワードを有効にする
        OneTimePassword.objects.filter(user=self.user).update(is_enabled=True)

        session = self.client.session
        session['otp_authenticated'] = True
        session.save()
        response = self.client.get('/settings/otp/enable')
        self.assertEqual(response.status_code, 403)

        response = self.client.post('/settings/otp/enable', {
            'otp_code': '123456'
        })
        self.assertEqual(response.status_code, 403)
        self.client.logout()

    def test_one_time_password_enable_view_login_no_setting_permission(self):
        '''
        ワンタイムパスワードを有効にするためのビューのテスト（ログインしている場合，設定権限がない）
        '''
        NoSettingPermission.objects.create(user=self.user)
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get('/settings/otp/enable')
        self.assertEqual(response.status_code, 403)

        response = self.client.post('/settings/otp/enable', {
            'otp_code': '123456'
        })
        self.assertEqual(response.status_code, 403)

    def test_one_time_password_enable_view_login_success_post(self):
        '''
        ワンタイムパスワードを有効にするためのビューのテスト（ワンタイムパスワード認証成功：POST）
        '''
        self.client.login(username='testuser', password='testpassword')
        # シークレットキーを取得する
        self.client.get('/settings/otp/get/secret_key')

        totp = pyotp.totp.TOTP(
            OneTimePassword.objects.get(user=self.user).secret_key
        )
        otp_code = totp.now()
        response = self.client.post('/settings/otp/enable', {
            'otp_code': otp_code
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'settings/complete.html')

    def test_one_time_password_enable_view_login_fail_post(self):
        '''
        ワンタイムパスワードを有効にするためのビューのテスト（ワンタイムパスワード認証失敗：POST）
        '''
        self.client.login(username='testuser', password='testpassword')
        # シークレットキーを取得する
        self.client.get('/settings/otp/get/secret_key')

        response = self.client.post('/settings/otp/enable', {
            'otp_code': '123456'
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'settings/otp/otp_setting.html')

    def test_one_time_password_enable_view_login_fail_post_max_attempts(self):
        '''
        ワンタイムパスワードを有効にするためのビューのテスト（ワンタイムパスワード認証失敗：最大試行回数に達した）
        '''
        self.client.login(username='testuser', password='testpassword')
        # シークレットキーを取得する
        self.client.get('/settings/otp/get/secret_key')

        for _ in range(5):
            response = self.client.post('/settings/otp/enable', {
                'otp_code': '123456'
            })
            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response, 'settings/otp/otp_setting.html')

        response = self.client.post('/settings/otp/enable', {
            'otp_code': '123456'
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'settings/otp/otp_setting.html')


# ワンタイムパスワードを無効にするためのビューのテスト
class OneTimePasswordDisableViewTests(TestCase):
    def setUp(self):
        '''
        テスト用アカウントを作成する
        '''
        self.user = User.objects.create_user(
            username='testuser', password='testpassword'
        )

    def test_one_time_password_disable_view_not_login(self):
        '''
        ワンタイムパスワードを無効にするためのビューのテスト（ログインしていない場合）
        '''
        response = self.client.get('/settings/otp/disable')
        self.assertEqual(response.status_code, 302)

        response = self.client.post('/settings/otp/disable', {
            'otp_code': '123456'
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response,
            '/accounts/login/?next=/settings/otp/disable'
        )

    def test_one_time_password_disable_view_login(self):
        '''
        ワンタイムパスワードを無効にするためのビューのテスト（ログインしている場合）
        '''
        self.client.login(username='testuser', password='testpassword')
        # シークレットキーを取得していない
        response = self.client.get('/settings/otp/disable')
        self.assertEqual(response.status_code, 403)

        response = self.client.post('/settings/otp/disable', {
            'otp_code': '123456'
        })
        self.assertEqual(response.status_code, 403)
        self.client.logout()

        self.client.login(username='testuser', password='testpassword')
        # シークレットキーを取得する
        self.client.get('/settings/otp/get/secret_key')

        response = self.client.get('/settings/otp/disable')
        self.assertEqual(response.status_code, 403)

        response = self.client.post('/settings/otp/disable', {
            'otp_code': '123456'
        })
        self.assertEqual(response.status_code, 403)

        # ワンタイムパスワードを有効にする
        OneTimePassword.objects.filter(user=self.user).update(is_enabled=True)

        session = self.client.session
        session['otp_authenticated'] = True
        session.save()
        response = self.client.get('/settings/otp/disable')
        self.assertEqual(response.status_code, 200)

        response = self.client.post('/settings/otp/disable', {
            'otp_code': '123456'
        })
        self.assertEqual(response.status_code, 200)
        self.client.logout()

    def test_one_time_password_disable_view_login_no_setting_permission(self):
        '''
        ワンタイムパスワードを無効にするためのビューのテスト（ログインしている場合，設定権限がない）
        '''
        NoSettingPermission.objects.create(user=self.user)
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get('/settings/otp/disable')
        self.assertEqual(response.status_code, 403)

        response = self.client.post('/settings/otp/disable', {
            'otp_code': '123456'
        })
        self.assertEqual(response.status_code, 403)

    def test_one_time_password_disable_view_login_success_post(self):
        '''
        ワンタイムパスワードを無効にするためのビューのテスト（ワンタイムパスワード認証成功：POST）
        '''
        self.client.login(username='testuser', password='testpassword')
        # シークレットキーを取得する
        self.client.get('/settings/otp/get/secret_key')

        # ワンタイムパスワードを有効にする
        OneTimePassword.objects.filter(user=self.user).update(is_enabled=True)
        session = self.client.session
        session['otp_authenticated'] = True
        session.save()

        totp = pyotp.totp.TOTP(
            OneTimePassword.objects.get(user=self.user).secret_key
        )
        otp_code = totp.now()
        response = self.client.post('/settings/otp/disable', {
            'otp_code': otp_code
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'settings/complete.html')

    def test_one_time_password_disable_view_login_fail_post(self):
        '''
        ワンタイムパスワードを無効にするためのビューのテスト（ワンタイムパスワード認証失敗：POST）
        '''
        self.client.login(username='testuser', password='testpassword')
        # シークレットキーを取得する
        self.client.get('/settings/otp/get/secret_key')

        # ワンタイムパスワードを有効にする
        OneTimePassword.objects.filter(user=self.user).update(is_enabled=True)
        session = self.client.session
        session['otp_authenticated'] = True
        session.save()

        response = self.client.post('/settings/otp/disable', {
            'otp_code': '123456'
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'settings/otp/otp_setting.html')

    def test_one_time_password_disable_view_login_fail_post_max_attempts(self):
        '''
        ワンタイムパスワードを無効にするためのビューのテスト（ワンタイムパスワード認証失敗：最大試行回数に達した）
        '''
        self.client.login(username='testuser', password='testpassword')
        # シークレットキーを取得する
        self.client.get('/settings/otp/get/secret_key')
        # ワンタイムパスワードを有効にする
        OneTimePassword.objects.filter(user=self.user).update(is_enabled=True)
        session = self.client.session
        session['otp_authenticated'] = True
        session.save()

        for _ in range(5):
            response = self.client.post('/settings/otp/disable', {
                'otp_code': '123456'
            })
            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response, 'settings/otp/otp_setting.html')

        response = self.client.post('/settings/otp/disable', {
            'otp_code': '123456'
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'settings/otp/otp_setting.html')


# ワンタイムパスワードを削除するためのビューのテスト
class OneTimePasswordDeleteViewTests(TestCase):
    def setUp(self):
        '''
        テスト用アカウントを作成する
        '''
        self.user = User.objects.create_user(
            username='testuser', password='testpassword'
        )

    def test_one_time_password_delete_view_not_login(self):
        '''
        ワンタイムパスワードを削除するためのビューのテスト（ログインしていない場合）
        '''
        response = self.client.get('/settings/otp/delete')
        self.assertEqual(response.status_code, 302)

        response = self.client.post('/settings/otp/delete', {
            'otp_code': '123456'
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response,
            '/accounts/login/?next=/settings/otp/delete'
        )

    def test_one_time_password_delete_view_login(self):
        '''
        ワンタイムパスワードを削除するためのビューのテスト（ログインしている場合）
        '''
        self.client.login(username='testuser', password='testpassword')
        # シークレットキーを取得していない
        response = self.client.get('/settings/otp/delete')
        self.assertEqual(response.status_code, 403)

        response = self.client.post('/settings/otp/delete', {
            'otp_code': '123456'
        })
        self.assertEqual(response.status_code, 403)
        self.client.logout()

        self.client.login(username='testuser', password='testpassword')
        # シークレットキーを取得する
        self.client.get('/settings/otp/get/secret_key')

        response = self.client.get('/settings/otp/delete')
        self.assertEqual(response.status_code, 200)

        response = self.client.post('/settings/otp/delete', {
            'otp_code': '123456'
        })
        self.assertEqual(response.status_code, 200)

        # ワンタイムパスワードを有効にする
        OneTimePassword.objects.filter(user=self.user).update(is_enabled=True)

        session = self.client.session
        session['otp_authenticated'] = True
        session.save()
        response = self.client.get('/settings/otp/delete')
        self.assertEqual(response.status_code, 200)

        response = self.client.post('/settings/otp/delete', {
            'otp_code': '123456'
        })
        self.assertEqual(response.status_code, 200)
        self.client.logout()

    def test_one_time_password_delete_view_login_no_setting_permission(self):
        '''
        ワンタイムパスワードを削除するためのビューのテスト（ログインしている場合，設定権限がない）
        '''
        NoSettingPermission.objects.create(user=self.user)
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get('/settings/otp/delete')
        self.assertEqual(response.status_code, 403)

        response = self.client.post('/settings/otp/delete', {
            'otp_code': '123456'
        })
        self.assertEqual(response.status_code, 403)

    def test_one_time_password_delete_view_login_success_post(self):
        '''
        ワンタイムパスワードを削除するためのビューのテスト（ワンタイムパスワード認証成功：POST）
        '''
        self.client.login(username='testuser', password='testpassword')
        # シークレットキーを取得する
        self.client.get('/settings/otp/get/secret_key')

        # ワンタイムパスワードを有効にする
        OneTimePassword.objects.filter(user=self.user).update(is_enabled=True)
        session = self.client.session
        session['otp_authenticated'] = True
        session.save()

        totp = pyotp.totp.TOTP(
            OneTimePassword.objects.get(user=self.user).secret_key
        )
        otp_code = totp.now()
        response = self.client.post('/settings/otp/delete', {
            'otp_code': otp_code
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'settings/complete.html')

    def test_one_time_password_delete_view_login_fail_post(self):
        '''
        ワンタイムパスワードを削除するためのビューのテスト（ワンタイムパスワード認証失敗：POST）
        '''
        self.client.login(username='testuser', password='testpassword')
        # シークレットキーを取得する
        self.client.get('/settings/otp/get/secret_key')

        # ワンタイムパスワードを有効にする
        OneTimePassword.objects.filter(user=self.user).update(is_enabled=True)
        session = self.client.session
        session['otp_authenticated'] = True
        session.save()

        response = self.client.post('/settings/otp/delete', {
            'otp_code': '123456'
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'settings/otp/otp_setting.html')

    def test_one_time_password_delete_view_login_fail_post_max_attempts(self):
        '''
        ワンタイムパスワードを削除するためのビューのテスト（ワンタイムパスワード認証失敗：最大試行回数に達した）
        '''
        self.client.login(username='testuser', password='testpassword')
        # シークレットキーを取得する
        self.client.get('/settings/otp/get/secret_key')
        # ワンタイムパスワードを有効にする
        OneTimePassword.objects.filter(user=self.user).update(is_enabled=True)
        session = self.client.session
        session['otp_authenticated'] = True
        session.save()

        for _ in range(5):
            response = self.client.post('/settings/otp/delete', {
                'otp_code': '123456'
            })
            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response, 'settings/otp/otp_setting.html')

        response = self.client.post('/settings/otp/delete', {
            'otp_code': '123456'
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'settings/otp/otp_setting.html')


# ワンタイムパスワード認証
class OneTimePasswordAuthenticationTests(TestCase):
    def setUp(self):
        """
        テスト用アカウントを作成する
        """
        self.user = User.objects.create_user(
            username='testuser', password='testpassword'
        )

    def test_one_time_password_authentication_success(self):
        """
        ワンタイムパスワード認証のテスト（成功）
        """
        self.client.login(username='testuser', password='testpassword')
        # シークレットキーを取得する
        self.client.get('/settings/otp/get/secret_key')

        # ワンタイムパスワードを有効にする
        OneTimePassword.objects.filter(user=self.user).update(is_enabled=True)
        session = self.client.session
        session['otp_authenticated'] = True
        session.save()

        totp = pyotp.totp.TOTP(
            OneTimePassword.objects.get(user=self.user).secret_key
        )
        otp_code = totp.now()
        response = self.client.post('/accounts/otp/auth', {
            'otp_code': otp_code
        })
        self.assertEqual(response.status_code, 302)

    def test_one_time_password_authentication_fail(self):
        """
        ワンタイムパスワード認証のテスト（失敗）
        """
        self.client.login(username='testuser', password='testpassword')
        # シークレットキーを取得する
        self.client.get('/settings/otp/get/secret_key')

        # ワンタイムパスワードを有効にする
        OneTimePassword.objects.filter(user=self.user).update(is_enabled=True)
        session = self.client.session
        session['otp_authenticated'] = True
        session.save()

        response = self.client.post('/accounts/otp/auth', {
            'otp_code': '123456'
        })
        self.assertEqual(response.status_code, 200)

    def test_one_time_password_authentication_fail_max_attempts(self):
        """
        ワンタイムパスワード認証のテスト（失敗：最大試行回数に達した）
        """
        self.client.login(username='testuser', password='testpassword')
        # シークレットキーを取得する
        self.client.get('/settings/otp/get/secret_key')

        # ワンタイムパスワードを有効にする
        OneTimePassword.objects.filter(user=self.user).update(is_enabled=True)
        session = self.client.session
        session['otp_authenticated'] = True
        session.save()

        for _ in range(5):
            response = self.client.post('/accounts/otp/auth', {
                'otp_code': '123456'
            })
            self.assertEqual(response.status_code, 200)

        response = self.client.post('/accounts/otp/auth', {
            'otp_code': '123456'
        })
        self.assertEqual(response.status_code, 302)

    def test_one_time_password_authentication_recent_code_used(self):
        """
        ワンタイムパスワード認証のテスト（失敗：直近30秒のコードが使われた）
        """
        self.client.login(username='testuser', password='testpassword')
        # シークレットキーを取得する
        self.client.get('/settings/otp/get/secret_key')

        # ワンタイムパスワードを有効にする
        OneTimePassword.objects.filter(user=self.user).update(is_enabled=True)
        session = self.client.session
        session['otp_authenticated'] = True
        session.save()

        totp = pyotp.totp.TOTP(
            OneTimePassword.objects.get(user=self.user).secret_key
        )
        otp_code = totp.now()
        response = self.client.post('/accounts/otp/auth', {
            'otp_code': otp_code
        })
        self.assertEqual(response.status_code, 302)

        # 直近30秒のコードを再度使用する
        response = self.client.post('/accounts/otp/auth', {
            'otp_code': otp_code
        })
        self.assertEqual(response.status_code, 200)

    def test_one_time_password_authentication_enabled_redirect(self):
        """
        ワンタイムパスワード認証のテスト（失敗：ワンタイムパスワードが有効なときリダイレクト）
        """
        self.client.login(username='testuser', password='testpassword')
        # シークレットキーを取得する
        self.client.get('/settings/otp/get/secret_key')

        # ワンタイムパスワードを有効にする
        OneTimePassword.objects.filter(user=self.user).update(is_enabled=True)

        # ワンタイムパスワードページにリダイレクト
        response = self.client.get('/settings')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/otp/auth?next=/settings')

    def test_one_time_password_authentication_disabled_not_redirect(self):
        """
        ワンタイムパスワード認証のテスト（失敗：ワンタイムパスワードが無効なときリダイレクトしない）
        """
        self.client.login(username='testuser', password='testpassword')
        # シークレットキーを取得する
        self.client.get('/settings/otp/get/secret_key')

        # ワンタイムパスワードを無効にする
        OneTimePassword.objects.filter(user=self.user).update(is_enabled=False)
        session = self.client.session
        session['otp_authenticated'] = True
        session.save()

        # ワンタイムパスワードページにリダイレクトしない
        response = self.client.get('/settings')
        self.assertEqual(response.status_code, 200)
