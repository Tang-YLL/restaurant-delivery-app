---
name: 增加商品详情介绍
status: completed
created: 2026-01-02T15:38:30Z
updated: 2026-01-03T06:33:07Z
completed: 2026-01-03T06:33:07Z
progress: 100%
prd: .claude/prds/增加商品详情介绍.md
github: [Will be updated when synced to GitHub]
---

# Epic: 增加商品详情介绍

## Overview

本Epic旨在为商品详情页添加富文本内容展示能力，通过扩展后端数据模型、开发管理后台编辑器、优化移动端渲染，实现商品详细信息的全面展示，包括制作工艺、营养成分、食材来源等内容。

**技术目标**：
- 扩展商品数据模型支持富文本和分区内容
- 实现管理后台富文本编辑功能
- 优化移动端内容渲染性能
- 确保首屏加载 < 2秒

---

## Architecture Decisions

### 1. 数据存储策略

**决策**：采用分区内容存储而非单一大文本

**理由**：
- ✅ 便于内容复用和维护
- ✅ 支持灵活的内容展示顺序
- ✅ 便于实现多语言扩展
- ✅ 支持内容版本控制

**实现**：
- 创建`content_sections`表存储不同类型的内容分区
- 使用JSON字段存储富文本HTML内容
- 通过`display_order`字段控制展示顺序

### 2. 富文本编辑器选择

**决策**：使用Quill.js作为管理后台编辑器

**理由**：
- ✅ 轻量级（~100KB gzipped）
- ✅ 丰富的API和扩展性
- ✅ 良持Vue3生态
- ✅ 开源免费

**备选方案**：TinyMCE（功能更强大但体积较大）

### 3. 内容渲染方式

**决策**：移动端使用flutter_html渲染富文本

**理由**：
- ✅ Flutter生态最成熟的HTML渲染库
- ✅ 支持CSS样式和自定义渲染
- ✅ 性能可控（支持懒加载）
- ✅ 社区活跃，文档完善

**性能优化**：
- 图片懒加载
- 分段渲染（按内容分区）
- 预加载关键内容

### 4. 图片处理方案

**决策**：保持现有本地存储，预留云存储接口

**理由**：
- ✅ MVP阶段快速开发
- ✅ 降低初期成本
- ✅ 预留CDN迁移路径

**实现**：
- 复用现有图片上传API
- 使用WebP格式压缩图片
- 实现图片懒加载

---

## Technical Approach

### Frontend Components

#### 管理后台（Vue3）

**1. 商品详情编辑器组件**
```vue
<!-- ProductDetailEditor.vue -->
<template>
  <div class="product-detail-editor">
    <!-- 分区管理 -->
    <SectionManager
      v-model="sections"
      @add="addSection"
      @remove="removeSection"
      @reorder="reorderSections"
    />

    <!-- 富文本编辑器 -->
    <QuillEditor
      v-model="currentSection.content"
      :options="editorOptions"
      @imageUpload="handleImageUpload"
    />

    <!-- 预览 -->
    <ContentPreview
      :content="currentSection.content"
      :type="currentSection.type"
    />
  </div>
</template>
```

**关键功能**：
- 分区拖拽排序
- 实时预览
- 图片上传和裁剪
- 内容模板选择

**2. 营养成分表组件**
```vue
<!-- NutritionTable.vue -->
<template>
  <el-table :data="nutritionData" border>
    <el-table-column prop="nutrient" label="营养成分" />
    <el-table-column prop="per100g" label="每100克" />
    <el-table-column prop="perServing" label="每份" />
    <el-table-column prop="nrv" label="NRV%" />
  </el-table>
</template>
```

#### 移动端（Flutter）

**1. 商品详情页重构**
```dart
class ProductDetailPage extends StatelessWidget {
  Widget buildContentSections(List<ContentSection> sections) {
    return ListView.builder(
      itemCount: sections.length,
      itemBuilder: (context, index) {
        final section = sections[index];

        switch (section.type) {
          case 'story':
            return StorySectionWidget(section: section);
          case 'nutrition':
            return NutritionTableWidget(section: section);
          case 'process':
            return ProcessSectionWidget(section: section);
          default:
            return HtmlContentWidget(section: section);
        }
      },
    );
  }
}
```

**关键Widget**：
- `HtmlContentWidget`：使用flutter_html渲染富文本
- `NutritionTableWidget`：营养成分表格展示
- `ProcessSectionWidget`：制作步骤图文展示
- `LazyLoadImage`：图片懒加载组件

