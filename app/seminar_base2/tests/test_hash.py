from django.test import TestCase
from ..lib.hash import generate_hash


class HashTests(TestCase):
    '''
    ハッシュ生成のテストケース
    '''
    def test_generate_hash(self):
        '''
        generate_hash関数のテスト
        '''
        timestamp = '2024-06-01T12:00:00Z'
        expected_hash = 'b2a81c8bf036975c60c44c481b8f3e2188af7c770f6aba4fb84e35780248de49'  # noqa: E501
        self.assertEqual(generate_hash(timestamp), expected_hash)

        timestamp = '2024-06-01T12:00:00+09:00'
        expected_hash = '394393d8f60ef95145aa522dc1388d385be0ab3e07c087d3adc4a0f187e6b290'  # noqa: E501
        self.assertEqual(generate_hash(timestamp), expected_hash)

    def test_generate_hash_none(self):
        '''
        generate_hash関数のテスト（Noneを渡した場合）
        '''
        timestamp = None
        expected_hash = 'dc937b59892604f5a86ac96936cd7ff09e25f18ae6b758e8014a24c7fa039e91'  # noqa: E501
        self.assertEqual(generate_hash(timestamp), expected_hash)
