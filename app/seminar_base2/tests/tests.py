from django.test import TestCase
from django.contrib.auth.models import User
from ..models import Seminar, Members, File, Manager


# ホームのビューテスト
class IndexViewTests(TestCase):
    def test_index_view(self):
        '''
        ホームのビューのテスト
        '''
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)


# セミナーリストのビューテスト
class SeminarListViewTests(TestCase):
    def setUp(self):
        '''
        テスト用のセミナーを作成する
        '''
        self.seminar = Seminar.objects.create(
            title='Test Seminar',
            description='Test Description',
            content='# Test Content\nTest Content'
        )

    def test_seminar_list_view_not_login(self):
        '''
        セミナーリストのビューのテスト（ログインしていない場合）
        '''
        response = self.client.get('/seminar')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/?next=/seminar')

    def test_seminar_list_view_superuser(self):
        '''
        セミナーリストのビューのテスト（ログインしている場合，スーパーユーザー）
        '''
        User.objects.create_superuser(
            username='admin',
            password='adminpassword'
        )
        self.client.login(username='admin', password='adminpassword')

        response = self.client.get('/seminar')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'seminar_list.html')

    def test_seminar_list_view_login_staffuser(self):
        '''
        セミナーリストのビューのテスト（ログインしている場合，スタッフユーザー）
        '''
        User.objects.create_user(
            username='staffuser',
            password='staffpassword',
            is_staff=True
        )
        self.client.login(username='staffuser', password='staffpassword')

        response = self.client.get('/seminar')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'seminar_list.html')

    def test_seminar_list_view_login(self):
        '''
        セミナーリストのビューのテスト（ログインしている場合）
        '''
        User.objects.create_user(
            username='testuser',
            password='testpassword'
        )
        self.client.login(username='testuser', password='testpassword')

        response = self.client.get('/seminar')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'seminar_list.html')

    def test_seminar_list_view_login_manager(self):
        '''
        セミナーリストのビューのテスト（ログインしている場合，マネージャーであるユーザー）
        '''
        user = User.objects.create_user(
            username='testuser',
            password='testpassword'
        )
        self.seminar2 = Seminar.objects.create(
            title='Test Seminar2', description='Test Description2',
            content='# Test Content2\nTest Content2'
        )
        Manager.objects.create(user=user, seminar=self.seminar2)
        self.client.login(username='testuser', password='testpassword')

        response = self.client.get('/seminar')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'seminar_list.html')


