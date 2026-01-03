"""
图片处理工具测试

测试ImageProcessor的图片处理功能：
- 图片尺寸调整
- 图片压缩
- 图片格式验证
"""
import pytest
from PIL import Image
import io

from app.utils.image_processor import ImageProcessor


@pytest.mark.unit
def test_process_image_resize():
    """
    测试图片尺寸调整

    Given: 一张大尺寸图片（1200x800）
    When: 使用process_uploaded_image处理，max_width=800
    Then: 图片应该被等比例缩小到800x533
    """
    # Arrange - 创建一个1200x800的测试图片
    original_img = Image.new('RGB', (1200, 800), color='red')
    img_bytes = io.BytesIO()
    original_img.save(img_bytes, format='JPEG')
    img_data = img_bytes.getvalue()

    # Act - 处理图片
    processor = ImageProcessor()
    processed_data, ext = processor.process_uploaded_image(img_data, max_width=800)

    # Assert
    processed_img = Image.open(io.BytesIO(processed_data))
    assert processed_img.width == 800
    assert processed_img.height == 533  # 800 * (800/1200)
    assert ext == '.jpg'


@pytest.mark.unit
def test_process_image_compression():
    """
    测试图片压缩

    Given: 一张高质量图片
    When: 使用process_uploaded_image处理，quality=70
    Then: 处理后的图片应该比原图小
    """
    # Arrange - 创建测试图片
    original_img = Image.new('RGB', (1000, 1000), color='blue')
    img_bytes = io.BytesIO()
    original_img.save(img_bytes, format='JPEG', quality=100)
    img_data = img_bytes.getvalue()
    original_size = len(img_data)

    # Act - 压缩图片
    processor = ImageProcessor()
    processed_data, _ = processor.process_uploaded_image(img_data, quality=70)
    processed_size = len(processed_data)

    # Assert - 压缩后应该更小
    assert processed_size < original_size


@pytest.mark.unit
def test_validate_image_type():
    """
    测试图片格式验证

    Given: 不同格式的图片数据
    When: 调用get_image_format
    Then: 应该正确识别图片格式
    """
    # Arrange - 创建JPEG图片
    jpeg_img = Image.new('RGB', (100, 100), color='red')
    jpeg_bytes = io.BytesIO()
    jpeg_img.save(jpeg_bytes, format='JPEG')
    jpeg_data = jpeg_bytes.getvalue()

    # 创建PNG图片
    png_img = Image.new('RGB', (100, 100), color='blue')
    png_bytes = io.BytesIO()
    png_img.save(png_bytes, format='PNG')
    png_data = png_bytes.getvalue()

    # Act & Assert
    processor = ImageProcessor()
    assert processor.get_image_format(jpeg_data) == 'jpeg'
    assert processor.get_image_format(png_data) == 'png'


@pytest.mark.unit
def test_validate_image_size():
    """
    测试图片大小验证

    Given: 不同大小的图片数据
    When: 调用validate_image
    Then: 应该正确验证图片大小
    """
    # Arrange - 创建1MB的图片数据
    small_img = Image.new('RGB', (100, 100), color='red')
    img_bytes = io.BytesIO()
    small_img.save(img_bytes, format='JPEG')
    small_data = img_bytes.getvalue()

    # Act & Assert - 小于5MB应该通过
    processor = ImageProcessor()
    assert processor.validate_image(small_data, max_size=5 * 1024 * 1024) is True

    # 大于限制应该失败
    assert processor.validate_image(small_data, max_size=100) is False


@pytest.mark.unit
def test_process_rgba_image():
    """
    测试RGBA图片处理

    Given: 一张RGBA透明图片
    When: 使用process_uploaded_image处理
    Then: 应该被转换为JPEG格式（丢失透明通道）
    """
    # Arrange - 创建RGBA图片
    original_img = Image.new('RGBA', (500, 500), color=(255, 0, 0, 128))
    img_bytes = io.BytesIO()
    original_img.save(img_bytes, format='PNG')
    img_data = img_bytes.getvalue()

    # Act
    processor = ImageProcessor()
    processed_data, ext = processor.process_uploaded_image(img_data)

    # Assert
    processed_img = Image.open(io.BytesIO(processed_data))
    assert processed_img.mode == 'RGB'  # 应该被转换为RGB
    assert ext == '.jpg'


@pytest.mark.unit
def test_process_image_without_resize():
    """
    测试不需要调整尺寸的图片

    Given: 一张600像素宽的图片
    When: 使用process_uploaded_image处理，max_width=800
    Then: 图片不应该被调整尺寸
    """
    # Arrange - 创建600x400的图片
    original_img = Image.new('RGB', (600, 400), color='green')
    img_bytes = io.BytesIO()
    original_img.save(img_bytes, format='JPEG')
    img_data = img_bytes.getvalue()

    # Act
    processor = ImageProcessor()
    processed_data, _ = processor.process_uploaded_image(img_data, max_width=800)

    # Assert
    processed_img = Image.open(io.BytesIO(processed_data))
    assert processed_img.width == 600  # 不应该调整
    assert processed_img.height == 400
