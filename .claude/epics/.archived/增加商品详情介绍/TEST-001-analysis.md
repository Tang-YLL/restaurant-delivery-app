# TEST-001 任务分析

## 任务概述
为"增加商品详情介绍"功能的完整技术栈编写全面的单元测试和集成测试，确保代码质量和系统稳定性。

## 测试范围

### 后端测试（FastAPI）
- 数据库模型测试
- API端点测试
- 服务层测试
- 图片处理测试
- 集成测试

### 前端测试（Vue3）
- 组件单元测试
- API服务测试
- 工具函数测试

### 移动端测试（Flutter）
- Widget测试
- 数据模型测试
- Provider测试
- 集成测试

## 技术分析

### 后端测试技术栈
- **测试框架**: pytest, pytest-asyncio
- **HTTP测试**: httpx, TestClient
- **数据库测试**: SQLite内存数据库
- **Mock**: pytest-mock
- **覆盖率**: pytest-cov

### 前端测试技术栈
- **测试框架**: Vitest
- **组件测试**: @vue/test-utils
- **Mock**: vitest-fetch-mock

### 移动端测试技术栈
- **测试框架**: flutter_test
- **Mock**: mockito
- **集成测试**: flutter_driver

## 实施计划

### 1. 后端测试

#### 1.1 安装测试依赖
**文件**: `backend/requirements-dev.txt`

```txt
# Testing
pytest>=7.4.0
pytest-asyncio>=0.21.0
pytest-cov>=4.1.0
pytest-mock>=3.11.0
httpx>=0.24.0
```

安装：
```bash
cd backend
pip install -r requirements-dev.txt
```

#### 1.2 数据库模型测试
**文件**: `backend/tests/test_models.py`

```python
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import ContentSection, NutritionFact

@pytest.mark.asyncio
async def test_content_section_creation(db_session: AsyncSession):
    """测试内容分区创建"""
    section = ContentSection(
        product_id=1,
        section_type="story",
        title="菜品故事",
        content="<p>这是一个关于菜品的故事</p>",
        display_order=0
    )
    db_session.add(section)
    await db_session.commit()
    await db_session.refresh(section)

    assert section.id is not None
    assert section.section_type == "story"
    assert section.display_order == 0

@pytest.mark.asyncio
async def test_nutrition_fact_creation(db_session: AsyncSession):
    """测试营养成分创建"""
    nutrition = NutritionFact(
        product_id=1,
        serving_size="1份(200g)",
        calories=250.0,
        protein=15.0,
        fat=10.0,
        carbohydrates=30.0,
        sodium=500.0
    )
    db_session.add(nutrition)
    await db_session.commit()
    await db_session.refresh(nutrition)

    assert nutrition.id is not None
    assert nutrition.calories == 250.0
    assert nutrition.protein == 15.0

@pytest.mark.asyncio
async def test_content_section_cascade_delete(db_session: AsyncSession):
    """测试级联删除"""
    from app.models import Product

    # 创建商品
    product = Product(name="测试商品", price=10.0)
    db_session.add(product)
    await db_session.commit()
    await db_session.refresh(product)

    # 创建内容分区
    section = ContentSection(
        product_id=product.id,
        section_type="story",
        content="测试内容"
    )
    db_session.add(section)
    await db_session.commit()

    # 删除商品
    await db_session.delete(product)
    await db_session.commit()

    # 验证内容分区也被删除
    result = await db_session.get(ContentSection, section.id)
    assert result is None
```

#### 1.3 服务层测试
**文件**: `backend/tests/test_product_detail_service.py`