# レクチャーリストのビューテスト
class LectureListViewTests(TestCase):
    def setUp(self):
        '''
        テスト用のセミナーとレクチャーを作成する
        '''
        self.seminar1 = Seminar.objects.create(
            title='Test Seminar1',
            description='Test Description',
            content='# Test Content\nTest Content',
            public=True
        )
        self.seminar2 = Seminar.objects.create(
            title='Test Seminar2',
            description='Test Description',
            content='# Test Content\nTest Content',
            public=True
        )
        self.seminar3 = Seminar.objects.create(
            title='Test Seminar3',
            description='Test Description',
            content='# Test Content\nTest Content',
            public=False
        )

    def test_lecture_list_view_not_login(self):
        '''
        レクチャーリストのビューのテスト（ログインしていない場合）
        '''
        response = self.client.get(f'/lecture/{self.seminar1.uuid}')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response,
            f'/accounts/login/?next=/lecture/{self.seminar1.uuid}'
        )

    def test_lecture_list_view_login_superuser(self):
        '''
        レクチャーリストのビューのテスト（ログインしている場合，スーパーユーザー）
        '''
        User.objects.create_superuser(
            username='admin',
            password='adminpassword'
        )
        self.client.login(username='admin', password='adminpassword')

        response = self.client.get(f'/lecture/{self.seminar1.uuid}')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'lecture_list.html')

    def test_lecture_list_view_login_staffuser(self):
        '''
        レクチャーリストのビューのテスト（ログインしている場合，スタッフユーザー）
        '''
        User.objects.create_user(
            username='staffuser',
            password='staffpassword',
            is_staff=True
        )
        self.client.login(username='staffuser', password='staffpassword')

        response = self.client.get(f'/lecture/{self.seminar1.uuid}')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'lecture_list.html')

    def test_lecture_list_view_login_not_member(self):
        '''
        レクチャーリストのビューのテスト（ログインしている場合，受講者ではないユーザー）
        '''
        user = User.objects.create_user(
            username='testuser',
            password='testpassword'
        )
        Members.objects.create(user=user, seminar=self.seminar2)
        self.client.login(username='testuser', password='testpassword')

        response = self.client.get(f'/lecture/{self.seminar1.uuid}')
        self.assertEqual(response.status_code, 403)

    def test_lecture_list_view_login_member(self):
        '''
        レクチャーリストのビューのテスト（ログインしている場合，受講者であるユーザー）
        '''
        user = User.objects.create_user(
            username='testuser',
            password='testpassword'
        )
        Members.objects.create(user=user, seminar=self.seminar1)
        self.client.login(username='testuser', password='testpassword')

        response = self.client.get(f'/lecture/{self.seminar1.uuid}')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'lecture_list.html')

    def test_lecture_list_view_no_seminar(self):
        '''
        レクチャーリストのビューのテスト（ログインしている場合，受講者であるユーザー，存在しないセミナー）
        '''
        user = User.objects.create_user(
            username='testuser',
            password='testpassword'
        )
        Members.objects.create(user=user, seminar=self.seminar1)
        self.client.login(username='testuser', password='testpassword')

        response = self.client.get('/lecture/abcdefg')
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, '404.html')

    def test_lecture_list_view_login_manager(self):
        '''
        レクチャーリストのビューのテスト（ログインしている場合，マネージャーであるユーザー）
        '''
        user = User.objects.create_user(
            username='testuser',
            password='testpassword'
        )
        Manager.objects.create(user=user, seminar=self.seminar1)
        self.client.login(username='testuser', password='testpassword')

        response = self.client.get(f'/lecture/{self.seminar1.uuid}')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'lecture_list.html')

    def test_lecture_list_view_login_no_manager(self):
        '''
        レクチャーリストのビューのテスト（ログインしている場合，マネージャーでないユーザー）
        '''
        user = User.objects.create_user(
            username='testuser',
            password='testpassword'
        )
        Manager.objects.create(user=user, seminar=self.seminar2)
        self.client.login(username='testuser', password='testpassword')

        response = self.client.get(f'/lecture/{self.seminar1.uuid}')
        self.assertEqual(response.status_code, 403)

    def test_lecture_list_view_private_seminar(self):
        '''
        レクチャーリストのビューのテスト（ログインしている場合，受講者であるユーザー，非公開セミナー）
        '''
        user = User.objects.create_user(
            username='testuser',
            password='testpassword'
        )
        Members.objects.create(user=user, seminar=self.seminar3)
        self.client.login(username='testuser', password='testpassword')

        response = self.client.get(f'/lecture/{self.seminar3.uuid}')
        self.assertEqual(response.status_code, 403)

    def test_lecture_list_view_private_seminar_manager(self):
        '''
        レクチャーリストのビューのテスト（ログインしている場合，マネージャーであるユーザー，非公開セミナー）
        '''
        user = User.objects.create_user(
            username='testuser',
            password='testpassword'
        )
        Manager.objects.create(user=user, seminar=self.seminar3)
        self.client.login(username='testuser', password='testpassword')

        response = self.client.get(f'/lecture/{self.seminar3.uuid}')
        self.assertEqual(response.status_code, 403)

    def test_lecture_list_view_superuser(self):
        '''
        レクチャーリストのビューのテスト（ログインしている場合，スーパーユーザー，非公開セミナー）
        '''
        User.objects.create_superuser(
            username='admin',
            password='adminpassword'
        )
        self.client.login(username='admin', password='adminpassword')

        response = self.client.get(f'/lecture/{self.seminar3.uuid}')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'lecture_list.html')

    def test_lecture_list_view_staffuser(self):
        '''
        レクチャーリストのビューのテスト（ログインしている場合，スタッフユーザー，非公開セミナー）
        '''
        User.objects.create_user(
            username='staffuser',
            password='staffpassword',
            is_staff=True
        )
        self.client.login(username='staffuser', password='staffpassword')

        response = self.client.get(f'/lecture/{self.seminar3.uuid}')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'lecture_list.html')


