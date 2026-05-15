from django.test import TestCase
from django.contrib.auth.models import User
from seminar_base2.lib.authorization import (
    BaseAuthorizationMixin,
    MemberAuthorizationMixin,
    ManagerAuthorizationMixin
)
from ..models import Seminar, Members, Manager


class BaseAuthorizationMixinTests(TestCase):
    """
    BaseAuthorizationMixinのテスト
    """
    def setUp(self):
        self.mixin = BaseAuthorizationMixin()
        self.seminar = Seminar.objects.create(
            title='Test Seminar',
            public=True
        )

    def test_is_superuser_or_staff_superuser(self):
        '''
        is_superuser_or_staffメソッドのテスト（スーパーユーザーの場合）
        '''
        # スーパーユーザーの場合
        superuser = User(is_superuser=True, is_staff=False)
        self.assertTrue(self.mixin.is_superuser_or_staff(superuser))

    def test_is_superuser_or_staff_staff(self):
        '''
        is_superuser_or_staffメソッドのテスト（スタッフユーザーの場合）
        '''
        # スタッフユーザーの場合
        staff = User(is_superuser=False, is_staff=True)
        self.assertTrue(self.mixin.is_superuser_or_staff(staff))

    def test_is_superuser_or_staff_normal_user(self):
        '''
        is_superuser_or_staffメソッドのテスト（通常ユーザーの場合）
        '''
        # 通常ユーザーの場合
        normal_user = User(is_superuser=False, is_staff=False)
        self.assertFalse(self.mixin.is_superuser_or_staff(normal_user))

    def test_is_member_member(self):
        '''
        is_memberメソッドのテスト（参加者の場合）
        '''
        user = User.objects.create(username='testuser')
        Members.objects.create(user=user, seminar=self.seminar)
        self.assertTrue(self.mixin.is_member(user, self.seminar))

    def test_is_member_non_member(self):
        '''
        is_memberメソッドのテスト（非参加者の場合）
        '''
        user = User.objects.create(username='testuser')
        self.assertFalse(self.mixin.is_member(user, self.seminar))

    def test_is_manager_manager(self):
        '''
        is_managerメソッドのテスト（マネージャーの場合）
        '''
        user = User.objects.create(username='testuser')
        Manager.objects.create(user=user, seminar=self.seminar)

        self.assertTrue(self.mixin.is_manager(user, self.seminar))

    def test_is_manager_non_manager(self):
        '''
        is_managerメソッドのテスト（非マネージャーの場合）
        '''
        user = User.objects.create(username='testuser')
        self.assertFalse(self.mixin.is_manager(user, self.seminar))


class MemberAuthorizationMixinTests(TestCase):
    """
    MemberAuthorizationMixinのテスト
    """
    def setUp(self):
        self.mixin = MemberAuthorizationMixin()

        self.seminar_public = Seminar.objects.create(
            title='Test Seminar',
            public=True)
        self.seminar_private = Seminar.objects.create(
            title='Test Seminar Private',
            public=False
        )

        self.superuser = User.objects.create(
            username='superuser',
            is_superuser=True,
            is_staff=False
        )
        self.staff = User.objects.create(
            username='staff',
            is_superuser=False,
            is_staff=True
        )

        self.normal_user = User.objects.create(
            username='normal_user',
            is_superuser=False,
            is_staff=False
        )

        self.member_user = User.objects.create(
            username='member_user',
            is_superuser=False,
            is_staff=False
        )
        Members.objects.create(
            user=self.member_user,
            seminar=self.seminar_public
        )

        self.manager_user = User.objects.create(
            username='manager_user',
            is_superuser=False,
            is_staff=False
        )
        Manager.objects.create(
            user=self.manager_user,
            seminar=self.seminar_public
        )

    def test_is_member_access_superuser_public_seminar(self):
        '''
        is_member_accessメソッドのテスト（スーパーユーザーの場合，公開セミナー）
        '''
        self.assertTrue(
            self.mixin.is_member_access(self.superuser, self.seminar_public)
        )

    def test_is_member_access_superuser_private_seminar(self):
        '''
        is_member_accessメソッドのテスト（スーパーユーザーの場合，非公開セミナー）
        '''
        self.assertTrue(
            self.mixin.is_member_access(self.superuser, self.seminar_private)
        )

    def test_is_member_access_staff_public_seminar(self):
        '''
        is_member_accessメソッドのテスト（スタッフユーザーの場合，公開セミナー）
        '''
        self.assertTrue(
            self.mixin.is_member_access(self.staff, self.seminar_public)
        )

    def test_is_member_access_staff_private_seminar(self):
        '''
        is_member_accessメソッドのテスト（スタッフユーザーの場合，非公開セミナー）
        '''
        self.assertTrue(
            self.mixin.is_member_access(self.staff, self.seminar_private)
        )

    def test_is_member_access_normal_user_public_seminar(self):
        '''
        is_member_accessメソッドのテスト（通常ユーザーの場合，公開セミナー）
        '''
        self.assertFalse(
            self.mixin.is_member_access(self.normal_user, self.seminar_public)
        )

    def test_is_member_access_normal_user_private_seminar(self):
        '''
        is_member_accessメソッドのテスト（通常ユーザーの場合，非公開セミナー）
        '''
        self.assertFalse(
            self.mixin.is_member_access(self.normal_user, self.seminar_private)
        )

    def test_is_member_access_member_user_public_seminar(self):
        '''
        is_member_accessメソッドのテスト（参加者ユーザーの場合，公開セミナー）
        '''
        self.assertTrue(
            self.mixin.is_member_access(self.member_user, self.seminar_public)
        )

    def test_is_member_access_member_user_private_seminar(self):
        '''
        is_member_accessメソッドのテスト（参加者ユーザーの場合，非公開セミナー）
        '''
        self.assertFalse(
            self.mixin.is_member_access(self.member_user, self.seminar_private)
        )

    def test_is_member_access_manager_user_public_seminar(self):
        '''
        is_member_accessメソッドのテスト（マネージャーの場合，公開セミナー）
        '''
        self.assertTrue(
            self.mixin.is_member_access(self.manager_user, self.seminar_public)
        )

    def test_is_member_access_manager_user_private_seminar(self):
        '''
        is_member_accessメソッドのテスト（マネージャーの場合，非公開セミナー）
        '''
        self.assertFalse(
            self.mixin.is_member_access(
                self.manager_user,
                self.seminar_private
            )
        )


