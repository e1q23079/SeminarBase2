import uuid
from django.db import models
from django.contrib.auth.models import User
# from markdownx.models import MarkdownxField
import os

# Create your models here.

# セミナーモデル
class Seminar(models.Model):
    
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, verbose_name="UUID")
    
    title = models.CharField(max_length=200,verbose_name="セミナー名")
    description = models.TextField(verbose_name="詳細")
    
    # content = MarkdownxField(verbose_name="コンテンツ", blank=True)
    content = models.TextField(verbose_name="コンテンツ", blank=True)
    
    class Meta:
        verbose_name = "セミナー"
        verbose_name_plural = "「セミナー」 一覧"
        
        ordering = ['id']

    def __str__(self):
        return self.title
    
# レクチャーモデル
# class Lecture(models.Model):
    
#     uuid = models.UUIDField(default=uuid.uuid4,unique=True, editable=False, verbose_name="UUID")
    
#     seminar = models.ForeignKey(Seminar, on_delete=models.CASCADE, verbose_name="セミナー")
#     title = models.CharField(max_length=200,verbose_name="レクチャー名")
#     content = MarkdownxField(verbose_name="コンテンツ")

#     class Meta:
#         verbose_name = "レクチャー"
#         verbose_name_plural = "「レクチャー」 一覧"
        
#         ordering = ['id']
        
#     def __str__(self):
#         return self.title
    
# 参加者モデル
class Members(models.Model):
    
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, verbose_name="UUID")

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="ユーザー")
    
    seminar = models.ForeignKey(Seminar, on_delete=models.CASCADE, verbose_name="セミナー")
    
    def full_name(self):
        return f"{self.user.last_name} {self.user.first_name}"
    full_name.short_description = "名前"

    class Meta:
        verbose_name = "参加者"
        verbose_name_plural = "「参加者」 一覧"
        
        constraints = [
            models.UniqueConstraint(fields=['user', 'seminar'], name='unique_member_per_seminar')
        ]
        
        ordering = ['user__username']
        
    # 保存時にスタッフユーザーやスーパーユーザーを除外
    def save(self, *args, **kwargs):
        if self.user.is_staff or self.user.is_superuser:
            raise ValueError("Staff users and superusers cannot be added as seminar members.")
        super().save(*args, **kwargs)
        
    def __str__(self):
        return self.user.username
    
def get_seminar_file_path(instance, filename):
    """
    セミナーファイルの保存パスを生成する関数
    Args:
        instance (_type_): _description_
        filename (_type_): _description_

    Returns:
        _type_: _description_
    """
    ext = os.path.splitext(filename)[1]
    return f'seminar_base2/files/{instance.uuid}{ext}'

# ファイルモデル
class File(models.Model):
    
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, verbose_name="UUID")
    
    name = models.CharField(max_length=255, verbose_name="ファイル名")
    seminar = models.ForeignKey(Seminar, on_delete=models.CASCADE, verbose_name="セミナー")
    file = models.FileField(upload_to=get_seminar_file_path, verbose_name="ファイル")

    class Meta:
        verbose_name = "ファイル"
        verbose_name_plural = "「ファイル」 一覧"
        
        ordering = ['id']
        
    def __str__(self):
        return self.name