# ドキュメントのビューテスト
class DocumentViewTests(TestCase):
    def setUp(self):
        '''
        テスト用のセミナーとレクチャーを作成する
        '''
        self.seminar1 = Seminar.objects.create(
            title='Test Seminar1',
            description='Test Description',
            content='# Test Content\nTest Content',
            public=True
        )
        self.seminar2 = Seminar.objects.create(
            title='Test Seminar2',
            description='Test Description',
            content='# Test Content\nTest Content',
            public=True
        )
        self.seminar3 = Seminar.objects.create(
            title='Test Seminar3',
            description='Test Description',
            content='# Test Content\nTest Content',
            public=False
        )

    def test_doc_view_not_login(self):
        '''
        ドキュメントのビューのテスト（ログインしていない場合）
        '''
        response = self.client.get(f'/doc/{self.seminar1.uuid}?lec=1')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response,
            f'/accounts/login/?next=/doc/{self.seminar1.uuid}?lec=1'
        )

    def test_doc_view_login_superuser(self):
        '''
        ドキュメントのビューのテスト（ログインしている場合，スーパーユーザー）
        '''
        User.objects.create_superuser(
            username='admin',
            password='adminpassword'
        )
        self.client.login(username='admin', password='adminpassword')

        response = self.client.get(f'/doc/{self.seminar1.uuid}?lec=1')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'document.html')

    def test_doc_view_login_staffuser(self):
        '''
        ドキュメントのビューのテスト（ログインしている場合，スタッフユーザー）
        '''
        User.objects.create_user(
            username='staffuser',
            password='staffpassword',
            is_staff=True
        )
        self.client.login(username='staffuser', password='staffpassword')

        response = self.client.get(f'/doc/{self.seminar1.uuid}?lec=1')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'document.html')

    def test_doc_view_login_not_member(self):
        '''
        ドキュメントのビューのテスト（ログインしている場合，受講者ではないユーザー）
        '''
        user = User.objects.create_user(
            username='testuser',
            password='testpassword'
        )
        Members.objects.create(user=user, seminar=self.seminar2)
        self.client.login(username='testuser', password='testpassword')

        response = self.client.get(f'/doc/{self.seminar1.uuid}?lec=1')
        self.assertEqual(response.status_code, 403)

    def test_doc_view_login_member(self):
        '''
        ドキュメントのビューのテスト（ログインしている場合，受講者であるユーザー）
        '''
        user = User.objects.create_user(
            username='testuser',
            password='testpassword'
        )
        Members.objects.create(user=user, seminar=self.seminar1)
        self.client.login(username='testuser', password='testpassword')

        response = self.client.get(f'/doc/{self.seminar1.uuid}?lec=1')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'document.html')

    def test_doc_view_no_seminar(self):
        '''
        ドキュメントのビューのテスト（ログインしている場合，受講者であるユーザー, 存在しないセミナー）
        '''
        user = User.objects.create_user(
            username='testuser',
            password='testpassword'
        )
        Members.objects.create(user=user, seminar=self.seminar1)
        self.client.login(username='testuser', password='testpassword')

        response = self.client.get('/doc/abcdefg?lec=0')
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, '404.html')

    def test_doc_view_no_lecture(self):
        '''
        ドキュメントのビューのテスト（ログインしている場合，受講者であるユーザー, 存在しないレクチャー）
        '''
        user = User.objects.create_user(
            username='testuser',
            password='testpassword'
        )
        Members.objects.create(user=user, seminar=self.seminar1)
        self.client.login(username='testuser', password='testpassword')

        response = self.client.get(f'/doc/{self.seminar1.uuid}?lec=0')
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, '404.html')

    def test_doc_view_login_manager(self):
        '''
        ドキュメントのビューのテスト（ログインしている場合，マネージャーであるユーザー）
        '''
        user = User.objects.create_user(
            username='testuser',
            password='testpassword'
        )
        Manager.objects.create(user=user, seminar=self.seminar1)
        self.client.login(username='testuser', password='testpassword')

        response = self.client.get(f'/doc/{self.seminar1.uuid}?lec=1')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'document.html')

    def test_doc_view_login_no_manager(self):
        '''
        ドキュメントのビューのテスト（ログインしている場合，マネージャーでないユーザー）
        '''
        user = User.objects.create_user(
            username='testuser',
            password='testpassword'
        )
        Manager.objects.create(user=user, seminar=self.seminar2)
        self.client.login(username='testuser', password='testpassword')

        response = self.client.get(f'/doc/{self.seminar1.uuid}?lec=1')
        self.assertEqual(response.status_code, 403)

    def test_doc_view_progress_manage_off(self):
        '''
        ドキュメントのビューのテスト（進捗の更新，管理機能オフ）
        '''
        seminar1 = Seminar.objects.create(
            title='Test Seminar1',
            description='Test Description1',
            content='# Test Content1\nTest Content1',
            manage=False,
            public=True
        )

        user = User.objects.create_user(
            username='testuser', password='testpassword'
        )
        member = Members.objects.create(user=user, seminar=seminar1)
        self.client.login(username='testuser', password='testpassword')

        response = self.client.get(f'/doc/{seminar1.uuid}?lec=1')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'document.html')

        member.refresh_from_db()
        self.assertEqual(member.progress, 0)
        self.assertIsNone(member.last_access)

    def test_doc_view_progress_manage_on(self):
        '''
        ドキュメントのビューのテスト（進捗の更新，管理機能オン）
        '''
        seminar2 = Seminar.objects.create(
            title='Test Seminar2',
            description='Test Description2',
            content='# Test Content2\nTest Content2',
            manage=True,
            public=True
        )

        user = User.objects.create_user(
            username='testuser', password='testpassword'
        )
        member = Members.objects.create(user=user, seminar=seminar2)
        self.client.login(username='testuser', password='testpassword')

        response = self.client.get(f'/doc/{seminar2.uuid}?lec=1')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'document.html')

        member.refresh_from_db()
        self.assertEqual(member.progress, 1)
        self.assertIsNotNone(member.last_access)

    def test_doc_view_private_seminar_superuser(self):
        '''
        ドキュメントのビューのテスト（ログインしている場合，スーパーユーザー，非公開セミナー）
        '''
        User.objects.create_superuser(
            username='admin', password='adminpassword'
        )
        self.client.login(username='admin', password='adminpassword')

        response = self.client.get(f'/doc/{self.seminar3.uuid}?lec=1')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'document.html')

    def test_doc_view_private_seminar_staffuser(self):
        '''
        ドキュメントのビューのテスト（ログインしている場合，スタッフユーザー，非公開セミナー）
        '''
        User.objects.create_user(
            username='staffuser', password='staffpassword', is_staff=True
        )
        self.client.login(username='staffuser', password='staffpassword')

        response = self.client.get(f'/doc/{self.seminar3.uuid}?lec=1')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'document.html')

    def test_doc_view_private_seminar(self):
        '''
        ドキュメントのビューのテスト（ログインしている場合，受講者であるユーザー，非公開セミナー）
        '''
        user = User.objects.create_user(
            username='testuser', password='testpassword'
        )
        Members.objects.create(user=user, seminar=self.seminar3)
        self.client.login(username='testuser', password='testpassword')

        response = self.client.get(f'/doc/{self.seminar3.uuid}?lec=1')
        self.assertEqual(response.status_code, 403)

    def test_doc_view_private_seminar_manager(self):
        '''
        ドキュメントのビューのテスト（ログインしている場合，マネージャーであるユーザー，非公開セミナー）
        '''
        user = User.objects.create_user(
            username='testuser', password='testpassword'
        )
        Manager.objects.create(user=user, seminar=self.seminar3)
        self.client.login(username='testuser', password='testpassword')

        response = self.client.get(f'/doc/{self.seminar3.uuid}?lec=1')
        self.assertEqual(response.status_code, 403)