class ManagerAuthorizationMixinTests(TestCase):
    """
    ManagerAuthorizationMixinのテスト
    """
    def setUp(self):
        self.mixin = ManagerAuthorizationMixin()

        self.seminar_public = Seminar.objects.create(
            title='Test Seminar',
            public=True
        )
        self.seminar_private = Seminar.objects.create(
            title='Test Seminar Private',
            public=False
        )

        self.superuser = User.objects.create(
            username='superuser',
            is_superuser=True,
            is_staff=False
        )
        self.staff = User.objects.create(
            username='staff',
            is_superuser=False,
            is_staff=True
        )
        self.normal_user = User.objects.create(
            username='normal_user',
            is_superuser=False,
            is_staff=False
        )
        self.member_user = User.objects.create(
            username='member_user',
            is_superuser=False,
            is_staff=False
        )
        Members.objects.create(
            user=self.member_user,
            seminar=self.seminar_public
        )

        self.manager_user = User.objects.create(
            username='manager_user',
            is_superuser=False,
            is_staff=False
        )
        Manager.objects.create(
            user=self.manager_user,
            seminar=self.seminar_public
        )

    def test_is_manager_access_superuser_public_seminar(self):
        '''
        is_manager_accessメソッドのテスト（スーパーユーザーの場合，公開セミナー）
        '''
        self.assertTrue(
            self.mixin.is_manager_access(self.superuser, self.seminar_public)
        )

    def test_is_manager_access_superuser_private_seminar(self):
        '''
        is_manager_accessメソッドのテスト（スーパーユーザーの場合，非公開セミナー）
        '''
        self.assertTrue(
            self.mixin.is_manager_access(self.superuser, self.seminar_private)
        )

    def test_is_manager_access_staff_public_seminar(self):
        '''
        is_manager_accessメソッドのテスト（スタッフユーザーの場合，公開セミナー）
        '''
        self.assertTrue(
            self.mixin.is_manager_access(self.staff, self.seminar_public)
        )

    def test_is_manager_access_staff_private_seminar(self):
        '''
        is_manager_accessメソッドのテスト（スタッフユーザーの場合，非公開セミナー）
        '''
        self.assertTrue(
            self.mixin.is_manager_access(self.staff, self.seminar_private)
        )

    def test_is_manager_access_normal_user_public_seminar(self):
        '''
        is_manager_accessメソッドのテスト（通常ユーザーの場合，公開セミナー）
        '''
        self.assertFalse(
            self.mixin.is_manager_access(self.normal_user, self.seminar_public)
        )

    def test_is_manager_access_normal_user_private_seminar(self):
        '''
        is_manager_accessメソッドのテスト（通常ユーザーの場合，非公開セミナー）
        '''
        self.assertFalse(
            self.mixin.is_manager_access(
                self.normal_user,
                self.seminar_private
            )
        )

    def test_is_manager_access_member_user_public_seminar(self):
        '''
        is_manager_accessメソッドのテスト（参加者ユーザーの場合，公開セミナー）
        '''
        self.assertFalse(
            self.mixin.is_manager_access(self.member_user, self.seminar_public)
        )

    def test_is_manager_access_member_user_private_seminar(self):
        '''
        is_manager_accessメソッドのテスト（参加者ユーザーの場合，非公開セミナー）
        '''
        self.assertFalse(
            self.mixin.is_manager_access(
                self.member_user,
                self.seminar_private
            )
        )

    def test_is_manager_access_manager_user_public_seminar(self):
        '''
        is_manager_accessメソッドのテスト（マネージャーの場合，公開セミナー）
        '''
        self.assertTrue(
            self.mixin.is_manager_access(
                self.manager_user,
                self.seminar_public
            )
        )

    def test_is_manager_access_manager_user_private_seminar(self):
        '''
            is_manager_accessメソッドのテスト（マネージャーの場合，非公開セミナー）
        '''
        self.assertFalse(
            self.mixin.is_manager_access(
                self.manager_user,
                self.seminar_private
            )
        )