**2. 性能优化**
```dart
// 使用AutomaticKeepAliveClientMixin保持滚动位置
class ProductDetailPageState extends State<ProductDetailPage>
    with AutomaticKeepAliveClientMixin {
  @override
  bool get wantKeepAlive => true;

  // 图片缓存
  final CachedNetworkImageProvider imageProvider;

  // 预加载下一屏内容
  void _preloadNextSection(int currentIndex) {
    if (currentIndex < sections.length - 1) {
      precacheImage(WidgetProvider(sections[currentIndex + 1].heroImage));
    }
  }
}
```

### Backend Services

#### 1. 数据模型扩展

**新增表**：

```sql
-- 商品详情内容分区表
CREATE TABLE content_sections (
    id INTEGER PRIMARY KEY,
    product_id INTEGER NOT NULL,
    section_type VARCHAR(50) NOT NULL,  -- story, nutrition, ingredients, process, tips
    title VARCHAR(200),
    content TEXT NOT NULL,  -- 富文本HTML内容
    display_order INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
);

-- 营养成分表
CREATE TABLE nutrition_facts (
    id INTEGER PRIMARY KEY,
    product_id INTEGER NOT NULL,
    serving_size VARCHAR(50),  -- 如："1份(200g)"
    calories REAL,  -- 热量(kcal/100g)
    protein REAL,  -- 蛋白质(g/100g)
    fat REAL,  -- 脂肪(g/100g)
    carbohydrates REAL,  -- 碳水(g/100g)
    sodium REAL,  -- 钠(mg/100g)
    dietary_fiber REAL,  -- 膳食纤维(g/100g)
    sugars REAL,  -- 糖(g/100g)
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
);

-- 索引优化
CREATE INDEX idx_content_sections_product ON content_sections(product_id);
CREATE INDEX idx_content_sections_type ON content_sections(section_type);
CREATE INDEX idx_nutrition_facts_product ON nutrition_facts(product_id);
```

**现有表扩展**：
```sql
-- products表已有description字段，可继续使用简短描述
-- 新增字段可选：
ALTER TABLE products ADD COLUMN detail_description TEXT;  -- 长描述
ALTER TABLE products ADD COLUMN ingredients_list TEXT;  -- 食材列表
```

#### 2. API端点设计

```python
# 商品详情内容管理API
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/admin/products/{product_id}/details", tags=["商品详情管理"])

# 获取商品详情内容
@router.get("")
async def get_product_detail_sections(
    product_id: int,
    db: AsyncSession = Depends(get_db)
):
    """返回商品的所有内容分区"""
    pass

# 创建或更新内容分区
@router.post("/sections", response_model=MessageResponse)
async def upsert_content_section(
    product_id: int,
    section_data: ContentSectionCreate,
    db: AsyncSession = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """创建或更新商品详情内容分区"""
    pass

# 批量保存内容分区
@router.put("/sections/batch", response_model=MessageResponse)
async def batch_update_sections(
    product_id: int,
    sections: List[ContentSectionCreate],
    db: AsyncSession = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """批量保存多个内容分区"""
    pass

# 上传内容图片
@router.post("/images/upload", response_model=ImageUploadResponse)
async def upload_detail_image(
    file: UploadFile,
    product_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """上传商品详情图片（支持裁剪和压缩）"""
    pass

# 营养成分管理
@router.put("/nutrition", response_model=MessageResponse)
async def update_nutrition_facts(
    product_id: int,
    nutrition_data: NutritionFactsCreate,
    db: AsyncSession = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """更新营养成分信息"""
    pass

# 删除内容分区
@router.delete("/sections/{section_id}", response_model=MessageResponse)
async def delete_content_section(
    section_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """删除指定内容分区"""
    pass

# 用户端API
@router.get("/products/{product_id}/full-details")
async def get_full_product_details(
    product_id: int,
    db: AsyncSession = Depends(get_db)
):
    """返回完整商品详情（包含所有分区内容）"""
    pass
```

#### 3. 业务逻辑组件

**服务层架构**：

```python
# app/services/product_detail_service.py
class ProductDetailService:
    async def get_full_details(self, product_id: int, db: AsyncSession) -> dict:
        """获取商品完整详情（所有分区）"""
        pass

    async def save_content_section(
        self,
        section_data: ContentSectionCreate,
        db: AsyncSession
    ) -> ContentSection:
        """保存内容分区"""
        pass

    async def batch_update_sections(
        self,
        product_id: int,
        sections: List[ContentSectionCreate],
        db: AsyncSession
    ):
        """批量更新内容分区"""
        pass

    def sanitize_html(self, html_content: str) -> str:
        """HTML内容安全过滤（防XSS）"""
        from bleach import clean
        return clean(
            html_content,
            tags=['p', 'h1', 'h2', 'h3', 'strong', 'em', 'ul', 'ol', 'li',
                  'img', 'br', 'div', 'span', 'table', 'tr', 'td', 'th'],
            attributes={
                '*': ['class'],
                'img': ['src', 'alt', 'width', 'height'],
                'a': ['href', 'title']
            }
        )
```