# 印刷セミナーリストのビューテスト
class PrintListViewTests(TestCase):
    def setUp(self):
        '''
        テスト用のセミナーを作成する
        '''
        Seminar.objects.create(
            title='Test Seminar',
            description='Test Description',
            content='# Test Content\nTest Content',
            public=True
        )

    def test_print_list_view_not_login(self):
        '''
        印刷セミナーリストのビューのテスト（ログインしていない場合）
        '''
        response = self.client.get('/print-list')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/?next=/print-list')

    def test_print_list_view_login_superuser(self):
        '''
        印刷セミナーリストのビューのテスト（ログインしている場合，スーパーユーザー）
        '''
        User.objects.create_superuser(
            username='admin', password='adminpassword'
        )
        self.client.login(username='admin', password='adminpassword')

        response = self.client.get('/print-list')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'print_list.html')

    def test_print_list_view_login_staffuser(self):
        '''
        印刷セミナーリストのビューのテスト（ログインしている場合，スタッフユーザー）
        '''
        User.objects.create_user(
            username='staffuser', password='staffpassword', is_staff=True
        )
        self.client.login(username='staffuser', password='staffpassword')

        response = self.client.get('/print-list')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'print_list.html')

    def test_print_list_view_login(self):
        '''
        印刷セミナーリストのビューのテスト（ログインしている場合）
        '''
        User.objects.create_user(
            username='testuser', password='testpassword'
        )
        self.client.login(username='testuser', password='testpassword')

        response = self.client.get('/print-list')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'print_list.html')


