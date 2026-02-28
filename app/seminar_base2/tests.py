from django.test import TestCase
from django.contrib.auth.models import User
from .models import Seminar, Lecture, Members

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
        Seminar.objects.create(title='Test Seminar', description='Test Description')
    
    def test_seminar_list_view_not_login(self):
        '''
        セミナーリストのビューのテスト（ログインしていない場合）
        '''
        response = self.client.get('/seminar/')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/?next=/seminar/')
        
    def test_seminar_list_view_login(self):
        '''
        セミナーリストのビューのテスト（ログインしている場合）
        '''
        User.objects.create_user(username='testuser', password='testpassword')
        self.client.login(username='testuser', password='testpassword')
        
        response = self.client.get('/seminar/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'seminar_list.html')

# レクチャーリストのビューテスト
class LectureListViewTests(TestCase):
    def setUp(self):
        '''
        テスト用のセミナーとレクチャーを作成する
        '''
        self.seminar = Seminar.objects.create(title='Test Seminar', description='Test Description')
        Lecture.objects.create(seminar=self.seminar, title='Test Lecture', content='Test Content')
    
    def test_lecture_list_view_not_login(self):
        '''
        レクチャーリストのビューのテスト（ログインしていない場合）
        '''
        response = self.client.get(f'/lecture/{self.seminar.uuid}/')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f'/accounts/login/?next=/lecture/{self.seminar.uuid}/')
        
    def test_lecture_list_view_login_not_member(self):
        '''
        レクチャーリストのビューのテスト（ログインしている場合，受講者ではないユーザー）
        '''

        User.objects.create_user(username='testuser', password='testpassword')
        self.client.login(username='testuser', password='testpassword')
        
        response = self.client.get(f'/lecture/{self.seminar.uuid}/')
        self.assertEqual(response.status_code, 403)
        
    def test_lecture_list_view_login_member(self):
        ''' 
        レクチャーリストのビューのテスト（ログインしている場合，受講者であるユーザー）
        '''
        user = User.objects.create_user(username='testuser', password='testpassword')
        Members.objects.create(user=user, seminar=self.seminar)
        self.client.login(username='testuser', password='testpassword')
        
        response = self.client.get(f'/lecture/{self.seminar.uuid}/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'lecture_list.html')
        
# ドキュメントのビューテスト
class DocumentViewTests(TestCase):
    def setUp(self):
        '''
        テスト用のセミナーとレクチャーを作成する
        '''
        self.seminar = Seminar.objects.create(title='Test Seminar', description='Test Description')
        self.lecture = Lecture.objects.create(seminar=self.seminar, title='Test Lecture', content='Test Content')
    
    def test_document_view_not_login(self):
        '''
        ドキュメントのビューのテスト（ログインしていない場合）
        '''
        response = self.client.get(f'/doc/{self.seminar.uuid}/{self.lecture.uuid}/')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f'/accounts/login/?next=/doc/{self.seminar.uuid}/{self.lecture.uuid}/')
        
    def test_doc_view_login_not_member(self):
        '''
        ドキュメントのビューのテスト（ログインしている場合，受講者ではないユーザー）
        '''

        User.objects.create_user(username='testuser', password='testpassword')
        self.client.login(username='testuser', password='testpassword')
        
        response = self.client.get(f'/doc/{self.seminar.uuid}/{self.lecture.uuid}/')
        self.assertEqual(response.status_code, 403)
        
    def test_doc_view_login_member(self):
        ''' 
        ドキュメントのビューのテスト（ログインしている場合，受講者であるユーザー）
        '''
        user = User.objects.create_user(username='testuser', password='testpassword')
        Members.objects.create(user=user, seminar=self.seminar)
        self.client.login(username='testuser', password='testpassword')
        
        response = self.client.get(f'/doc/{self.seminar.uuid}/{self.lecture.uuid}/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'document.html')
        
# 印刷セミナーリストのビューテスト
class PrintListViewTests(TestCase):
    def setUp(self):
        '''
        テスト用のセミナーを作成する
        '''
        Seminar.objects.create(title='Test Seminar', description='Test Description')
    
    def test_print_list_view_not_login(self):
        '''
        印刷セミナーリストのビューのテスト（ログインしていない場合）
        '''
        response = self.client.get('/print-list/')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/?next=/print-list/')
        
    def test_print_list_view_login(self):
        '''
        印刷セミナーリストのビューのテスト（ログインしている場合）
        '''
        User.objects.create_user(username='testuser', password='testpassword')
        self.client.login(username='testuser', password='testpassword')
        
        response = self.client.get('/print-list/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'print_list.html')
        
# 印刷のビューテスト
class PrintViewTests(TestCase):
    def setUp(self):
        '''
        テスト用のセミナーとレクチャーを作成する
        '''
        self.seminar = Seminar.objects.create(title='Test Seminar', description='Test Description')
        self.lecture = Lecture.objects.create(seminar=self.seminar, title='Test Lecture', content='Test Content')
    
    def test_print_view_not_login(self):
        '''
        印刷のビューのテスト（ログインしていない場合）
        '''
        response = self.client.get(f'/print/{self.seminar.uuid}/')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f'/accounts/login/?next=/print/{self.seminar.uuid}/')
        
    def test_print_view_login_not_member(self):
        '''
        印刷のビューのテスト（ログインしている場合，受講者ではないユーザー）
        '''

        User.objects.create_user(username='testuser', password='testpassword')
        self.client.login(username='testuser', password='testpassword')
        
        response = self.client.get(f'/print/{self.seminar.uuid}/')
        self.assertEqual(response.status_code, 403)
        
    def test_print_view_login_member(self):
        ''' 
        印刷のビューのテスト（ログインしている場合，受講者であるユーザー）
        '''
        user = User.objects.create_user(username='testuser', password='testpassword')
        Members.objects.create(user=user, seminar=self.seminar)
        self.client.login(username='testuser', password='testpassword')
        
        response = self.client.get(f'/print/{self.seminar.uuid}/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'print.html')