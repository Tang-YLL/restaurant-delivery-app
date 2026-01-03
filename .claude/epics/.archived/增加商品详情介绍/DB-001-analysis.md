# DB-001 任务分析

## 任务概述
设计和创建商品详情数据模型，包括content_sections和nutrition_facts两张表，以及对应的SQLAlchemy模型。

## 技术分析

### 数据库表设计

#### content_sections表
```sql
CREATE TABLE content_sections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL,
    section_type VARCHAR(50) NOT NULL,  -- 'story', 'nutrition', 'ingredients', 'process', 'tips'
    title VARCHAR(200),
    content TEXT NOT NULL,  -- 富文本HTML
    display_order INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
);

CREATE INDEX idx_content_sections_product ON content_sections(product_id);
CREATE INDEX idx_content_sections_type ON content_sections(section_type);
```

#### nutrition_facts表
```sql
CREATE TABLE nutrition_facts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL,
    serving_size VARCHAR(50),  -- 如 "1份(200g)"
    calories REAL,  -- 热量 (kcal/100g)
    protein REAL,  -- 蛋白质 (g/100g)
    fat REAL,  -- 脂肪 (g/100g)
    carbohydrates REAL,  -- 碳水 (g/100g)
    sodium REAL,  -- 钠 (mg/100g)
    dietary_fiber REAL,  -- 膳食纤维 (g/100g)
    sugars REAL,  -- 糖 (g/100g)
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
);

CREATE INDEX idx_nutrition_facts_product ON nutrition_facts(product_id);
```

### SQLAlchemy模型设计

#### ContentSection模型
```python
class ContentSection(Base):
    __tablename__ = "content_sections"

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    section_type = Column(String(50), nullable=False)  # story, nutrition, ingredients, process, tips
    title = Column(String(200))
    content = Column(Text, nullable=False)
    display_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    product = relationship("Product", back_populates="content_sections")
```

#### NutritionFact模型
```python
class NutritionFact(Base):
    __tablename__ = "nutrition_facts"

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    serving_size = Column(String(50))
    calories = Column(Float)
    protein = Column(Float)
    fat = Column(Float)
    carbohydrates = Column(Float)
    sodium = Column(Float)
    dietary_fiber = Column(Float)
    sugars = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

    # 关系
    product = relationship("Product", back_populates="nutrition_fact")
```

### 需要修改的Product模型
需要在现有的Product模型中添加关系：
```python
class Product(Base):
    # ... 现有字段 ...

    # 新增关系
    content_sections = relationship("ContentSection", back_populates="product", cascade="all, delete-orphan")
    nutrition_fact = relationship("NutritionFact", back_populates="product", uselist=False, cascade="all, delete-orphan")
```

## 实施步骤

### 步骤1: 创建Alembic迁移脚本
```bash
cd backend
alembic revision -m "add_product_details"
```

### 步骤2: 编写upgrade和downgrade方法
在生成的迁移文件中实现表创建和回滚逻辑

### 步骤3: 创建SQLAlchemy模型
在`backend/app/models/__init__.py`中添加模型类

### 步骤4: 更新Product模型
添加relationship关系

### 步骤5: 执行迁移
```bash
alembic upgrade head
```

### 步骤6: 验证
- 检查表是否创建成功
- 验证外键约束
- 测试关系是否正常工作

## 风险和注意事项

1. **外键约束**: 确保products表已存在，否则迁移会失败
2. **级联删除**: ON DELETE CASCADE确保删除product时自动删除相关内容
3. **现有数据**: 迁移不应影响现有products数据
4. **回滚测试**: 确保downgrade方法可以正确回滚

## 文件清单

**新建文件**:
- `backend/alembic/versions/xxxx_add_product_details.py`

**修改文件**:
- `backend/app/models/__init__.py`

**参考文档**:
- `.claude/epics/增加商品详情介绍/epic.md` - 架构设计
- `.claude/epics/增加商品详情介绍/tasks.md` - Task DB-001详细需求
