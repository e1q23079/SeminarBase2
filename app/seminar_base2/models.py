import uuid
from django.db import models
from markdownx.models import MarkdownxField

# Create your models here.

# セミナーモデル
class Seminar(models.Model):
    
    uuid = models.UUIDField(default=uuid.uuid4,unique=True, editable=False, verbose_name="UUID")
    
    title = models.CharField(max_length=200,verbose_name="セミナー名")
    description = models.TextField(verbose_name="詳細")
    
    class Meta:
        verbose_name = "セミナー"
        verbose_name_plural = "「セミナー」 一覧"
        
        ordering = ['id']

    def __str__(self):
        return self.title
    
# レクチャーモデル
class Lecture(models.Model):
    
    uuid = models.UUIDField(default=uuid.uuid4,unique=True, editable=False, verbose_name="UUID")
    
    seminar = models.ForeignKey(Seminar, on_delete=models.CASCADE, verbose_name="セミナー")
    title = models.CharField(max_length=200,verbose_name="レクチャー名")
    content = MarkdownxField(verbose_name="コンテンツ")

    class Meta:
        verbose_name = "レクチャー"
        verbose_name_plural = "「レクチャー」 一覧"
        
        ordering = ['id']
        
    def __str__(self):
        return self.title