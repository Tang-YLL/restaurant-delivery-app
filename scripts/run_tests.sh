#!/bin/bash

# 测试脚本 - 运行所有测试

set -e

# 颜色
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}运行测试套件${NC}"
echo -e "${GREEN}========================================${NC}"

cd backend

echo ""
echo -e "${YELLOW}1. 代码风格检查 (flake8)...${NC}"
flake8 app/ tests/ || echo "flake8检查发现问题"

echo ""
echo -e "${YELLOW}2. 类型检查 (mypy)...${NC}"
mypy app/ || echo "mypy检查发现问题"

echo ""
echo -e "${YELLOW}3. 运行单元测试并生成覆盖率报告...${NC}"
pytest -v \
    --cov=app \
    --cov-report=term-missing \
    --cov-report=html \
    --cov-report=json \
    tests/

echo ""
echo -e "${GREEN}测试完成!${NC}"
echo -e "覆盖率报告: htmlcov/index.html"
echo -e "JSON报告: coverage.json"

# 显示覆盖率
if [ -f coverage.json ]; then
    echo ""
    echo -e "${YELLOW}覆盖率摘要:${NC}"
    python -c "import json; data=json.load(open('coverage.json')); print(f\"总覆盖率: {data['totals']['percent_covered']:.2f}%\")"
fi
