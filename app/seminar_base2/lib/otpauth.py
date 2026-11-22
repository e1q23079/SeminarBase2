import pyotp
import qrcode
import base64
from io import BytesIO
from django.contrib.auth import logout
from ..models import OneTimePassword


class OTPAuth:
    """
    ワンタイムパスワード認証のためのクラスです。
    """
    def __init__(self, request):
        """
        コンストラクタ
        :param request: DjangoのHttpRequestオブジェクト
        """
        self.request = request
        self.user = request.user
        self.otp_obj = OneTimePassword.objects.filter(user=self.user).first()
        self.max_attempts = 5  # 最大試行回数

    def _set_authenticated(self):
        """
        ユーザーをワンタイムパスワード認証済みに設定します。
        """
        self.request.session['otp_authenticated'] = True

    def is_otp_enabled(self):
        """
        ユーザーがワンタイムパスワードを有効にしているかどうかを判定します。
        """
        return self.otp_obj and self.otp_obj.is_enabled

    def get_otp(self):
        """
        ユーザーのワンタイムパスワードを取得します。
        """
        if self.otp_obj:
            # 既存のワンタイムパスワードがある場合は秘密鍵を取得
            otp_secret_key = self.otp_obj.secret_key
        else:
            # 新しい秘密鍵を生成
            otp_secret_key = pyotp.random_base32()
            self.otp_obj, _ = OneTimePassword.objects.update_or_create(
                user=self.user,
                defaults={'secret_key': otp_secret_key, 'is_enabled': False}
            )
        # URIを生成
        totp = pyotp.totp.TOTP(otp_secret_key)
        uri = totp.provisioning_uri(
            name=self.user.username,
            issuer_name="SeminarBase2"
        )
        # QRコードを生成
        img = qrcode.make(uri)
        buffer = BytesIO()
        img.save(buffer, 'PNG')
        qr_code = base64.b64encode(buffer.getvalue()).decode('utf-8')
        return qr_code, otp_secret_key

    def enable_otp(self):
        """
        ユーザーのワンタイムパスワードを有効にします。
        """
        if self.otp_obj:
            self.otp_obj.is_enabled = True
            self.otp_obj.save()

    def disable_otp(self):
        """
        ユーザーのワンタイムパスワードを無効にします。
        """
        if self.otp_obj:
            self.otp_obj.is_enabled = False
            self.otp_obj.save()

    def is_otp_secret_key_set(self):
        """
        ユーザーのワンタイムパスワードの秘密鍵が設定されているかどうかを判定します。
        """
        return self.otp_obj is not None and self.otp_obj.secret_key is not None

    def delete_otp(self):
        """
        ユーザーのワンタイムパスワードを削除します。
        """
        if self.otp_obj:
            self.otp_obj.delete()
            self.otp_obj = None

    def is_otp_required(self):
        """
        ユーザーがワンタイムパスワード認証を必要とするかどうかを判定します。
        """
        if self.otp_obj and self.otp_obj.is_enabled:
            return True
        return False

    def is_authenticated(self):
        """
        ユーザーがワンタイムパスワード認証済みかどうかを判定します。
        """
        return self.request.session.get('otp_authenticated', False)

    def verify_otp(self, otp_code):
        """
        ワンタイムパスワードを検証します。（ログイン時の認証用）
        :param otp_code: ユーザーが入力したワンタイムパスワード
        :return: 検証に成功した場合はTrue、失敗した場合はFalseとエラーメッセージ
        """
        if self.otp_obj is None or self.otp_obj.secret_key is None:
            return False, "ワンタイムパスワードが設定されていません。"
        totp = pyotp.totp.TOTP(self.otp_obj.secret_key)
        if totp.verify(otp_code, valid_window=1):
            self._set_authenticated()
            if self.otp_obj:
                self.otp_obj.last_used_code = otp_code
                self.otp_obj.save()
            return True, None
        return False, "ワンタイムパスワードが正しくありません。"

    def authenticate(self, otp_code):
        """
        ワンタイムパスワードを検証します。（非ログイン時の認証用）
        失敗した場合は試行回数をカウントし、最大試行回数を超えた場合はセッションをリセットして再ログインを要求します。
        :param otp_code: ユーザーが入力したワンタイムパスワード
        :return: 認証に成功した場合はTrue、失敗した場合はFalseとエラーメッセージ、エラーコード
        """
        # ワンタイムパスワードが有効でない場合は認証を失敗させる
        if not self.otp_obj or not self.otp_obj.is_enabled:
            return False, "ワンタイムパスワードが有効ではありません。", "otp_not_enabled"
        # リプレイ攻撃防止のため、最後に使用したコードと比較
        if otp_code == self.otp_obj.last_used_code:
            return (
                False,
                "このコードは既に使用されています。30秒後に表示される新しいコードを使用してください。",
                "otp_already_used"
            )
        # 最大試行回数を超えた場合は認証を失敗させる
        if self.request.session.get(
            'otp_attempts_count', 0
        ) >= self.max_attempts:
            # 最大試行回数を超えた場合はセッションをリセットして再ログインを要求
            logout(self.request)
            return (
                False,
                "最大試行回数を超えました。再度ログインしてください。",
                "otp_max_attempts_exceeded"
            )
        # ワンタイムパスワードを検証
        is_authenticated, error_message = self.verify_otp(otp_code)
        if is_authenticated:
            self.request.session['otp_attempts_count'] = 0  # 試行回数をリセット
            return True, None, None
        self.request.session[
            'otp_attempts_count'
        ] = self.request.session.get(
            'otp_attempts_count', 0
        ) + 1  # 試行回数を増加
        return False, error_message, "otp_invalid"
