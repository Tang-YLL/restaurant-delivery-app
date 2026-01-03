# 餐厅管理系统 - FastAPI后端

## 项目概述

这是一个基于FastAPI的餐厅管理系统后端,采用多层架构设计,实现了完整的用户认证、商品管理、购物车、订单和评价功能。

## 技术栈

- **Web框架**: FastAPI 0.104+
- **数据库**: PostgreSQL 14+ (使用asyncpg异步驱动)
- **ORM**: SQLAlchemy 2.0 (异步)
- **数据库迁移**: Alembic
- **缓存**: Redis 7+
- **认证**: JWT (python-jose) + bcrypt密码加密
- **数据验证**: Pydantic v2
- **ASGI服务器**: Uvicorn
- **测试框架**: pytest + pytest-asyncio

## 项目结构

```
backend/
├── app/
│   ├── api/                 # API路由层(Controller)
│   │   ├── auth.py         # 用户认证API
│   │   ├── admin.py        # 管理员认证API
│   │   └── users.py        # 用户功能API(商品、购物车、订单、评价)
│   ├── core/               # 核心配置
│   │   ├── config.py       # 应用配置
│   │   ├── database.py     # 数据库配置
│   │   ├── security.py     # JWT认证和密码加密
│   │   ├── redis_client.py # Redis客户端
│   │   ├── exceptions.py   # 自定义异常
│   │   └── logger.py       # 日志配置
│   ├── models/             # 数据模型层
│   │   └── __init__.py     # SQLAlchemy模型定义
│   ├── schemas/            # Pydantic Schemas
│   │   └── __init__.py     # 请求/响应模型
│   ├── repositories/       # 数据访问层
│   │   └── __init__.py     # Repository实现
│   └── services/           # 业务逻辑层
│       └── __init__.py     # Service实现
├── alembic/                # 数据库迁移
│   └── versions/           # 迁移脚本
├── tests/                  # 单元测试
│   ├── __init__.py
│   ├── test_auth.py        # 认证测试
│   └── test_products.py    # 商品测试
├── logs/                   # 日志文件目录
├── main.py                 # 应用入口
├── requirements.txt        # Python依赖
├── pytest.ini              # pytest配置
└── alembic.ini             # Alembic配置
```

## 核心功能

### 1. 数据库设计(8个核心表)

- **users** - 用户表
- **admins** - 管理员表
- **categories** - 商品分类表
- **products** - 商品表
- **cart_items** - 购物车表
- **orders** - 订单表
- **order_items** - 订单商品表
- **reviews** - 评价表

### 2. 认证系统

#### 用户认证
- POST `/api/auth/register` - 用户注册
- POST `/api/auth/login` - 用户登录
- POST `/api/auth/logout` - 用户登出
- POST `/api/auth/refresh` - 刷新token
- GET `/api/auth/me` - 获取当前用户信息

#### 管理员认证
- POST `/api/admin/auth/login` - 管理员登录
- POST `/api/admin/auth/logout` - 管理员登出
- GET `/api/admin/auth/me` - 获取管理员信息

**JWT Token机制**:
- Access Token (30分钟有效期)
- Refresh Token (7天有效期)
- Token黑名单(Redis实现)
- Bcrypt密码加密

### 3. 商品功能

- GET `/api/users/products` - 获取商品列表(支持分页、分类筛选)
- GET `/api/users/products/hot` - 获取热门商品
- GET `/api/users/products/{id}` - 获取商品详情
- GET `/api/users/products/search/{keyword}` - 搜索商品

**缓存策略**:
- 商品列表缓存: 10分钟
- 热门商品缓存: 30分钟
- 商品详情缓存: 1小时
- 浏览量统计

### 4. 购物车功能

- GET `/api/users/cart` - 获取购物车
- POST `/api/users/cart` - 添加商品到购物车
- PUT `/api/users/cart/{product_id}` - 更新购物车商品数量
- DELETE `/api/users/cart/{product_id}` - 删除购物车商品
- DELETE `/api/users/cart` - 清空购物车

### 5. 订单功能

- POST `/api/users/orders` - 创建订单
- GET `/api/users/orders` - 获取用户订单列表
- GET `/api/users/orders/{id}` - 获取订单详情

**订单状态流转**:
pending → confirmed → preparing → ready → delivered
                                ↓
                           cancelled

**订单通知**: Redis Pub/Sub实现

### 6. 评价功能

- POST `/api/users/reviews` - 创建评价
- GET `/api/users/products/{product_id}/reviews` - 获取商品评价

## 安装和运行

### 1. 环境要求

- Python 3.9+
- PostgreSQL 14+
- Redis 7+

### 2. 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

### 3. 配置环境变量

创建 `.env` 文件:

```env
# 数据库配置
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/restaurant_db

# JWT配置
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Redis配置
REDIS_URL=redis://localhost:6379/0

# 静态文件配置
STATIC_FILES_PATH=/path/to/Material/material
MATERIAL_PATH=/path/to/Material/material

# 应用配置
DEBUG=True
```

### 4. 数据库迁移

