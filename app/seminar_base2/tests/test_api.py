from django.test import TestCase
from ..models import Seminar, Manager, User, Members


class RequestHashAPITests(TestCase):
    '''
    RequestHashViewのAPIテストケース
    '''
    def setUp(self):
        '''
        テスト用のセミナーを作成する
        '''
        self.seminar1 = Seminar.objects.create(
            title='Test Seminar 1',
            description='Test Description 1',
            content='# Test Content 1\nTest Content 1',
            manage=True,
            public=True
        )
        self.seminar2 = Seminar.objects.create(
            title='Test Seminar 2',
            description='Test Description 2',
            content='# Test Content 2\nTest Content 2',
            manage=True,
            public=True
        )
        self.seminar3 = Seminar.objects.create(
            title='Test Seminar 3',
            description='Test Description 3',
            content='# Test Content 3\nTest Content 3',
            manage=True,
            public=False
        )
        self.seminar4 = Seminar.objects.create(
            title='Test Seminar 4',
            description='Test Description 4',
            content='# Test Content 4\nTest Content 4',
            manage=False,
            public=True
        )

    def test_manager_request_view_not_login(self):
        '''
        マネージャーリクエストページのビューのテスト（ログインしていない場合）
        '''
        response = self.client.get(
            f'/api/manager/request_hash/{self.seminar1.uuid}'
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response,
            f'/accounts/login/?next=/api/manager/request_hash/{self.seminar1.uuid}'     # noqa: E501
        )

    def test_manager_request_view_login_superuser(self):
        '''
        マネージャーリクエストページのビューのテスト（ログインしている場合，スーパーユーザー）
        '''
        User.objects.create_superuser(
            username='admin', password='adminpassword'
        )
        self.client.login(
            username='admin',
            password='adminpassword'
        )

        response = self.client.get(
            f'/api/manager/request_hash/{self.seminar1.uuid}'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        data = response.json()
        self.assertEqual(data['status'], 'success')

    def test_manager_request_view_login_staffuser(self):
        '''
        マネージャーリクエストページのビューのテスト（ログインしている場合，スタッフユーザー）
        '''
        User.objects.create_user(
            username='staffuser',
            password='staffpassword',
            is_staff=True
        )
        self.client.login(
            username='staffuser',
            password='staffpassword'
        )

        response = self.client.get(
            f'/api/manager/request_hash/{self.seminar1.uuid}'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        data = response.json()
        self.assertEqual(data['status'], 'success')

    def test_manager_request_view_login_not_manager(self):
        '''
        マネージャーリクエストページのビューのテスト（ログインしている場合，マネージャーでないユーザー）
        '''
        user = User.objects.create_user(
            username='testuser', password='testpassword'
        )
        Manager.objects.create(user=user, seminar=self.seminar2)
        self.client.login(username='testuser', password='testpassword')

        response = self.client.get(
            f'/api/manager/request_hash/{self.seminar1.uuid}'
        )
        self.assertEqual(response.status_code, 403)

    def test_manager_request_view_login_manager(self):
        '''
        マネージャーリクエストページのビューのテスト（ログインしている場合，マネージャーであるユーザー）
        '''
        user = User.objects.create_user(
            username='testuser', password='testpassword'
        )
        Manager.objects.create(user=user, seminar=self.seminar1)
        self.client.login(username='testuser', password='testpassword')

        response = self.client.get(
            f'/api/manager/request_hash/{self.seminar1.uuid}'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        data = response.json()
        self.assertEqual(data['status'], 'success')

    def test_manager_request_view_private_seminar(self):
        '''
        マネージャーリクエストページのビューのテスト（ログインしている場合，マネージャーであるユーザー，非公開セミナー）
        '''
        user = User.objects.create_user(
            username='testuser', password='testpassword'
        )
        Manager.objects.create(user=user, seminar=self.seminar3)
        self.client.login(username='testuser', password='testpassword')

        response = self.client.get(
            f'/api/manager/request_hash/{self.seminar3.uuid}'
        )
        self.assertEqual(response.status_code, 403)

    def test_manager_request_view_superuser(self):
        '''
        マネージャーリクエストページのビューのテスト（ログインしている場合，スーパーユーザー，非公開セミナー）
        '''
        User.objects.create_superuser(
            username='admin', password='adminpassword'
        )
        self.client.login(username='admin', password='adminpassword')
        response = self.client.get(
            f'/api/manager/request_hash/{self.seminar3.uuid}'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        data = response.json()
        self.assertEqual(data['status'], 'success')

    def test_manager_request_view_staffuser(self):
        '''
        マネージャーリクエストページのビューのテスト（ログインしている場合，スタッフユーザー，非公開セミナー）
        '''
        User.objects.create_user(
            username='staffuser', password='staffpassword', is_staff=True
        )
        self.client.login(username='staffuser', password='staffpassword')
        response = self.client.get(
            f'/api/manager/request_hash/{self.seminar3.uuid}'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        data = response.json()
        self.assertEqual(data['status'], 'success')

    def test_manager_request_view_no_manage(self):
        '''
        マネージャーリクエストページのビューのテスト（ログインしている場合，マネージャーであるユーザー，管理機能オフのセミナー）
        '''
        user = User.objects.create_user(
            username='testuser', password='testpassword'
        )
        Manager.objects.create(user=user, seminar=self.seminar4)
        self.client.login(username='testuser', password='testpassword')

        response = self.client.get(
            f'/api/manager/request_hash/{self.seminar4.uuid}'
        )
        self.assertEqual(response.status_code, 404)


class RequestAPITests(TestCase):
    '''
    RequestViewのAPIテストケース
    '''
    def setUp(self):
        '''
        テスト用のセミナーを作成する
        '''
        self.seminar1 = Seminar.objects.create(
            title='Test Seminar 1',
            description='Test Description 1',
            content='# Test Content 1\nTest Content 1',
            manage=True,
            public=True
        )
        self.seminar2 = Seminar.objects.create(
            title='Test Seminar 2',
            description='Test Description 2',
            content='# Test Content 2\nTest Content 2',
            manage=True,
            public=True
        )
        self.seminar3 = Seminar.objects.create(
            title='Test Seminar 3',
            description='Test Description 3',
            content='# Test Content 3\nTest Content 3',
            manage=True,
            public=False
        )
        self.seminar4 = Seminar.objects.create(
            title='Test Seminar 4',
            description='Test Description 4',
            content='# Test Content 4\nTest Content 4',
            manage=False,
            public=True
        )

    def test_request_view_not_login(self):
        '''
        リクエストページのビューのテスト（ログインしていない場合）
        '''
        response = self.client.post(f'/api/request/{self.seminar1.uuid}')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response,
            f'/accounts/login/?next=/api/request/{self.seminar1.uuid}'
        )

    def test_request_view_login_not_member(self):
        '''
        リクエストページのビューのテスト（ログインしている場合，セミナーの参加者でないユーザー）
        '''
        User.objects.create_user(
            username='testuser', password='testpassword'
        )
        self.client.login(username='testuser', password='testpassword')
        response = self.client.post(f'/api/request/{self.seminar1.uuid}')
        self.assertEqual(response.status_code, 403)

    def test_request_view_login_member(self):
        '''
        リクエストページのビューのテスト（ログインしている場合，セミナーの参加者であるユーザー）
        '''
        User.objects.create_user(
            username='testuser', password='testpassword'
        )
        self.client.login(username='testuser', password='testpassword')
        Members.objects.create(
            seminar=self.seminar1,
            user=User.objects.get(username='testuser')
        )
        response = self.client.post(f'/api/request/{self.seminar1.uuid}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        data = response.json()
        self.assertEqual(data['status'], 'success')
        member = Members.objects.get(
            seminar=self.seminar1,
            user=User.objects.get(username='testuser')
        )
        self.assertTrue(member.request)

    def test_request_view_login_member_no_manage(self):
        '''
        リクエストページのビューのテスト（ログインしている場合，セミナーの参加者であるユーザー，管理機能オフのセミナー）
        '''
        User.objects.create_user(
            username='testuser', password='testpassword'
        )
        self.client.login(username='testuser', password='testpassword')
        Members.objects.create(
            seminar=self.seminar4,
            user=User.objects.get(username='testuser')
        )
        response = self.client.post(f'/api/request/{self.seminar4.uuid}')
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response['Content-Type'], 'application/json')
        data = response.json()
        self.assertEqual(data['status'], 'error')
        member = Members.objects.get(
            seminar=self.seminar4,
            user=User.objects.get(username='testuser')
        )
        self.assertFalse(member.request)

    def test_request_view_login_member_private_seminar(self):
        '''
        リクエストページのビューのテスト（ログインしている場合，セミナーの参加者であるユーザー，非公開セミナー）
        '''
        User.objects.create_user(
            username='testuser', password='testpassword'
        )
        self.client.login(username='testuser', password='testpassword')
        Members.objects.create(
            seminar=self.seminar3,
            user=User.objects.get(username='testuser')
        )
        response = self.client.post(f'/api/request/{self.seminar3.uuid}')
        self.assertEqual(response.status_code, 403)
        member = Members.objects.get(
            seminar=self.seminar3,
            user=User.objects.get(username='testuser')
        )
        self.assertFalse(member.request)
