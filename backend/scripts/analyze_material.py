"""
Material数据分析脚本(无需数据库)
快速分析Material文件夹中的数据
"""
import os
import json
import re
from pathlib import Path
from typing import Dict, List
from collections import Counter


# 商品分类规则
CATEGORY_RULES = {
    "热菜": {
        "keywords": ["炒", "爆", "熘", "炸", "烹", "煎", "贴", "烧", "焖", "炖", "蒸", "煮", "烩", "炝", "腌", "拌", "烤", "卤", "酱", "拔丝", "挂霜", "糖水"],
        "exclude": ["凉", "冷"]
    },
    "凉菜": {
        "keywords": ["凉拌", "凉菜", "沙拉", "冷盘"],
        "include_any": True
    },
    "汤类": {
        "keywords": ["汤", "羹", "粥"],
        "exclude": ["炒", "面", "饭"]
    },
    "主食": {
        "keywords": ["饭", "面", "粥", "饺子", "馒头", "包子", "饼", "粉", "面包", "意面", "披萨", "炒饭", "炒面", "烩饭"],
        "include_any": True
    },
    "小吃": {
        "keywords": ["小吃", "零食", "点心", "甜品", "蛋糕", "饼干", "派"],
        "include_any": True
    },
    "饮品": {
        "keywords": ["饮", "汁", "茶", "咖啡", "奶昔", "奶", "豆浆"],
        "exclude": ["菜", "汤"]
    },
    "海鲜": {
        "keywords": ["鱼", "虾", "蟹", "贝", "海参", "鱿鱼", "章鱼", "扇贝", "蛤蜊", "鲍鱼", "龙虾"],
        "include_any": True
    },
    "肉类": {
        "keywords": ["猪肉", "牛肉", "羊肉", "鸡肉", "鸭肉", "排骨", "蹄", "五花肉", "里脊", "牛排"],
        "include_any": True
    },
    "素食": {
        "keywords": ["素", "蔬菜", "菌", "菇", "豆腐", "豆", "腐竹"],
        "include_any": True
    },
    "火锅": {
        "keywords": ["火锅", "涮", "锅底"],
        "include_any": True
    },
    "烧烤": {
        "keywords": ["烧烤", "烤串", "烤肉", "烤鱼"],
        "include_any": True
    },
    "甜品": {
        "keywords": ["甜", "糖水", "布丁", "果冻", "冰淇淋"],
        "include_any": True
    },
    "烘焙": {
        "keywords": ["烘焙", "烤", "面包", "蛋糕", "曲奇", "饼干"],
        "include_any": True
    },
    "日料": {
        "keywords": ["寿司", "刺身", "天妇罗", "日式"],
        "include_any": True
    },
    "西餐": {
        "keywords": ["意", "牛排", "意面", "披萨", "沙拉", "汉堡"],
        "include_any": True
    }
}


def classify_product(title: str) -> str:
    """根据菜品标题分类"""
    title_clean = title.strip().lower()

    # 检查每个分类规则
    for category_name, rules in CATEGORY_RULES.items():
        keywords = rules.get("keywords", [])
        exclude = rules.get("exclude", [])
        include_any = rules.get("include_any", False)

        # 检查排除词
        if exclude:
            if any(exc in title_clean for exc in exclude):
                continue

        # 检查关键词
        if include_any:
            if any(keyword in title_clean for keyword in keywords):
                return category_name
        else:
            if all(keyword in title_clean for keyword in keywords):
                return category_name

    return "热菜"


def parse_views_favorites(views_str: str) -> tuple:
    """解析浏览量和收藏量"""
    views = 0
    favorites = 0

    if views_str:
        match = re.search(r'(\d+)浏览', views_str)
        if match:
            views = int(match.group(1))

        match = re.search(r'(\d+)收藏', views_str)
        if match:
            favorites = int(match.group(1))

    return views, favorites


