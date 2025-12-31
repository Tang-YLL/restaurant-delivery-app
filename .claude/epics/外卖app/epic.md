---
name: 外卖app
status: backlog
created: 2025-12-31T13:44:17Z
progress: 0%
prd: .claude/prds/外卖app.md
github: [Will be updated when synced to GitHub]
---

# Epic: 快餐连锁店外卖配送系统

## Overview

构建一个完整的外卖配送平台,包含Flutter用户移动端、Vue3管理后台和Python后端API服务。系统支持外卖配送和到店自取两种模式,目标日订单量100-500单。采用RESTful API架构,JWT认证,PostgreSQL持久化,Redis缓存优化性能。MVP阶段使用模拟支付,后期支持接入真实支付系统。

**关键优势**: 已有3668个菜品数据和图片资源(Material文件夹),可快速启动开发和测试。

## Architecture Decisions

### 核心技术选型

**前端技术栈**
- **Flutter移动端**: Provider状态管理 + Dio网络请求 + Material Design 3 UI
- **Vue3管理后台**: TypeScript + Vite + Element Plus + Pinia + ECharts数据可视化

**后端技术栈**
- **FastAPI**: 异步高性能、自动OpenAPI文档、原生类型提示
- **SQLAlchemy**: 声明式ORM、数据库迁移管理
- **Redis**: 订单缓存、会话管理、实时通知队列
- **PostgreSQL**: ACID事务、JSON字段支持、高性能查询

**数据存储策略**
- **MVP阶段**: 使用Material文件夹本地图片 + 静态文件服务
- **后期扩展**: 可选云存储(OSS/COS)用于CDN加速

### 架构模式

**三层分离架构**
- 表现层: Flutter移动端 + Vue3管理后台
- 应用层: FastAPI RESTful API服务
- 数据层: PostgreSQL + Redis + 本地静态文件(图片)

**认证授权**
- JWT Token认证(用户端/管理员端分离)
- Rate Limiting防刷
- 密码bcrypt加密

**实时通信**
- WebSocket订单通知(新订单推送到管理后台)
- 轮询备用方案(移动端订单状态刷新)

## Technical Approach

### Phase 0: 数据准备(新增优先阶段)

**核心任务**
1. **数据导入脚本**: 解析Material文件夹3668个JSON文件
2. **静态文件配置**: 配置FastAPI静态文件服务指向Material文件夹
3. **商品分类整理**: 从菜品名称中提取分类标签(热菜、凉菜、汤类、主食等)
4. **数据库初始化**: 导入商品数据和分类到PostgreSQL
5. **数据验证**: 验证JSON完整性、图片文件存在性

**技术实现**
```python
# 数据导入脚本示例
import json
from pathlib import Path

MATERIAL_DIR = Path("Material/material")
def import_dish_data():
    for json_file in MATERIAL_DIR.glob("*.json"):
        with open(json_file) as f:
            data = json.load(f)
        # 解析并导入到数据库
        # image_url使用相对路径: /static/images/xxx.png
```

### Flutter移动端组件

**核心模块**
1. **认证模块**: 手机号登录 + 模拟验证码(1234) + JWT持久化
2. **商品模块**: 分类列表 + 商品卡片 + 详情页 + 搜索 + 收藏
3. **购物车**: 本地状态管理 + 实时金额计算 + 数量调整
4. **订单模块**: 配送方式选择 + 模拟支付 + 订单状态轮询 + 取消订单
5. **评价模块**: 星级评分 + 文字评价 + 图片上传(可选)
6. **个人中心**: 订单历史 + 地址管理 + 个人资料

**状态管理方案**
- Provider全局状态(用户信息、购物车)
- 局部状态(InheritedWidget)
- 持久化(SharedPreferences/Hive)

### Vue3管理后台组件

**核心页面**
1. **登录页**: 管理员认证 + JWT Token
2. **订单管理**: 订单列表(筛选/分页) + 订单详情 + 状态更新 + 声音通知 + 导出CSV
3. **商品管理**: 商品列表 + 商品编辑(本地图片路径) + 分类管理 + 库存管理
4. **数据统计**: 今日概览卡片 + ECharts趋势图 + 热销商品排行
5. **用户管理**: 用户列表 + 用户详情 + 消费统计
6. **评价管理**: 评价列表 + 回复评价 + 删除评价

**技术实现**
- Pinia状态管理(用户信息、订单通知)
- Axios拦截器(JWT注入、错误处理)
- WebSocket实时订单通知
- ECharts数据可视化

### Python后端服务

**API模块设计**

