"""공지 삭제 (중복 정리용). 첨부파일 R2 객체까지 함께 정리한다.

    python manage.py delete_notices --ids 2 3 4            # 미리보기
    python manage.py delete_notices --ids 2 3 4 --apply    # 실제 삭제
"""
import json
import os
from datetime import datetime

from django.core.management.base import BaseCommand
from django.db import transaction

from api.models import Notice


class Command(BaseCommand):
    help = '지정한 id 의 공지를 삭제한다 (기본은 드라이런)'

    def add_arguments(self, parser):
        parser.add_argument('--ids', type=int, nargs='+', required=True)
        parser.add_argument('--backup-dir', type=str, default='backups')
        parser.add_argument('--apply', action='store_true')

    def handle(self, *args, **opts):
        notices = list(Notice.objects.filter(id__in=opts['ids']))
        found = {n.id for n in notices}
        missing = set(opts['ids']) - found

        self.stdout.write('')
        for n in notices:
            content = getattr(n, 'notice_content', None)
            self.stdout.write(f'  삭제 대상 id={n.id} date={n.date:%Y-%m-%d %H:%M} '
                              f'title={n.title[:40]!r} 첨부 {n.attachments.count()}건 '
                              f'본문 {len(content.content) if content else 0}자')
        if missing:
            self.stdout.write(self.style.WARNING(f'  존재하지 않는 id: {sorted(missing)}'))
        if not notices:
            return

        backup = []
        for n in notices:
            content = getattr(n, 'notice_content', None)
            backup.append({
                'id': n.id, 'title': n.title, 'date': n.date.isoformat(),
                'content': content.content if content else None,
                'attachments': [{'id': a.id, 'name': a.name, 'file': str(a.file), 'size': a.size}
                                for a in n.attachments.all()],
            })
        os.makedirs(opts['backup_dir'], exist_ok=True)
        stamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = os.path.join(opts['backup_dir'], f'notices_deleted_{stamp}.json')
        with open(backup_path, 'w', encoding='utf-8') as fp:
            json.dump(backup, fp, ensure_ascii=False, indent=2)
        self.stdout.write(self.style.SUCCESS(f'  백업 저장: {backup_path}'))

        if not opts['apply']:
            self.stdout.write(self.style.WARNING(
                '\n  드라이런입니다. 실제 삭제하려면 --apply 를 붙이세요.\n'))
            return

        with transaction.atomic():
            for n in notices:
                for attachment in n.attachments.all():
                    if attachment.file:
                        attachment.file.delete(save=False)
                n.delete()

        self.stdout.write(self.style.SUCCESS(f'\n  {len(notices)}건 삭제 완료\n'))
