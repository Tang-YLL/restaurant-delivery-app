# 餐厅管理系统部署文档

## 目录
- [系统要求](#系统要求)
- [快速开始](#快速开始)
- [详细部署步骤](#详细部署步骤)
- [生产环境配置](#生产环境配置)
- [Docker部署](#docker部署)
- [数据库管理](#数据库管理)
- [性能测试](#性能测试)
- [监控和日志](#监控和日志)
- [故障排查](#故障排查)
- [安全建议](#安全建议)

## 系统要求

### 硬件要求
- **最低配置**:
  - CPU: 2核
  - 内存: 4GB
  - 磁盘: 20GB可用空间

- **推荐配置**:
  - CPU: 4核+
  - 内存: 8GB+
  - 磁盘: 50GB+ SSD

### 软件要求
- **操作系统**:
  - Linux (Ubuntu 20.04+, CentOS 7+, Debian 10+)
  - macOS 10.15+
  - Windows 10+ (WSL2)

- **必需软件**:
  - Docker: 20.10+
  - Docker Compose: 2.0+
  - Git: 2.0+

- **开发环境(可选)**:
  - Python: 3.11+
  - Node.js: 18+
  - Flutter: 3.16+ (移动端开发)

## 快速开始

### 1. 克隆项目

```bash
git clone <repository-url>
cd general\ final
```

### 2. 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑环境变量
nano .env
```

必填配置项:
```bash
# 数据库密码
DB_PASSWORD=your_secure_password

# Redis密码
REDIS_PASSWORD=your_redis_password

# JWT密钥(至少32字符)
SECRET_KEY=your-very-secure-secret-key-change-this-in-production
```

### 3. 一键部署

```bash
# 开发环境
./deploy.sh dev

# 生产环境
./deploy.sh production
```

### 4. 访问应用

- **后端API**: http://localhost:8000
- **API文档**: http://localhost:8000/docs
- **管理后台**: http://localhost

## 详细部署步骤

### 步骤1: 安装Docker

#### Ubuntu/Debian:
```bash
# 更新包索引
sudo apt-get update

# 安装依赖
sudo apt-get install apt-transport-https ca-certificates curl software-properties-common

# 添加Docker官方GPG密钥
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -

# 添加Docker仓库
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"

# 安装Docker
sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-compose-plugin

# 启动Docker服务
sudo systemctl start docker
sudo systemctl enable docker

# 验证安装
docker --version
docker compose version
```

#### CentOS/RHEL:
```bash
# 安装依赖
sudo yum install -y yum-utils

# 添加Docker仓库
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo

# 安装Docker
sudo yum install docker-ce docker-ce-cli containerd.io docker-compose-plugin

# 启动Docker
sudo systemctl start docker
sudo systemctl enable docker
```

#### macOS:
```bash
# 下载并安装Docker Desktop
# https://www.docker.com/products/docker-desktop

# 验证安装
docker --version
```

### 步骤2: 配置环境变量

#### 开发环境 (.env)
```bash
# 应用配置
APP_NAME=餐厅管理系统
DEBUG=True
ENVIRONMENT=development

# 数据库配置
DB_PASSWORD=dev_password_123
DATABASE_URL=postgresql+asyncpg://postgres:dev_password_123@postgres:5432/restaurant_db

# Redis配置
REDIS_PASSWORD=redis_password_123
REDIS_URL=redis://:redis_password_123@redis:6379/0

# JWT配置
SECRET_KEY=development-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS配置
CORS_ORIGINS=http://localhost,http://localhost:3000,http://localhost:8080

# 静态文件
STATIC_FILES_PATH=/app/static

# 短信配置(测试)
SMS_ACCESS_KEY=test
SMS_SECRET_KEY=test
SMS_SIGN_NAME=测试签名
```

#### 生产环境 (.env.production)
```bash
# 应用配置
APP_NAME=餐厅管理系统
DEBUG=False
ENVIRONMENT=production

# 数据库配置(使用强密码)
DB_PASSWORD=<strong-password-here>
DATABASE_URL=postgresql+asyncpg://postgres:<strong-password-here>@postgres:5432/restaurant_db

# Redis配置
REDIS_PASSWORD=<strong-redis-password>
REDIS_URL=redis://:<strong-redis-password>@redis:6379/0

# JWT配置(必须修改)
SECRET_KEY=<minimum-32-character-random-string>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS配置(仅允许你的域名)
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# 其他配置...
LOG_LEVEL=INFO
LOG_FILE=/app/logs/app.log
```

**生成安全密钥**:
```bash
# 生成随机密钥
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 步骤3: 准备静态文件

```bash
# 创建静态文件目录
mkdir -p Material/material

# 上传商品图片到 Material/material/ 目录
# 支持的格式: jpg, jpeg, png, gif, webp
```

### 步骤4: 构建前端

```bash
cd vue-admin

# 安装依赖
npm install

# 构建生产版本
npm run build

# 验证构建
ls -la dist/
```

### 步骤5: 启动服务

```bash
# 返回项目根目录
cd ..

# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 检查服务状态
docker-compose ps
```

### 步骤6: 初始化数据库

```bash
# 运行数据库迁移
docker-compose exec backend alembic upgrade head

# 初始化测试数据(可选)
docker-compose exec backend python scripts/init_test_data.py

# 创建管理员账户
docker-compose exec backend python -c "
from app.core.security import get_password_hash
from app.models import Admin
from app.core.database import get_db
import asyncio

async def create_admin():
    async for db in get_db():
        admin = Admin(
            username='admin',
            email='admin@example.com',
            hashed_password=get_password_hash('admin123')
        )
        db.add(admin)
        await db.commit()
        print('管理员创建成功!')
        break

asyncio.run(create_admin())
"
```

## 生产环境配置

### SSL/HTTPS配置

#### 1. 使用Let's Encrypt免费证书

```bash
# 安装certbot
sudo apt-get install certbot

# 生成证书
sudo certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com

# 证书路径
# /etc/letsencrypt/live/yourdomain.com/fullchain.pem
# /etc/letsencrypt/live/yourdomain.com/privkey.pem

# 复制证书到项目
mkdir -p nginx/ssl
sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem nginx/ssl/cert.pem
sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem nginx/ssl/key.pem
```

#### 2. 配置Nginx HTTPS

编辑 `nginx.conf`,取消HTTPS部分的注释:

```nginx
server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # 其他配置同HTTP...
}

# HTTP重定向到HTTPS
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}
```

#### 3. 自动续期证书

```bash
# 添加cron任务
sudo crontab -e

# 添加以下行(每天凌晨2点检查续期)
0 2 * * * certbot renew --quiet && docker cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem restaurant_admin:/etc/nginx/ssl/cert.pem && docker cp /etc/letsencrypt/live/yourdomain.com/privkey.pem restaurant_admin:/etc/nginx/ssl/key.pem && docker exec restaurant_admin nginx -s reload
```

### 防火墙配置

```bash
# Ubuntu/Debian (UFW)
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable

# CentOS/RHEL (firewalld)
sudo firewall-cmd --permanent --add-service=ssh
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload
```

### 日志管理

#### 配置日志轮转

创建 `/etc/logrotate.d/restaurant`:

```
/Volumes/545S/general final/backend/logs/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0644 www-data www-data
    sharedscripts
    postrotate
        docker-compose exec backend kill -USR1 $(cat /app/gunicorn.pid)
    endscript
}
```

## Docker部署

### 常用命令

```bash
# 启动所有服务
docker-compose up -d

# 停止所有服务
docker-compose down

# 重启服务
docker-compose restart

# 查看日志
docker-compose logs -f [service_name]

# 查看服务状态
docker-compose ps

# 进入容器
docker-compose exec backend bash
docker-compose exec postgres psql -U postgres -d restaurant_db

# 更新镜像
docker-compose pull
docker-compose up -d --build

# 清理未使用的资源
docker system prune -a
```

### 扩展服务

```bash
# 扩展后端服务(3个实例)
docker-compose up -d --scale backend=3

# 扩展需要负载均衡器,建议使用Nginx配置upstream
```

### 资源限制

编辑 `docker-compose.yml` 添加资源限制:

```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
```

## 数据库管理

### 备份数据库

```bash
# 使用备份脚本
./scripts/backup.sh

# 手动备份
docker exec restaurant_postgres pg_dump -U postgres restaurant_db > backup.sql

# 压缩备份
gzip backup.sql
```

### 恢复数据库

```bash
# 解压备份
gunzip backup.sql.gz

# 恢复数据
docker exec -i restaurant_postgres psql -U postgres restaurant_db < backup.sql
```

### 数据库迁移

```bash
# 创建迁移
docker-compose exec backend alembic revision --autogenerate -m "描述"

# 应用迁移
docker-compose exec backend alembic upgrade head

# 回滚迁移
docker-compose exec backend alembic downgrade -1

# 查看迁移历史
docker-compose exec backend alembic history
```

### 直接访问数据库

```bash
# 连接到PostgreSQL
docker-compose exec postgres psql -U postgres -d restaurant_db

# 常用SQL命令
\dt          # 列出所有表
\d users     # 查看表结构
SELECT * FROM users LIMIT 10;
\q           # 退出
```

## 性能测试

### 运行Locust测试

```bash
# 使用测试脚本
./scripts/run_locust.sh http://localhost:8000 100 10

# 或手动运行
cd backend
locust -f locustfile.py --host=http://localhost:8000 --users=100 --spawn-rate=10
```

访问 http://localhost:8089 查看测试仪表盘。

### 性能基准

**目标性能指标**:
- API响应时间: < 200ms (P95)
- 并发用户: 100+ 无性能降级
- 错误率: < 0.1%
- 数据库查询: < 100ms (P95)

### 性能优化建议

1. **数据库优化**:
   - 添加索引到常用查询字段
   - 使用连接池
   - 启用查询缓存

2. **Redis缓存**:
   - 缓存热点数据(商品列表、热门商品)
   - 使用Redis作为会话存储

3. **Nginx优化**:
   - 启用Gzip压缩
   - 配置静态文件缓存
   - 调整worker进程数

## 监控和日志

### 查看应用日志

```bash
# 查看所有日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f backend
docker-compose logs -f postgres

# 查看最近100行
docker-compose logs --tail=100 backend
```

### 监控指标

**关键指标**:
- CPU使用率
- 内存使用率
- 磁盘I/O
- 网络流量
- API响应时间
- 错误率

**监控工具推荐**:
- Prometheus + Grafana
- Datadog
- New Relic
- Sentry (错误追踪)

### 设置告警

建议配置以下告警:
- 服务宕机
- API错误率 > 1%
- 响应时间 > 1s
- 数据库连接失败
- 磁盘空间 < 10%

## 故障排查

### 常见问题

#### 1. 容器启动失败

```bash
# 查看详细日志
docker-compose logs backend

# 检查配置
docker-compose config

# 重新构建
docker-compose up -d --build
```

#### 2. 数据库连接失败

```bash
# 检查PostgreSQL状态
docker-compose ps postgres

# 查看数据库日志
docker-compose logs postgres

# 测试连接
docker-compose exec backend python -c "
from app.core.database import test_connection
import asyncio
asyncio.run(test_connection())
"
```

#### 3. API返回500错误

```bash
# 查看后端日志
docker-compose logs -f backend

# 检查环境变量
docker-compose exec backend env | grep DATABASE

# 进入容器调试
docker-compose exec backend bash
```

#### 4. 静态文件无法访问

```bash
# 检查静态文件挂载
docker-compose exec backend ls -la /app/static

# 检查文件权限
chmod -R 755 Material/material/
```

#### 5. 内存不足

```bash
# 查看资源使用
docker stats

# 限制容器内存
# 编辑docker-compose.yml,添加内存限制
```

### 日志位置

- **应用日志**: `backend/logs/app.log`
- **Docker日志**: `docker-compose logs`
- **Nginx日志**:
  - 访问日志: `/var/log/nginx/access.log`
  - 错误日志: `/var/log/nginx/error.log`

## 安全建议

### 1. 密码安全
- 使用强密码(至少16字符,包含大小写字母、数字、特殊字符)
- 定期更换密码
- 不要在代码中硬编码密码

### 2. 网络安全
- 启用HTTPS
- 配置防火墙
- 限制数据库访问(仅内网)
- 使用VPN管理服务器

### 3. 应用安全
- 保持依赖更新
- 定期扫描漏洞
- 启用安全头(CSP, X-Frame-Options等)
- 实施速率限制

### 4. 数据安全
- 定期备份数据
- 加密敏感数据
- 实施审计日志
- 最小权限原则

### 5. 监控安全
- 监控异常登录
- 监控API滥用
- 设置入侵检测
- 定期安全审计

## 更新和维护

### 更新应用

```bash
# 1. 备份数据
./scripts/backup.sh

# 2. 拉取最新代码
git pull origin main

# 3. 更新依赖
cd backend && pip install -r requirements.txt

# 4. 重新构建
docker-compose build backend

# 5. 运行迁移
docker-compose exec backend alembic upgrade head

# 6. 重启服务
docker-compose up -d
```

### 定期维护任务

- **每日**: 检查日志、监控系统状态
- **每周**: 备份数据库、清理日志
- **每月**: 更新依赖、安全扫描、性能测试
- **每季度**: 全面安全审计、灾难恢复演练

## 支持

如有问题,请查看:
- 项目README: `/README.md`
- API文档: http://localhost:8000/docs
- 后端文档: `/backend/README.md`
- 问题追踪: [GitHub Issues]

---

**最后更新**: 2025-12-31
**版本**: 1.0.0
