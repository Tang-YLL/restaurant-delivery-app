#!/bin/bash

# Locust性能测试脚本

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

HOST=${1:-http://localhost:8000}
USERS=${2:-100}
SPAWN_RATE=${3:-10}

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Locust性能测试${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "目标主机: $HOST"
echo "并发用户数: $USERS"
echo "启动速率: $SPAWN_RATE (用户/秒)"
echo ""

cd backend

# 检查locust是否安装
if ! command -v locust &> /dev/null; then
    echo -e "${YELLOW}Locust未安装,正在安装...${NC}"
    pip install locust
fi

# 运行Locust
echo -e "${GREEN}启动Locust Web界面...${NC}"
echo "访问 http://localhost:8089 开始测试"
echo ""

locust -f locustfile.py --host="$HOST" --users="$USERS" --spawn-rate="$SPAWN_RATE" --web-port=8089
