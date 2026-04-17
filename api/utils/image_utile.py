from PIL import Image, ImageOps
from django.core.files.base import ContentFile
import io
import os
import uuid


def resize_image(image_file, scale=0.5, quality=85):
    if not image_file:
        return None
    try:
        img = Image.open(image_file)
        img = ImageOps.exif_transpose(img)

        new_width = int(img.size[0] * scale)
        new_height = int(img.size[1] * scale)
        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

        buffer = io.BytesIO()
        img.save(buffer, format='JPEG', quality=quality)

        new_filename = generate_unique_filename(image_file.name)
        return ContentFile(buffer.getvalue(), name=new_filename)

    except Exception:
        return None


def process_request_image(request, field='image'):
    """request에서 이미지 파일을 꺼내 리사이즈 처리 후 반환. 없으면 None."""
    image_file = request.FILES.get(field)
    return resize_image(image_file) if image_file else None


def generate_unique_filename(original_name):
    ext = os.path.splitext(original_name)[1]
    return f"{uuid.uuid4().hex}{ext}"