```python
import pytest
from app.services.product_detail_service import ProductDetailService
from app.schemas import ContentSectionCreate

@pytest.mark.asyncio
async def test_sanitize_html(db_session: AsyncSession):
    """测试HTML清洗"""
    service = ProductDetailService()

    # 测试XSS过滤
    dirty_html = '<p>安全内容</p><script>alert("XSS")</script>'
    clean_html = service.sanitize_html(dirty_html)

    assert '<script>' not in clean_html
    assert '<p>安全内容</p>' in clean_html

@pytest.mark.asyncio
async def test_create_content_section(db_session: AsyncSession, test_product):
    """测试创建内容分区"""
    service = ProductDetailService()

    section_data = ContentSectionCreate(
        section_type="story",
        title="测试标题",
        content="<p>测试内容</p>",
        display_order=0
    )

    section = await service.create_content_section(
        test_product.id,
        section_data,
        db_session
    )

    assert section.id is not None
    assert section.product_id == test_product.id
    assert section.section_type == "story"

@pytest.mark.asyncio
async def test_get_full_details(db_session: AsyncSession, test_product):
    """测试获取完整详情"""
    service = ProductDetailService()

    # 创建测试数据
    section = ContentSection(
        product_id=test_product.id,
        section_type="story",
        content="测试内容"
    )
    nutrition = NutritionFact(
        product_id=test_product.id,
        calories=200.0
    )
    db_session.add_all([section, nutrition])
    await db_session.commit()

    # 获取完整详情
    details = await service.get_full_details(test_product.id, db_session)

    assert details['product'] is not None
    assert len(details['content_sections']) == 1
    assert details['nutrition_facts'] is not None
```

#### 1.4 API端点测试
**文件**: `backend/tests/test_api_product_details.py`

```python
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_get_product_detail_sections(test_db, auth_headers):
    """测试获取内容分区列表"""
    response = client.get(
        "/api/v1/admin/products/1/details",
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert 'content_sections' in data
    assert isinstance(data['content_sections'], list)

def test_create_content_section(test_db, auth_headers):
    """测试创建内容分区"""
    section_data = {
        "section_type": "story",
        "title": "测试标题",
        "content": "<p>测试内容</p>",
        "display_order": 0
    }

    response = client.post(
        "/api/v1/admin/products/1/details/sections",
        json=section_data,
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data['section_type'] == "story"
    assert data['title'] == "测试标题"

def test_update_content_section(test_db, auth_headers):
    """测试更新内容分区"""
    update_data = {
        "title": "更新后的标题",
        "content": "<p>更新后的内容</p>"
    }

    response = client.put(
        "/api/v1/admin/products/1/details/sections/1",
        json=update_data,
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data['title'] == "更新后的标题"

def test_delete_content_section(test_db, auth_headers):
    """测试删除内容分区"""
    response = client.delete(
        "/api/v1/admin/products/1/details/sections/1",
        headers=auth_headers
    )

    assert response.status_code == 200

def test_upload_product_detail_image(test_db, auth_headers, test_image):
    """测试图片上传"""
    files = {"file": ("test.jpg", test_image, "image/jpeg")}

    response = client.post(
        "/api/v1/admin/products/1/details/images/upload",
        files=files,
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert 'url' in data
    assert data['filename'].endswith('.jpg')

def test_update_nutrition_facts(test_db, auth_headers):
    """测试更新营养成分"""
    nutrition_data = {
        "serving_size": "1份(200g)",
        "calories": 250.0,
        "protein": 15.0,
        "fat": 10.0,
        "carbohydrates": 30.0,
        "sodium": 500.0
    }

    response = client.put(
        "/api/v1/admin/products/1/nutrition",
        json=nutrition_data,
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data['calories'] == 250.0
```

#### 1.5 图片处理测试
**文件**: `backend/tests/test_image_processor.py`

```python
import pytest
from io import BytesIO
from PIL import Image
from app.utils.image_processor import ImageProcessor

def test_process_image_resize():
    """测试图片缩放"""
    # 创建大图片
    img = Image.new('RGB', (2000, 1500), color='red')
    img_bytes = BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)

    # 处理图片
    processed = ImageProcessor.process_uploaded_image(
        img_bytes.read(),
        max_width=800
    )

    # 验证缩放
    processed_img = Image.open(BytesIO(processed))
    assert processed_img.width <= 800
    assert processed_img.format == 'JPEG'

def test_process_image_compression():
    """测试图片压缩"""
    img = Image.new('RGB', (1000, 800), color='blue')
    img_bytes = BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)

    original_size = len(img_bytes.read())
    img_bytes.seek(0)

    processed = ImageProcessor.process_uploaded_image(
        img_bytes.read(),
        quality=70
    )

    # 验证压缩
    assert len(processed) < original_size

def test_validate_image_type():
    """测试图片类型验证"""
    # 测试有效图片
    valid_img = Image.new('RGB', (100, 100))
    img_bytes = BytesIO()
    valid_img.save(img_bytes, format='JPEG')
    img_bytes.seek(0)

    assert ImageProcessor.validate_image_type(img_bytes) is True

    # 测试无效文件
    invalid_file = BytesIO(b"Not an image")
    invalid_file.seek(0)

    assert ImageProcessor.validate_image_type(invalid_file) is False
```

