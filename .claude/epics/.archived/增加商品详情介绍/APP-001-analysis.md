# APP-001 任务分析

## 任务概述
使用flutter_html实现Flutter移动端的富文本内容渲染，创建商品详情页的分区Widget。

## 技术分析

### 技术栈
- **移动框架**: Flutter
- **工作目录**: `flutter_app_new/`

### 功能需求

#### 1. 安装依赖
在`flutter_app_new/pubspec.yaml`中添加：
```yaml
dependencies:
  flutter_html: ^3.0.0-beta.2
  cached_network_image: ^3.3.0
```

安装：
```bash
cd flutter_app_new
flutter pub get
```

#### 2. 创建数据模型
**文件**: `flutter_app_new/lib/data/models/content_section.dart`

```dart
class ContentSection {
  final int? id;
  final int productId;
  final String sectionType; // story, nutrition, ingredients, process, tips
  final String? title;
  final String content; // HTML content
  final int displayOrder;
  final DateTime? createdAt;
  final DateTime? updatedAt;

  ContentSection({
    this.id,
    required this.productId,
    required this.sectionType,
    this.title,
    required this.content,
    required this.displayOrder,
    this.createdAt,
    this.updatedAt,
  });

  factory ContentSection.fromJson(Map<String, dynamic> json) {
    return ContentSection(
      id: json['id'] as int?,
      productId: json['product_id'] as int,
      sectionType: json['section_type'] as String,
      title: json['title'] as String?,
      content: json['content'] as String,
      displayOrder: json['display_order'] as int? ?? 0,
      createdAt: json['created_at'] != null
          ? DateTime.parse(json['created_at'] as String)
          : null,
      updatedAt: json['updated_at'] != null
          ? DateTime.parse(json['updated_at'] as String)
          : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'product_id': productId,
      'section_type': sectionType,
      'title': title,
      'content': content,
      'display_order': displayOrder,
      'created_at': createdAt?.toIso8601String(),
      'updated_at': updatedAt?.toIso8601String(),
    };
  }
}
```

#### 3. 创建分区Widget

**通用HTML渲染Widget**: `flutter_app_new/lib/widgets/html_content_widget.dart`

```dart
import 'package:flutter/material.dart';
import 'package:flutter_html/flutter_html.dart';
import 'package:cached_network_image/cached_network_image.dart';

class HtmlContentWidget extends StatelessWidget {
  final String content;
  final String? title;

  const HtmlContentWidget({
    Key? key,
    required this.content,
    this.title,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        if (title != null && title!.isNotEmpty)
          Padding(
            padding: const EdgeInsets.all(16.0),
            child: Text(
              title!,
              style: Theme.of(context).textTheme.titleLarge,
            ),
          ),
        Html(
          data: content,
          style: {
            'body': Style(
              fontSize: FontSize(16.0),
              lineHeight: const LineHeight(1.5),
              color: Colors.black87,
              padding: HtmlPaddings.all(16),
            ),
            'h1': Style(
              fontSize: FontSize(24.0),
              fontWeight: FontWeight.bold,
              padding: HtmlPaddings.symmetric(vertical: 16),
            ),
            'h2': Style(
              fontSize: FontSize(20.0),
              fontWeight: FontWeight.bold,
              padding: HtmlPaddings.symmetric(vertical: 14),
            ),
            'h3': Style(
              fontSize: FontSize(18.0),
              fontWeight: FontWeight.bold,
              padding: HtmlPaddings.symmetric(vertical: 12),
            ),
            'p': Style(
              margin: Margins.only(bottom: 12),
            ),
            'ul': Style(
              padding: HtmlPaddings.left(24),
            ),
            'ol': Style(
              padding: HtmlPaddings.left(24),
            ),
            'li': Style(
              margin: Margins.only(bottom: 8),
            ),
            'img': Style(
              width: Width(100, Unit.percent),
              margin: Margins.symmetric(vertical: 16),
            ),
          },
          onImageTap: (url, _, __) {
            // 图片点击事件（可以打开大图预览）
            debugPrint('Image tapped: $url');
          },
          onLinkTap: (url, _, __) {
            // 链接点击事件
            debugPrint('Link tapped: $url');
          },
          customWidgetBuilder: (element) {
            // 自定义图片渲染（使用缓存）
            if (element.localName == 'img') {
              final src = element.attributes['src'];
              if (src != null) {
                return CachedNetworkImage(
                  imageUrl: src,
                  placeholder: (context, url) => Container(
                    height: 200,
                    color: Colors.grey[200],
                    child: const Center(child: CircularProgressIndicator()),
                  ),
                  errorWidget: (context, url, error) => Container(
                    height: 200,
                    color: Colors.grey[300],
                    child: const Icon(Icons.broken_image),
                  ),
                );
              }
            }
            return null;
          },
        ),
      ],
    );
  }
}
```

