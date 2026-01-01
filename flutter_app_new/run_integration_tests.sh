#!/bin/bash

# 集成测试运行脚本
# 用于快速运行外卖App的集成测试

set -e

echo "======================================"
echo "外卖App集成测试脚本"
echo "======================================"
echo ""

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 项目根目录
PROJECT_ROOT="/Volumes/545S/general final"
FLUTTER_APP="$PROJECT_ROOT/flutter_app_new"
BACKEND_DIR="$PROJECT_ROOT/backend"

# 检查后端是否运行
echo "1. 检查后端服务..."
if curl -s http://localhost:8001/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓ 后端服务正在运行${NC}"
    curl -s http://localhost:8001/health | python3 -m json.tool
else
    echo -e "${RED}✗ 后端服务未运行${NC}"
    echo "请先启动后端服务:"
    echo "  cd $BACKEND_DIR"
    echo "  source venv/bin/activate"
    echo "  python -m uvicorn main:app --host 0.0.0.0 --port 8001 --reload"
    exit 1
fi

echo ""
echo "2. 检查Flutter环境..."
cd "$FLUTTER_APP"

# 检查Flutter安装
if ! command -v flutter &> /dev/null; then
    echo -e "${RED}✗ Flutter未安装${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Flutter已安装${NC}"
flutter --version

echo ""
echo "3. 检查可用设备..."
DEVICES=$(flutter devices)
if echo "$DEVICES" | grep -q "No devices found"; then
    echo -e "${RED}✗ 没有可用的设备${NC}"
    echo "请启动模拟器:"
    echo "  iOS: open -a Simulator"
    echo "  Android: emulator -avd <name>"
    exit 1
fi
echo -e "${GREEN}✓ 找到可用设备:${NC}"
echo "$DEVICES" | grep -E "iPhone|Android|emulator"

echo ""
echo "4. 安装依赖..."
flutter pub get
echo -e "${GREEN}✓ 依赖安装完成${NC}"

echo ""
echo "======================================"
echo "运行集成测试"
echo "======================================"
echo ""

# 获取测试文件列表
TEST_FILES=(
    "integration_test/auth_test.dart"
    "integration_test/product_browsing_test.dart"
    "integration_test/shopping_test.dart"
    "integration_test/order_tracking_test.dart"
    "integration_test/api_test.dart"
)

# 统计变量
TOTAL_TESTS=${#TEST_FILES[@]}
PASSED_TESTS=0
FAILED_TESTS=0

# 运行每个测试
for i in "${!TEST_FILES[@]}"; do
    TEST_FILE="${TEST_FILES[$i]}"
    echo "----------------------------------------"
    echo "运行测试 [$((i+1))/$TOTAL_TESTS]: $TEST_FILE"
    echo "----------------------------------------"

    if flutter test "$TEST_FILE"; then
        echo -e "${GREEN}✓ 测试通过${NC}"
        ((PASSED_TESTS++))
    else
        echo -e "${RED}✗ 测试失败${NC}"
        ((FAILED_TESTS++))
    fi
    echo ""
done

# 显示测试结果摘要
echo "======================================"
echo "测试结果摘要"
echo "======================================"
echo "总测试数: $TOTAL_TESTS"
echo -e "${GREEN}通过: $PASSED_TESTS${NC}"
echo -e "${RED}失败: $FAILED_TESTS${NC}"
echo ""

if [ $FAILED_TESTS -eq 0 ]; then
    echo -e "${GREEN}🎉 所有测试通过！${NC}"
    exit 0
else
    echo -e "${RED}⚠️  有测试失败，请检查日志${NC}"
    exit 1
fi