#### 1.6 运行后端测试
**文件**: `backend/pytest.ini`

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts =
    -v
    --cov=app
    --cov-report=html
    --cov-report=term-missing
    --asyncio-mode=auto
```

运行测试：
```bash
cd backend
pytest                          # 运行所有测试
pytest tests/test_models.py     # 运行特定文件
pytest -v                       # 详细输出
pytest --cov=app               # 生成覆盖率报告
```

### 2. Vue3管理后台测试

#### 2.1 安装测试依赖
```bash
cd vue-admin
npm install -D vitest @vue/test-utils @vitest/ui jsdom
```

#### 2.2 配置Vitest
**文件**: `vue-admin/vitest.config.ts`

```typescript
import { defineConfig } from 'vitest/config'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./src/tests/setup.ts'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'html', 'json'],
      exclude: [
        'node_modules/',
        'src/tests/',
      ]
    }
  }
})
```

#### 2.3 QuillEditor组件测试
**文件**: `vue-admin/src/tests/components/QuillEditor.test.ts`

```typescript
import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import QuillEditor from '@/components/QuillEditor.vue'

describe('QuillEditor', () => {
  it('renders correctly', () => {
    const wrapper = mount(QuillEditor, {
      props: {
        modelValue: '<p>Initial content</p>'
      }
    })

    expect(wrapper.find('.quill-editor-wrapper').exists()).toBe(true)
  })

  it('emits update:modelValue on content change', async () => {
    const wrapper = mount(QuillEditor, {
      props: {
        modelValue: ''
      }
    })

    // 模拟内容变化
    await wrapper.vm.handleUpdate('<p>New content</p>')

    expect(wrapper.emitted('update:modelValue')).toBeTruthy()
    expect(wrapper.emitted('update:modelValue')![0]).toEqual(['<p>New content</p>'])
  })

  it('displays character count', () => {
    const wrapper = mount(QuillEditor, {
      props: {
        modelValue: '<p>Hello World</p>'
      }
    })

    expect(wrapper.vm.contentLength).toBe(11) // 不包含HTML标签
  })
})
```

#### 2.4 NutritionEditor组件测试
**文件**: `vue-admin/src/tests/components/NutritionEditor.test.ts`

```typescript
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import NutritionEditor from '@/components/NutritionEditor.vue'

describe('NutritionEditor', () => {
  it('calculates NRV% correctly', () => {
    const wrapper = mount(NutritionEditor, {
      props: {
        modelValue: {
          protein: 60,
          fat: 60,
          carbohydrates: 300,
          sodium: 2000
        }
      }
    })

    expect(wrapper.vm.calculateNRV('protein', 60)).toBe(100)
    expect(wrapper.vm.calculateNRV('fat', 30)).toBe(50)
    expect(wrapper.vm.calculateNRV('sodium', 400)).toBe(20)
  })

  it('validates protein range', async () => {
    const wrapper = mount(NutritionEditor, {
      props: {
        modelValue: { protein: 150 } // 超出范围
      }
    })

    const isValid = await wrapper.vm.validate()
    expect(isValid).toBe(false)
  })

  it('emits update:modelValue on form change', async () => {
    const wrapper = mount(NutritionEditor, {
      props: {
        modelValue: { calories: 0 }
      }
    })

    await wrapper.vm.formData.calories = 250
    await wrapper.vm.$nextTick()

    expect(wrapper.emitted('update:modelValue')).toBeTruthy()
  })
})
```

#### 2.5 API服务测试
**文件**: `vue-admin/src/tests/api/product.test.ts`

```typescript
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { createContentSection, updateNutritionFacts } from '@/api/product'
import { fetch } from 'vitest-fetch-mock'

vi.mock('vitest-fetch-mock')

