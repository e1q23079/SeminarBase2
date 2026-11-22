from django.test import TestCase, RequestFactory
from ..lib.redirecturlvalid import is_valid_redirect_url


class RedirectUrlValidTest(TestCase):
    """
    SeminarBase2のリダイレクトURL検証機能のテストケース
    """
    def setUp(self):
        """
        テストのセットアップ
        """
        self.factory = RequestFactory()
        self.request = self.factory.get('/')

    def test_is_valid_redirect_url(self):
        """
        有効なリダイレクトURLが正しく検証されることを確認（有効なURL）
        """
        # 有効なURL
        rtn = is_valid_redirect_url('/dashboard/', self.request)
        self.assertEqual(rtn, '/dashboard/')

    def test_is_valid_redirect_url_invalid(self):
        """
        無効なリダイレクトURLが正しく検証されることを確認（無効なURL）
        """
        # 無効なURL
        rtn = is_valid_redirect_url('http://example.com', self.request)
        self.assertEqual(rtn, '/')
