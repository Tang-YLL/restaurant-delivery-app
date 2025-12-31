#!/usr/bin/env python3
"""
快速验证脚本 - 检查任务003实现是否完整
"""
import sys
import os

def check_file_exists(filepath, description):
    """检查文件是否存在"""
    if os.path.exists(filepath):
        print(f"✅ {description}: {filepath}")
        return True
    else:
        print(f"❌ {description}: {filepath}")
        return False

def check_import(module_path, description):
    """检查模块是否可以导入"""
    try:
        parts = module_path.split('.')
        module = __import__(module_path)
        for part in parts[1:]:
            module = getattr(module, part)
        print(f"✅ {description}")
        return True
    except Exception as e:
        print(f"❌ {description}: {e}")
        return False

def main():
    print("=" * 60)
    print("任务003: 商品和购物车API实现 - 验证检查")
    print("=" * 60)
    print()

    checks = []

    # 1. 检查API路由文件
    print("1. 检查API路由文件...")
    checks.append(check_file_exists(
        "/Volumes/545S/general final/backend/app/api/products.py",
        "商品API路由"
    ))
    checks.append(check_file_exists(
        "/Volumes/545S/general final/backend/app/api/categories.py",
        "分类API路由"
    ))
    checks.append(check_file_exists(
        "/Volumes/545S/general final/backend/app/api/cart.py",
        "购物车API路由"
    ))
    print()

    # 2. 检查模型更新
    print("2. 检查数据模型...")
    try:
        sys.path.insert(0, '/Volumes/545S/general final/backend')
        from app.models import Product
        product_fields = [f.name for f in Product.__table__.columns]
        required_fields = ['price', 'stock', 'sales_count', 'description', 'is_active']

        for field in required_fields:
            if field in product_fields:
                print(f"✅ Product模型包含字段: {field}")
                checks.append(True)
            else:
                print(f"❌ Product模型缺少字段: {field}")
                checks.append(False)
    except Exception as e:
        print(f"❌ 无法导入Product模型: {e}")
        checks.append(False)
    print()

    # 3. 检查Repository
    print("3. 检查Repository层...")
    try:
        from app.repositories import CategoryRepository
        print("✅ CategoryRepository 已定义")
        checks.append(True)

        repo_methods = ['get_active_categories', 'get_by_code', 'get_by_name']
        for method in repo_methods:
            if hasattr(CategoryRepository, method):
                print(f"✅ CategoryRepository.{method} 已实现")
                checks.append(True)
            else:
                print(f"❌ CategoryRepository.{method} 未实现")
                checks.append(False)
    except Exception as e:
        print(f"❌ 无法导入CategoryRepository: {e}")
        checks.append(False)
    print()

    # 4. 检查Service
    print("4. 检查Service层...")
    try:
        from app.services import CategoryService, ProductService, CartService

        print("✅ CategoryService 已定义")
        print("✅ ProductService 已定义")
        print("✅ CartService 已定义")
        checks.extend([True, True, True])

        # 检查关键方法
        category_methods = ['get_categories', 'create_category', 'update_category', 'delete_category']
        for method in category_methods:
            if hasattr(CategoryService, method):
                print(f"✅ CategoryService.{method} 已实现")
                checks.append(True)
            else:
                print(f"❌ CategoryService.{method} 未实现")
                checks.append(False)

        product_methods = ['get_products', 'get_hot_products', 'search_products']
        for method in product_methods:
            if hasattr(ProductService, method):
                print(f"✅ ProductService.{method} 已实现")
                checks.append(True)
            else:
                print(f"❌ ProductService.{method} 未实现")
                checks.append(False)

        cart_methods = ['get_cart_summary', 'add_item']
        for method in cart_methods:
            if hasattr(CartService, method):
                print(f"✅ CartService.{method} 已实现")
                checks.append(True)
            else:
                print(f"❌ CartService.{method} 未实现")
                checks.append(False)

    except Exception as e:
        print(f"❌ 无法导入Service: {e}")
        checks.append(False)
    print()

    # 5. 检查路由注册
    print("5. 检查路由注册...")
    try:
        with open('/Volumes/545S/general final/backend/main.py', 'r') as f:
            main_content = f.read()

            if 'products.router' in main_content:
                print("✅ products.router 已注册")
                checks.append(True)
            else:
                print("❌ products.router 未注册")
                checks.append(False)

            if 'categories.router' in main_content:
                print("✅ categories.router 已注册")
                checks.append(True)
            else:
                print("❌ categories.router 未注册")
                checks.append(False)

            if 'cart.router' in main_content:
                print("✅ cart.router 已注册")
                checks.append(True)
            else:
                print("❌ cart.router 未注册")
                checks.append(False)
    except Exception as e:
        print(f"❌ 无法检查main.py: {e}")
        checks.append(False)
    print()

    # 6. 检查测试文件
    print("6. 检查测试文件...")
    checks.append(check_file_exists(
        "/Volumes/545S/general final/backend/tests/test_products.py",
        "商品和购物车测试文件"
    ))
    print()

    # 7. 统计结果
    print("=" * 60)
    total_checks = len(checks)
    passed_checks = sum(checks)
    failed_checks = total_checks - passed_checks
    success_rate = (passed_checks / total_checks * 100) if total_checks > 0 else 0

    print(f"验证结果: {passed_checks}/{total_checks} 项通过")
    print(f"成功率: {success_rate:.1f}%")
    print()

    if failed_checks == 0:
        print("🎉 所有检查通过! 任务003实现完整!")
        return 0
    else:
        print(f"⚠️  {failed_checks} 项检查未通过,请检查实现")
        return 1

if __name__ == "__main__":
    sys.exit(main())