describe('Product API', () => {
  beforeEach(() => {
    fetch.resetMocks()
  })

  it('creates content section successfully', async () => {
    fetch.mockResponseOnce(JSON.stringify({
      success: true,
      data: {
        id: 1,
        section_type: 'story',
        title: '测试标题',
        content: '<p>测试内容</p>'
      }
    }))

    const result = await createContentSection(1, {
      section_type: 'story',
      title: '测试标题',
      content: '<p>测试内容</p>',
      display_order: 0
    })

    expect(result.id).toBe(1)
    expect(result.section_type).toBe('story')
    expect(fetch).toHaveBeenCalledTimes(1)
  })

  it('handles API errors', async () => {
    fetch.mockRejectOnce(new Error('Network error'))

    await expect(
      createContentSection(1, {} as any)
    ).rejects.toThrow('Network error')
  })
})
```

#### 2.6 运行前端测试
在`package.json`中添加：
```json
{
  "scripts": {
    "test": "vitest",
    "test:ui": "vitest --ui",
    "test:coverage": "vitest --coverage"
  }
}
```

运行测试：
```bash
npm test              # 运行所有测试
npm run test:ui       # UI模式
npm run test:coverage # 生成覆盖率报告
```

### 3. Flutter移动端测试

#### 3.1 Widget测试
**文件**: `flutter_app_new/test/widgets/html_content_widget_test.dart`

```dart
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_app_new/widgets/html_content_widget.dart';

void main() {
  testWidgets('HtmlContentWidget renders title', (WidgetTester tester) async {
    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: HtmlContentWidget(
            content: '<p>Test content</p>',
            title: 'Test Title',
          ),
        ),
      ),
    );

    expect(find.text('Test Title'), findsOneWidget);
  });

  testWidgets('HtmlContentWidget renders HTML content', (WidgetTester tester) async {
    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: HtmlContentWidget(
            content: '<h1>Heading</h1><p>Paragraph</p>',
          ),
        ),
      ),
    );

    expect(find.text('Heading'), findsOneWidget);
    expect(find.text('Paragraph'), findsOneWidget);
  });
}
```

#### 3.2 数据模型测试
**文件**: `flutter_app_new/test/models/content_section_test.dart`

```dart
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_app_new/data/models/content_section.dart';

void main() {
  test('ContentSection fromJson parses correctly', () {
    final json = {
      'id': 1,
      'product_id': 10,
      'section_type': 'story',
      'title': 'Test Title',
      'content': '<p>Test content</p>',
      'display_order': 0,
      'created_at': '2024-01-01T00:00:00Z',
      'updated_at': '2024-01-01T00:00:00Z',
    };

    final section = ContentSection.fromJson(json);

    expect(section.id, 1);
    expect(section.productId, 10);
    expect(section.sectionType, 'story');
    expect(section.title, 'Test Title');
    expect(section.content, '<p>Test content</p>');
  });

  test('ContentSection toJson serializes correctly', () {
    final section = ContentSection(
      id: 1,
      productId: 10,
      sectionType: 'story',
      title: 'Test Title',
      content: '<p>Test content</p>',
      displayOrder: 0,
    );

    final json = section.toJson();

    expect(json['id'], 1);
    expect(json['product_id'], 10);
    expect(json['section_type'], 'story');
  });
}
```

#### 3.3 Provider测试
**文件**: `flutter_app_new/test/providers/product_provider_test.dart`

```dart
import 'package:flutter_test/flutter_test.dart';
import 'package:mockito/mockito.dart';
import 'package:mockito/annotations.dart';
import 'package:flutter_app_new/providers/product_provider.dart';
import 'package:flutter_app_new/repositories/product_repository.dart';

