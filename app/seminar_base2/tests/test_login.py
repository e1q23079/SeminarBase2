from django.test import TestCase, override_settings
from django.http import HttpResponse
from django.views import View
from django.urls import path
from ..models import Seminar, User, Members, Manager, File
from ..lib.login import LoginMemberRequiredMixin, LoginManagerRequiredMixin


class DummyMemberView(LoginMemberRequiredMixin, View):
    """
    メンバービュー
    """
    def get(self, request, *args, **kwargs):
        return HttpResponse("OK")


class DummyManagerView(LoginManagerRequiredMixin, View):
    """
    マネージャービュー
    """
    def get(self, request, *args, **kwargs):
        return HttpResponse("OK")


# テスト用のURLパターンを定義
urlpatterns = [
    path(
        'dummy_member/',
        DummyMemberView.as_view(),
        name='dummy_member_list'
    ),
    path(
        'dummy_member/<uuid:seminar_id>/',
        DummyMemberView.as_view(),
        name='dummy_member_detail'
    ),
    path(
        'dummy_file/<uuid:uuid>/',
        DummyMemberView.as_view(),
        name='dummy_file_detail'
    ),
    path(
        'dummy_manager/',
        DummyManagerView.as_view(),
        name='dummy_manager_list'
    ),
    path(
        'dummy_manager/<uuid:seminar_id>/',
        DummyManagerView.as_view(),
        name='dummy_manager_detail'
    ),
]


