# 快速启动指南

## 5分钟快速部署

### 前置条件
- Docker已安装
- Docker Compose已安装
- Git已安装

### 步骤1: 克隆项目
```bash
git clone <repository-url>
cd "general final"
```

### 步骤2: 配置环境变量
```bash
# 复制环境变量模板
cp .env.example .env

# 编辑环境变量(至少修改这些值)
# DB_PASSWORD=your_secure_password
# REDIS_PASSWORD=your_redis_password
# SECRET_KEY=your-very-secure-secret-key-min-32-chars
nano .env
```

### 步骤3: 一键部署
```bash
# 添加执行权限
chmod +x deploy.sh

# 运行部署脚本
./deploy.sh dev
```

### 步骤4: 访问应用
等待所有服务启动完成后(约2-3分钟),访问:

- **后端API**: http://localhost:8000
- **API文档**: http://localhost:8000/docs
- **管理后台**: http://localhost

## 默认账号

### 管理员账号
需要先创建管理员账号,请参考[部署文档](DEPLOYMENT.md)。

### 测试用户
可以自行注册,或使用测试脚本创建。

## 常用命令

```bash
# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down

# 重启服务
docker-compose restart

# 运行测试
./scripts/run_tests.sh

# 性能测试
./scripts/run_locust.sh http://localhost:8000 100 10

# 数据备份
./scripts/backup.sh
```

## 下一步

- 阅读完整[部署文档](DEPLOYMENT.md)
- 查看[项目总结](PROJECT_SUMMARY.md)
- 浏览[API文档](http://localhost:8000/docs)

## 遇到问题?

查看[部署文档](DEPLOYMENT.md)的故障排查部分,或提交Issue。