# 印刷のビューテスト
class PrintViewTests(TestCase):
    def setUp(self):
        '''
        テスト用のセミナーとレクチャーを作成する
        '''
        self.seminar1 = Seminar.objects.create(
            title='Test Seminar1',
            description='Test Description1',
            content='# Test Content1\nTest Content1',
            public=True
        )
        self.seminar2 = Seminar.objects.create(
            title='Test Seminar2',
            description='Test Description2',
            content='# Test Content2\nTest Content2',
            public=True
        )
        self.seminar3 = Seminar.objects.create(
            title='Test Seminar3',
            description='Test Description3',
            content='# Test Content3\nTest Content3',
            public=False
        )

    def test_print_view_not_login(self):
        '''
        印刷のビューのテスト（ログインしていない場合）
        '''
        response = self.client.get(f'/print/{self.seminar1.uuid}')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response,
            f'/accounts/login/?next=/print/{self.seminar1.uuid}'
        )

        response = self.client.get(f'/print/{self.seminar1.uuid}?lec=1')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response,
            f'/accounts/login/?next=/print/{self.seminar1.uuid}?lec=1'
        )

    def test_print_view_login_superuser(self):
        '''
        印刷のビューのテスト（ログインしている場合，スーパーユーザー）
        '''
        User.objects.create_superuser(
            username='admin', password='adminpassword'
        )
        self.client.login(username='admin', password='adminpassword')

        response = self.client.get(f'/print/{self.seminar1.uuid}')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'print.html')

        response = self.client.get(f'/print/{self.seminar1.uuid}?lec=1')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'print.html')

    def test_print_view_login_staffuser(self):
        '''
        印刷のビューのテスト（ログインしている場合，スタッフユーザー）
        '''
        User.objects.create_user(
            username='staffuser', password='staffpassword', is_staff=True
        )
        self.client.login(username='staffuser', password='staffpassword')

        response = self.client.get(f'/print/{self.seminar1.uuid}')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'print.html')

        response = self.client.get(f'/print/{self.seminar1.uuid}?lec=1')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'print.html')

    def test_print_view_login_not_member(self):
        '''
        印刷のビューのテスト（ログインしている場合，受講者ではないユーザー）
        '''
        user = User.objects.create_user(
            username='testuser', password='testpassword'
        )
        Members.objects.create(user=user, seminar=self.seminar2)
        self.client.login(username='testuser', password='testpassword')

        response = self.client.get(f'/print/{self.seminar1.uuid}')
        self.assertEqual(response.status_code, 403)

        response = self.client.get(f'/print/{self.seminar1.uuid}?lec=1')
        self.assertEqual(response.status_code, 403)

    def test_print_view_login_member(self):
        '''
        印刷のビューのテスト（ログインしている場合，受講者であるユーザー）
        '''
        user = User.objects.create_user(
            username='testuser', password='testpassword'
        )
        Members.objects.create(user=user, seminar=self.seminar1)
        self.client.login(username='testuser', password='testpassword')

        response = self.client.get(f'/print/{self.seminar1.uuid}')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'print.html')

        response = self.client.get(f'/print/{self.seminar1.uuid}?lec=1')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'print.html')

    def test_print_view_no_seminar(self):
        '''
        印刷のビューのテスト（ログインしている場合，受講者であるユーザー, 存在しないセミナー）
        '''
        user = User.objects.create_user(
            username='testuser', password='testpassword'
        )
        Members.objects.create(user=user, seminar=self.seminar1)
        self.client.login(username='testuser', password='testpassword')

        response = self.client.get('/print/abcdefg')
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, '404.html')

    def test_print_view_no_lecture(self):
        '''
        印刷のビューのテスト（ログインしている場合，受講者であるユーザー, 存在しないレクチャー）
        '''
        user = User.objects.create_user(
            username='testuser', password='testpassword'
        )
        Members.objects.create(user=user, seminar=self.seminar1)
        self.client.login(username='testuser', password='testpassword')

        response = self.client.get(f'/print/{self.seminar1.uuid}?lec=0')
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, '404.html')

    def test_print_view_login_manager(self):
        '''
        印刷のビューのテスト（ログインしている場合，マネージャーであるユーザー）
        '''
        user = User.objects.create_user(
            username='testuser', password='testpassword'
        )
        Manager.objects.create(user=user, seminar=self.seminar1)
        self.client.login(username='testuser', password='testpassword')

        response = self.client.get(f'/print/{self.seminar1.uuid}')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'print.html')

        response = self.client.get(f'/print/{self.seminar1.uuid}?lec=1')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'print.html')

    def test_print_view_login_not_manager(self):
        '''
        印刷のビューのテスト（ログインしている場合，マネージャーでないユーザー）
        '''
        user = User.objects.create_user(
            username='testuser', password='testpassword'
        )
        Manager.objects.create(user=user, seminar=self.seminar2)
        self.client.login(username='testuser', password='testpassword')

        response = self.client.get(f'/print/{self.seminar1.uuid}')
        self.assertEqual(response.status_code, 403)

        response = self.client.get(f'/print/{self.seminar1.uuid}?lec=1')
        self.assertEqual(response.status_code, 403)

    def test_print_view_private_seminar_superuser(self):
        '''
        印刷のビューのテスト（ログインしている場合，スーパーユーザー，非公開セミナー）
        '''
        User.objects.create_superuser(
            username='admin', password='adminpassword'
        )
        self.client.login(username='admin', password='adminpassword')

        response = self.client.get(f'/print/{self.seminar3.uuid}')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'print.html')

        response = self.client.get(f'/print/{self.seminar3.uuid}?lec=1')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'print.html')

    def test_print_view_private_seminar_staffuser(self):
        '''
        印刷のビューのテスト（ログインしている場合，スタッフユーザー，非公開セミナー）
        '''
        User.objects.create_user(
            username='staffuser', password='staffpassword', is_staff=True
        )
        self.client.login(username='staffuser', password='staffpassword')

        response = self.client.get(f'/print/{self.seminar3.uuid}')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'print.html')

        response = self.client.get(f'/print/{self.seminar3.uuid}?lec=1')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'print.html')

    def test_print_view_private_seminar(self):
        '''
        印刷のビューのテスト（ログインしている場合，受講者であるユーザー，非公開セミナー）
        '''
        user = User.objects.create_user(
            username='testuser', password='testpassword'
        )
        Members.objects.create(user=user, seminar=self.seminar3)
        self.client.login(username='testuser', password='testpassword')

        response = self.client.get(f'/print/{self.seminar3.uuid}')
        self.assertEqual(response.status_code, 403)

        response = self.client.get(f'/print/{self.seminar3.uuid}?lec=1')
        self.assertEqual(response.status_code, 403)

    def test_print_view_private_seminar_manager(self):
        '''
        印刷のビューのテスト（ログインしている場合，マネージャーであるユーザー，非公開セミナー）
        '''
        user = User.objects.create_user(
            username='testuser', password='testpassword'
        )
        Manager.objects.create(user=user, seminar=self.seminar3)
        self.client.login(username='testuser', password='testpassword')

        response = self.client.get(f'/print/{self.seminar3.uuid}')
        self.assertEqual(response.status_code, 403)

        response = self.client.get(f'/print/{self.seminar3.uuid}?lec=1')
        self.assertEqual(response.status_code, 403)