@override_settings(ROOT_URLCONF=__name__)
class LoginMemberRequiredMixinTests(TestCase):
    """
    LoginMemberRequiredMixinのテスト
    """
    def setUp(self):
        """
        テスト用のデータをセットアップする
        """
        # ユーザーを作成
        self.superuser = User.objects.create_superuser(
            username='superuser',
            password='password'
        )
        self.staff_user = User.objects.create_user(
            username='staff',
            password='password',
            is_staff=True
        )

        self.normal_user = User.objects.create_user(
            username='normal',
            password='password'
        )
        self.member_user = User.objects.create_user(
            username='member',
            password='password'
        )
        self.manager_user = User.objects.create_user(
            username='manager',
            password='password'
        )

        # セミナーを作成
        self.seminar_public = Seminar.objects.create(
            title='Test Seminar',
            content='Test Content',
            public=True
        )
        self.seminar_private = Seminar.objects.create(
            title='Test Seminar',
            content='Test Content',
            public=False
        )

        # セミナーにメンバーとマネージャーを追加
        Members.objects.create(
            seminar=self.seminar_public,
            user=self.member_user
        )
        Manager.objects.create(
            seminar=self.seminar_public,
            user=self.manager_user
        )
        Members.objects.create(
            seminar=self.seminar_private,
            user=self.member_user
        )
        Manager.objects.create(
            seminar=self.seminar_private,
            user=self.manager_user
        )

        # ファイルを作成
        self.file_public = File.objects.create(
            seminar=self.seminar_public,
            name='Test File',
            file='test.txt'
        )
        self.file_private = File.objects.create(
            seminar=self.seminar_private,
            name='Test File',
            file='test.txt'
        )

    def test_member_access_superuser_public(self):
        """
        スーパーユーザーはアクセスできることをテストする
        """
        # スーパーユーザーでログイン
        self.client.login(username='superuser', password='password')

        # メンバービューにアクセス
        response = self.client.get('/dummy_member/')
        self.assertEqual(response.status_code, 200)

        # メンバービューにセミナーIDを指定してアクセス
        response = self.client.get(
            f'/dummy_member/{self.seminar_public.uuid}/'
        )
        self.assertEqual(response.status_code, 200)

    def test_member_access_superuser_private(self):
        """
        スーパーユーザーは非公開セミナーにもアクセスできることをテストする
        """
        # スーパーユーザーでログイン
        self.client.login(username='superuser', password='password')

        # メンバービューにセミナーIDを指定してアクセス
        response = self.client.get(
            f'/dummy_member/{self.seminar_private.uuid}/'
        )
        self.assertEqual(response.status_code, 200)

    def test_member_access_staff_user_public(self):
        """
        スタッフユーザーはアクセスできることをテストする
        """
        # スタッフユーザーでログイン
        self.client.login(username='staff', password='password')

        # メンバービューにアクセス
        response = self.client.get('/dummy_member/')
        self.assertEqual(response.status_code, 200)

        # メンバービューにセミナーIDを指定してアクセス
        response = self.client.get(
            f'/dummy_member/{self.seminar_public.uuid}/'
        )
        self.assertEqual(response.status_code, 200)

    def test_member_access_staff_user_private(self):
        """
        スタッフユーザーは非公開セミナーにもアクセスできることをテストする
        """
        # スタッフユーザーでログイン
        self.client.login(username='staff', password='password')

        # メンバービューにセミナーIDを指定してアクセス
        response = self.client.get(
            f'/dummy_member/{self.seminar_private.uuid}/'
        )
        self.assertEqual(response.status_code, 200)

    def test_member_access_member_user_public(self):
        """
        メンバーはアクセスできることをテストする
        """
        # メンバーでログイン
        self.client.login(username='member', password='password')

        # メンバービューにアクセス
        response = self.client.get('/dummy_member/')
        self.assertEqual(response.status_code, 200)

        # メンバービューにセミナーIDを指定してアクセス
        response = self.client.get(
            f'/dummy_member/{self.seminar_public.uuid}/'
        )
        self.assertEqual(response.status_code, 200)

    def test_member_access_member_user_private(self):
        """
        メンバーは非公開セミナーにはアクセスできないことをテストする
        """
        # メンバーでログイン
        self.client.login(username='member', password='password')

        # メンバービューにセミナーIDを指定してアクセス
        response = self.client.get(
            f'/dummy_member/{self.seminar_private.uuid}/'
        )
        self.assertEqual(response.status_code, 403)

    def test_member_access_normal_user(self):
        """
        一般ユーザーはアクセスできないことをテストする
        """
        # 一般ユーザーでログイン
        self.client.login(username='normal', password='password')

        # メンバービューにアクセス
        response = self.client.get('/dummy_member/')
        self.assertEqual(response.status_code, 403)

        # メンバービューにセミナーIDを指定してアクセス
        response = self.client.get(
            f'/dummy_member/{self.seminar_public.uuid}/'
        )
        self.assertEqual(response.status_code, 403)

    def test_member_access_manager_user_public(self):
        """
        マネージャーはアクセスできることをテストする
        """
        # マネージャーでログイン
        self.client.login(username='manager', password='password')

        # メンバービューにアクセス
        response = self.client.get('/dummy_member/')
        self.assertEqual(response.status_code, 200)

        # メンバービューにセミナーIDを指定してアクセス
        response = self.client.get(
            f'/dummy_member/{self.seminar_public.uuid}/'
        )
        self.assertEqual(response.status_code, 200)

    def test_member_access_manager_user_private(self):
        """
        マネージャーは非公開セミナーにはアクセスできないことをテストする
        """
        # マネージャーでログイン
        self.client.login(username='manager', password='password')

        # メンバービューにセミナーIDを指定してアクセス
        response = self.client.get(
            f'/dummy_member/{self.seminar_private.uuid}/'
        )
        self.assertEqual(response.status_code, 403)

    def test_member_access_file_superuser_public(self):
        """
        スーパーユーザーはファイルにアクセスできることをテストする
        """
        # スーパーユーザーでログイン
        self.client.login(username='superuser', password='password')

        # ファイル詳細ビューにアクセス
        response = self.client.get(
            f'/dummy_file/{self.file_public.uuid}/'
        )
        self.assertEqual(response.status_code, 200)

    def test_member_access_file_superuser_private(self):
        """
        スーパーユーザーは非公開セミナーのファイルにもアクセスできることをテストする
        """
        # スーパーユーザーでログイン
        self.client.login(username='superuser', password='password')

        # ファイル詳細ビューにアクセス
        response = self.client.get(
            f'/dummy_file/{self.file_private.uuid}/'
        )
        self.assertEqual(response.status_code, 200)

    def test_member_access_file_staff_user_public(self):
        """
        スタッフユーザーはファイルにアクセスできることをテストする
        """
        # スタッフユーザーでログイン
        self.client.login(username='staff', password='password')

        # ファイル詳細ビューにアクセス
        response = self.client.get(
            f'/dummy_file/{self.file_public.uuid}/'
        )
        self.assertEqual(response.status_code, 200)

    def test_member_access_file_staff_user_private(self):
        """
        スタッフユーザーは非公開セミナーのファイルにもアクセスできることをテストする
        """
        # スタッフユーザーでログイン
        self.client.login(username='staff', password='password')

        # ファイル詳細ビューにアクセス
        response = self.client.get(
            f'/dummy_file/{self.file_private.uuid}/'
        )
        self.assertEqual(response.status_code, 200)

    def test_member_access_file_member_user(self):
        """
        メンバーはファイルにアクセスできることをテストする
        """
        # メンバーでログイン
        self.client.login(username='member', password='password')

        # ファイル詳細ビューにアクセス
        response = self.client.get(
            f'/dummy_file/{self.file_public.uuid}/'
        )
        self.assertEqual(response.status_code, 200)

    def test_member_access_file_normal_user(self):
        """
        一般ユーザーはファイルにアクセスできないことをテストする
        """
        # 一般ユーザーでログイン
        self.client.login(username='normal', password='password')

        # ファイル詳細ビューにアクセス
        response = self.client.get(f'/dummy_file/{self.file_public.uuid}/')
        self.assertEqual(response.status_code, 403)

    def test_member_access_file_manager_user_public(self):
        """
        マネージャーはファイルにアクセスできることをテストする
        """
        # マネージャーでログイン
        self.client.login(username='manager', password='password')

        # ファイル詳細ビューにアクセス
        response = self.client.get(f'/dummy_file/{self.file_public.uuid}/')
        self.assertEqual(response.status_code, 200)

    def test_member_access_file_manager_user_private(self):
        """
        マネージャーは非公開セミナーのファイルにはアクセスできないことをテストする
        """
        # マネージャーでログイン
        self.client.login(username='manager', password='password')

        # ファイル詳細ビューにアクセス
        response = self.client.get(f'/dummy_file/{self.file_private.uuid}/')
        self.assertEqual(response.status_code, 403)


