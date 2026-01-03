# 项目目录结构说明

整理后的清晰项目结构：

```
general final/
│
├── 📄 README.md                    # 项目主文档
├── 📄 CLAUDE.md                    # Claude AI项目说明
├── 📄 .gitignore                   # Git忽略文件配置
├── 🔧 deploy.sh                    # 一键部署脚本
│
├── 📁 backend/                     # Python FastAPI后端
│   ├── app/                        # 应用代码
│   │   ├── api/                    # API路由(60+端点)
│   │   ├── core/                   # 核心配置(数据库、JWT、Redis)
│   │   ├── models/                 # 数据库模型(9个表)
│   │   ├── schemas/                # Pydantic数据验证
│   │   ├── services/               # 业务逻辑层
│   │   └── repositories/           # 数据访问层
│   ├── tests/                      # 测试文件(68个用例)
│   ├── alembic/                    # 数据库迁移
│   ├── scripts/                    # 工具脚本
│   ├── main.py                     # FastAPI应用入口
│   ├── Dockerfile                  # Docker镜像配置
│   └── requirements.txt            # Python依赖
│
├── 📁 flutter_app/                 # Flutter移动端
│   ├── lib/                        # Dart源代码
│   │   ├── data/                   # 数据模型
│   │   ├── presentation/           # UI层
│   │   │   ├── pages/              # 页面(15+个)
│   │   │   ├── providers/          # 状态管理
│   │   │   ├── widgets/            # 通用组件
│   │   │   └── routes/             # 路由配置
│   │   ├── services/               # 服务层
│   │   └── core/                   # 核心配置
│   └── pubspec.yaml                # Flutter依赖配置
│
├── 📁 vue-admin/                   # Vue3管理后台
│   ├── src/                        # Vue3源代码
│   │   ├── api/                    # API接口
│   │   ├── components/             # 组件
│   │   ├── router/                 # 路由配置
│   │   ├── stores/                 # Pinia状态管理
│   │   ├── types/                  # TypeScript类型
│   │   ├── utils/                  # 工具函数
│   │   ├── views/                  # 页面(20+个)
│   │   └── main.ts                 # 应用入口
│   ├── package.json                # Node依赖配置
│   └── vite.config.ts              # Vite构建配置
│
├── 📁 config/                      # 配置文件目录
│   ├── docker-compose.yml          # Docker编排配置
│   ├── nginx.conf                  # Nginx配置
│   ├── .env.example                # 环境变量模板
│   └── .env.production             # 生产环境配置
│
├── 📁 docs/                        # 项目文档目录
│   ├── README.md                   # 项目主文档(从根目录移入)
│   ├── DEPLOYMENT.md               # 部署指南
│   ├── PROJECT_SUMMARY.md          # 项目总结
│   ├── QUICKSTART.md               # 快速开始
│   ├── CHECKLIST.md                # 验收清单
│   ├── TASK010_COMPLETION_REPORT.md # 任务完成报告
│   ├── FINAL_SUMMARY.txt           # 最终总结
│   ├── PROJECT_STRUCTURE.txt       # 项目结构
│   ├── 交付清单.md                  # 交付物清单
│   ├── 任务001-完成报告.md          # 任务报告
│   └── 项目总览.md                  # 项目总览
│
├── 📁 scripts/                     # 工具脚本目录
│   ├── run_tests.sh                # 运行测试
│   ├── run_locust.sh               # 性能测试
│   └── backup.sh                   # 数据备份
│
├── 📁 Material/                    # 静态资源目录
│   └── material/                   # 菜品图片和数据(1834个)
│
└── 📁 .claude/                     # Claude AI配置目录
    ├── agents/                     # AI代理配置
    ├── commands/                   # 自定义命令
    ├── ccpm/                       # 项目管理系统
    ├── epics/                      # Epic任务文件
    ├── prds/                       # PRD文档
    ├── rules/                      # AI规则
    └── scripts/                    # 脚本文件
```

## 整理前后对比

### 整理前 ❌
- 根目录有20+个散落的文档文件
- 配置文件混杂在代码中
- 临时文件未清理
- 目录结构不清晰

### 整理后 ✅
- 根目录只有4个核心文件
- 所有配置文件集中在`config/`
- 所有文档集中在`docs/`
- 清晰的三层架构结构
- 临时文件已清理

## 文件说明

### 根目录文件
- **README.md** - 项目主文档，包含项目介绍、快速开始、技术栈等
- **CLAUDE.md** - Claude AI的项目说明文件
- **deploy.sh** - 一键部署脚本，支持开发/生产环境
- **.gitignore** - Git版本控制忽略文件配置

### config/ 目录
存放所有配置文件，包括：
- Docker编排配置
- Nginx反向代理配置
- 环境变量配置

### docs/ 目录
存放所有项目文档，包括：
- 部署指南
- API文档
- 项目总结
- 快速开始指南

### scripts/ 目录
存放工具脚本，包括：
- 测试脚本
- 性能测试脚本
- 备份脚本

## 快速访问

### 开发相关
- 后端代码: `backend/`
- 移动端代码: `flutter_app/`
- 管理后台代码: `vue-admin/`

### 配置相关
- Docker配置: `config/docker-compose.yml`
- 环境变量: `config/.env.example`
- Nginx配置: `config/nginx.conf`

### 文档相关
- 快速开始: `docs/QUICKSTART.md`
- 部署指南: `docs/DEPLOYMENT.md`
- 项目总结: `docs/PROJECT_SUMMARY.md`

### 脚本相关
- 一键部署: `./deploy.sh`
- 运行测试: `scripts/run_tests.sh`
- 性能测试: `scripts/run_locust.sh`

## 维护建议

1. **添加新功能时**
   - 后端功能: 在`backend/app/`下创建对应模块
   - 移动端功能: 在`flutter_app/lib/presentation/pages/`下创建页面
   - 管理后台功能: 在`vue-admin/src/views/`下创建页面

2. **添加新文档时**
   - 统一放在`docs/`目录下
   - 更新本文件的文档列表

3. **添加新配置时**
   - 统一放在`config/`目录下
   - 在`config/.env.example`中添加注释说明

4. **添加新脚本时**
   - 统一放在`scripts/`目录下
   - 添加可执行权限: `chmod +x scripts/xxx.sh`

## 清理完成的文件

已清理以下临时和散落的文件：
- ✅ 删除 `.spec-workflow/` (临时工作目录)
- ✅ 删除 `.DS_Store` (macOS系统文件)
- ✅ 移动所有文档到 `docs/` 目录
- ✅ 移动所有配置到 `config/` 目录

项目现在结构清晰，易于维护和部署！