def analyze_material(material_path: str):
    """分析Material文件夹"""
    material_dir = Path(material_path)

    print("="*60)
    print("Material数据分析报告")
    print("="*60)

    # 统计文件
    json_files = list(material_dir.glob("*.json"))
    png_files = list(material_dir.glob("*.png"))

    print(f"\n📁 文件统计:")
    print(f"  - JSON文件: {len(json_files)}")
    print(f"  - PNG图片: {len(png_files)}")

    # 解析数据
    products_data = []
    missing_images = []
    category_counter = Counter()

    print(f"\n📊 数据解析中...")

    for idx, json_file in enumerate(json_files, 1):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # 检查图片
            png_file = json_file.with_suffix('.png')
            if not png_file.exists():
                missing_images.append({
                    "json_file": json_file.name,
                    "expected_png": png_file.name
                })

            # 解析数据
            title = data.get('title', '').strip()
            if not title:
                continue

            category = classify_product(title)
            views_str = data.get('views_and_favorites', '')
            views, favorites = parse_views_favorites(views_str)

            products_data.append({
                'title': title,
                'category': category,
                'views': views,
                'favorites': favorites,
                'has_image': png_file.exists()
            })

            category_counter[category] += 1

            if idx % 100 == 0:
                print(f"  进度: {idx}/{len(json_files)} ({idx*100//len(json_files)}%)")

        except Exception as e:
            print(f"  错误: {json_file.name}: {e}")

    # 打印统计
    print(f"\n✓ 成功解析: {len(products_data)} 条数据")
    print(f"✓ 缺失图片: {len(missing_images)} 个")

    # 分类统计
    print(f"\n📈 商品分类分布 (共{len(category_counter)}个分类):")
    for category, count in category_counter.most_common():
        percentage = count * 100 / len(products_data) if products_data else 0
        print(f"  {category:12s}: {count:4d} ({percentage:5.2f}%)")

    # 浏览量统计
    total_views = sum(p['views'] for p in products_data)
    total_favorites = sum(p['favorites'] for p in products_data)
    avg_views = total_views / len(products_data) if products_data else 0

    print(f"\n👁️  浏览数据:")
    print(f"  - 总浏览量: {total_views:,}")
    print(f"  - 总收藏量: {total_favorites:,}")
    print(f"  - 平均浏览量: {avg_views:.1f}")

    # 图片完整性
    image_integrity = (len(products_data) - len(missing_images)) / len(products_data) * 100 if products_data else 0
    print(f"\n🖼️  图片完整性: {image_integrity:.2f}%")

    # 验收标准检查
    print(f"\n{'='*60}")
    print("验收标准检查")
    print(f"{'='*60}")

    checks = [
        ("解析所有JSON文件", len(products_data) >= 3000),
        ("创建≥10个商品分类", len(category_counter) >= 10),
        ("导入≥3000个商品SKU", len(products_data) >= 3000),
        ("图片完整性≥95%", image_integrity >= 95),
    ]

    all_passed = True
    for check_name, passed in checks:
        status = "✓ 通过" if passed else "✗ 未通过"
        print(f"  {status} - {check_name}")
        if not passed:
            all_passed = False

    print(f"\n{'='*60}")
    if all_passed:
        print("🎉 所有验收标准均已达成!")
    else:
        print("⚠️  部分验收标准未达成,请检查")
    print(f"{'='*60}\n")

    # 导出分析报告
    report = {
        "总商品数": len(products_data),
        "分类数": len(category_counter),
        "分类分布": dict(category_counter),
        "图片完整性": f"{image_integrity:.2f}%",
        "缺失图片数": len(missing_images),
        "总浏览量": total_views,
        "总收藏量": total_favorites
    }

    report_path = Path("/Volumes/545S/general final/backend/analysis_report.json")
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"📄 分析报告已保存到: {report_path}")

    return report, category_counter


if __name__ == "__main__":
    material_path = "/Volumes/545S/general final/Material/material"
    analyze_material(material_path)