**用户端API** (`/api/`)
- `POST /auth/register` - 用户注册
- `POST /auth/login` - 用户登录
- `GET /products` - 商品列表(分类/搜索/分页)
- `GET /products/{id}` - 商品详情
- `GET /categories` - 分类列表
- `GET/POST/PUT/DELETE /cart` - 购物车CRUD
- `POST /orders` - 创建订单
- `GET /orders` - 用户订单列表
- `GET /orders/{id}` - 订单详情
- `PUT /orders/{id}/cancel` - 取消订单
- `POST /orders/{id}/review` - 提交订单评价

**管理端API** (`/api/admin/`)
- `POST /login` - 管理员登录
- `GET /orders` - 所有订单列表(筛选/分页)
- `PUT /orders/{id}/status` - 更新订单状态
- `GET/POST/PUT /products` - 商品管理CRUD
- `GET/POST/PUT /categories` - 分类管理CRUD
- `GET /statistics` - 统计数据(今日/趋势/热销)
- `GET /users` - 用户列表
- `GET /reviews` - 评价管理

**静态文件服务**
```python
from fastapi.staticfiles import StaticFiles
app.mount("/static", StaticFiles(directory="Material/material"), name="static")
# 访问URL: http://domain/static/菜花炒干虾仁.png
```

**核心业务逻辑**
- 订单状态机: 待接单 → 制作中 → 配送中/待取餐 → 已完成
- 库存扣减: 下单时锁定库存,取消订单释放
- 订单通知: Redis Pub/Sub推送新订单到管理后台
- 数据统计: 异步定时任务预计算统计指标

### 数据库Schema设计

**核心表结构**
```sql
-- 用户表
users(id, phone, password_hash, nickname, avatar, created_at)

-- 分类表
categories(id, name, sort_order, created_at)

-- 商品表
products(id, category_id, name, description, price, image_url, stock, sales_count, is_active, created_at)

-- 购物车表
cart_items(id, user_id, product_id, quantity, created_at)

-- 订单表
orders(id, user_id, order_no, total_amount, delivery_type, delivery_address, pickup_name, pickup_phone, status, remark, created_at)

-- 订单商品表
order_items(id, order_id, product_id, product_name, price, quantity, subtotal)

-- 评价表
reviews(id, order_id, user_id, product_id, rating, content, images, created_at)

-- 管理员表
admins(id, username, password_hash, role, created_at)
```

**索引优化**
- 订单表: (user_id, created_at), (status, created_at)
- 商品表: (category_id, is_active), (name)用于搜索
- 购物车: (user_id)

### Infrastructure & Deployment

**容器化部署**
```yaml
services:
  - flutter-app (打包后的APK/IPA)
  - vue3-admin (Nginx静态托管)
  - fastapi-backend (Gunicorn + Uvicorn)
  - postgresql (官方镜像)
  - redis (官方镜像)
  - nginx (反向代理 + SSL + 静态文件服务)
```

**性能优化**
- Redis缓存: 商品列表、热门商品、统计数据
- 数据库连接池: SQLAlchemy引擎配置
- 本地图片服务: Nginx直接服务Material文件夹图片
- API响应缓存: 统计数据缓存5分钟

**监控告警**
- 日志收集: Python logging + 结构化JSON输出
- 性能监控: API响应时间、数据库查询时间
- 错误追踪: Sentry集成(可选)
- 健康检查: `/health`端点

## Implementation Strategy

### 开发阶段划分

**Phase 0: 数据准备 (1周)**
- 数据导入脚本开发(JSON解析)
- 静态文件服务配置(本地图片)
- 商品分类整理和标签提取
- 数据库初始化和数据导入
- 数据验证和测试

**Phase 1: 基础架构 (1-2周)**
- 项目初始化、Git仓库建立
- 后端FastAPI项目搭建 + 数据库Schema设计
- Flutter项目脚手架 + 基础路由
- Vue3项目脚手架 + UI组件库集成

**Phase 2: 后端API开发 (2周)**
- 用户认证系统(JWT + 模拟验证码)
- 商品/分类CRUD接口
- 购物车接口
- 订单接口(创建、状态更新)
- 评价接口
- 管理后台API(订单管理、商品管理、统计)
- 单元测试编写

**Phase 3: Flutter移动端开发 (2-3周)**
- 登录注册页面
- 商品浏览页面(分类、搜索、详情)
- 购物车功能
- 下单流程(配送方式、模拟支付)
- 订单列表和详情
- 评价功能
- 个人中心
- UI优化和交互细节

