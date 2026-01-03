# 🍔 餐厅外卖配送系统

一个完整的快餐连锁店外卖配送平台，包含Flutter移动端、Vue3管理后台和Python后端API服务。

## ✨ 项目特性

- 📱 **Flutter移动端** - 支持iOS和Android的现代化外卖App
- 💻 **Vue3管理后台** - 功能强大的Web管理界面
- 🚀 **FastAPI后端** - 高性能异步Python后端
- 📦 **Docker部署** - 一键容器化部署
- 🔒 **安全可靠** - JWT认证 + 多重安全防护
- ⚡ **高性能** - 异步I/O + Redis缓存
- 📊 **数据统计** - 完整的数据分析和可视化

## 🚀 快速开始

### 方式1: Docker一键部署 (推荐)

```bash
# 克隆项目
cd "/Volumes/545S/general final"

# 配置环境变量
cp config/.env.example config/.env
nano config/.env  # 修改数据库密码等配置

# 一键启动
chmod +x deploy.sh
./deploy.sh dev

# 访问应用
# 后端API: http://localhost:8000
# API文档: http://localhost:8000/docs
# 管理后台: http://localhost
```

### 方式2: 手动启动

**后端API**:
```bash
cd backend
pip install -r requirements.txt
alembic upgrade head
python main.py
# 访问: http://localhost:8000/docs
```

**Vue3管理后台**:
```bash
cd vue-admin
npm install
npm run dev
# 访问: http://localhost:5173
# 登录: admin / admin123
```

**Flutter移动端**:
```bash
cd flutter_app
flutter pub get
flutter run
# 测试登录: 任意11位手机号 / 验证码1234
```

## 📁 项目结构

```
.
├── backend/          # Python FastAPI后端
│   ├── app/         # 应用代码
│   ├── tests/       # 测试文件(68个用例)
│   └── main.py      # 应用入口
├── flutter_app/     # Flutter移动端
│   └── lib/         # Dart代码
├── vue-admin/       # Vue3管理后台
│   └── src/         # Vue3代码
├── Material/        # 静态资源(1834个菜品)
├── config/          # 配置文件
│   ├── docker-compose.yml
│   ├── nginx.conf
│   └── .env.production
├── scripts/         # 工具脚本
├── docs/            # 项目文档
├── deploy.sh        # 一键部署脚本
└── README.md        # 本文件
```

## 🔑 默认账号

**管理员后台**:
- 用户名: `admin`
- 密码: `admin123`

**移动端测试**:
- 手机号: 任意11位号码
- 验证码: `1234`

## 📚 文档

### 项目文档
- [部署指南](docs/DEPLOYMENT.md) - 完整的部署步骤
- [项目总结](docs/PROJECT_SUMMARY.md) - 详细的技术总结
- [快速开始](docs/QUICKSTART.md) - 5分钟快速启动
- [API文档](docs/API_GUIDE.md) - 后端API使用指南
- [文档归档](docs/ARCHIVE_README.md) - 开发日志、脚本和报告

### 开发报告
- [总体测试报告](docs/reports/TEST_REPORT.md) - 总体测试报告
- [API兼容性报告](docs/reports/API_COMPATIBILITY_REPORT.md) - API兼容性报告
- [项目交付清单](docs/reports/交付清单.md) - 项目交付清单
- [后端报告](docs/reports/backend/) - 后端开发报告
- [Vue管理后台报告](docs/reports/vue-admin/) - Vue管理后台报告
- [Flutter移动端报告](docs/reports/flutter/) - Flutter移动端报告

## 🛠️ 技术栈

### 后端
- **框架**: FastAPI + SQLAlchemy 2.0 (异步)
- **数据库**: PostgreSQL 14 + Redis 7
- **认证**: JWT (用户端 + 管理端分离)
- **测试**: pytest (68个测试用例)

### 移动端
- **框架**: Flutter 3.19+ (Dart)
- **状态管理**: Provider
- **网络**: Dio (JWT自动注入)
- **存储**: Hive (本地持久化)

### 管理后台
- **框架**: Vue 3.3 + TypeScript
- **构建**: Vite 5.0
- **UI库**: Element Plus
- **图表**: ECharts 6.0

## 📊 项目统计

- API端点: 60+个
- 数据表: 9个
- 代码行数: ~13,000行
- 测试用例: 68个
- Flutter页面: 15+个
- Vue3页面: 20+个

## 🔧 常用命令

```bash
# Docker部署
./deploy.sh dev          # 开发环境
./deploy.sh production   # 生产环境

# 查看日志
cd config && docker-compose logs -f

# 停止服务
cd config && docker-compose down

# 重启服务
cd config && docker-compose restart

# 运行测试
cd backend && pytest

# 性能测试
cd backend && locust -f locustfile.py
```

## 🎯 功能清单

### 📱 移动端功能
- ✅ 手机号验证码登录
- ✅ 商品浏览(分类、搜索、筛选)
- ✅ 购物车管理
- ✅ 下单流程(外卖/自取)
- ✅ 订单管理和状态跟踪
- ✅ 商品评价(星级+图片)
- ✅ 收货地址管理
- ✅ 商品收藏
- ✅ 个人中心

### 💻 管理后台功能
- ✅ 数据统计仪表板
- ✅ 订单管理(查询、更新、导出)
- ✅ 商品管理(CRUD、库存)
- ✅ 用户管理
- ✅ 评价管理
- ✅ WebSocket实时订单通知

### 🔧 后端API
- ✅ 用户认证系统
- ✅ 商品管理API
- ✅ 购物车API
- ✅ 订单系统API
- ✅ 评价系统API
- ✅ 管理后台API
- ✅ 统计分析API

## 📖 许可证

本项目采用 MIT 许可证。

## 🙏 致谢

感谢使用本系统！如有问题，请查看[文档](docs/)或提交Issue。