### Infrastructure

#### 1. 数据库迁移

```python
# alembic/versions/xxx_add_product_details.py
from alembic import op
import sqlalchemy as sa

def upgrade():
    # 创建content_sections表
    op.create_table(
        'content_sections',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('section_type', sa.String(50), nullable=False),
        sa.Column('title', sa.String(200)),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('display_order', sa.Integer(), default=0),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ondelete='CASCADE')
    )
    op.create_index('idx_content_sections_product', 'content_sections', ['product_id'])

    # 创建nutrition_facts表
    op.create_table(
        'nutrition_facts',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('serving_size', sa.String(50)),
        sa.Column('calories', sa.Float()),
        sa.Column('protein', sa.Float()),
        sa.Column('fat', sa.Float()),
        sa.Column('carbohydrates', sa.Float()),
        sa.Column('sodium', sa.Float()),
        sa.Column('dietary_fiber', sa.Float()),
        sa.Column('sugars', sa.Float()),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ondelete='CASCADE')
    )
    op.create_index('idx_nutrition_facts_product', 'nutrition_facts', ['product_id'])

def downgrade():
    op.drop_table('content_sections')
    op.drop_table('nutrition_facts')
```

#### 2. 图片处理优化

```python
# app/utils/image_processor.py
from PIL import Image
import io

class ImageProcessor:
    @staticmethod
    def process_uploaded_image(
        image_data: bytes,
        max_width: int = 800,
        quality: int = 85
    ) -> bytes:
        """处理上传的图片：调整尺寸、压缩、转WebP"""
        img = Image.open(io.BytesIO(image_data))

        # 调整尺寸（保持宽高比）
        ratio = max_width / img.width if img.width > max_width else 1
        new_size = (int(img.width * ratio), int(img.height * ratio))
        img = img.resize(new_size, Image.LANCZOS)

        # 转换为RGB（处理RGBA）
        if img.mode in ('RGBA', 'LA'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[-1])
            img = background

        # 压缩为JPEG
        output = io.BytesIO()
        img.save(output, format='JPEG', quality=quality, optimize=True)
        return output.getvalue()
```

#### 3. 性能监控

```python
# 添加性能监控日志
import time
from functools import wraps

def log_performance(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start = time.time()
        result = await func(*args, **kwargs)
        duration = time.time() - start

        print(f"⏱️ [Performance] {func.__name__}: {duration:.3f}s")

        if duration > 1.0:  # 超过1秒警告
            print(f"⚠️ [Slow Query] {func.__name__} took {duration:.3f}s")

        return result
    return wrapper

# 使用示例
@log_performance
async def get_full_product_details(product_id: int, db: AsyncSession):
    pass
```

---

## Implementation Strategy

### Phase 1: 数据层和后端API（Day 1-3）

**目标**：完成数据模型设计和基础API

**任务**：
1. 设计并创建数据库表结构
2. 编写Alembic迁移脚本
3. 实现ProductDetailService服务层
4. 开发商品详情CRUD API端点
5. 实现图片上传和处理逻辑
6. 编写单元测试（覆盖率>80%）

**验收标准**：
- ✅ 数据库表创建成功
- ✅ API可通过Postman测试
- ✅ 单元测试全部通过
- ✅ API响应时间 < 200ms

**关键依赖**：现有Product模型、数据库连接

### Phase 2: 管理后台编辑功能（Day 4-6）

**目标**：完成管理后台富文本编辑器

**任务**：
1. 集成Quill.js富文本编辑器
2. 开发分区管理组件（增删改排序）
3. 实现图片上传和预览功能
4. 开发营养成分表编辑器
5. 实现内容模板功能
6. 前后端联调测试

**验收标准**：
- ✅ 可以创建和编辑5种类型的内容分区
- ✅ 富文本编辑器功能完整
- ✅ 图片上传成功率100%
- ✅ 内容预览正确显示
- ✅ 批量保存功能正常

**关键依赖**：Vue3、Element Plus、Quill.js、后端API

### Phase 3: 移动端详情页展示（Day 7-9）

**目标**：完成移动端详情页渲染和优化

**任务**：
1. 设计并实现分区内容Widget
2. 集成flutter_html渲染富文本
3. 实现图片懒加载和缓存
4. 优化滚动性能（预加载、KeepAlive）
5. 实现加载骨架屏
6. 性能测试和优化