# ファイルプロテクトのテスト
class ProtectFileTests(TestCase):
    def setUp(self):
        '''
        テスト用のセミナーを作成する
        '''
        self.seminar1 = Seminar.objects.create(
            title='Test Seminar1',
            description='Test Description',
            content='# Test Content\nTest Content',
            public=True
        )
        self.seminar2 = Seminar.objects.create(
            title='Test Seminar2',
            description='Test Description',
            content='# Test Content\nTest Content',
            public=True
        )
        self.seminar3 = Seminar.objects.create(
            title='Test Seminar3',
            description='Test Description',
            content='# Test Content\nTest Content',
            public=False
        )
        self.file = File.objects.create(
            seminar=self.seminar1,
            name='Test File',
            file='test.txt'
        )

    def test_protect_file_not_login(self):
        '''
        ファイルが保護されているかのテスト（ログインしていない場合）
        '''
        response = self.client.get(f'/file/{self.file.uuid}')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response,
            f'/accounts/login/?next=/file/{self.file.uuid}'
        )

    def test_protect_file_login_superuser(self):
        '''
        ファイルが保護されているかのテスト（ログインしている場合，スーパーユーザー）
        '''
        User.objects.create_superuser(
            username='admin', password='adminpassword'
        )
        self.client.login(username='admin', password='adminpassword')

        response = self.client.get(f'/file/{self.file.uuid}')
        self.assertEqual(response.status_code, 200)

    def test_protect_file_login_staffuser(self):
        '''
        ファイルが保護されているかのテスト（ログインしている場合，スタッフユーザー）
        '''
        User.objects.create_user(
            username='staffuser', password='staffpassword', is_staff=True
        )
        self.client.login(username='staffuser', password='staffpassword')

        response = self.client.get(f'/file/{self.file.uuid}')
        self.assertEqual(response.status_code, 200)

    def test_protect_file_login_not_member(self):
        '''
        ファイルが保護されているかのテスト（ログインしている場合，受講者ではないユーザー）
        '''
        user = User.objects.create_user(
            username='testuser', password='testpassword'
        )
        Members.objects.create(user=user, seminar=self.seminar2)
        self.client.login(username='testuser', password='testpassword')

        response = self.client.get(f'/file/{self.file.uuid}')
        self.assertEqual(response.status_code, 403)

    def test_protect_file_login_member(self):
        '''
        ファイルが保護されているかのテスト（ログインしている場合，受講者であるユーザー）
        '''
        user = User.objects.create_user(
            username='testuser', password='testpassword'
        )
        Members.objects.create(user=user, seminar=self.seminar1)
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(f'/file/{self.file.uuid}')
        self.assertEqual(response.status_code, 200)

    def test_protect_file_direct_access(self):
        '''
        ファイルに直接アクセスした場合のテスト
        '''
        response = self.client.get(
            f'/media/seminar_base2/files/{self.file.name}'
        )
        self.assertEqual(response.status_code, 404)

    def test_protect_file_login_manager(self):
        '''
        ファイルが保護されているかのテスト（ログインしている場合，マネージャーであるユーザー）
        '''
        user = User.objects.create_user(
            username='testuser', password='testpassword'
        )
        Manager.objects.create(user=user, seminar=self.seminar1)
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(f'/file/{self.file.uuid}')
        self.assertEqual(response.status_code, 200)

    def test_protect_file_login_not_manager(self):
        '''
        ファイルが保護されているかのテスト（ログインしている場合，マネージャーでないユーザー）
        '''
        user = User.objects.create_user(
            username='testuser', password='testpassword'
        )
        Manager.objects.create(user=user, seminar=self.seminar2)
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(f'/file/{self.file.uuid}')
        self.assertEqual(response.status_code, 403)

    def test_protect_file_private_seminar_superuser(self):
        '''
        ファイルが保護されているかのテスト（ログインしている場合，スーパーユーザー，非公開セミナー）
        '''
        User.objects.create_superuser(
            username='admin', password='adminpassword'
        )
        self.client.login(username='admin', password='adminpassword')
        response = self.client.get(f'/file/{self.file.uuid}')
        self.assertEqual(response.status_code, 200)

    def test_protect_file_private_seminar_staffuser(self):
        '''
        ファイルが保護されているかのテスト（ログインしている場合，スタッフユーザー，非公開セミナー）
        '''
        User.objects.create_user(
            username='staffuser', password='staffpassword', is_staff=True
        )
        self.client.login(username='staffuser', password='staffpassword')
        response = self.client.get(f'/file/{self.file.uuid}')
        self.assertEqual(response.status_code, 200)

    def test_protect_file_private_seminar(self):
        '''
        ファイルが保護されているかのテスト（ログインしている場合，受講者であるユーザー，非公開セミナー）
        '''
        user = User.objects.create_user(
            username='testuser', password='testpassword'
        )
        Members.objects.create(user=user, seminar=self.seminar3)
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(f'/file/{self.file.uuid}')
        self.assertEqual(response.status_code, 403)

    def test_protect_file_private_seminar_manager(self):
        '''
        ファイルが保護されているかのテスト（ログインしている場合，マネージャーであるユーザー，非公開セミナー）
        '''
        user = User.objects.create_user(
            username='testuser', password='testpassword'
        )
        Manager.objects.create(user=user, seminar=self.seminar3)
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(f'/file/{self.file.uuid}')
        self.assertEqual(response.status_code, 403)


