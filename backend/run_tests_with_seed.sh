#!/bin/bash
# 运行测试并显示详细输出

echo "=========================================="
echo "运行后端测试（带种子数据）"
echo "=========================================="

# 激活虚拟环境（如果存在）
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# 运行测试
python -m pytest tests/ \
    -v \
    --tb=short \
    --disable-warnings \
    --cov=app \
    --cov-report=term-missing \
    --cov-report=html \
    "$@"

# 显示测试结果摘要
echo ""
echo "=========================================="
echo "测试完成！"
echo "覆盖率报告: htmlcov/index.html"
echo "=========================================="