**验收标准**：
- ✅ 详情页首屏加载 < 2秒
- ✅ 滚动流畅（60fps）
- ✅ 图片加载无卡顿
- ✅ 支持iOS和Android
- ✅ 内存占用 < 150MB

**关键依赖**：flutter_html、cached_network_image、后端API

### Phase 4: 测试和上线（Day 10）

**目标**：完成测试、优化和上线

**任务**：
1. 功能测试（全部用户故事）
2. 性能测试（压力测试、加载速度）
3. 安全测试（XSS、SQL注入）
4. 兼容性测试（不同设备）
5. Bug修复和优化
6. 编写用户文档
7. 灰度发布（10%用户）

**验收标准**：
- ✅ 所有P0、P1功能测试通过
- ✅ 性能指标达标
- ✅ 无安全漏洞
- ✅ 用户文档完整
- ✅ 灰度发布无重大问题

**关键依赖**：测试团队、运维团队

---

## Task Breakdown Preview

- [ ] **DB-001**: 设计和创建商品详情数据模型（content_sections、nutrition_facts表）
- [ ] **API-001**: 开发商品详情内容CRUD API（获取、创建、更新、删除分区）
- [ ] **API-002**: 开发图片上传和处理API（裁剪、压缩、WebP转换）
- [ ] **API-003**: 开发营养成分管理API（创建、更新、删除）
- [ ] **ADMIN-001**: 实现管理后台富文本编辑器组件（集成Quill.js）
- [ ] **ADMIN-002**: 实现分区管理功能（拖拽排序、批量操作）
- [ ] **ADMIN-003**: 实现营养成分表编辑器组件
- [ ] **APP-001**: 开发移动端富文本渲染Widget（集成flutter_html）
- [ ] **APP-002**: 实现图片懒加载和性能优化（缓存、预加载）
- [ ] **TEST-001**: 编写单元测试和集成测试（覆盖率>80%）

---

## Dependencies

### 内部依赖

1. **现有商品管理模块**
   - Product模型和数据库表
   - 商品CRUD API
   - 图片上传功能

2. **管理后台框架**
   - Vue3 + Element Plus
   - API请求封装
   - 路由和权限系统

3. **移动端框架**
   - Flutter商品详情页
   - ProductProvider状态管理
   - CartProvider购物车

### 外部依赖

1. **Quill.js** (v1.3.6+) - 富文本编辑器
   - CDN: https://cdn.quilljs.com/1.3.6/quill.js
   - Vue适配器: @vueup/vue-quill

2. **flutter_html** (v3.0.0-beta.2) - Flutter HTML渲染
   - Pub: flutter_html

3. **bleach** (v6.0.0) - HTML清理和XSS防护
   - PyPI: bleach

4. **Pillow** (v10.0.0+) - Python图片处理
   - PyPI: Pillow

### 团队协作

- **前端开发**：1人（Flutter + Vue3）
- **后端开发**：1人（FastAPI + SQLAlchemy）
- **UI设计**：0.5人（兼职，提供设计稿）
- **测试**：0.5人（兼职，执行测试用例）

---

## Success Criteria (Technical)

### 性能基准

| 指标 | 目标值 | 测量方法 |
|------|--------|----------|
| API响应时间 | < 200ms | Postman测试 |
| 首屏加载时间 | < 2秒 | Flutter DevTools |
| 富文本渲染时间 | < 1秒 | 性能监控日志 |
| 滚动帧率 | ≥ 55fps | Flutter性能分析 |
| 内存占用 | < 150MB | Flutter DevTools |
| APK增量大小 | < 5MB | 构建产物分析 |

### 质量标准

| 类型 | 标准 | 测试方法 |
|------|------|----------|
| 代码覆盖率 | ≥ 80% | pytest/coverage |
| XSS漏洞 | 0个 | OWASP ZAP扫描 |
| SQL注入 | 0个 | SQL注入测试 |
| 崩溃率 | < 0.1% | Firebase Crashlytics |
| 用户满意度 | ≥ 4.2/5.0 | 用户调研 |

### 功能验收

- [ ] 管理后台可以创建5种类型的内容分区
- [ ] 富文本编辑器支持10种格式化选项
- [ ] 移动端正确渲染所有HTML内容
- [ ] 图片懒加载工作正常
- [ ] 营养成分表数据正确显示
- [ ] 批量操作成功率100%
- [ ] 内容保存后5秒内同步到移动端

---

## Estimated Effort

### 总体时间估算

**开发周期**：10个工作日（2周）

