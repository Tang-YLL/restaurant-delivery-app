"""
Material数据导入脚本
从Material文件夹导入菜品JSON数据到数据库
"""
import os
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.models import Base, Category, Product, ProductStatus
from app.core.config import get_settings

settings = get_settings()


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
    """
    根据菜品标题分类

    Args:
        title: 菜品标题

    Returns:
        分类名称
    """
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
            # 包含任一关键词即可
            if any(keyword in title_clean for keyword in keywords):
                return category_name
        else:
            # 默认包含所有关键词
            if all(keyword in title_clean for keyword in keywords):
                return category_name

    # 默认分类为"热菜"
    return "热菜"


def parse_views_favorites(views_str: str) -> Tuple[int, int]:
    """
    解析浏览量和收藏量字符串

    Args:
        views_str: 浏览量和收藏量字符串,如 "74434浏览"

    Returns:
        (views, favorites) 元组
    """
    views = 0
    favorites = 0

    if views_str:
        # 提取数字
        match = re.search(r'(\d+)浏览', views_str)
        if match:
            views = int(match.group(1))

        match = re.search(r'(\d+)收藏', views_str)
        if match:
            favorites = int(match.group(1))

    return views, favorites


def scan_material_files(material_path: str) -> List[Dict]:
    """
    扫描Material文件夹,解析所有JSON文件

    Args:
        material_path: Material文件夹路径

    Returns:
        解析后的菜品数据列表
    """
    material_dir = Path(material_path)
    products_data = []

    print(f"开始扫描目录: {material_path}")

    # 扫描所有JSON文件
    json_files = list(material_dir.glob("*.json"))
    total_files = len(json_files)

    print(f"找到 {total_files} 个JSON文件")

    for idx, json_file in enumerate(json_files, 1):
        try:
            # 读取JSON文件
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # 检查对应的图片文件
            png_file = json_file.with_suffix('.png')
            if not png_file.exists():
                print(f"警告: 图片文件不存在: {png_file.name}")
                continue

            # 解析数据
            title = data.get('title', '').strip()
            if not title:
                print(f"警告: 标题为空: {json_file.name}")
                continue

            # 分类
            category = classify_product(title)

            # 解析浏览量和收藏量
            views_str = data.get('views_and_favorites', '')
            views, favorites = parse_views_favorites(views_str)

            # 本地图片路径 (相对于material目录)
            local_image_path = f"/static/{png_file.name}"

            product_data = {
                'title': title,
                'detail_url': data.get('detail_url', ''),
                'image_url': data.get('image_url', ''),
                'local_image_path': local_image_path,
                'ingredients': data.get('ingredients', ''),
                'views': views,
                'favorites': favorites,
                'category': category,
                'json_file': str(json_file),
                'png_file': str(png_file)
            }

            products_data.append(product_data)

            if idx % 100 == 0:
                print(f"已处理: {idx}/{total_files} ({idx*100//total_files}%)")

        except json.JSONDecodeError as e:
            print(f"错误: JSON解析失败 {json_file.name}: {e}")
        except Exception as e:
            print(f"错误: 处理文件失败 {json_file.name}: {e}")

    print(f"解析完成,共 {len(products_data)} 条数据")
    return products_data