**故事分区Widget**: `flutter_app_new/lib/widgets/story_section_widget.dart`

```dart
import 'package:flutter/material.dart';
import 'html_content_widget.dart';

class StorySectionWidget extends StatelessWidget {
  final String content;
  final String? title;

  const StorySectionWidget({
    Key? key,
    required this.content,
    this.title,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.all(16),
      child: HtmlContentWidget(
        content: content,
        title: title ?? '菜品故事',
      ),
    );
  }
}
```

**营养表格Widget**: `flutter_app_new/lib/widgets/nutrition_table_widget.dart`

```dart
import 'package:flutter/material.dart';

class NutritionTableWidget extends StatelessWidget {
  final Map<String, dynamic> nutritionData;

  const NutritionTableWidget({
    Key? key,
    required this.nutritionData,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.all(16),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              '营养成分表',
              style: Theme.of(context).textTheme.titleLarge,
            ),
            const SizedBox(height: 16),
            if (nutritionData['serving_size'] != null)
              Text('份量: ${nutritionData['serving_size']}'),
            const SizedBox(height: 16),
            _buildNutritionTable(),
          ],
        ),
      ),
    );
  }

  Widget _buildNutritionTable() {
    final nutrients = [
      {'name': '热量', 'value': nutritionData['calories'], 'unit': 'kcal'},
      {'name': '蛋白质', 'value': nutritionData['protein'], 'unit': 'g'},
      {'name': '脂肪', 'value': nutritionData['fat'], 'unit': 'g'},
      {'name': '碳水化合物', 'value': nutritionData['carbohydrates'], 'unit': 'g'},
      {'name': '钠', 'value': nutritionData['sodium'], 'unit': 'mg'},
    ];

    return Table(
      border: TableBorder.all(color: Colors.grey[300]!),
      columnWidths: const {
        0: FlexColumnWidth(2),
        1: FlexColumnWidth(1),
        2: FlexColumnWidth(1),
      },
      children: [
        TableRow(
          decoration: BoxDecoration(color: Colors.grey[100]),
          children: [
            _buildTableCell('营养成分', isHeader: true),
            _buildTableCell('含量', isHeader: true),
            _buildTableCell('单位', isHeader: true),
          ],
        ),
        ...nutrients.map((nutrient) {
          return TableRow(
            children: [
              _buildTableCell(nutrient['name'] as String),
              _buildTableCell((nutrient['value'] ?? '-').toString()),
              _buildTableCell(nutrient['unit'] as String),
            ],
          );
        }).toList(),
      ],
    );
  }

  Widget _buildTableCell(String text, {bool isHeader = false}) {
    return Padding(
      padding: const EdgeInsets.all(8),
      child: Text(
        text,
        style: TextStyle(
          fontWeight: isHeader ? FontWeight.bold : FontWeight.normal,
        ),
      ),
    );
  }
}
```

#### 4. 更新Product模型
**文件**: `flutter_app_new/lib/data/models/product.dart`

在Product类中添加：
```dart
class Product {
  // ... 现有字段 ...

  // 新增字段
  List<ContentSection>? contentSections;
  Map<String, dynamic>? nutritionFacts;

  factory Product.fromJson(Map<String, dynamic> json) {
    return Product(
      // ... 现有字段解析 ...

      // 新增字段解析
      contentSections: json['content_sections'] != null
          ? (json['content_sections'] as List)
              .map((e) => ContentSection.fromJson(e as Map<String, dynamic>))
              .toList()
          : null,
      nutritionFacts: json['nutrition_facts'] as Map<String, dynamic>?,
    );
  }
}
```

#### 5. 更新API服务
**文件**: `flutter_app_new/lib/repositories/product_repository.dart`

