from django.test import TestCase
from django.contrib.auth.models import User
from .models import Seminar, Members

# Create your tests here.

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
        Seminar.objects.create(title='Test Seminar', description='Test Description',  content='# Test Content\nTest Content')
    
    def test_seminar_list_view_not_login(self):
        '''
        セミナーリストのビューのテスト（ログインしていない場合）
        '''
        response = self.client.get('/seminar')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/?next=/seminar')
        
    def test_seminar_list_view_login(self):
        '''
        セミナーリストのビューのテスト（ログインしている場合）
        '''
        User.objects.create_user(username='testuser', password='testpassword')
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
        self.seminar = Seminar.objects.create(title='Test Seminar', description='Test Description', content='# Test Content\nTest Content')
        # Lecture.objects.create(seminar=self.seminar, title='Test Lecture', content='Test Content')
    
    def test_lecture_list_view_not_login(self):
        '''
        レクチャーリストのビューのテスト（ログインしていない場合）
        '''
        response = self.client.get(f'/lecture/{self.seminar.uuid}')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f'/accounts/login/?next=/lecture/{self.seminar.uuid}')
        
    def test_lecture_list_view_login_not_member(self):
        '''
        レクチャーリストのビューのテスト（ログインしている場合，受講者ではないユーザー）
        '''

        User.objects.create_user(username='testuser', password='testpassword')
        self.client.login(username='testuser', password='testpassword')
        
        response = self.client.get(f'/lecture/{self.seminar.uuid}')
        self.assertEqual(response.status_code, 403)
        
    def test_lecture_list_view_login_member(self):
        ''' 
        レクチャーリストのビューのテスト（ログインしている場合，受講者であるユーザー）
        '''
        user = User.objects.create_user(username='testuser', password='testpassword')
        Members.objects.create(user=user, seminar=self.seminar)
        self.client.login(username='testuser', password='testpassword')
        
        response = self.client.get(f'/lecture/{self.seminar.uuid}')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'lecture_list.html')
        
    def test_lecture_list_view_no_seminar(self):
        ''' 
        レクチャーリストのビューのテスト（ログインしている場合，受講者であるユーザー，存在しないセミナー）
        '''
        user = User.objects.create_user(username='testuser', password='testpassword')
        Members.objects.create(user=user, seminar=self.seminar)
        self.client.login(username='testuser', password='testpassword')
        
        response = self.client.get(f'/lecture/abcdefg')
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, '404.html')
        
# ドキュメントのビューテスト
class DocumentViewTests(TestCase):
    def setUp(self):
        '''
        テスト用のセミナーとレクチャーを作成する
        '''
        self.seminar = Seminar.objects.create(title='Test Seminar', description='Test Description',  content='# Test Content\nTest Content')
        # self.lecture = Lecture.objects.create(seminar=self.seminar, title='Test Lecture', content='Test Content')
    
    def test_document_view_not_login(self):
        '''
        ドキュメントのビューのテスト（ログインしていない場合）
        '''
        response = self.client.get(f'/doc/{self.seminar.uuid}?lec=1')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f'/accounts/login/?next=/doc/{self.seminar.uuid}?lec=1')
        
    def test_doc_view_login_not_member(self):
        '''
        ドキュメントのビューのテスト（ログインしている場合，受講者ではないユーザー）
        '''

        User.objects.create_user(username='testuser', password='testpassword')
        self.client.login(username='testuser', password='testpassword')
        
        response = self.client.get(f'/doc/{self.seminar.uuid}?lec=1')
        self.assertEqual(response.status_code, 403)
        
    def test_doc_view_login_member(self):
        ''' 
        ドキュメントのビューのテスト（ログインしている場合，受講者であるユーザー）
        '''
        user = User.objects.create_user(username='testuser', password='testpassword')
        Members.objects.create(user=user, seminar=self.seminar)
        self.client.login(username='testuser', password='testpassword')
        
        response = self.client.get(f'/doc/{self.seminar.uuid}?lec=1')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'document.html')
        
    def test_doc_view_no_seminar(self):
        ''' 
        ドキュメントのビューのテスト（ログインしている場合，受講者であるユーザー, 存在しないセミナー）
        '''
        user = User.objects.create_user(username='testuser', password='testpassword')
        Members.objects.create(user=user, seminar=self.seminar)
        self.client.login(username='testuser', password='testpassword')
        
        response = self.client.get(f'/doc/abcdefg?lec=0')
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, '404.html')
        
    def test_doc_view_no_lecture(self):
        ''' 
        ドキュメントのビューのテスト（ログインしている場合，受講者であるユーザー, 存在しないレクチャー）
        '''
        user = User.objects.create_user(username='testuser', password='testpassword')
        Members.objects.create(user=user, seminar=self.seminar)
        self.client.login(username='testuser', password='testpassword')
        
        response = self.client.get(f'/doc/{self.seminar.uuid}?lec=0')
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, '404.html')
        
