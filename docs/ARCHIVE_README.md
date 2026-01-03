# 项目文档归档

本目录包含项目开发过程中的各类文档、日志和脚本归档。

## 目录结构

```
docs/
├── logs/           # 应用日志文件
├── scripts/        # 测试和辅助脚本
├── reports/        # 项目报告和文档
│   ├── backend/    # 后端相关报告
│   ├── vue-admin/  # Vue管理后台报告
│   └── flutter/    # Flutter移动端报告
└── README.md       # 本文件
```

## 日志文件 (logs/)

- `app_YYYY-MM-DD.log` - 按日期归档的应用日志
- `app.log` - 当前应用日志
- `error_YYYY-MM-DD.log` - 按日期归档的错误日志
- `backend.log` - 后端服务日志
- `test_results.log` - 测试结果日志
- `test-results.log` - 测试执行日志
- `vite.log` - Vue 开发服务器日志

## 脚本文件 (scripts/)

### 临时测试脚本
- `generate_product_data.py` - 生成商品测试数据
- `generate_product_test_data.py` - 生成商品详情测试数据
- `insert_test_reviews.py` - 插入测试评论数据

### 后端测试脚本
- `test_admin_api.py` - 管理后台 API 测试
- `test_api_content_sections.py` - 商品详情 API 测试
- `test_db_models.py` - 数据库模型测试
- `test_downgrade.py` - 数据库降级测试
- `test_image_upload.py` - 图片上传测试
- `test_token_debug.py` - Token 调试脚本

## 报告文档 (reports/)

### 后端报告 (backend/)
- `ADMIN_API_DOCUMENTATION.md` - 管理后台 API 文档
- `ADMIN_IMPLEMENTATION_SUMMARY.md` - 管理后台实现总结
- `ADMIN_TEST_REPORT.md` - 管理后台测试报告
- `API_DOCUMENTATION.md` - API 文档
- `API_GUIDE.md` - API 使用指南
- `API_TESTING_GUIDE.md` - API 测试指南
- `CHECKLIST.md` - 后端开发检查清单
- `IMAGE_UPLOAD_TEST.md` - 图片上传测试文档
- `ORDERS_AND_REVIEWS_API_GUIDE.md` - 订单和评论 API 指南
- `TASK_003_SUMMARY.md` - 任务 003 总结
- `TASK_004_SUMMARY.md` - 任务 004 总结
- `TEST_DATA_README.md` - 测试数据说明

### Vue 管理后台报告 (vue-admin/)
- `ADMIN-003-SUMMARY.md` - 管理后台 003 功能总结
- `IMAGE_CATEGORY_FIX.md` - 图片分类修复说明
- `ISSUE_015_SUMMARY.md` - 问题 015 总结
- `PLAYWRIGHT_TEST_REPORT.md` - E2E 测试报告
- `PRODUCT_FIXES.md` - 商品管理修复说明
- `PROJECT_SUMMARY.md` - 项目总结
- `QUICKSTART.md` - 快速开始指南
- `README_TESTING.md` - 测试说明
- `README.md` - Vue 管理后台说明
- `TESTING_REPORT.md` - 测试报告

### Flutter 移动端报告 (flutter/)
- `INTEGRATION_TEST_REPORT.md` - 集成测试报告
- `MIGRATION_GUIDE.md` - 迁移指南
- `PROJECT_SETUP.md` - 项目设置说明
- `README.md` - Flutter 移动端说明
- `TEST_REPORT.md` - 测试报告

### 项目总体报告
- `API_COMPATIBILITY_REPORT.md` - API 兼容性报告
- `TEST_REPORT.md` - 总体测试报告
- `TASK010_COMPLETION_REPORT.md` - 任务 010 完成报告
- `交付清单.md` - 项目交付清单
- `任务001-完成报告.md` - 任务 001 完成报告
- `项目总览.md` - 项目总览

## 注意事项

1. **日志文件** 不应提交到版本控制系统
2. **脚本文件** 仅用于开发测试，生产环境不使用
3. **报告文件** 记录了开发过程，可作为参考

## 清理策略

- 日志文件：保留最近 7 天的日志
- 测试脚本：保留用于回归测试
- 报告文档：永久保留作为历史记录

## 相关文件

- 主项目 README: `/README.md`
- 项目文档: `/docs/`
- Epic 归档: `/.claude/epics/.archived/`