**工作量分布**：
- 后端开发：30小时（Day 1-3 + 部分Day 10）
- 前端开发：40小时（Day 4-9）
- 测试：8小时（Day 10）
- 文档：4小时（穿插进行）
- 缓冲：6小时（应对不可预期问题）

### 关键路径

**Critical Path**：
1. 数据库设计 → 后端API → 管理后台 → 移动端 → 测试
2. 任何阶段延期都会影响整体进度

**风险缓冲**：
- 预留1天缓冲时间
- Phase 2和Phase 3可部分并行（前端先行开发UI）

### 资源需求

- **开发人员**：2人（1前端 + 1后端）
- **测试人员**：0.5人（第10天全职）
- **设计人员**：0.5人（前期设计，兼职）
- **服务器资源**：
  - 数据库存储：+10MB（前100个商品）
  - 图片存储：+50MB（每个商品平均500KB）
  - CDN流量：+5GB/月（估算）

### 成本估算

- **开发成本**：约120人时
- **服务器成本**：约50元/月（存储+CDN）
- **运维成本**：约10元/月（备份、监控）

---

## Risk Assessment & Mitigation

### 技术风险

| 风险 | 概率 | 影响 | 缓解措施 |
|------|------|------|----------|
| flutter_html渲染性能问题 | 中 | 高 | 提前性能测试，准备WebView备选方案 |
| 富文本XSS攻击 | 低 | 高 | 使用bleach严格过滤，前端也做防护 |
| Quill.js兼容性问题 | 低 | 中 | 技术验证，准备TinyMCE备选 |
| 数据库存储空间不足 | 低 | 中 | 监控使用量，预留云存储方案 |

### 进度风险

| 风险 | 概率 | 影响 | 缓解措施 |
|------|------|------|----------|
| 移动端性能优化超期 | 中 | 高 | 提前设置性能基准，并行开发优化 |
| 富文本编辑器功能复杂 | 中 | 中 | 从MVP开始，逐步扩展功能 |
| 测试时间不足 | 中 | 中 | 自动化测试，提前介入测试 |

### 业务风险

| 风险 | 概率 | 影响 | 缓解措施 |
|------|------|------|----------|
| 运营人员不会使用编辑器 | 中 | 中 | 提供培训和操作手册，预设内容模板 |
| 用户不阅读详情内容 | 低 | 高 | 灰度发布后收集数据，优化内容展示 |

---

## 附录

### 技术选型对比

#### 富文本编辑器

| 特性 | Quill.js | TinyMCE | CKEditor |
|------|----------|---------|----------|
| 体积(gzip) | ~100KB | ~500KB | ~300KB |
| Vue3支持 | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ |
| 学习曲线 | 低 | 中 | 高 |
| 扩展性 | 好 | 优秀 | 优秀 |
| 成本 | 免费 | 免费/付费 | 免费/付费 |
| **选择** | ✅ | 备选 | 备选 |

#### Flutter HTML渲染库

| 特性 | flutter_html | webview_flutter | html |
|------|-------------|-----------------|----- |
| 渲染性能 | ⭐⭐⭐ | ⭐⭐ | ⭐ |
| 自定义能力 | 好 | 优秀 | 差 |
| 包大小 | ~500KB | ~5MB | ~100KB |
| 社区支持 | 活跃 | 官方支持 | 弱 |
| **选择** | ✅ | 备选方案 | 不推荐 |

### 数据模型关系图

```
products (1)
    │
    ├──── (1:N) ─── content_sections
    │                       ├─ section_type: "story"
    │                       ├─ section_type: "nutrition"
    │                       ├─ section_type: "ingredients"
    │                       └─ section_type: "process"
    │
    └──── (1:1) ─── nutrition_facts
```

### API响应格式示例

```json
{
  "product": {
    "id": 1,
    "title": "青椒炒肉",
    "description": "新鲜青椒搭配嫩滑猪肉...",
    "detail_sections": [
      {
        "id": 1,
        "section_type": "story",
        "title": "菜品故事",
        "content": "<p>这是一道经典川菜...</p>",
        "display_order": 1
      },
      {
        "id": 2,
        "section_type": "nutrition",
        "title": "营养成分",
        "content": "<table>...</table>",
        "display_order": 2
      }
    ],
    "nutrition_facts": {
      "serving_size": "1份(200g)",
      "calories": 180,
      "protein": 12.5,
      "fat": 8.3,
      "carbohydrates": 5.2,
      "sodium": 450
    }
  }
}
```

---

**Epic版本**: v1.0
**创建日期**: 2026-01-02
**状态**: 待分解
**预计完成**: 2026-01-16（2周后）
