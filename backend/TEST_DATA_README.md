# 测试数据导入说明

## 概述

测试种子数据已配置完成，包含：
- **4个商品分类**: 热菜、凉菜、主食、汤类
- **12个示例商品**: 每个分类3个商品

## 自动加载（推荐用于测试）

测试会**自动加载种子数据**，无需手动操作！

每次运行测试时，`tests/conftest.py` 中的 `_seed_test_data()` 函数会自动：
1. 创建测试数据库
2. 导入4个分类
3. 导入12个示例商品

### 商品列表

**热菜** (3个)
- 青椒炒肉 - ¥28.00 (热门)
- 红烧肉 - ¥48.00 (热门)
- 鱼香肉丝 - ¥32.00

**凉菜** (3个)
- 拍黄瓜 - ¥12.00
- 凉拌木耳 - ¥18.00
- 口水鸡 - ¥38.00 (热门)

**主食** (3个)
- 白米饭 - ¥2.00
- 蛋炒饭 - ¥15.00
- 牛肉面 - ¥22.00 (热门)

**汤类** (3个)
- 紫菜蛋花汤 - ¥8.00
- 冬瓜排骨汤 - ¥35.00
- 番茄鸡蛋汤 - ¥12.00

## 手动导入（用于生产/开发）

如需导入完整的Material数据到真实数据库：

### 方法1: 使用导入脚本

```bash
cd backend
python scripts/seed_test_data.py
```

这将从 `/Volumes/545S/general final/Material/material` 导入最多50个商品。

### 方法2: 自定义导入

编辑 `scripts/seed_test_data.py` 中的 `limit` 参数：

```python
await import_products_from_material(
    db=db,
    category_map=category_map,
    material_dir=material_dir,
    limit=100  # 修改为需要的数量
)
```

## 数据源说明

- **路径**: `/Volumes/545S/general final/Material/material`
- **格式**: 每道菜有 `.json` (数据) 和 `.png` (图片) 文件
- **总数**: 约1800+道菜品

### JSON数据结构

```json
{
  "title": "菜名",
  "detail_url": "详情页URL",
  "image_url": "图片URL",
  "ingredients": "食材信息",
  "views_and_favorites": "浏览量",
  "local_image_path": "本地图片路径"
}
```

### 自动分类规则

导入脚本会根据菜名自动分类：

| 分类 | 关键词 |
|------|--------|
| 热菜 | 炒、烧、炖、焖、煮、烩、熘、爆、煎、炸、蒸、烤 |
| 凉菜 | 拌、凉、沙拉、泡菜 |
| 主食 | 饭、面、馒头、包子、饺子、饼、粥、粉、面包、糕 |
| 汤类 | 汤、羹 |
| 甜品 | 糖、甜、奶昔、布丁、果冻 |
| 饮品 | 茶、咖啡、汁、奶、水 |
| 小吃 | 串、卷、薯条、鸡翅、鸡块、丸子 |

### 自动定价规则

基于浏览量自动定价：

| 浏览量 | 价格 |
|--------|------|
| > 50000 | ¥68.00 |
| > 30000 | ¥48.00 |
| > 10000 | ¥38.00 |
| ≤ 10000 | ¥28.00 |

## 运行测试

### 完整测试（带覆盖率）

```bash
./run_tests_with_seed.sh
```

### 快速测试（无覆盖率）

```bash
python -m pytest tests/ -v --tb=short
```

### 只测试特定模块

```bash
# 只测试商品模块
python -m pytest tests/test_products.py -v

# 只测试购物车
python -m pytest tests/test_cart.py -v

# 只测试安全相关
python -m pytest tests/test_security.py -v
```

## 故障排查

### 问题: Material目录找不到

```bash
# 检查目录是否存在
ls -la "/Volumes/545S/general final/Material/material"

# 如果路径不同，修改 scripts/seed_test_data.py 中的 material_dir 变量
```

### 问题: 测试仍然失败

1. 检查种子数据是否加载（测试开始时会有提示）
2. 确认数据库连接正常
3. 查看详细错误信息：`python -m pytest tests/ -vv`

### 问题: 需要更多测试数据

1. 编辑 `tests/conftest.py` 中的 `_seed_test_data()` 函数
2. 添加更多商品到 `products_data` 列表

## 相关文件

- `tests/conftest.py` - 测试配置和种子数据加载
- `scripts/seed_test_data.py` - 手动导入脚本
- `run_tests_with_seed.sh` - 测试运行脚本

## 更新日志

- **2025-01-01**: 初始版本
  - 自动加载4个分类、12个商品
  - 支持从Material目录导入完整数据
  - 自动分类和定价规则