# マネージャーリストページのビューテスト
class ManagerListViewTests(TestCase):
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

    def test_manager_list_view_not_login(self):
        '''
        マネージリストページのビューのテスト（ログインしていない場合）
        '''
        response = self.client.get('/manager')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/?next=/manager')

    def test_manager_list_view_login_superuser(self):
        '''
        マネージリストページのビューのテスト（ログインしている場合，スーパーユーザー）
        '''
        User.objects.create_superuser(
            username='admin', password='adminpassword'
        )
        self.client.login(username='admin', password='adminpassword')

        response = self.client.get('/manager')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'manage_list.html')

    def test_manager_list_view_login_staffuser(self):
        '''
        マネージリストページのビューのテスト（ログインしている場合，スタッフユーザー）
        '''
        User.objects.create_user(
            username='staffuser', password='staffpassword', is_staff=True
        )
        self.client.login(username='staffuser', password='staffpassword')

        response = self.client.get('/manager')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'manage_list.html')

    def test_manager_list_view_login(self):
        '''
        マネージリストページのビューのテスト（ログインしている場合，マネージャーであるユーザー）
        '''
        user = User.objects.create_user(
            username='testuser', password='testpassword'
        )
        Manager.objects.create(user=user, seminar=self.seminar1)
        self.client.login(username='testuser', password='testpassword')

        response = self.client.get('/manager')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'manage_list.html')

    def test_manager_list_view_login_not_manager(self):
        '''
        マネージリストページのビューのテスト（ログインしている場合，マネージャーでないユーザー）
        '''
        User.objects.create_user(
            username='testuser', password='testpassword'
        )
        self.client.login(username='testuser', password='testpassword')

        response = self.client.get('/manager')
        self.assertEqual(response.status_code, 403)


