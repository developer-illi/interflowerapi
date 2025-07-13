from PIL import Image, ImageOps
from django.core.files.base import ContentFile
import io
import os
import uuid

def resize_image(image_file, scale=0.5, quality=85):
    try:
        img = Image.open(image_file)

        # EXIF 회전 정보 자동 적용
        img = ImageOps.exif_transpose(img)

        # 새로운 사이즈 계산 (scale 기준)
        new_width = int(img.size[0] * scale)
        new_height = int(img.size[1] * scale)
        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

        print('--------')
        print(new_width)
        print(new_height)
        print('--------')

        # 이미지 저장용 버퍼
        buffer = io.BytesIO()
        img.save(buffer, format='JPEG', quality=quality)

        # 고유 파일명 생성
        new_filename = generate_unique_filename(image_file.name)

        # ContentFile 생성 시 name 지정
        resized_file = ContentFile(buffer.getvalue(), name=new_filename)

        return resized_file

    except Exception as e:
        print(e)
        return None
# def resize_image(image_file, width, quality):
#     try:
#         img = Image.open(image_file)
#
#         # EXIF 회전 정보 자동 적용
#         img = ImageOps.exif_transpose(img)
#
#         # 비율 유지하며 리사이즈
#         w_percent = (width / float(img.size[0]))
#         h_size = int((float(img.size[1]) * float(w_percent)))
#         img = img.resize((width, h_size), Image.Resampling.LANCZOS)
#         print('--------')
#         print(width)
#         print(h_size)
#         print('--------')
#         # 이미지 저장용 버퍼
#         buffer = io.BytesIO()
#         img.save(buffer, format='JPEG', quality=quality)
#
#         # 고유 파일명 생성
#         new_filename = generate_unique_filename(image_file.name)
#
#         # ContentFile 생성 시 name 지정
#         resized_file = ContentFile(buffer.getvalue(), name=new_filename)
#
#         return resized_file
#
#     except Exception as e:
#         print(e)
#         return None

def generate_unique_filename(original_name):
    """UUID 기반 고유 파일명 생성"""
    ext = os.path.splitext(original_name)[1]
    return f"{uuid.uuid4().hex}{ext}"