**Phase 4: Vue3管理后台开发 (1-2周)**
- 登录页和权限控制
- 订单管理(列表、详情、状态更新、导出)
- 商品管理(列表、编辑、本地图片路径、分类管理)
- 数据统计仪表板(今日概览、趋势图)
- 用户管理和评价管理
- WebSocket实时订单通知

**Phase 5: 联调测试 (1周)**
- 前后端联调
- 功能测试
- 性能测试(并发100用户)
- 安全测试(SQL注入、XSS、Rate Limiting)
- Bug修复

**Phase 6: 部署上线 (1周)**
- Docker镜像构建
- 服务器环境配置
- 数据库迁移
- SSL证书配置
- 生产环境部署
- 监控配置

### 风险缓解措施

**技术风险**
- **风险**: Flutter开发人员不熟悉
- **缓解**: 使用成熟UI组件库、参考官方示例、预留学习时间

**性能风险**
- **风险**: 高峰期并发压力
- **缓解**: Redis缓存、数据库索引优化、连接池配置、负载测试

**集成风险**
- **风险**: 前后端接口对接问题
- **缓解**: 优先开发后端API + OpenAPI文档、Mock数据先行开发前端

### 测试策略

**单元测试**
- Python后端: pytest + coverage ≥ 70%
- 核心业务逻辑必须有测试(订单创建、库存扣减)

**集成测试**
- API接口测试: Postman Collection + 自动化脚本
- 端到端测试: 手动测试核心流程(注册→浏览→下单→评价)

**性能测试**
- Locust并发测试: 模拟100并发用户
- 数据库慢查询监控

## Task Breakdown Preview

任务分解将遵循以下分类(总任务数控制在10个以内):

### Phase 0: 数据准备
- [ ] **数据准备**: Material文件夹数据导入、静态文件配置、商品分类整理

### Phase 1-2: 后端层
- [ ] **后端基础设施**: FastAPI项目、数据库Schema、Redis、JWT认证、Alembic
- [ ] **商品和购物车API**: 商品/分类CRUD、购物车接口、库存管理
- [ ] **订单和评价API**: 订单创建、状态机、评价系统、并发安全
- [ ] **管理后台API**: 管理员认证、订单管理、统计查询、用户管理

### Phase 3: Flutter移动端
- [ ] **Flutter基础框架**: 项目初始化、路由、Provider、Dio、Hive、主题
- [ ] **Flutter核心功能**: 登录、浏览、购物车、下单、订单管理、模拟支付
- [ ] **Flutter高级功能**: 评价、个人中心、地址管理、UI优化、通知

### Phase 4: Vue3管理后台
- [ ] **Vue3管理后台**: 项目搭建、登录认证、订单管理、商品管理、数据统计、实时通知

### Phase 5-6: 测试部署
- [ ] **测试和部署**: 单元测试、API测试、性能测试、Docker部署、生产环境

## Dependencies

### 外部依赖
- **云服务**: 阿里云ECS/腾讯云CVM
- **数据库**: 云数据库或自建PostgreSQL
- **对象存储**: MVP阶段可选(使用本地Material文件夹图片)
- **域名SSL**: 域名购买和SSL证书申请

### 内部依赖
- **菜品数据资源**: Material文件夹包含3668个菜品JSON和PNG文件
- **门店信息**: 配送范围、营业时间
- **测试账号**: 测试用户和管理员账号
- **UI设计**: 品牌Logo、颜色规范(可选,使用组件库默认样式)

### 技术依赖
- **开发工具**: Flutter SDK、Node.js、Python 3.9+
- **开发人员**: Flutter开发1人 + Vue3开发1人 + Python开发1人
- **时间资源**: 6-8周开发周期

## Success Criteria (Technical)

### 性能基准
- **API响应时间**: P95 < 500ms(普通接口), P95 < 1s(数据查询)
- **数据库查询**: 所有查询 < 100ms
- **并发支持**: 100并发用户无性能降级
- **移动端启动**: 冷启动 < 3秒

### 质量标准
- **测试覆盖率**: Python后端 ≥ 70%
- **API成功率**: ≥ 99.5%
- **崩溃率**: Flutter App < 1%
- **可用性**: 系统可用性 ≥ 99%

### 安全要求
- **零重大安全事件**: 无数据泄露、无资金损失
- **认证**: 所有API接口JWT认证
- **密码**: bcrypt加密存储
- **防护**: SQL注入防护、XSS防护、Rate Limiting

### 功能验收
- **核心流程完整性**: 用户可以完成完整下单流程
- **管理后台功能**: 管理员可以处理订单、管理商品、查看统计
- **数据一致性**: 订单状态准确、库存扣减正确、统计数据准确
- **数据指标**: 系统上线时≥3000个商品SKU、≥10个分类、≥95%图片完整性

