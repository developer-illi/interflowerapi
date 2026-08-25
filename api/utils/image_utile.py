from PIL import Image, ImageOps
from django.core.files.base import ContentFile
from rest_framework.exceptions import ValidationError
import io
import os
import uuid

# 첨부파일 정책 (공지사항 첨부 등에서 공용으로 사용)
ALLOWED_FILE_EXTENSIONS = {
    '.pdf', '.hwp', '.hwpx', '.doc', '.docx', '.xls', '.xlsx',
    '.ppt', '.pptx', '.zip', '.jpg', '.jpeg', '.png',
}
MAX_FILE_SIZE = 20 * 1024 * 1024  # 20MB


def resize_image(image_file, scale=0.5, quality=85):
    """이미지를 리사이즈해 ContentFile로 반환.

    예전 구현은 모든 예외를 삼키고 None을 반환했다. 그 결과 HEIC/알파 PNG 등
    Pillow가 JPEG로 저장하지 못하는 파일이 '이미지 없는 레코드'로 조용히 저장됐고,
    목록 직렬화에서 ImageField.url 접근 시 ValueError가 나 API 전체가 500이 됐다.
    (운영 DB api_local_content id=93 이 실제 사례)

    따라서 실패는 삼키지 않고 ValidationError(400)로 올린다.
    """
    if not image_file:
        return None

    try:
        img = Image.open(image_file)
    except Exception as exc:
        raise ValidationError(
            '이미지 파일을 열 수 없습니다. jpg 또는 png 형식으로 올려주세요. '
            '(아이폰 HEIC 사진은 지원하지 않습니다)'
        ) from exc

    try:
        img = ImageOps.exif_transpose(img)

        # RGBA/LA/P 모드는 JPEG로 저장할 수 없다. 흰 배경에 합성해 RGB로 변환.
        if img.mode in ('RGBA', 'LA', 'P'):
            img = img.convert('RGBA')
            background = Image.new('RGB', img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[-1])
            img = background
        elif img.mode != 'RGB':
            img = img.convert('RGB')

        new_width = max(1, int(img.size[0] * scale))
        new_height = max(1, int(img.size[1] * scale))
        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

        buffer = io.BytesIO()
        img.save(buffer, format='JPEG', quality=quality)
    except Exception as exc:
        raise ValidationError(f'이미지 처리에 실패했습니다: {exc}') from exc

    new_filename = generate_unique_filename(image_file.name, force_ext='.jpg')
    return ContentFile(buffer.getvalue(), name=new_filename)


def process_request_image(request, field='image'):
    """request에서 이미지 파일을 꺼내 리사이즈 처리 후 반환. 없으면 None.

    처리에 실패하면 None을 반환하지 않고 ValidationError(400)를 던진다.
    """
    image_file = request.FILES.get(field)
    return resize_image(image_file) if image_file else None


def generate_unique_filename(original_name, force_ext=None):
    ext = force_ext or os.path.splitext(original_name or '')[1]
    return f"{uuid.uuid4().hex}{ext}"


def validate_attachment(uploaded_file):
    """공지 첨부파일 확장자/용량 검증. 위반 시 ValidationError(400)."""
    ext = os.path.splitext(uploaded_file.name or '')[1].lower()
    if ext not in ALLOWED_FILE_EXTENSIONS:
        raise ValidationError(
            f"'{uploaded_file.name}' 은(는) 허용되지 않는 형식입니다. "
            f"허용 형식: {', '.join(sorted(ALLOWED_FILE_EXTENSIONS))}"
        )
    if uploaded_file.size > MAX_FILE_SIZE:
        raise ValidationError(
            f"'{uploaded_file.name}' 의 크기가 20MB를 초과합니다."
        )
    return uploaded_file
