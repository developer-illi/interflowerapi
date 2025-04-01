# management/commands/update_article_categories.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from api.models import *

class Command(BaseCommand):
    help = '7일 지난 최근이슈를 보도자료로 전환합니다'

    def handle(self, *args, **kwargs):
        cutoff = timezone.now() - timedelta(days=7)
        outdated_articles = News.objects.filter(category='issue', created_at__lt=cutoff)
        count = outdated_articles.update(category='press')
        self.stdout.write(self.style.SUCCESS(f'{count}건의 기사 업데이트 완료'))