from django.db import models
from django.utils import timezone
from datetime import timedelta
# Create your models here.
class Greeting(models.Model):
    title = models.TextField(null=True, default='제목을 입력해주세요')
    content = models.TextField(null=True, default='내용을 입력해주세요')
    name = models.CharField(max_length=10, default='이름을 입력해주세요')

    def __str__(self):
        return self.name


class News(models.Model):
    CATEGORY_CHOICES = [
        ('issue', '최근 이슈'),
        ('press', '보도자료'),
    ]

    title = models.TextField(null=True, default="공지 제목을 입력하세요")
    type = models.IntegerField(null=True, default=1)  # 1 = 국제꽃예술인협회, 2 = 언론보도
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES, default='최근이슈')

    def update_category(self):
        if timezone.now() - self.created_at > timedelta(days=7):
            self.category = 'press'
            self.save()