def import_categories(db: Session) -> Dict[str, Category]:
    """
    创建或获取商品分类

    Args:
        db: 数据库会话

    Returns:
        分类字典 {分类名称: Category对象}
    """
    categories_dict = {}

    # 定义分类
    categories_data = [
        {"name": "热菜", "code": "HOT_DISH", "description": "各类热菜菜品", "sort_order": 1},
        {"name": "凉菜", "code": "COLD_DISH", "description": "凉拌、冷盘等凉菜", "sort_order": 2},
        {"name": "汤类", "code": "SOUP", "description": "各类汤品", "sort_order": 3},
        {"name": "主食", "code": "STAPLE", "description": "米饭、面食等主食", "sort_order": 4},
        {"name": "小吃", "code": "SNACK", "description": "各类小吃", "sort_order": 5},
        {"name": "饮品", "code": "DRINK", "description": "各类饮品", "sort_order": 6},
        {"name": "海鲜", "code": "SEAFOOD", "description": "海鲜类菜品", "sort_order": 7},
        {"name": "肉类", "code": "MEAT", "description": "肉类菜品", "sort_order": 8},
        {"name": "素食", "code": "VEGETARIAN", "description": "素食菜品", "sort_order": 9},
        {"name": "火锅", "code": "HOTPOT", "description": "火锅相关", "sort_order": 10},
        {"name": "烧烤", "code": "BBQ", "description": "烧烤类菜品", "sort_order": 11},
        {"name": "甜品", "code": "DESSERT", "description": "甜品", "sort_order": 12},
        {"name": "烘焙", "code": "BAKING", "description": "烘焙食品", "sort_order": 13},
        {"name": "日料", "code": "JAPANESE", "description": "日式料理", "sort_order": 14},
        {"name": "西餐", "code": "WESTERN", "description": "西式料理", "sort_order": 15},
        {"name": "其他", "code": "OTHER", "description": "其他分类", "sort_order": 99},
    ]

    for cat_data in categories_data:
        # 检查分类是否已存在
        category = db.query(Category).filter(Category.name == cat_data["name"]).first()

        if not category:
            category = Category(**cat_data)
            db.add(category)
            db.flush()
            print(f"创建分类: {cat_data['name']}")

        categories_dict[cat_data["name"]] = category

    db.commit()
    print(f"共创建/更新 {len(categories_dict)} 个分类")
    return categories_dict


def import_products(db: Session, products_data: List[Dict], categories_dict: Dict[str, Category]):
    """
    导入商品数据

    Args:
        db: 数据库会话
        products_data: 商品数据列表
        categories_dict: 分类字典
    """
    print(f"开始导入 {len(products_data)} 条商品数据...")

    success_count = 0
    skip_count = 0
    error_count = 0

    for idx, product_data in enumerate(products_data, 1):
        try:
            # 检查是否已存在
            existing = db.query(Product).filter(Product.title == product_data['title']).first()

            if existing:
                skip_count += 1
                if idx % 100 == 0:
                    print(f"进度: {idx}/{len(products_data)}, 跳过: {skip_count}, 新增: {success_count}")
                continue

            # 获取分类
            category_name = product_data['category']
            category = categories_dict.get(category_name)

            if not category:
                print(f"警告: 分类不存在 {category_name},使用'其他'分类")
                category = categories_dict.get("其他")

            # 创建商品
            product = Product(
                title=product_data['title'],
                category_id=category.id,
                detail_url=product_data['detail_url'],
                image_url=product_data['image_url'],
                local_image_path=product_data['local_image_path'],
                ingredients=product_data['ingredients'],
                views=product_data['views'],
                favorites=product_data['favorites'],
                status=ProductStatus.ACTIVE
            )

            db.add(product)
            success_count += 1

            if idx % 100 == 0:
                print(f"进度: {idx}/{len(products_data)}, 跳过: {skip_count}, 新增: {success_count}")
                db.commit()

        except Exception as e:
            error_count += 1
            print(f"错误: 导入商品失败 {product_data.get('title', 'Unknown')}: {e}")
            db.rollback()

    db.commit()
    print(f"导入完成: 新增 {success_count}, 跳过 {skip_count}, 错误 {error_count}")


