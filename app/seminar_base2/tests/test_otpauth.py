from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from django.contrib.sessions.backends.db import SessionStore
from ..models import OneTimePassword
from ..lib.otpauth import OTPAuth
import pyotp


class OTPAuthTest(TestCase):
    """
    SeminarBase2のワンタイムパスワード認証機能のテストケース
    """
    def setUp(self):
        """
        テストのセットアップ
        """
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword'
        )
        self.factory = RequestFactory()
        self.request = self.factory.get('/')
        self.request.user = self.user

        # セッションを設定
        self.request.session = SessionStore()

    def test_get_otp(self):
        """
        ワンタイムパスワードの取得が正しく行われることを確認
        """
        otp_auth = OTPAuth(self.request)
        qr_code, otp_secret_key = otp_auth.get_otp()
        self.assertIsNotNone(qr_code)
        self.assertIsNotNone(otp_secret_key)
        otp_auth = OTPAuth(self.request)
        qr_code2, otp_secret_key2 = otp_auth.get_otp()
        self.assertEqual(qr_code, qr_code2)
        self.assertEqual(otp_secret_key, otp_secret_key2)

    def test_enable_disable_otp_enabled(self):
        """
        ワンタイムパスワードの有効化
        """
        otp_auth = OTPAuth(self.request)
        otp_auth.get_otp()  # シークレットキーを生成
        otp_auth.disable_otp()
        otp_auth.enable_otp()
        otp_obj = OneTimePassword.objects.get(user=self.request.user)
        self.assertTrue(otp_obj.is_enabled)
        self.assertTrue(otp_auth.is_otp_required())

    def test_disable_otp_disabled(self):
        """
        ワンタイムパスワードの無効化が正しく行われることを確認
        """
        otp_auth = OTPAuth(self.request)
        otp_auth.get_otp()  # シークレットキーを生成
        otp_auth.enable_otp()
        otp_auth.disable_otp()
        otp_obj = OneTimePassword.objects.get(user=self.request.user)
        self.assertFalse(otp_obj.is_enabled)
        self.assertFalse(otp_auth.is_otp_required())

    def test_delete_otp(self):
        """
        ワンタイムパスワードの削除が正しく行われることを確認
        """
        otp_auth = OTPAuth(self.request)
        otp_auth.get_otp()
        otp_obj = OneTimePassword.objects.get(user=self.request.user)
        self.assertIsNotNone(otp_obj)

        otp_auth.delete_otp()
        otp_obj = OneTimePassword.objects.filter(
            user=self.request.user
        ).first()
        self.assertIsNone(otp_obj)
        self.assertFalse(otp_auth.is_otp_secret_key_set())

    def test_authenticate_valid_code(self):
        """
        ワンタイムパスワードの認証が正しく行われることを確認（有効なコード）
        """
        otp_auth = OTPAuth(self.request)
        qr_code, otp_secret_key = otp_auth.get_otp()
        otp_auth.enable_otp()
        self.assertIsNotNone(qr_code)
        self.assertIsNotNone(otp_secret_key)

        totp = pyotp.totp.TOTP(otp_secret_key)
        valid_code = totp.now()

        (
            is_authenticated,
            error_message,
            error_code
        ) = otp_auth.authenticate(valid_code)
        self.assertTrue(is_authenticated)
        self.assertIsNone(error_message)
        self.assertIsNone(error_code)

    def test_authenticate_invalid_code(self):
        """
        ワンタイムパスワードの認証が正しく行われることを確認（無効なコード）
        """
        otp_auth = OTPAuth(self.request)
        qr_code, otp_secret_key = otp_auth.get_otp()
        otp_auth.enable_otp()
        self.assertIsNotNone(qr_code)
        self.assertIsNotNone(otp_secret_key)
        invalid_code = '123456'
        (
            is_authenticated,
            error_message,
            error_code
        ) = otp_auth.authenticate(invalid_code)
        self.assertFalse(is_authenticated)
        self.assertIsNotNone(error_message)
        self.assertIsNotNone(error_code)

    def test_authenticate_max_attempts_exceeded(self):
        """
        ワンタイムパスワードの認証が正しく行われることを確認（最大試行回数超過）
        """
        otp_auth = OTPAuth(self.request)
        qr_code, otp_secret_key = otp_auth.get_otp()
        otp_auth.enable_otp()
        self.assertIsNotNone(qr_code)
        self.assertIsNotNone(otp_secret_key)

        invalid_code = '123456'

        for _ in range(otp_auth.max_attempts):
            (
                is_authenticated,
                _,
                error_code
            ) = otp_auth.authenticate(invalid_code)
            self.assertFalse(is_authenticated)
            self.assertEqual(error_code, 'otp_invalid')

        (
            is_authenticated,
            _,
            error_code
        ) = otp_auth.authenticate(invalid_code)
        self.assertFalse(is_authenticated)
        self.assertEqual(error_code, 'otp_max_attempts_exceeded')

    def test_authenticate_replay_attack(self):
        """
        ワンタイムパスワードの認証が正しく行われることを確認（リプレイ攻撃防止）
        """
        otp_auth = OTPAuth(self.request)
        qr_code, otp_secret_key = otp_auth.get_otp()
        otp_auth.enable_otp()
        self.assertIsNotNone(qr_code)
        self.assertIsNotNone(otp_secret_key)

        totp = pyotp.totp.TOTP(otp_secret_key)
        valid_code = totp.now()

        (
            is_authenticated,
            _,
            error_code
        ) = otp_auth.authenticate(valid_code)
        self.assertTrue(is_authenticated)

        (
            is_authenticated,
            _,
            error_code
        ) = otp_auth.authenticate(valid_code)
        self.assertFalse(is_authenticated)
        self.assertEqual(error_code, 'otp_already_used')

    def test_is_authenticated(self):
        """
        ワンタイムパスワード認証済みかどうかを判定するis_authenticatedメソッドのテスト
        """
        otp_auth = OTPAuth(self.request)
        otp_auth.get_otp()
        self.assertFalse(otp_auth.is_authenticated())
        self.request.session['otp_authenticated'] = True
        self.assertTrue(otp_auth.is_authenticated())

    def test_is_otp_required(self):
        """
        ワンタイムパスワード認証が必要かどうかを判定するis_otp_requiredメソッドのテスト
        """
        otp_auth = OTPAuth(self.request)
        otp_auth.get_otp()
        otp_auth.disable_otp()
        self.assertFalse(otp_auth.is_otp_required())
        otp_auth.enable_otp()
        self.assertTrue(otp_auth.is_otp_required())

    def test_is_otp_secret_key_set(self):
        """
        ワンタイムパスワードのシークレットキーが設定されているかどうかを判定するis_otp_secret_key_setメソッドのテスト
        """
        otp_auth = OTPAuth(self.request)
        otp_auth.get_otp()
        self.assertTrue(otp_auth.is_otp_secret_key_set())
        otp_auth.delete_otp()
        self.assertFalse(otp_auth.is_otp_secret_key_set())
        otp_auth.get_otp()
        self.assertTrue(otp_auth.is_otp_secret_key_set())
