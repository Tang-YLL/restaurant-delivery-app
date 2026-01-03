"""
从Material目录复制商品图片并更新商品数据
"""
import os
import shutil
import glob
from pathlib import Path

# 源目录和目标目录
MATERIAL_DIR = "/Volumes/545S/general final/Material/material"
TARGET_DIR = "/Volumes/545S/general final/backend/public/images/products"

# 商品与图片的匹配关系
PRODUCT_IMAGE_MAPPING = {
    "青椒炒肉": ["青椒炒肉", "尖椒牛肉"],
    "红烧肉": ["鲍鱼红烧肉", "红烧肉"],
    "鱼香肉丝": ["鱼香"],
    "宫保鸡丁": ["宫保鸡丁"],
    "蛋炒饭": ["蛋炒饭"],
    "白米饭": ["白米饭"],
    "扬州炒饭": ["扬州炒饭", "菠萝炒饭", "彩椒炒饭", "炒饭"],
    "紫菜蛋花汤": ["紫菜.*蛋", "紫菜", "蛋花汤"],
    "酸梅汤": ["酸梅.*汤", "酸梅", "梅子汤", "绿豆.*汤", "紫菜.*蛋"],  # 如果找不到，用绿豆汤或紫菜蛋花汤替代
    "番茄鸡蛋汤": ["番茄.*蛋.*汤", "番茄.*汤", "番茄蛋"],
    "冬瓜排骨汤": ["冬瓜.*排骨汤", "冬瓜.*汤"],
    "鲜榨橙汁": ["橙.*汁", "鲜榨.*橙", "橙"],
    "冰镇酸梅汤": ["冰镇.*酸梅", "酸梅.*汤", "酸梅", "绿豆.*汤", "冬瓜.*汤"],  # 如果找不到，用绿豆汤或冬瓜汤替代
    "柠檬蜂蜜茶": ["柠檬.*蜂蜜茶", "柠檬.*茶", "柠檬"],
    "绿豆汤": ["绿豆.*汤", "绿豆"],
    "拍黄瓜": ["凉拌.*黄瓜", "黄瓜"],
    "糖醋排骨": ["糖醋.*排骨", "糖醋.*排"],
    "红豆沙": ["红豆"],
    "水果沙拉": ["水果.*沙拉", "水果"],
    "银耳莲子汤": ["银耳.*莲子", "银耳"],
}


def find_image_for_product(product_name):
    """为商品查找匹配的图片"""
    if product_name not in PRODUCT_IMAGE_MAPPING:
        print(f"  ⚠️  商品 '{product_name}' 没有配置图片映射")
        return None

    keywords = PRODUCT_IMAGE_MAPPING[product_name]

    # 搜索匹配的图片
    for keyword in keywords:
        # 使用正则表达式模式
        import re
        pattern = os.path.join(MATERIAL_DIR, f"{keyword}.png")

        # 遍历目录查找匹配的文件
        try:
            for filename in os.listdir(MATERIAL_DIR):
                if filename.endswith('.png') and re.search(keyword, filename, re.IGNORECASE):
                    image_path = os.path.join(MATERIAL_DIR, filename)
                    print(f"  ✓ '{product_name}' -> {filename}")
                    return image_path
        except Exception as e:
            continue

    print(f"  ⚠️  商品 '{product_name}' 未找到匹配图片")
    return None


def copy_images():
    """复制图片到目标目录"""
    print("=" * 80)
    print("从Material目录复制商品图片")
    print("=" * 80)

    # 确保目标目录存在
    os.makedirs(TARGET_DIR, exist_ok=True)

    # 清空目标目录（删除旧图片）
    print("\n清空目标目录...")
    old_files = glob.glob(os.path.join(TARGET_DIR, "*.png")) + glob.glob(os.path.join(TARGET_DIR, "*.jpg"))
    for old_file in old_files:
        os.remove(old_file)
    print(f"  删除了 {len(old_files)} 个旧文件")

    # 为每个商品复制图片
    print("\n复制商品图片:")
    print("-" * 80)

    copied_files = []
    for product_name in PRODUCT_IMAGE_MAPPING.keys():
        image_path = find_image_for_product(product_name)

        if image_path:
            # 生成新的文件名（保持原文件名）
            filename = os.path.basename(image_path)
            target_path = os.path.join(TARGET_DIR, filename)

            # 复制文件
            shutil.copy2(image_path, target_path)
            copied_files.append(filename)

    print("-" * 80)
    print(f"\n✅ 成功复制 {len(copied_files)} 张图片")

    # 生成交互式Python代码，输出图片映射
    print("\n商品图片映射:")
    print("-" * 80)
    image_mapping = {}
    for product_name in PRODUCT_IMAGE_MAPPING.keys():
        image_path = find_image_for_product(product_name)
        if image_path:
            filename = os.path.basename(image_path)
            image_mapping[product_name] = f"/images/products/{filename}"
            print(f"{product_name}: {filename}")

    return image_mapping


if __name__ == "__main__":
    print("\n开始复制商品图片...\n")
    image_mapping = copy_images()

    print("\n" + "=" * 80)
    print("复制完成！")
    print("=" * 80)
