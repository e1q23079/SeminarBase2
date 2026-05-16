# Docのテスト
from django.test import TestCase
from ..lib.doc import Doc


class DocTests(TestCase):
    """
    Docクラスのテストケース
    """
    def setUp(self):
        '''
        テスト用のドキュメントを作成する
        '''
        self.doc = Doc(
            "# Test Lecture\nTest Content\n# Test Lecture2\nTest Content2\n# Test Lecture3\nTest Content3\n"    # noqa: E501
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

    def test_get_lecture_count(self):
        '''
        ドキュメントからレクチャーの数を取得するテスト
        '''
        self.assertEqual(self.doc.get_lecture_count(), 3)
