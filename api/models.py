from django.db import models
from django.utils import timezone
from datetime import timedelta
# Create your models here.

#협회소개-인삿말
class Association_greeting(models.Model):
    title = models.TextField(null=True, default='제목을 입력해주세요')
    content = models.TextField(null=True, default='내용을 입력해주세요')
    name = models.CharField(max_length=10, default='이름을 입력해주세요')

    def __str__(self):
        return self.name
#협회소개 - 연혁

#연혁 - 연도
class Association_history_year(models.Model):
    year = models.TextField(null=False, default='2026')

    def __str__(self):
        return self.year
#연혁 - 연도+월+subscript sub_table
class Association_history_month(models.Model):
    month = models.TextField(null=False, default='2026.04')
    content = models.TextField(null=False, default='내용')
    img = models.ImageField(upload_to='history_img', null=True)

    def __str__(self):
        return self.content

#협회 소식
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
    def __str__(self):
        return self.title

#협회 소식 -- 내용
class News_content(models.Model):
    BLOCK_TYPES = (
        ('text', 'Text'),
        ('image', 'Image'),
        # ('video', 'Video'), 등 추가 가능
    )
    news = models.ForeignKey(News, related_name='blocks', on_delete=models.CASCADE)
    block_type = models.CharField(max_length=10, choices=BLOCK_TYPES)
    content = models.TextField()  # 텍스트일 경우 내용, 이미지일 경우 이미지 URL 혹은 관련 정보
    order = models.IntegerField(default=0)

#주요 사업( ex -- 국제꽃장식대회, 꽃생활화, 고양꽃박람회, 농업박람회, 양재플라워페스타)
class Industry(models.Model):
    title = models.CharField(max_length=252, default='국제꽃장식대회')
    sub_title = models.TextField(null=True, default='글로벌 플로리스트 주요사업')
    content = models.TextField(null=True)

    def __str__(self):
        return self.title

#주요사업 - 국제꽃장식대회 - content
class Internationer_flower_content(models.Model):
    title = models.CharField(max_length=100, null=False, default='flower')
    content = models.TextField(null=True)
    img = models.ImageField(upload_to='Inter_flower')
    create_at = models.DateTimeField(auto_now_add=True)
    industry = models.ForeignKey(on_delete=models.CASCADE)

    def __str__(self):
        return self.title