# マネージャーページのビューテスト
class ManagerViewTests(TestCase):
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

    def test_manager_view_not_login(self):
        '''
        マネージャーページのビューのテスト（ログインしていない場合）
        '''
        response = self.client.get(f'/manager/{self.seminar1.uuid}')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response,
            f'/accounts/login/?next=/manager/{self.seminar1.uuid}'
        )

    def test_manager_view_login_superuser(self):
        '''
        マネージャーページのビューのテスト（ログインしている場合，スーパーユーザー）
        '''
        User.objects.create_superuser(
            username='admin', password='adminpassword'
        )
        self.client.login(username='admin', password='adminpassword')

        response = self.client.get(f'/manager/{self.seminar1.uuid}')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'manager.html')

    def test_manager_view_login_staffuser(self):
        '''
        マネージャーページのビューのテスト（ログインしている場合，スタッフユーザー）
        '''
        User.objects.create_user(
            username='staffuser', password='staffpassword', is_staff=True
        )
        self.client.login(username='staffuser', password='staffpassword')

        response = self.client.get(f'/manager/{self.seminar1.uuid}')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'manager.html')

    def test_manager_view_login_not_manager(self):
        '''
        マネージャーページのビューのテスト（ログインしている場合，マネージャーでないユーザー）
        '''
        user = User.objects.create_user(
            username='testuser', password='testpassword'
        )
        Manager.objects.create(user=user, seminar=self.seminar2)
        self.client.login(username='testuser', password='testpassword')

        response = self.client.get(f'/manager/{self.seminar1.uuid}')
        self.assertEqual(response.status_code, 403)

    def test_manager_view_login_manager(self):
        '''
        マネージャーページのビューのテスト（ログインしている場合，マネージャーであるユーザー）
        '''
        user = User.objects.create_user(
            username='testuser', password='testpassword'
        )
        Manager.objects.create(user=user, seminar=self.seminar1)
        self.client.login(username='testuser', password='testpassword')

        response = self.client.get(f'/manager/{self.seminar1.uuid}')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'manager.html')

    def test_manager_view_private_seminar(self):
        '''
        マネージャーページのビューのテスト（ログインしている場合，マネージャーであるユーザー，非公開セミナー）
        '''
        user = User.objects.create_user(
            username='testuser', password='testpassword'
        )
        Manager.objects.create(user=user, seminar=self.seminar3)
        self.client.login(username='testuser', password='testpassword')

        response = self.client.get(f'/manager/{self.seminar3.uuid}')
        self.assertEqual(response.status_code, 403)

    def test_manager_view_superuser(self):
        '''
        マネージャーページのビューのテスト（ログインしている場合，スーパーユーザー，非公開セミナー）
        '''
        User.objects.create_superuser(
            username='admin', password='adminpassword'
        )
        self.client.login(username='admin', password='adminpassword')
        response = self.client.get(f'/manager/{self.seminar3.uuid}')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'manager.html')

    def test_manager_view_staffuser(self):
        '''
        マネージャーページのビューのテスト（ログインしている場合，スタッフユーザー，非公開セミナー）
        '''
        User.objects.create_user(
            username='staffuser', password='staffpassword', is_staff=True
        )
        self.client.login(username='staffuser', password='staffpassword')
        response = self.client.get(f'/manager/{self.seminar3.uuid}')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'manager.html')
