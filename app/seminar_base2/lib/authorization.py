from django.contrib.auth.models import User
from ..models import Seminar, Members, Manager


# ベースミックスイン
class BaseAuthorizationMixin():
    def is_superuser_or_staff(self, user: User):
        """
        ユーザーがスーパーユーザーまたはスタッフユーザーであるかを判定するメソッド
        """
        return user.is_superuser or user.is_staff

    def is_member(self, user: User, seminar: Seminar=None):
        """
        ユーザーがセミナーの参加者であるかを判定するメソッド
        """
        if seminar:
            return seminar.members.filter(user=user).exists()
        return Members.objects.filter(user=user).exists()

    def is_manager(self, user: User, seminar: Seminar=None):
        """
        ユーザーがセミナーのマネージャーであるかを判定するメソッド
        """
        if seminar:
            return seminar.managers.filter(user=user).exists()
        return Manager.objects.filter(user=user).exists()


# 参加者認証ミックスイン
class MemberAuthorizationMixin(BaseAuthorizationMixin):
    def is_member_access(self, user: User, seminar: Seminar=None):
        """
        参加者認証のロジックを定義するメソッド
        """
        # 管理者・スタッフはアクセス許可する
        if self.is_superuser_or_staff(user):
            return True

        # 非公開の場合アクセス拒否する
        if seminar:
            if not seminar.public:
                return False

        # 参加者はアクセス許可する
        if self.is_member(user, seminar):
            return True
        # マネージャーはアクセス許可する
        if self.is_manager(user, seminar):
            return True

        # それ以外はアクセス拒否する
        return False


# マネージャー認証ミックスイン
class ManagerAuthorizationMixin(BaseAuthorizationMixin):
    def is_manager_access(self, user: User, seminar: Seminar=None):
        """
        マネージャー認証のロジックを定義するメソッド
        """
        # 管理者・スタッフはアクセス許可する
        if self.is_superuser_or_staff(user):
            return True

        # 非公開の場合アクセス拒否する
        if seminar:
            if not seminar.public:
                return False

        # マネージャーはアクセス許可する
        if self.is_manager(user, seminar):
            return True

        # それ以外はアクセス拒否する
        return False
