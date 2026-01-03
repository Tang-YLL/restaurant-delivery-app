#!/bin/bash

echo "================================"
echo "任务003: 商品和购物车API实现"
echo "快速文件检查"
echo "================================"
echo ""

passed=0
total=0

check_file() {
    total=$((total + 1))
    if [ -f "$1" ]; then
        echo "✅ $1"
        passed=$((passed + 1))
    else
        echo "❌ $1"
    fi
}

check_content() {
    total=$((total + 1))
    if grep -q "$2" "$1" 2>/dev/null; then
        echo "✅ $1 包含: $2"
        passed=$((passed + 1))
    else
        echo "❌ $1 缺少: $2"
    fi
}

echo "1. API路由文件..."
check_file "app/api/products.py"
check_file "app/api/categories.py"
check_file "app/api/cart.py"
echo ""

echo "2. 模型字段检查..."
check_content "app/models/__init__.py" "price = Column"
check_content "app/models/__init__.py" "stock = Column"
check_content "app/models/__init__.py" "sales_count = Column"
echo ""

echo "3. Repository检查..."
check_content "app/repositories/__init__.py" "class CategoryRepository"
check_content "app/repositories/__init__.py" "validate_stock"
echo ""

echo "4. Service检查..."
check_content "app/services/__init__.py" "class CategoryService"
check_content "app/services/__init__.py" "get_cart_summary"
echo ""

echo "5. 路由注册..."
check_content "main.py" "products.router"
check_content "main.py" "categories.router"
check_content "main.py" "cart.router"
echo ""

echo "6. 测试文件..."
check_file "tests/test_products.py"
echo ""

echo "7. 文档文件..."
check_file "TASK_003_SUMMARY.md"
check_file "API_GUIDE.md"
echo ""

echo "================================"
echo "检查结果: $passed/$total 项通过"
echo "成功率: $(( passed * 100 / total ))%"
echo "================================"

if [ $passed -eq $total ]; then
    echo "🎉 所有检查通过!"
    exit 0
else
    echo "⚠️  部分检查未通过"
    exit 1
fi
