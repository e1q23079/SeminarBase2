from django.test import TestCase
from ..lib.members import get_last_request_time
from ..models import Seminar, Members
from django.contrib.auth.models import User
from django.utils import timezone
import datetime


class MembersTests(TestCase):
    """
    Membersのテスト
    """
    def test_get_last_request_time_with_members(self):
        '''
        get_last_request_time関数のテスト（メンバーが存在する場合）
        '''
        seminar = Seminar.objects.create(title='Test Seminar')
        user1 = User.objects.create_user(
            username='user1',
            password='password1'
        )
        user2 = User.objects.create_user(
            username='user2',
            password='password2'
        )

        # メンバーを作成して最後のリクエスト時間を設定する
        Members.objects.create(
            seminar=seminar,
            user=user1,
            last_request=timezone.make_aware(
                datetime.datetime(2027, 6, 1, 12, 0, 0)
            )
        )
        Members.objects.create(
            seminar=seminar,
            user=user2,
            last_request=timezone.make_aware(
                datetime.datetime(2024, 6, 1, 13, 0, 0)
            )
        )

        # 最後のリクエスト時間が正しく取得できることを確認する
        self.assertEqual(
            get_last_request_time(seminar),
            timezone.make_aware(datetime.datetime(2027, 6, 1, 12, 0, 0))
        )

    def test_get_last_request_time_no_members(self):
        '''
        get_last_request_time関数のテスト（メンバーが存在しない場合）
        '''
        # メンバーが存在しない場合はNoneが返されることを確認する
        seminar_no_members = Seminar.objects.create(title='No Members Seminar')
        self.assertIsNone(get_last_request_time(seminar_no_members))
