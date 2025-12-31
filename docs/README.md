# 餐厅管理系统 (Restaurant Management System)

<div align="center">

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.11+-green)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-teal)
![Vue](https://img.shields.io/badge/Vue-3.3+-brightgreen)
![Flutter](https://img.shields.io/badge/Flutter-3.16+-blue)
![License](https://img.shields.io/badge/license-MIT-orange)

一个功能完整的现代化餐厅外卖管理系统,支持移动端、管理后台和完整的外卖业务流程

[快速开始](#快速开始) • [功能特性](#功能特性) • [技术栈](#技术栈) • [部署文档](#部署文档) • [API文档](#api文档)

</div>

---

## 目录

- [项目简介](#项目简介)
- [功能特性](#功能特性)
- [技术架构](#技术架构)
- [快速开始](#快速开始)
- [项目结构](#项目结构)
- [API文档](#api文档)
- [测试](#测试)
- [部署](#部署)
- [贡献指南](#贡献指南)
- [常见问题](#常见问题)
- [许可证](#许可证)

## 项目简介

这是一个功能完整的餐厅管理系统,包含:

- **移动端用户应用** (Flutter) - 支持iOS和Android
- **Web管理后台** (Vue3) - 管理商品、订单、用户等
- **后端API服务** (FastAPI) - RESTful API设计
- **数据库系统** (PostgreSQL + Redis) - 持久化和缓存

### 主要功能

✅ 用户注册登录、手机验证
✅ 商品浏览、搜索、分类
✅ 购物车管理
✅ 订单创建、支付、追踪
✅ 商品评价系统
✅ 管理后台数据分析
✅ 审计日志记录
✅ Docker容器化部署

## 功能特性

### 用户端功能

| 模块 | 功能 |
|------|------|
| **认证** | 手机号注册/登录、短信验证码、JWT认证 |
| **商品** | 商品浏览、分类筛选、搜索、热门推荐 |
| **购物车** | 添加/修改/删除商品、实时同步 |
| **订单** | 创建订单(自取/配送)、在线支付、状态追踪 |
| **评价** | 商品评分、文字评价、查看评价 |

### 管理后台功能

| 模块 | 功能 |
|------|------|
| **仪表盘** | 销售统计、订单统计、用户统计、热门商品 |
| **商品管理** | 商品CRUD、库存管理、上下架、批量操作 |
| **订单管理** | 订单列表、状态更新、订单详情 |
| **用户管理** | 用户列表、用户详情、封禁/解封 |
| **评价管理** | 评价审核、回复评价、删除评价 |
| **数据分析** | 销售趋势、商品排行、用户增长 |
| **审计日志** | 操作记录、日志查询 |

### 技术特性

🔒 **安全**: JWT认证、密码加密、SQL/XSS防护、速率限制
⚡ **高性能**: 异步I/O、Redis缓存、数据库连接池
📦 **容器化**: Docker + Docker Compose一键部署
📱 **跨平台**: Flutter支持iOS/Android, Vue3支持所有现代浏览器
🔧 **易扩展**: RESTful API、模块化设计、微服务架构

## 技术架构

### 技术栈

#### 后端
- **框架**: FastAPI 0.104+
- **数据库**: PostgreSQL 14
- **缓存**: Redis 7
- **ORM**: SQLAlchemy 2.0
- **迁移**: Alembic
- **认证**: JWT (python-jose)
- **文档**: Swagger/OpenAPI

#### 前端管理后台
- **框架**: Vue 3.3+ (Composition API)
- **语言**: TypeScript
- **UI库**: Element Plus
- **构建**: Vite
- **状态管理**: Pinia
- **路由**: Vue Router

#### 移动端
- **框架**: Flutter 3.16+
- **语言**: Dart
- **状态管理**: Provider
- **网络请求**: Dio
- **本地存储**: SharedPreferences

#### 部署
- **容器**: Docker + Docker Compose
- **反向代理**: Nginx
- **Web服务器**: Uvicorn

### 系统架构图

```
┌─────────────┬─────────────┬─────────────┐
│  Flutter    │  Vue3 Admin │   Vue3 Web  │
│  Mobile App │   Backend   │   Frontend  │
└──────┬──────┴──────┬──────┴──────┬──────┘
       │            │             │
       └────────────┴─────────────┘
                    │
         ┌──────────┴──────────┐
         │     Nginx (80/443)  │
         └──────────┬──────────┘
                    │
    ┌───────────────┼───────────────┐
    │               │               │
┌───┴───┐      ┌────┴────┐    ┌───┴────┐
│ FastAPI│      │PostgreSQL│    │ Redis  │
│ :8000  │      │ :5432   │    │ :6379  │
└────────┘      └─────────┘    └────────┘
```

## 快速开始

### 环境要求

- Docker 20.10+
- Docker Compose 2.0+
- Git

### 一键部署

```bash
# 1. 克隆项目
git clone <repository-url>
cd general\ final

# 2. 配置环境变量
cp .env.example .env
nano .env  # 修改必要的配置

# 3. 一键部署
chmod +x deploy.sh
./deploy.sh dev

# 4. 访问应用
# 后端API: http://localhost:8000
# API文档: http://localhost:8000/docs
# 管理后台: http://localhost
```

### 本地开发

#### 后端开发

```bash
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 配置数据库
cp .env.example .env
# 编辑.env配置数据库连接

# 运行迁移
alembic upgrade head

# 启动服务
python main.py
```

#### 前端开发

```bash
cd vue-admin

# 安装依赖
npm install

# 配置API地址
cp .env.development.example .env.development

# 启动开发服务器
npm run dev

# 构建生产版本
npm run build
```

#### 移动端开发

```bash
cd flutter_app

# 获取依赖
flutter pub get

# 运行iOS
flutter run -d ios

# 运行Android
flutter run -d android

# 构建发布版本
flutter build apk
flutter build ios
```

## 项目结构

```
general final/
├── backend/                    # Python FastAPI后端
│   ├── app/                   # 应用代码
│   │   ├── api/              # API路由
│   │   ├── core/             # 核心配置
│   │   ├── models/           # 数据模型
│   │   ├── schemas/          # Pydantic模式
│   │   ├── repositories/     # 数据访问层
│   │   └── services/         # 业务逻辑层
│   ├── tests/                # 测试文件
│   ├── alembic/              # 数据库迁移
│   ├── scripts/              # 工具脚本
│   ├── Dockerfile            # Docker镜像
│   └── main.py               # 应用入口
├── vue-admin/                 # Vue3管理后台
│   ├── src/                  # 源代码
│   │   ├── api/             # API调用
│   │   ├── components/      # 组件
│   │   ├── views/           # 页面
│   │   ├── router/          # 路由
│   │   └── store/           # 状态管理
│   ├── dist/                 # 构建输出
│   └── package.json          # 依赖配置
├── flutter_app/               # Flutter移动端
│   ├── lib/                  # Dart代码
│   │   ├── core/            # 核心功能
│   │   ├── features/        # 功能模块
│   │   └── shared/          # 共享组件
│   └── pubspec.yaml          # 依赖配置
├── Material/                  # 静态资源
├── scripts/                   # 部署脚本
├── docker-compose.yml         # Docker编排
├── nginx.conf                 # Nginx配置
├── deploy.sh                  # 部署脚本
├── DEPLOYMENT.md             # 部署文档
├── PROJECT_SUMMARY.md        # 项目总结
└── README.md                 # 本文件
```

## API文档

### 访问在线文档

启动后端服务后,访问以下地址查看完整的API文档:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 主要API端点

#### 认证
```
POST   /api/v1/auth/register   # 用户注册
POST   /api/v1/auth/login      # 用户登录
POST   /api/v1/auth/logout     # 用户登出
GET    /api/v1/auth/me         # 获取当前用户
```

#### 商品
```
GET    /api/v1/products             # 获取商品列表
GET    /api/v1/products/hot         # 获取热门商品
GET    /api/v1/products/{id}        # 获取商品详情
GET    /api/v1/products/category/{id} # 按分类获取
```

#### 购物车
```
GET    /api/v1/cart           # 获取购物车
POST   /api/v1/cart           # 添加商品
PUT    /api/v1/cart/{id}      # 更新商品
DELETE /api/v1/cart/{id}      # 删除商品
```

#### 订单
```
GET    /api/v1/orders/my      # 获取我的订单
POST   /api/v1/orders         # 创建订单
GET    /api/v1/orders/{id}    # 获取订单详情
```

#### 管理后台
```
POST   /api/v1/admin/auth/login        # 管理员登录
GET    /api/v1/admin/analytics/dashboard # 仪表盘统计
GET    /api/v1/admin/orders            # 订单管理
GET    /api/v1/admin/products          # 商品管理
```

更多API详情请查看在线文档。

## 测试

### 运行测试

```bash
cd backend

# 运行所有测试
pytest

# 运行测试并生成覆盖率报告
pytest --cov=app --cov-report=html

# 查看覆盖率报告
open htmlcov/index.html
```

### 性能测试

```bash
# 使用Locust进行性能测试
./scripts/run_locust.sh http://localhost:8000 100 10

# 访问 http://localhost:8089 查看测试仪表盘
```

### 安全测试

```bash
# 运行安全测试
pytest -m security
```

## 部署

### Docker部署 (推荐)

```bash
# 生产环境部署
./deploy.sh production

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

详细部署说明请查看 [部署文档](DEPLOYMENT.md)。

### 生产环境配置

1. **修改环境变量**: 编辑 `.env.production`
2. **配置SSL证书**: 使用Let's Encrypt免费证书
3. **设置防火墙**: 仅开放80/443端口
4. **配置备份**: 设置定时数据库备份
5. **监控告警**: 配置应用监控和日志收集

### 常用命令

```bash
# 数据库备份
./scripts/backup.sh

# 数据库恢复
docker exec -i restaurant_postgres psql -U postgres restaurant_db < backup.sql

# 查看日志
docker-compose logs -f backend

# 重启服务
docker-compose restart

# 更新服务
git pull
docker-compose up -d --build
```

## 贡献指南

欢迎贡献代码、报告问题或提出建议!

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

### 代码规范

- **Python**: 遵循PEP 8规范,使用Black格式化
- **TypeScript/Vue**: 遵循Vue3风格指南
- **Dart**: 遵循Flutter官方规范

## 常见问题

### 1. Docker容器启动失败?

```bash
# 查看详细日志
docker-compose logs backend

# 检查端口占用
lsof -i :8000
```

### 2. 数据库连接失败?

```bash
# 检查PostgreSQL状态
docker-compose ps postgres

# 验证环境变量
docker-compose exec backend env | grep DATABASE
```

### 3. 前端无法访问后端API?

检查CORS配置和API地址:
```javascript
// vue-admin/.env.development
VITE_API_BASE_URL=http://localhost:8000
```

### 4. 如何重置数据库?

```bash
# 删除所有数据
docker-compose down -v

# 重新初始化
docker-compose up -d
docker-compose exec backend alembic upgrade head
```

更多问题请查看 [部署文档](DEPLOYMENT.md)或提交Issue。

## 相关文档

- [后端API文档](backend/README_BACKEND.md)
- [部署指南](DEPLOYMENT.md)
- [项目总结](PROJECT_SUMMARY.md)
- [API指南](backend/API_GUIDE.md)
- [Vue管理后台文档](vue-admin/README.md)
- [Flutter移动端文档](flutter_app/README.md)

## 技术支持

如有问题或建议,请通过以下方式联系:

- 提交 [GitHub Issues]
- 发送邮件至项目维护者
- 加入讨论组

## 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 致谢

感谢以下开源项目:

- [FastAPI](https://fastapi.tiangolo.com/)
- [Vue.js](https://vuejs.org/)
- [Flutter](https://flutter.dev/)
- [Element Plus](https://element-plus.org/)
- [SQLAlchemy](https://www.sqlalchemy.org/)

---

<div align="center">

**如果这个项目对你有帮助,请给一个 ⭐️**

Made with ❤️ by Project Team

</div>
