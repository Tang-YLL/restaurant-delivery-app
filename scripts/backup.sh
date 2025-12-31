#!/bin/bash

# 数据库备份脚本

set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

# 备份目录
BACKUP_DIR="./backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="$BACKUP_DIR/restaurant_db_$TIMESTAMP.sql"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}数据库备份${NC}"
echo -e "${GREEN}========================================${NC}"

# 创建备份目录
mkdir -p "$BACKUP_DIR"

# 检查PostgreSQL容器是否运行
if ! docker ps | grep -q restaurant_postgres; then
    echo -e "${RED}错误: PostgreSQL容器未运行${NC}"
    exit 1
fi

# 执行备份
echo "正在备份数据库..."
docker exec restaurant_postgres pg_dump -U postgres restaurant_db > "$BACKUP_FILE"

# 压缩备份
echo "压缩备份文件..."
gzip "$BACKUP_FILE"

echo -e "${GREEN}备份完成!${NC}"
echo "备份文件: ${BACKUP_FILE}.gz"

# 清理30天前的备份
echo "清理旧备份..."
find "$BACKUP_DIR" -name "*.gz" -mtime +30 -delete
echo "清理完成"
