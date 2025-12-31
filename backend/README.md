# 后端项目说明文档

## 项目结构

```
backend/
├── app/
│   ├── models/            # 数据库模型
│   │   └── __init__.py    # Category和Product模型
│   ├── api/               # API路由(待添加)
│   ├── core/              # 核心配置
│   │   ├── config.py      # 应用配置
│   │   └── database.py    # 数据库连接
│   └── main.py            # FastAPI应用入口
├── scripts/               # 工具脚本
│   ├── analyze_material.py      # Material数据分析(无需DB)
│   └── import_material_data.py  # Material数据导入(需要DB)
├── migrations/            # Alembic迁移配置
│   ├── env.py
│   └── script.py.mako
├── alembic/               # Alembic版本文件
│   └── versions/
│       └── 20241231_init_db.py
├── alembic.ini            # Alembic配置
├── main.py                # FastAPI应用
├── requirements.txt       # Python依赖
├── .env                   # 环境变量
└── .env.example           # 环境变量示例
```

## 安装步骤

### 1. 安装Python依赖

```bash
cd /Volumes/545S/general\ final/backend
pip3 install -r requirements.txt
```

### 2. 配置PostgreSQL数据库

#### 安装PostgreSQL (如未安装)

macOS (使用Homebrew):
```bash
brew install postgresql@14
brew services start postgresql@14
```

#### 创建数据库

```bash
# 创建数据库用户(可选)
psql -U postgres -c "CREATE USER restaurant_user WITH PASSWORD 'your_password';"

# 创建数据库
psql -U postgres -c "CREATE DATABASE restaurant_db OWNER restaurant_user;"

# 或使用默认postgres用户
psql -U postgres -c "CREATE DATABASE restaurant_db;"
```

### 3. 配置环境变量

编辑 `.env` 文件,设置数据库连接:

```env
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/restaurant_db
```

### 4. 初始化数据库

#### 方式1: 使用Alembic迁移

```bash
# 安装Alembic
pip3 install alembic

# 运行迁移
cd /Volumes/545S/general\ final/backend
alembic upgrade head
```

#### 方式2: 直接使用SQLAlchemy创建表

```bash
cd /Volumes/545S/general\ final/backend
python3 -c "from app.core.database import init_db; init_db(); print('数据库初始化完成!')"
```

### 5. 导入Material数据

```bash
cd /Volumes/545S/general\ final/backend
python3 scripts/import_material_data.py
```

## 快速开始

### 快速分析Material数据(无需数据库)

```bash
cd /Volumes/545S/general\ final/backend
python3 scripts/analyze_material.py
```

输出示例:
```
============================================================
Material数据分析报告
============================================================

📁 文件统计:
  - JSON文件: 1834
  - PNG图片: 1834

✓ 成功解析: 1834 条数据
✓ 缺失图片: 0 个

📈 商品分类分布 (共12个分类):
  热菜          :  794 (43.29%)
  主食          :  385 (20.99%)
  素食          :  311 (16.96%)
  ...
```

### 启动FastAPI服务

```bash
cd /Volumes/545S/general\ final/backend
python3 main.py
```

访问:
- API文档: http://localhost:8000/docs
- 静态文件: http://localhost:8000/static/
- 健康检查: http://localhost:8000/health

## 数据库Schema

### Categories(分类表)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| name | String(100) | 分类名称(唯一) |
| code | String(50) | 分类代码(唯一) |
| description | Text | 分类描述 |
| sort_order | Integer | 排序 |
| is_active | Boolean | 是否启用 |
| created_at | DateTime | 创建时间 |
| updated_at | DateTime | 更新时间 |

### Products(商品表)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| title | String(500) | 商品标题 |
| category_id | Integer | 分类ID(外键) |
| detail_url | String(1000) | 详情链接 |
| image_url | String(1000) | 原始图片URL |
| local_image_path | String(1000) | 本地图片路径 |
| ingredients | Text | 食材信息 |
| views | Integer | 浏览量 |
| favorites | Integer | 收藏量 |
| status | Enum | 商品状态 |
| sort_order | Integer | 排序 |
| created_at | DateTime | 创建时间 |
| updated_at | DateTime | 更新时间 |

## 商品分类规则

系统支持15个商品分类,自动从菜品名称中识别:

1. 热菜 - 炒、爆、炸、烧、焖等烹饪方式
2. 凉菜 - 凉拌、凉菜、沙拉
3. 汤类 - 汤、羹、粥
4. 主食 - 饭、面、饺子、馒头
5. 小吃 - 小吃、零食、点心
6. 饮品 - 饮、汁、茶、咖啡
7. 海鲜 - 鱼、虾、蟹、贝
8. 肉类 - 猪肉、牛肉、羊肉、鸡肉
9. 素食 - 蔬菜、菌菇、豆腐
10. 火锅 - 火锅、涮
11. 烧烤 - 烧烤、烤串
12. 甜品 - 甜、糖水、布丁
13. 烘焙 - 面包、蛋糕、饼干
14. 日料 - 寿司、刺身
15. 西餐 - 意面、披萨、牛排

## 数据验证报告

数据导入完成后,系统会生成验证报告并保存到:
- `/Volumes/545S/general final/backend/validation_report.json`

报告内容包括:
- 商品总数
- 分类总数
- 分类分布统计
- 图片完整性
- 缺失图片列表
- 浏览量统计

## 验收标准

✓ **已达成**:
- 数据导入脚本可成功解析所有JSON文件 (1834个)
- 静态文件服务配置正确 (访问路径: /static/菜品名.png)
- 创建12个商品分类(超过要求≥10个)
- 图片完整性100%(超过要求≥95%)

**注**: 实际Material文件夹包含1834个菜品文件,而非预期的3668个。所有文件均已成功解析和分类。

## 常见问题

### Q: 数据库连接失败?

A: 检查以下几点:
1. PostgreSQL服务是否运行
2. `.env`文件中的DATABASE_URL是否正确
3. 数据库用户和密码是否正确

### Q: 静态文件无法访问?

A: 确认 `STATIC_FILES_PATH` 在 `.env` 中设置为正确的Material路径

### Q: Alembic命令不存在?

A: 确保已安装alembic: `pip3 install alembic`

## 下一步

1. 实现完整的REST API (CRUD操作)
2. 添加商品搜索和筛选功能
3. 实现图片上传功能
4. 添加用户认证系统
5. 实现订单管理功能

## 技术栈

- Python 3.9+
- FastAPI 0.104.1
- SQLAlchemy 2.0.23
- Alembic 1.12.1
- PostgreSQL
- Uvicorn (ASGI服务器)
