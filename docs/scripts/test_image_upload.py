"""
测试图片上传API
"""
import asyncio
import requests
from pathlib import Path
import io

# 配置
BASE_URL = "http://localhost:8000"
# 需要先登录获取 token
ADMIN_TOKEN = "YOUR_ADMIN_TOKEN_HERE"


def create_test_image(size=(1920, 1080), color=(255, 0, 0)):
    """创建测试图片"""
    from PIL import Image
    img = Image.new('RGB', size, color)
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='JPEG')
    img_bytes.seek(0)
    return img_bytes


def test_upload_small_image():
    """测试上传小图片"""
    print("\n=== 测试1: 上传小图片 (<100KB) ===")
    img = create_test_image(size=(400, 300), color=(100, 150, 200))

    files = {'file': ('test_small.jpg', img, 'image/jpeg')}
    headers = {'Authorization': f'Bearer {ADMIN_TOKEN}'}

    response = requests.post(
        f"{BASE_URL}/admin/products/1/details/images/upload",
        files=files,
        headers=headers
    )

    print(f"状态码: {response.status_code}")
    print(f"响应: {response.json()}")


def test_upload_large_image():
    """测试上传大图片"""
    print("\n=== 测试2: 上传大图片 (>1MB) ===")
    img = create_test_image(size=(1920, 1080), color=(200, 100, 50))

    files = {'file': ('test_large.jpg', img, 'image/jpeg')}
    headers = {'Authorization': f'Bearer {ADMIN_TOKEN}'}

    response = requests.post(
        f"{BASE_URL}/admin/products/1/details/images/upload",
        files=files,
        headers=headers
    )

    print(f"状态码: {response.status_code}")
    print(f"响应: {response.json()}")
    data = response.json().get('data', {})
    if data:
        print(f"原始大小: {data.get('original_size')} bytes")
        print(f"压缩后: {data.get('size')} bytes")
        print(f"压缩率: {data.get('compression_ratio')}")


def test_upload_png():
    """测试上传PNG格式"""
    print("\n=== 测试3: 上传PNG格式图片 ===")
    from PIL import Image
    img = Image.new('RGBA', (800, 600), (255, 0, 0, 128))
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)

    files = {'file': ('test_png.png', img_bytes, 'image/png')}
    headers = {'Authorization': f'Bearer {ADMIN_TOKEN}'}

    response = requests.post(
        f"{BASE_URL}/admin/products/1/details/images/upload",
        files=files,
        headers=headers
    )

    print(f"状态码: {response.status_code}")
    print(f"响应: {response.json()}")


def test_upload_invalid_file():
    """测试上传非法文件"""
    print("\n=== 测试4: 上传非法文件 (PDF) ===")
    pdf_content = b"%PDF-1.4 fake pdf content"

    files = {'file': ('test.pdf', io.BytesIO(pdf_content), 'application/pdf')}
    headers = {'Authorization': f'Bearer {ADMIN_TOKEN}'}

    response = requests.post(
        f"{BASE_URL}/admin/products/1/details/images/upload",
        files=files,
        headers=headers
    )

    print(f"状态码: {response.status_code}")
    print(f"响应: {response.json()}")


def test_upload_oversized_file():
    """测试上传超大文件"""
    print("\n=== 测试5: 上传超大文件 (>5MB) ===")
    # 创建6MB的假图片
    large_data = b'x' * (6 * 1024 * 1024)

    files = {'file': ('huge.jpg', io.BytesIO(large_data), 'image/jpeg')}
    headers = {'Authorization': f'Bearer {ADMIN_TOKEN}'}

    response = requests.post(
        f"{BASE_URL}/admin/products/1/details/images/upload",
        files=files,
        headers=headers
    )

    print(f"状态码: {response.status_code}")
    print(f"响应: {response.json()}")


if __name__ == "__main__":
    print("开始测试图片上传API...")
    print(f"BASE_URL: {BASE_URL}")
    print("注意: 请先设置有效的 ADMIN_TOKEN")

    if ADMIN_TOKEN == "YOUR_ADMIN_TOKEN_HERE":
        print("\n警告: 请先设置有效的管理员 Token!")
        exit(1)

    try:
        test_upload_small_image()
        test_upload_large_image()
        test_upload_png()
        test_upload_invalid_file()
        test_upload_oversized_file()

        print("\n=== 测试完成 ===")
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()
