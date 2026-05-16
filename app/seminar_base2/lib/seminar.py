from ..models import Seminar
from django.contrib.auth.models import User

# TODO: アクセス（このファイルは使わない？）

def is_member(seminar: Seminar, user: User) -> Seminar:
    """_summary_

    Args:
        seminar (Seminar): _description_
        user (User): _description_

    Returns:
        Seminar: _description_
    """
    seminar.is_member = (seminar.public and seminar.members_set.filter(user=user).exists()) or user.is_superuser or (seminar.public and seminar.manager_set.filter(user=user).exists())
    return seminar

def is_manager(seminar: Seminar, user: User) -> Seminar:
    """_summary_

    Args:
        seminar (Seminar): _description_
        user (User): _description_

    Returns:
        Seminar: _description_
    """
    seminar.is_manager = (seminar.public and seminar.manager_set.filter(user=user).exists()) or user.is_superuser
    return seminar
