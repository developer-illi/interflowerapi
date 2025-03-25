from django.db import models

# Create your models here.
class Greeting(models.Model):
    title = models.TextField(null=True, default='제목을 입력해주세요')
    content = models.TextField(null=True, default='내용을 입력해주세요')
    name = models.CharField(max_length=10, default='이름을 입력해주세요')

