"""국외전시(Overseas) 탭 병합.

    # 미리보기 (기본값: 아무것도 바꾸지 않음)
    python manage.py merge_overseas --source 10 --target 9 --title BUGA

    # 실제 적용
    python manage.py merge_overseas --source 10 --target 9 --title BUGA --apply

R2 객체는 건드리지 않는다. 자식 레코드의 FK 만 옮기므로 이미지 URL 이 그대로 유지된다.
"""
import json
import os
from datetime import datetime

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from api.models import Overseas, Overseas_content


class Command(BaseCommand):
    help = '국외전시 탭 두 개를 하나로 병합한다 (자식 이미지 레코드 이관 후 원본 삭제)'

    def add_arguments(self, parser):
        parser.add_argument('--source', type=int, required=True, help='없어질 쪽 Overseas id')
        parser.add_argument('--target', type=int, required=True, help='남을 쪽 Overseas id')
        parser.add_argument('--title', type=str, default=None, help='병합 후 target 의 title/sub_title')
        parser.add_argument('--backup-dir', type=str, default='backups')
        parser.add_argument('--apply', action='store_true', help='실제로 적용 (없으면 드라이런)')

    def handle(self, *args, **opts):
        source_id, target_id = opts['source'], opts['target']
        if source_id == target_id:
            raise CommandError('source 와 target 이 같습니다.')

        try:
            source = Overseas.objects.get(id=source_id)
            target = Overseas.objects.get(id=target_id)
        except Overseas.DoesNotExist as exc:
            raise CommandError(f'Overseas 레코드를 찾을 수 없습니다: {exc}')

        source_children = list(Overseas_content.objects.filter(overseas=source))
        target_children = list(Overseas_content.objects.filter(overseas=target))

        self.stdout.write('')
        self.stdout.write(f'  source  id={source.id} title={source.title!r} 사진 {len(source_children)}건')
        self.stdout.write(f'  target  id={target.id} title={target.title!r} 사진 {len(target_children)}건')
        self.stdout.write(f'  병합 후 title={opts["title"] or target.title!r} 사진 '
                          f'{len(source_children) + len(target_children)}건')
        self.stdout.write('')

        # --- 백업 ---
        backup = {
            'created_at': datetime.now().isoformat(),
            'source': {'id': source.id, 'title': source.title, 'sub_title': source.sub_title,
                       'content': source.content, 'headerImage': str(source.headerImage)},
            'target': {'id': target.id, 'title': target.title, 'sub_title': target.sub_title,
                       'content': target.content, 'headerImage': str(target.headerImage)},
            'children': [
                {'id': ch.id, 'overseas_id': ch.overseas_id, 'title': ch.title,
                 'date': ch.date.isoformat() if ch.date else None,
                 'description': ch.description, 'image': str(ch.image)}
                for ch in source_children + target_children
            ],
        }
        os.makedirs(opts['backup_dir'], exist_ok=True)
        stamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = os.path.join(opts['backup_dir'],
                                   f'overseas_merge_{source_id}_into_{target_id}_{stamp}.json')
        with open(backup_path, 'w', encoding='utf-8') as fp:
            json.dump(backup, fp, ensure_ascii=False, indent=2)
        self.stdout.write(self.style.SUCCESS(f'  백업 저장: {backup_path}'))

        if not opts['apply']:
            self.stdout.write(self.style.WARNING(
                '\n  드라이런입니다. 실제 적용하려면 --apply 를 붙이세요.\n'))
            return

        with transaction.atomic():
            moved = Overseas_content.objects.filter(overseas=source).update(overseas=target)

            # 이관이 끝난 뒤에만 삭제한다. (CASCADE 로 사진이 날아가는 것 방지)
            remaining = Overseas_content.objects.filter(overseas=source).count()
            if remaining:
                raise CommandError(f'이관되지 않은 자식 {remaining}건이 남아 삭제를 중단합니다.')

            if opts['title']:
                target.title = opts['title']
                target.sub_title = opts['title']
                target.save(update_fields=['title', 'sub_title'])

            source.delete()

        total = Overseas_content.objects.filter(overseas=target).count()
        self.stdout.write(self.style.SUCCESS(
            f'\n  완료: {moved}건 이관, target id={target.id} title={target.title!r} 사진 {total}건\n'))