添加获取完整详情的方法：
```dart
Future<ApiResponse<Product>> getFullProductDetails(String productId) async {
  try {
    final response = await _apiClient.get(
      '/products/$productId/full-details',
    );

    if (response.statusCode == 200) {
      final data = json.decode(response.body);
      if (data['success'] == true) {
        return ApiResponse.success(
          Product.fromJson(data['data']),
        );
      }
    }

    return ApiResponse.error('获取商品详情失败');
  } catch (e) {
    return ApiResponse.error(e.toString());
  }
}
```

#### 6. 重构商品详情页
**文件**: `flutter_app_new/lib/presentation/pages/product_detail_page.dart`

添加内容分区列表：
```dart
class ProductDetailPage extends StatelessWidget {
  final Product product;

  const ProductDetailPage({
    Key? key,
    required this.product,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text(product.title)),
      body: SingleChildScrollView(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // 现有的商品图片、价格等信息...

            // 新增：内容分区列表
            if (product.contentSections != null && product.contentSections!.isNotEmpty)
              ...product.contentSections!.map((section) {
                return _buildSectionWidget(section);
              }).toList(),

            // 新增：营养成分表
            if (product.nutritionFacts != null)
              NutritionTableWidget(nutritionData: product.nutritionFacts!),
          ],
        ),
      ),
    );
  }

  Widget _buildSectionWidget(ContentSection section) {
    switch (section.sectionType) {
      case 'story':
        return StorySectionWidget(
          content: section.content,
          title: section.title,
        );
      case 'nutrition':
        return HtmlContentWidget(
          content: section.content,
          title: section.title,
        );
      case 'ingredients':
      case 'process':
      case 'tips':
      default:
        return HtmlContentWidget(
          content: section.content,
          title: section.title ?? _getDefaultTitle(section.sectionType),
        );
    }
  }

  String _getDefaultTitle(String sectionType) {
    switch (sectionType) {
      case 'ingredients':
        return '食材来源';
      case 'process':
        return '制作工艺';
      case 'tips':
        return '食用贴士';
      default:
        return '详情';
    }
  }
}
```

## 实施步骤

### 步骤1: 安装依赖
```bash
cd flutter_app_new
flutter pub add flutter_html cached_network_image
```

### 步骤2: 创建ContentSection数据模型
创建`lib/data/models/content_section.dart`

### 步骤3: 创建分区Widget
- HtmlContentWidget（通用HTML渲染）
- StorySectionWidget（故事分区）
- NutritionTableWidget（营养表格）

### 步骤4: 更新Product模型
添加contentSections和nutritionFacts字段

### 步骤5: 更新API服务
添加getFullProductDetails方法

### 步骤6: 重构商品详情页
显示内容分区列表和营养表格

### 步骤7: 测试
- 测试HTML渲染
- 测试图片加载
- 测试不同分区类型
- 测试iOS和Android

## 验收标准

| 验收标准 | 测试方法 |
|---------|---------|
| 正确渲染HTML内容 | 显示标题、段落、列表 |
| 4种分区Widget正常显示 | story/nutrition/ingredients/process |
| 数据模型解析正确 | JSON转换测试 |
| 不影响原有功能 | 图片、价格、加购正常 |
| iOS和Android显示一致 | 在两个平台测试 |

## 文件清单

**新建文件**:
- `flutter_app_new/lib/data/models/content_section.dart`
- `flutter_app_new/lib/widgets/html_content_widget.dart`
- `flutter_app_new/lib/widgets/story_section_widget.dart`
- `flutter_app_new/lib/widgets/nutrition_table_widget.dart`

**修改文件**:
- `flutter_app_new/lib/data/models/product.dart`
- `flutter_app_new/lib/repositories/product_repository.dart`
- `flutter_app_new/lib/presentation/pages/product_detail_page.dart`
- `flutter_app_new/pubspec.yaml`

## 技术要点

### flutter_html配置
- 自定义CSS样式
- 处理链接点击事件
- 图片自适应

### 图片缓存
- 使用cached_network_image
- 占位符和错误图
- 缓存策略

### 性能优化
- 使用ListView.builder
- 懒加载（下一阶段）
- 保持滚动位置

## 注意事项

1. **HTML安全**: 后端已过滤XSS，前端可以信任
2. **图片URL**: 使用ImageUtils.getImageUrl()处理相对路径
3. **空值处理**: contentSections和nutritionFacts可能为null
4. **向后兼容**: 不影响现有功能
5. **平台差异**: iOS和Android可能需要调整样式

## 与其他任务的集成

- **依赖API-001**: 调用full-details API获取数据
- **为APP-002准备**: 提供Widget基础供性能优化
