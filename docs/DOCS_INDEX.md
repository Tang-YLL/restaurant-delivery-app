# 项目文档说明

## 📁 目录结构

```
general final/
├── README.md                  # 项目主文档(快速开始)
├── deploy.sh                  # 一键部署脚本
│
├── backend/                   # Python后端
├── flutter_app/               # Flutter移动端
├── vue-admin/                 # Vue3管理后台
│
├── config/                    # 配置文件
│   ├── docker-compose.yml
│   ├── nginx.conf
│   └── .env.production
│
├── docs/                      # 📖 正式项目文档
│   ├── README.md              # 项目主文档(复制)
│   ├── DEPLOYMENT.md          # 部署指南
│   ├── PROJECT_SUMMARY.md     # 项目总结
│   ├── QUICKSTART.md          # 快速开始(5分钟)
│   ├── CHECKLIST.md           # 验收清单
│   └── PROJECT_STRUCTURE.md   # 目录结构说明
│
├── reports/                   # 📊 开发过程报告
│   ├── 任务001-完成报告.md     # 任务完成报告
│   ├── 项目总览.md            # 项目总览
│   ├── 交付清单.md            # 交付物清单
│   ├── TASK010_COMPLETION_REPORT.md
│   ├── FINAL_SUMMARY.txt
│   └── PROJECT_STRUCTURE.txt
│
├── scripts/                   # 工具脚本
└── Material/                  # 静态资源
```

## 📖 docs/ - 正式项目文档

存放**正式的项目文档**，供日常维护和部署使用：

| 文件 | 说明 |
|------|------|
| **README.md** | 项目主文档，包含介绍、快速开始、技术栈 |
| **DEPLOYMENT.md** | 完整的部署指南(系统要求、步骤、故障排查) |
| **PROJECT_SUMMARY.md** | 项目详细总结(架构、API、数据库) |
| **QUICKSTART.md** | 5分钟快速启动指南 |
| **CHECKLIST.md** | 项目验收清单 |
| **PROJECT_STRUCTURE.md** | 目录结构说明 |

## 📊 reports/ - 开发过程报告

存放**开发过程中的临时报告**，记录任务完成情况：

| 文件 | 说明 |
|------|------|
| **任务001-完成报告.md** | 任务001的数据准备报告 |
| **项目总览.md** | 项目开发初期的总览 |
| **交付清单.md** | 任务001的交付物清单 |
| **TASK010_COMPLETION_REPORT.md** | 最后任务的完成报告 |
| **FINAL_SUMMARY.txt** | 项目最终总结 |
| **PROJECT_STRUCTURE.txt** | 旧版目录结构说明 |

> 💡 **注意**: `reports/` 目录中的文件是开发过程中的临时记录，不需要特别维护。

## 🎯 使用建议

### 日常开发
参考 `docs/` 目录下的文档

### 查看项目状态
查看 `reports/` 目录下的报告文件

### 新增文档
- **正式文档** → 放在 `docs/`
- **临时报告** → 放在 `reports/`

### 部署项目
```bash
# 快速开始
cat docs/QUICKSTART.md

# 完整部署
cat docs/DEPLOYMENT.md
./deploy.sh dev
```

## 📂 文档分类

### 面向用户
- **README.md** - 了解项目
- **QUICKSTART.md** - 快速上手

### 面向开发者
- **DEPLOYMENT.md** - 部署配置
- **PROJECT_SUMMARY.md** - 技术细节
- **PROJECT_STRUCTURE.md** - 代码结构

### 面向项目管理
- **CHECKLIST.md** - 验收标准
- **reports/** - 任务完成情况
