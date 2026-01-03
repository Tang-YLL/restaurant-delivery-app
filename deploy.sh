#!/bin/bash

# 餐厅管理系统部署脚本
# 使用方法: ./deploy.sh [environment]
# environment: dev|production (默认: dev)

set -e  # 遇到错误立即退出

# 项目根目录
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_DIR="$PROJECT_ROOT/config"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查Docker是否安装
check_docker() {
    log_info "检查Docker安装..."
    if ! command -v docker &> /dev/null; then
        log_error "Docker未安装,请先安装Docker"
        exit 1
    fi
    log_info "Docker已安装: $(docker --version)"
}

# 检查Docker Compose是否安装
check_docker_compose() {
    log_info "检查Docker Compose安装..."
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        log_error "Docker Compose未安装,请先安装Docker Compose"
        exit 1
    fi
    log_info "Docker Compose已安装"
}

# 创建必要的目录
create_directories() {
    log_info "创建必要的目录..."
    mkdir -p backend/logs
    mkdir -p Material/material
    mkdir -p nginx/ssl
    log_info "目录创建完成"
}

# 检查环境变量文件
check_env_file() {
    local env_file=$1
    if [ ! -f "$env_file" ]; then
        log_warn "环境变量文件 $env_file 不存在,创建默认文件..."
        cp backend/.env.example "$env_file" 2>/dev/null || true
        log_warn "请编辑 $env_file 并设置正确的配置值"
    fi
}

# 构建Vue3管理后台
build_admin() {
    log_info "构建Vue3管理后台..."
    cd vue-admin

    # 检查node_modules是否存在
    if [ ! -d "node_modules" ]; then
        log_info "安装依赖..."
        npm install
    fi

    log_info "开始构建..."
    npm run build

    if [ -d "dist" ]; then
        log_info "管理后台构建成功"
        cd "$PROJECT_ROOT"
    else
        log_error "管理后台构建失败"
        exit 1
    fi
}

# 停止并删除旧容器
stop_containers() {
    log_info "停止现有容器..."
    cd "$CONFIG_DIR"
    docker-compose down 2>/dev/null || true
    cd "$PROJECT_ROOT"
    log_info "容器已停止"
}

# 拉取最新镜像
pull_images() {
    log_info "拉取Docker镜像..."
    cd "$CONFIG_DIR"
    docker-compose pull
    cd "$PROJECT_ROOT"
    log_info "镜像拉取完成"
}

# 构建自定义镜像
build_images() {
    log_info "构建Docker镜像..."
    cd "$CONFIG_DIR"
    docker-compose build
    cd "$PROJECT_ROOT"
    log_info "镜像构建完成"
}

# 启动服务
start_services() {
    local env_file=$1
    log_info "启动服务(使用环境: $env_file)..."

    cd "$CONFIG_DIR"
    if [ -f "$env_file" ]; then
        docker-compose --env-file "$env_file" up -d
    else
        docker-compose up -d
    fi
    cd "$PROJECT_ROOT"

    log_info "服务启动中..."
    sleep 5

    # 检查服务状态
    log_info "检查服务状态..."
    cd "$CONFIG_DIR"
    docker-compose ps
    cd "$PROJECT_ROOT"
}

# 运行数据库迁移
run_migrations() {
    log_info "运行数据库迁移..."
    cd "$CONFIG_DIR"
    docker-compose exec backend alembic upgrade head || log_warn "数据库迁移失败或已跳过"
    cd "$PROJECT_ROOT"
    log_info "数据库迁移完成"
}

# 初始化数据
init_data() {
    log_info "初始化测试数据..."
    cd "$CONFIG_DIR"
    docker-compose exec backend python scripts/init_test_data.py || log_warn "数据初始化失败或已跳过"
    cd "$PROJECT_ROOT"
    log_info "数据初始化完成"
}

# 健康检查
health_check() {
    log_info "执行健康检查..."

    # 等待服务启动
    sleep 10

    # 检查后端API
    if curl -f http://localhost:8000/health &> /dev/null; then
        log_info "后端API健康检查通过"
    else
        log_warn "后端API健康检查失败"
    fi

    # 检查管理后台
    if curl -f http://localhost/ &> /dev/null; then
        log_info "管理后台健康检查通过"
    else
        log_warn "管理后台健康检查失败"
    fi
}

# 显示访问信息
show_access_info() {
    echo ""
    log_info "========================================"
    log_info "部署完成!"
    log_info "========================================"
    echo ""
    log_info "访问地址:"
    echo "  - 后端API: http://localhost:8000"
    echo "  - API文档: http://localhost:8000/docs"
    echo "  - 管理后台: http://localhost"
    echo ""
    log_info "常用命令:"
    echo "  - 查看日志: cd config && docker-compose logs -f"
    echo "  - 停止服务: cd config && docker-compose down"
    echo "  - 重启服务: cd config && docker-compose restart"
    echo ""
    log_info "数据库连接:"
    echo "  - Host: localhost"
    echo "  - Port: 5432"
    echo "  - Database: restaurant_db"
    echo "  - User: postgres"
    echo "  - Password: 参见config/.env文件"
    echo ""
}

# 主部署流程
main() {
    local environment=${1:-dev}
    local env_file="config/.env"

    log_info "========================================="
    log_info "餐厅管理系统部署脚本"
    log_info "环境: $environment"
    log_info "========================================="

    # 前置检查
    check_docker
    check_docker_compose
    create_directories

    # 设置环境文件
    if [ "$environment" = "production" ]; then
        env_file="config/.env.production"
        check_env_file "$env_file"
    else
        check_env_file "config/.env"
    fi

    # 构建管理后台
    build_admin

    # Docker操作
    stop_containers
    pull_images
    build_images
    start_services "$env_file"

    # 数据库操作
    run_migrations
    if [ "$environment" != "production" ]; then
        init_data
    fi

    # 健康检查
    health_check

    # 显示访问信息
    show_access_info
}

# 执行主函数
main "$@"
