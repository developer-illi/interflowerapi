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

#연혁 - 연도 -- 묶어야 한다라..

class History_set_up(models.Model): #묶는 작업 중
    dis_type = models.TextField(default='history', null=True)
    title = models.TextField(default='2025', null=False)

    def __str__(self):
        return self.title
class History_content(models.Model):
    date = models.TextField(null=False)
    history = models.ForeignKey(History_set_up, on_delete=models.CASCADE)

    def __str__(self):
        return self.date
class History_event(models.Model):
    content = models.TextField(null=True, default='content add')
    img = models.ImageField(upload_to='history_img', null=True)
    history_content = models.ForeignKey(History_content, on_delete=models.CASCADE)

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

#주요 사업
class Local(models.Model):#국내전시
    title = models.CharField(max_length=252, default='국내전시')
    sub_title = models.TextField(null=True, default='글로벌 플로리스트 주요사업')
    content = models.TextField(null=True)
    img = models.ImageField(upload_to='Local', null=True)

    def __str__(self):
        return self.title

#주요사업 - 국제꽃장식대회 - content
class Local_content(models.Model):#국내전시 - sub_content
    title = models.CharField(max_length=100, null=False, default='flower')
    content = models.TextField(null=True)
    img = models.ImageField(upload_to='Local_sub_content', null=True)
    create_at = models.DateTimeField(auto_now_add=True)
    local = models.ForeignKey(Local, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

#주요산업 -- 국외전시
class Overseas(models.Model):#국외전시
    title = models.CharField(max_length=252, default='국외전시')
    sub_title = models.TextField(null=True, default='글로벌 플로리스트 주요사업')
    content = models.TextField(null=True)
    img = models.ImageField(upload_to='Overseas', null=True)

    def __str__(self):
        return self.title

#주요산업 - 국외전시 - subcontent
class Overseas_content(models.Model):#국외전시 - sub_content
    title = models.CharField(max_length=100, null=False, default='flower')
    content = models.TextField(null=True)
    img = models.ImageField(upload_to='Overseas_sub_content', null=True)
    create_at = models.DateTimeField(auto_now_add=True)
    overseas = models.ForeignKey(Overseas ,on_delete=models.CASCADE)

    def __str__(self):
        return self.title

#주요산업 - 자격증
class License(models.Model):
    title = models.CharField(max_length=252, default='국외전시')
    sub_title = models.TextField(null=True, default='글로벌 플로리스트 주요사업')
    content = models.TextField(null=True)
    img = models.ImageField(upload_to='Overseas', null=True)

    def __str__(self):
        return self.title

#주요산업 - 자격증 - 자격증content
class License_content(models.Model):#자격증
    title = models.CharField(max_length=200, null=False, default="자격증")
    content = models.TextField(null=True, default='content')
    img = models.ImageField(upload_to="License", null=True)
    license_script = models.TextField(null=True, default='content')
    link = models.TextField(null=True)

    def __str__(self):
        return self.title

#주요산업 - 대외활동
class Contests(models.Model):
    title = models.CharField(max_length=200, null=False, default='대외활동')
    sub_title = models.TextField(null=True)
    content = models.TextField(null=True, default='content')
    img = models.ImageField(upload_to='Contests', null=True)

    def __str__(self):
        return self.title

#주요사업 - 대외활동 - content
class Contests_content(models.Model):
    title = models.CharField(max_length=200, null=False, default='대외활동')
    upload_date = models.DateTimeField(auto_now=True)
    place = models.TextField(null=True)
    contests = models.ForeignKey(Contests, related_name='contest_title', on_delete=models.CASCADE)

#주요사업 - 대외활동 - content - 게시판
class Contests_Block(models.Model):
    BLOCK_TYPES = (
        ('text', 'Text'),
        ('image', 'Image'),
        ('video', 'Video'),
    )
    contests_content = models.ForeignKey(Contests_content, related_name='contests_block', on_delete=models.CASCADE)
    block_type = models.CharField(max_length=10, choices=BLOCK_TYPES)
    content = models.TextField()  # 텍스트 내용이거나, 이미지 URL, 동영상 링크 등
    order = models.IntegerField(default=0)  # 게시글 내 노출 순서

    def __str__(self):
        return self.content

#공지사항
class Notice(models.Model):
    title = models.CharField(max_length=200, null=False)
    upload_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        self.title

#공지사항 - 게시판내용
class Notice_content(models.Model):
    BLOCK_TYPES = (
        ('text', 'Text'),
        ('image', 'Image'),
        ('video', 'Video'),
    )
    notice = models.ForeignKey(Notice, related_name='notice_content', on_delete=models.CASCADE)
    block_type = models.CharField(max_length=10, choices=BLOCK_TYPES)
    content = models.TextField()  # 텍스트 내용이거나, 이미지 URL, 동영상 링크 등
    order = models.IntegerField(default=0)  # 게시글 내 노출 순서

    def __str__(self):
        return self.notice