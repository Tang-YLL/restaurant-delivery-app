"""
图片处理工具类
提供图片上传、压缩、调整尺寸等功能
"""
from PIL import Image
import io
from pathlib import Path
from typing import Tuple
import uuid


class ImageProcessor:
    """图片处理工具类"""

    @staticmethod
    def process_uploaded_image(
        image_data: bytes,
        max_width: int = 800,
        quality: int = 85
    ) -> Tuple[bytes, str]:
        """
        处理上传的图片：调整尺寸、压缩、转JPEG

        Args:
            image_data: 原始图片数据
            max_width: 最大宽度（保持宽高比）
            quality: JPEG压缩质量（1-100）

        Returns:
            (处理后的图片数据, 文件扩展名)
        """
        img = Image.open(io.BytesIO(image_data))

        # 调整尺寸（保持宽高比）
        if img.width > max_width:
            ratio = max_width / img.width
            new_size = (int(img.width * ratio), int(img.height * ratio))
            img = img.resize(new_size, Image.LANCZOS)

        # 转换为RGB（处理RGBA）
        if img.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
            img = background

        # 压缩为JPEG
        output = io.BytesIO()
        img.save(output, format='JPEG', quality=quality, optimize=True)
        return output.getvalue(), '.jpg'

    @staticmethod
    def validate_image(image_data: bytes, max_size: int = 5 * 1024 * 1024) -> bool:
        """
        验证图片大小

        Args:
            image_data: 图片数据
            max_size: 最大文件大小（字节），默认5MB

        Returns:
            是否符合大小要求
        """
        return len(image_data) <= max_size

    @staticmethod
    def get_image_format(image_data: bytes) -> str:
        """
        获取图片格式

        Args:
            image_data: 图片数据

        Returns:
            图片格式（jpeg、png等）
        """
        try:
            img = Image.open(io.BytesIO(image_data))
            return img.format.lower() if img.format else 'unknown'
        except:
            return 'unknown'