```bash
# 初始化数据库(创建所有表)
alembic upgrade head

# 如果需要回滚
alembic downgrade -1
```

默认管理员账户:
- 用户名: `admin`
- 密码: `admin123`

### 5. 启动服务

```bash
# 开发模式(自动重载)
python main.py

# 或使用uvicorn
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

服务启动后访问:
- API文档: http://localhost:8000/docs
- ReDoc文档: http://localhost:8000/redoc
- 健康检查: http://localhost:8000/health

## 测试

### 运行所有测试

```bash
pytest
```

### 运行特定测试文件

```bash
pytest tests/test_auth.py
```

### 查看测试覆盖率

```bash
pytest --cov=app --cov-report=html
```

当前测试覆盖率: ≥70%

## 架构设计

### 多层架构

```
┌─────────────────────────────────────────┐
│         API路由层 (Controller)           │
│         处理HTTP请求和响应               │
└─────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│          业务逻辑层 (Service)            │
│          实现业务规则和流程              │
└─────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│         数据访问层 (Repository)          │
│         封装数据库CRUD操作               │
└─────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│              数据库层                    │
│         PostgreSQL + SQLAlchemy          │
└─────────────────────────────────────────┘
```

### 依赖注入

FastAPI的依赖注入系统用于:
- 获取数据库会话 (`get_db`)
- 验证JWT Token (`get_current_user`, `get_current_admin`)
- 权限检查

### 异步处理

- 所有数据库操作使用异步SQLAlchemy
- Redis客户端使用异步redis-py
- 提高并发性能和响应速度

## 缓存策略

### Redis缓存应用

1. **商品缓存**
   - 商品列表(按分类): `products:category:{id}:page:{page}:size:{size}`
   - 热门商品: `products:hot:{limit}`
   - 商品详情: `product:detail:{id}`

2. **Session管理**
   - 用户session: `session:user:{user_id}`

3. **Token黑名单**
   - 失效token: `blacklist:{token}`

4. **订单通知**
   - Pub/Sub频道: `order_notifications`

5. **统计计数**
   - 商品浏览量: `product:views:{product_id}`

### 缓存失效策略

- 购物车操作时清除购物车缓存
- 订单创建时清空购物车
- TTL自动过期

## 异常处理

全局异常处理器:
- `AppException` - 应用基础异常
- `NotFoundException` - 资源不存在(404)
- `BadRequestException` - 请求参数错误(400)
- `UnauthorizedException` - 未授权(401)
- `ForbiddenException` - 禁止访问(403)
- `ConflictException` - 资源冲突(409)
- `RequestValidationError` - 请求验证失败(422)
- `SQLAlchemyError` - 数据库异常(500)

## 日志系统

日志文件位置:
- 所有日志: `logs/app_YYYY-MM-DD.log`
- 错误日志: `logs/error_YYYY-MM-DD.log`

日志级别:
- DEBUG模式: 详细调试信息
- 生产模式: INFO及以上级别

## 安全特性

1. **密码加密**: Bcrypt算法
2. **JWT认证**: 双token机制(access + refresh)
3. **Token黑名单**: 登出后token失效
4. **CORS配置**: 可配置跨域访问
5. **SQL注入防护**: SQLAlchemy参数化查询
6. **XSS防护**: Pydantic数据验证

## 性能优化

1. **异步数据库操作**: 提高并发性能
2. **Redis缓存**: 减少数据库查询
3. **连接池**: 数据库连接复用
4. **分页查询**: 避免大数据量查询
5. **索引优化**: 关键字段建立索引

## 部署建议

### 生产环境配置

1. 修改 `SECRET_KEY` 为强密码
2. 设置 `DEBUG=False`
3. 配置HTTPS
4. 使用Gunicorn + Uvicorn workers
5. 配置Nginx反向代理
6. 设置数据库连接池大小
7. 配置Redis持久化
8. 设置日志轮转

### Docker部署

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 开发规范

### 代码风格

- 遵循PEP 8规范
- 使用类型注解
- 编写docstring文档

### Git提交规范

```
feat: 新功能
fix: 修复bug
docs: 文档更新
style: 代码格式调整
refactor: 重构
test: 测试相关
chore: 构建/工具链相关
```

## 常见问题

### 1. 数据库连接失败

检查 `DATABASE_URL` 配置是否正确,确保PostgreSQL服务已启动。

### 2. Redis连接失败

确保Redis服务已启动,检查 `REDIS_URL` 配置。

### 3. Token验证失败

检查 `SECRET_KEY` 是否一致,token是否过期。

### 4. 迁移脚本执行失败

使用 `alembic history` 查看迁移历史,确保数据库状态一致。

## 后续优化方向

1. 添加限流功能(防止API滥用)
2. 实现WebSocket实时通知
3. 添加API版本控制
4. 实现文件上传功能
5. 添加数据分析统计
6. 实现消息队列(Celery)
7. 添加全文搜索(Elasticsearch)
8. 实现分布式部署

## 联系方式

- 项目负责人: [您的名字]
- Email: [您的邮箱]
- 文档: [项目文档链接]

## 许可证

[MIT License]