def validate_data(db: Session, material_path: str) -> Dict:
    """
    数据验证

    Args:
        db: 数据库会话
        material_path: Material文件夹路径

    Returns:
        验证报告字典
    """
    print("\n" + "="*50)
    print("开始数据验证...")
    print("="*50)

    report = {
        "total_products": 0,
        "total_categories": 0,
        "missing_images": [],
        "category_distribution": {},
        "image_integrity": 0.0
    }

    # 统计商品和分类
    report["total_products"] = db.query(Product).count()
    report["total_categories"] = db.query(Category).count()

    print(f"商品总数: {report['total_products']}")
    print(f"分类总数: {report['total_categories']}")

    # 分类分布
    categories = db.query(Category).all()
    for category in categories:
        count = db.query(Product).filter(Product.category_id == category.id).count()
        report["category_distribution"][category.name] = count
        print(f"  - {category.name}: {count}")

    # 图片完整性检查
    material_dir = Path(material_path)
    products = db.query(Product).all()

    missing_count = 0
    for product in products:
        # 从local_image_path提取文件名
        image_filename = product.local_image_path.split('/')[-1]
        image_path = material_dir / image_filename

        if not image_path.exists():
            report["missing_images"].append({
                "product_id": product.id,
                "title": product.title,
                "image_path": str(image_path)
            })
            missing_count += 1

    if report["total_products"] > 0:
        report["image_integrity"] = (report["total_products"] - missing_count) / report["total_products"] * 100

    print(f"\n图片完整性: {report['image_integrity']:.2f}%")
    print(f"缺失图片数量: {missing_count}")

    if missing_count > 0 and missing_count <= 10:
        print("\n缺失图片列表:")
        for item in report["missing_images"]:
            print(f"  - ID:{item['product_id']} {item['title']}")

    print("\n" + "="*50)
    return report


def save_validation_report(report: Dict, output_path: str = "/Volumes/545S/general final/backend/validation_report.json"):
    """
    保存验证报告到JSON文件

    Args:
        report: 验证报告字典
        output_path: 输出文件路径
    """
    report_with_timestamp = {
        "timestamp": datetime.now().isoformat(),
        "report": report
    }

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(report_with_timestamp, f, ensure_ascii=False, indent=2)

    print(f"\n验证报告已保存到: {output_path}")


def main():
    """主函数"""
    print("="*50)
    print("Material数据导入工具")
    print("="*50)

    # 创建数据库引擎
    engine = create_engine(settings.DATABASE_URL, echo=False)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()

    try:
        # 1. 扫描Material文件
        print("\n步骤 1: 扫描Material文件")
        products_data = scan_material_files(settings.MATERIAL_PATH)

        if not products_data:
            print("错误: 没有找到任何有效数据")
            return

        # 2. 导入分类
        print("\n步骤 2: 导入商品分类")
        categories_dict = import_categories(db)

        # 3. 导入商品
        print("\n步骤 3: 导入商品数据")
        import_products(db, products_data, categories_dict)

        # 4. 数据验证
        print("\n步骤 4: 数据验证")
        report = validate_data(db, settings.MATERIAL_PATH)

        # 5. 保存验证报告
        save_validation_report(report)

        # 打印最终统计
        print("\n" + "="*50)
        print("导入完成!")
        print("="*50)
        print(f"✓ 成功导入商品: {report['total_products']} 条")
        print(f"✓ 创建分类: {report['total_categories']} 个")
        print(f"✓ 图片完整性: {report['image_integrity']:.2f}%")

        if report['total_products'] >= 3000:
            print(f"✓ 达成目标: 导入≥3000个商品SKU")
        else:
            print(f"⚠ 未达成目标: 仅导入{report['total_products']}个商品SKU,目标≥3000")

        if report['image_integrity'] >= 95:
            print(f"✓ 达成目标: 图片完整性≥95%")
        else:
            print(f"⚠ 未达成目标: 图片完整性{report['image_integrity']:.2f}%,目标≥95%")

        if report['total_categories'] >= 10:
            print(f"✓ 达成目标: 创建≥10个商品分类")
        else:
            print(f"⚠ 未达成目标: 仅创建{report['total_categories']}个分类,目标≥10")

    except Exception as e:
        print(f"\n错误: 导入失败: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    main()
