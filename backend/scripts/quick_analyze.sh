#!/bin/bash
# Material数据快速分析脚本

echo "=================================="
echo "Material数据快速分析"
echo "=================================="
echo ""

cd "/Volumes/545S/general final/backend"

# 运行分析脚本
python3 scripts/analyze_material.py

echo ""
echo "=================================="
echo "分析完成!"
echo "详细报告: backend/analysis_report.json"
echo "=================================="