# 印刷セミナーリストのビューテスト
class PrintListViewTests(TestCase):
    def setUp(self):
        '''
        テスト用のセミナーを作成する
        '''
        Seminar.objects.create(title='Test Seminar', description='Test Description',  content='# Test Content\nTest Content')
    
    def test_print_list_view_not_login(self):
        '''
        印刷セミナーリストのビューのテスト（ログインしていない場合）
        '''
        response = self.client.get('/print-list')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/?next=/print-list')
        
    def test_print_list_view_login(self):
        '''
        印刷セミナーリストのビューのテスト（ログインしている場合）
        '''
        User.objects.create_user(username='testuser', password='testpassword')
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
        self.seminar = Seminar.objects.create(title='Test Seminar', description='Test Description',  content='# Test Content\nTest Content')
        # self.lecture = Lecture.objects.create(seminar=self.seminar, title='Test Lecture', content='Test Content')
    
    def test_print_view_not_login(self):
        '''
        印刷のビューのテスト（ログインしていない場合）
        '''
        response = self.client.get(f'/print/{self.seminar.uuid}')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f'/accounts/login/?next=/print/{self.seminar.uuid}')
        
        response = self.client.get(f'/print/{self.seminar.uuid}?lec=1')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f'/accounts/login/?next=/print/{self.seminar.uuid}?lec=1')
        
    def test_print_view_login_not_member(self):
        '''
        印刷のビューのテスト（ログインしている場合，受講者ではないユーザー）
        '''

        User.objects.create_user(username='testuser', password='testpassword')
        self.client.login(username='testuser', password='testpassword')
        
        response = self.client.get(f'/print/{self.seminar.uuid}')
        self.assertEqual(response.status_code, 403)
        
        response = self.client.get(f'/print/{self.seminar.uuid}?lec=1')
        self.assertEqual(response.status_code, 403)
        
    def test_print_view_login_member(self):
        ''' 
        印刷のビューのテスト（ログインしている場合，受講者であるユーザー）
        '''
        user = User.objects.create_user(username='testuser', password='testpassword')
        Members.objects.create(user=user, seminar=self.seminar)
        self.client.login(username='testuser', password='testpassword')
        
        response = self.client.get(f'/print/{self.seminar.uuid}')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'print.html')
        
        response = self.client.get(f'/print/{self.seminar.uuid}?lec=1')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'print.html')
        
    def test_print_view_no_seminar(self):
        ''' 
        印刷のビューのテスト（ログインしている場合，受講者であるユーザー, 存在しないセミナー）
        '''
        user = User.objects.create_user(username='testuser', password='testpassword')
        Members.objects.create(user=user, seminar=self.seminar)
        self.client.login(username='testuser', password='testpassword')
        
        response = self.client.get(f'/print/abcdefg')
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, '404.html')
        
    def test_print_view_no_lecture(self):
        ''' 
        印刷のビューのテスト（ログインしている場合，受講者であるユーザー, 存在しないレクチャー）
        '''
        user = User.objects.create_user(username='testuser', password='testpassword')
        Members.objects.create(user=user, seminar=self.seminar)
        self.client.login(username='testuser', password='testpassword')
        
        response = self.client.get(f'/print/{self.seminar.uuid}?lec=0')
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, '404.html')

# Docのテスト
from .lib.doc import Doc

class DocTests(TestCase):
    def setUp(self):
        '''
        テスト用のドキュメントを作成する
        '''
        self.doc = Doc(
            '''
            <h1>Test Lecture</h1>
            <p>Test Content</p>
            <h1>Test Lecture2</h1>
            <p>Test Content2</p>
            <h1>Test Lecture3</h1>
            <p>Test Content3</p>
            '''
        )

    def test_get_lectures(self):
        '''
        ドキュメントからレクチャーを取得するテスト
        '''
        self.assertEqual(self.doc.get_lectures(), [{
            "title": "Test Lecture",
            "content": "<p>Test Content</p>",
            "chapter": 1,
            "prev": None,
            "next": 2
        }, {
            "title": "Test Lecture2",
            "content": "<p>Test Content2</p>",
            "chapter": 2,
            "prev": 1,
            "next": 3
        }, {
            "title": "Test Lecture3",
            "content": "<p>Test Content3</p>",
            "chapter": 3,
            "prev": 2,
            "next": None  
        }])
        
    def test_get_lecture_titles(self):
        '''
        ドキュメントからレクチャーのタイトル一覧を取得するテスト
        '''
        self.assertEqual(self.doc.get_lecture_titles(), [{
            "title": "Test Lecture",
            "chapter": 1
        }, {
            "title": "Test Lecture2",
            "chapter": 2
        }, {
            "title": "Test Lecture3",
            "chapter": 3
        }])

    def test_get_lecture(self):
        '''
        ドキュメントからチャプター番号でレクチャーを取得するテスト
        '''
        self.assertEqual(self.doc.get_lecture(2), {
            "title": "Test Lecture2",
            "content": "<p>Test Content2</p>",
            "chapter": 2,
            "prev": 1,
            "next": 3
        })
        self.assertEqual(self.doc.get_lecture(4), None)
