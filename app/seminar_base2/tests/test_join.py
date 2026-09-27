from datetime import datetime
from django.test import TestCase
from ..lib.join import get_join_valid_until, is_join_valid


class JoinTests(TestCase):
    '''
    参加受付の有効期限のテストケース
    '''
    def test_get_join_valid_until(self):
        '''
        get_join_valid_until関数のテスト
        '''
        now = datetime(2024, 6, 1, 12, 0, 0)
        expected_valid_until = datetime(2024, 6, 1, 12, 1, 0)
        self.assertEqual(get_join_valid_until(now), expected_valid_until)

    def test_is_join_valid(self):
        '''
        is_join_valid関数のテスト
        '''
        join_issued_at = datetime(2024, 6, 1, 12, 0, 0)
        now_valid = datetime(2024, 6, 1, 12, 0, 30)
        now_invalid = datetime(2024, 6, 1, 12, 2, 0)

        self.assertTrue(is_join_valid(join_issued_at, now_valid))
        self.assertFalse(is_join_valid(join_issued_at, now_invalid))