@override_settings(ROOT_URLCONF=__name__)
class LoginManagerRequiredMixinTests(TestCase):
    """
    LoginManagerRequiredMixinのテスト
    """
    def setUp(self):
        """
        テスト用のデータをセットアップする
        """
        # ユーザーを作成
        self.superuser = User.objects.create_superuser(
            username='superuser',
            password='password'
        )
        self.staff_user = User.objects.create_user(
            username='staff',
            password='password',
            is_staff=True
        )

        self.normal_user = User.objects.create_user(
            username='normal',
            password='password'
        )
        self.member_user = User.objects.create_user(
            username='member',
            password='password'
        )
        self.manager_user = User.objects.create_user(
            username='manager',
            password='password'
        )

        # セミナーを作成
        self.seminar_public = Seminar.objects.create(
            title='Test Seminar',
            content='Test Content',
            public=True
        )
        self.seminar_private = Seminar.objects.create(
            title='Test Seminar',
            content='Test Content',
            public=False
        )

        # セミナーにメンバーとマネージャーを追加
        Members.objects.create(
            seminar=self.seminar_public,
            user=self.member_user
        )
        Manager.objects.create(
            seminar=self.seminar_public,
            user=self.manager_user
        )
        Members.objects.create(
            seminar=self.seminar_private,
            user=self.member_user
        )
        Manager.objects.create(
            seminar=self.seminar_private,
            user=self.manager_user
        )

    def test_manager_access_superuser_public(self):
        """
        スーパーユーザーはアクセスできることをテストする
        """
        # スーパーユーザーでログイン
        self.client.login(username='superuser', password='password')

        # マネージャービューにアクセス
        response = self.client.get('/dummy_manager/')
        self.assertEqual(response.status_code, 200)

        # マネージャービューにセミナーIDを指定してアクセス
        response = self.client.get(
            f'/dummy_manager/{self.seminar_public.uuid}/'
        )
        self.assertEqual(response.status_code, 200)

    def test_manager_access_superuser_private(self):
        """
        スーパーユーザーは非公開セミナーにもアクセスできることをテストする
        """
        # スーパーユーザーでログイン
        self.client.login(username='superuser', password='password')

        # マネージャービューにセミナーIDを指定してアクセス
        response = self.client.get(
            f'/dummy_manager/{self.seminar_private.uuid}/'
        )
        self.assertEqual(response.status_code, 200)

    def test_manager_access_staff_user_public(self):
        """
        スタッフユーザーはアクセスできることをテストする
        """
        # スタッフユーザーでログイン
        self.client.login(username='staff', password='password')

        # マネージャービューにアクセス
        response = self.client.get('/dummy_manager/')
        self.assertEqual(response.status_code, 200)

        # マネージャービューにセミナーIDを指定してアクセス
        response = self.client.get(
            f'/dummy_manager/{self.seminar_public.uuid}/'
        )
        self.assertEqual(response.status_code, 200)

    def test_manager_access_staff_user_private(self):
        """
        スタッフユーザーは非公開セミナーにもアクセスできることをテストする
        """
        # スタッフユーザーでログイン
        self.client.login(username='staff', password='password')

        # マネージャービューにセミナーIDを指定してアクセス
        response = self.client.get(
            f'/dummy_manager/{self.seminar_private.uuid}/'
        )
        self.assertEqual(response.status_code, 200)

    def test_manager_access_member_user(self):
        """
        メンバーはアクセスできないことをテストする
        """
        # メンバーでログイン
        self.client.login(username='member', password='password')

        # マネージャービューにアクセス
        response = self.client.get('/dummy_manager/')
        self.assertEqual(response.status_code, 403)

        # マネージャービューにセミナーIDを指定してアクセス
        response = self.client.get(
            f'/dummy_manager/{self.seminar_public.uuid}/'
        )
        self.assertEqual(response.status_code, 403)

    def test_manager_access_normal_user(self):
        """
        一般ユーザーはアクセスできないことをテストする
        """
        # 一般ユーザーでログイン
        self.client.login(username='normal', password='password')

        # マネージャービューにアクセス
        response = self.client.get('/dummy_manager/')
        self.assertEqual(response.status_code, 403)

        # マネージャービューにセミナーIDを指定してアクセス
        response = self.client.get(
            f'/dummy_manager/{self.seminar_public.uuid}/'
        )
        self.assertEqual(response.status_code, 403)

    def test_manager_access_manager_user_public(self):
        """
        マネージャーはアクセスできることをテストする
        """
        # マネージャーでログイン
        self.client.login(username='manager', password='password')

        # マネージャービューにアクセス
        response = self.client.get('/dummy_manager/')
        self.assertEqual(response.status_code, 200)

        # マネージャービューにセミナーIDを指定してアクセス
        response = self.client.get(
            f'/dummy_manager/{self.seminar_public.uuid}/'
        )
        self.assertEqual(response.status_code, 200)

    def test_manager_access_manager_user_private(self):
        """
        マネージャーは非公開セミナーにはアクセスできないことをテストする
        """
        # マネージャーでログイン
        self.client.login(username='manager', password='password')

        # マネージャービューにセミナーIDを指定してアクセス
        response = self.client.get(
            f'/dummy_manager/{self.seminar_private.uuid}/'
        )
        self.assertEqual(response.status_code, 403)
