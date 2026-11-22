from .models import ResetRequest
from django.shortcuts import redirect
from .lib.otpauth import OTPAuth


EXCLUDED_PATHS = ['/setting', '/accounts/logout/']


class SettingRequestMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # ログインしていない場合は除外
        if not request.user.is_authenticated:
            return self.get_response(request)
        # 除外ページへのアクセスは許可
        if request.path in EXCLUDED_PATHS:
            return self.get_response(request)
        # 再設定要求が存在する場合は設定ページにリダイレクト
        reset_request = ResetRequest.objects.filter(user=request.user).exists()
        if reset_request:
            return redirect('/setting')
        return self.get_response(request)


class OneTimePasswordMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.excluded_paths = ['/accounts/otp/auth', '/accounts/logout/']

    def __call__(self, request):
        # ログインしていない場合は除外
        if not request.user.is_authenticated:
            return self.get_response(request)
        # 除外ページへのアクセスは許可
        if request.path in self.excluded_paths:
            return self.get_response(request)
        # ワンタイムパスワード認証が必要な場合は認証ページにリダイレクト
        opt_auth = OTPAuth(request)
        otp_obj = opt_auth.is_otp_required()
        if otp_obj and not opt_auth.is_authenticated():
            return redirect(f'/accounts/otp/auth?next={request.path}')
        return self.get_response(request)