@GenerateMocks([ProductRepository])
void main() {
  late ProductProvider provider;
  late MockProductRepository mockRepository;

  setUp(() {
    mockRepository = MockProductRepository();
    provider = ProductProvider(mockRepository);
  });

  test('loadProductDetails returns product', () async {
    final testProduct = Product(
      id: 1,
      title: 'Test Product',
      price: 10.0,
    );

    when(mockRepository.getProductDetails('1'))
        .thenAnswer((_) async => ApiResponse.success(testProduct));

    await provider.loadProductDetails('1');

    expect(provider.product, testProduct);
    expect(provider.isLoading, false);
    verify(mockRepository.getProductDetails('1')).called(1);
  });
}
```

#### 3.4 运行Flutter测试
```bash
cd flutter_app_new
flutter test                              # 运行所有测试
flutter test test/widgets/                # 运行特定目录
flutter test --coverage                   # 生成覆盖率
flutter test --update-goldens             # 更新快照测试
```

### 4. 集成测试

#### 4.1 后端集成测试
**文件**: `backend/tests/test_integration.py`

```python
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_full_product_detail_workflow():
    """测试完整的商品详情工作流"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # 1. 创建商品
        product_response = await client.post(
            "/api/v1/admin/products",
            json={"name": "测试商品", "price": 10.0}
        )
        product_id = product_response.json()["id"]

        # 2. 创建内容分区
        section_response = await client.post(
            f"/api/v1/admin/products/{product_id}/details/sections",
            json={
                "section_type": "story",
                "content": "<p>菜品故事</p>"
            }
        )
        assert section_response.status_code == 200

        # 3. 上传图片
        # ...

        # 4. 更新营养成分
        nutrition_response = await client.put(
            f"/api/v1/admin/products/{product_id}/nutrition",
            json={"calories": 250, "protein": 15}
        )
        assert nutrition_response.status_code == 200

        # 5. 获取完整详情
        details_response = await client.get(
            f"/api/v1/products/{product_id}/full-details"
        )
        assert details_response.status_code == 200
        data = details_response.json()
        assert len(data["content_sections"]) == 1
        assert data["nutrition_facts"]["calories"] == 250
```

## 验收标准

| 测试类型 | 覆盖率目标 | 测试数量 |
|---------|-----------|---------|
| 后端单元测试 | ≥80% | ≥30个测试 |
| 后端集成测试 | 关键流程100% | ≥10个测试 |
| Vue组件测试 | ≥70% | ≥15个测试 |
| Flutter Widget测试 | ≥70% | ≥20个测试 |
| 整体测试 | - | ≥75个测试 |

## 测试命令汇总

### 后端测试
```bash
cd backend
pytest                           # 运行所有测试
pytest -v                        # 详细输出
pytest --cov=app                # 生成覆盖率报告
pytest --cov=app --cov-report=html  # HTML覆盖率报告
```

### Vue3前端测试
```bash
cd vue-admin
npm test                        # 运行所有测试
npm run test:ui                 # UI模式
npm run test:coverage           # 覆盖率报告
```

### Flutter移动端测试
```bash
cd flutter_app_new
flutter test                    # 运行所有测试
flutter test --coverage         # 生成覆盖率
flutter test test/widgets/      # 运行Widget测试
```

### 全部测试
```bash
# 从项目根目录
./backend/pytest && cd vue-admin && npm test && cd ../flutter_app_new && flutter test
```

## 文件清单

**新建文件**:
- `backend/tests/test_models.py`
- `backend/tests/test_product_detail_service.py`
- `backend/tests/test_api_product_details.py`
- `backend/tests/test_image_processor.py`
- `backend/tests/test_integration.py`
- `backend/pytest.ini`
- `backend/requirements-dev.txt`
- `vue-admin/vitest.config.ts`
- `vue-admin/src/tests/setup.ts`
- `vue-admin/src/tests/components/QuillEditor.test.ts`
- `vue-admin/src/tests/components/NutritionEditor.test.ts`
- `vue-admin/src/tests/api/product.test.ts`
- `flutter_app_new/test/widgets/html_content_widget_test.dart`
- `flutter_app_new/test/models/content_section_test.dart`
- `flutter_app_new/test/providers/product_provider_test.dart`

## 测试最佳实践

### 1. 命名规范
- 测试文件: `test_*.py` (Python), `*.test.ts` (Vue), `*_test.dart` (Flutter)
- 测试函数: `test_<功能>_<场景>`
- 描述性命名: 一眼看出测试什么

### 2. 测试结构（AAA模式）
```python
def test_something():
    # Arrange - 准备测试数据
    data = prepareTestData()

    # Act - 执行被测试的功能
    result = functionUnderTest(data)

    # Assert - 验证结果
    assert result == expected
```

### 3. Mock使用
- Mock外部依赖（API、数据库）
- 不要Mock被测试的代码
- 使用真实的值对象

### 4. 测试隔离
- 每个测试独立运行
- 使用测试数据库
- 清理测试数据

### 5. 持续集成
- 在CI/CD中运行测试
- 测试失败阻止合并
- 生成覆盖率报告

## 注意事项

1. **测试数据库**: 使用内存SQLite，不影响生产数据库
2. **API密钥**: 测试环境使用测试密钥
3. **异步测试**: 使用pytest-asyncio处理async函数
4. **Mock图片**: 使用固定尺寸测试图片
5. **超时设置**: 集成测试设置合理超时

## 与其他任务的集成

- **依赖所有开发任务**: 测试覆盖已实现的所有功能
- **CI/CD集成**: 自动化测试流程
- **质量保证**: 确保代码质量符合标准