## Estimated Effort

### 总体时间估算: 6-8周

**开发阶段细分**
- Phase 0(数据准备): 1周
- 后端开发: 3周(包含数据库设计和API开发)
- Flutter开发: 2.5周
- Vue3开发: 1.5周
- 联调测试: 1周
- 部署上线: 1周

**关键路径**
1. 数据准备 → 后端API开发 → Flutter/Vue3功能开发 → 联调测试 → 部署
2. 依赖关系: 前端依赖后端API,数据准备优先

**资源需求**
- 3名开发人员全职投入
- 每周技术评审会议
- 预留20%缓冲时间处理意外问题

**里程碑**
- Week 1: 数据导入完成,后端API框架搭建
- Week 3: 后端API完成,前端Mock数据开发
- Week 5: Flutter和Vue3核心功能完成
- Week 7: 联调测试完成,Beta版本发布
- Week 8: 生产环境部署,正式上线

## Next Steps

Epic重新生成完成，包含Material文件夹数据准备优化。建议执行以下步骤:

1. **查看任务**: 运行 `/pm:epic-show 外卖app` 查看详细任务列表
2. **同步GitHub**: 运行 `/pm:epic-sync 外卖app` 推送到GitHub Issues
3. **开始开发**: 根据任务依赖关系开始并行开发
4. **并行开发**: 运行 `/pm:epic-start 外卖app` 启动多Agent并行开发工作流

## Tasks Created

总任务数: 10个

### Phase 0: 数据准备 (1个任务)
- [ ] **001.md** - 数据准备 - Material文件解析与数据库初始化 (M/16h, parallel: true)
  - 解析Material文件夹3668个JSON文件
  - 配置FastAPI静态文件服务
  - 商品分类整理（热菜、凉菜、汤类、主食等）
  - 数据库初始化和数据验证

### Phase 1-2: 后端层 (4个任务)
- [ ] **002.md** - 后端基础设施 - FastAPI项目架构与数据库设计 (L/24h, depends: [001], parallel: false)
  - FastAPI项目、8个核心数据库表、Redis、JWT认证、Alembic
- [ ] **003.md** - 商品和购物车API实现 (M/16h, depends: [002], parallel: true)
  - 商品/分类CRUD、购物车接口、库存管理、商品搜索
- [ ] **004.md** - 订单和评价API实现 (L/20h, depends: [002,003], parallel: true)
  - 订单创建、状态机、评价系统、并发安全、事务处理
- [ ] **005.md** - 管理后台API实现 (L/20h, depends: [002,003,004], parallel: true)
  - 管理员认证、订单管理、统计查询、用户管理、评价管理

### Phase 3: Flutter移动端 (3个任务)
- [ ] **006.md** - Flutter基础框架搭建 (M/12h, parallel: true)
  - 项目初始化、路由、Provider、Dio、Hive、主题、Mock数据
- [ ] **007.md** - Flutter核心功能开发 (XL/32h, depends: [006], parallel: false)
  - 登录、浏览、购物车、下单、订单管理、模拟支付
- [ ] **008.md** - Flutter高级功能与UI优化 (L/20h, depends: [007], parallel: true)
  - 评价、个人中心、地址管理、UI优化、通知、转场动画

### Phase 4: Vue3管理后台 (1个任务)
- [ ] **009.md** - Vue3管理后台完整开发 (XL/40h, parallel: true)
  - 项目搭建、登录认证、订单管理、商品管理、数据统计、实时通知

### Phase 5-6: 测试部署 (1个任务)
- [ ] **010.md** - 测试和生产环境部署 (L/24h, depends: [005,008,009], parallel: false)
  - 单元测试(≥70%)、API测试、性能测试、Docker部署、生产环境

### 并行性分析
- **可并行任务**: 6个 (001/006/009初期并行, 003/004/005/008中期并行)
- **串行任务**: 4个 (002依赖001, 007依赖006, 010依赖所有功能任务)
- **总工时**: 212小时 ≈ 26.5个工作日 (3人团队约6-8周，含Phase 0数据准备)

### 关键优化点
- ✅ **新增Phase 0**: 优先处理Material文件夹数据导入，快速启动
- ✅ **本地图片服务**: MVP阶段使用本地静态文件，无需云存储
- ✅ **数据驱动开发**: 3668个现成菜品数据，大幅减少录入工作
- ✅ **并行开发策略**: 数据准备完成后，后端、Flutter、Vue3可并行推进
