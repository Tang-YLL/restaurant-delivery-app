#!/bin/bash

# FastAPI后端启动脚本

echo "================================"
echo "餐厅管理系统 - FastAPI后端"
echo "================================"
echo ""

# 检查Python版本
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "检测到Python版本: $python_version"

# 检查是否存在虚拟环境
if [ ! -d "venv" ]; then
    echo "创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
echo "激活虚拟环境..."
source venv/bin/activate

# 安装依赖
echo "检查并安装依赖..."
pip install -q -r requirements.txt

# 检查.env文件
if [ ! -f ".env" ]; then
    echo "警告: .env文件不存在,从.env.example复制..."
    cp .env.example .env
    echo "请编辑.env文件配置数据库和Redis连接信息"
fi

# 运行数据库迁移
echo "运行数据库迁移..."
alembic upgrade head

# 启动服务
echo ""
echo "================================"
echo "启动FastAPI服务..."
echo "API文档地址: http://localhost:8000/docs"
echo "健康检查: http://localhost:8000/health"
echo "================================"
echo ""

python main.py
