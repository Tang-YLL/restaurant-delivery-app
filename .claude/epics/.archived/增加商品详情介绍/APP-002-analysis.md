# APP-002 任务分析

## 任务概述
优化Flutter移动端商品详情页的图片加载性能，实现懒加载、缓存策略和流畅的滚动体验。

## 技术分析

### 技术栈
- **移动框架**: Flutter
- **依赖库**: flutter_html, cached_network_image, flutter_cache_manager
- **工作目录**: `flutter_app_new/`

### 功能需求

#### 1. 安装依赖
在`flutter_app_new/pubspec.yaml`中添加：
```yaml
dependencies:
  flutter_html: ^3.0.0-beta.2
  cached_network_image: ^3.3.0
  flutter_cache_manager: ^3.3.1
  visibility_detector: ^0.4.0+2  # 用于检测Widget可见性
```

安装：
```bash
cd flutter_app_new
flutter pub get
```

#### 2. 创建图片懒加载Widget
**文件**: `flutter_app_new/lib/widgets/lazy_load_image_widget.dart`

```dart
import 'package:flutter/material.dart';
import 'package:cached_network_image/cached_network_image.dart';
import 'package:visibility_detector/visibility_detector.dart';

class LazyLoadImageWidget extends StatefulWidget {
  final String imageUrl;
  final double? width;
  final double? height;
  final BoxFit fit;

  const LazyLoadImageWidget({
    Key? key,
    required this.imageUrl,
    this.width,
    this.height,
    this.fit = BoxFit.cover,
  }) : super(key: key);

  @override
  State<LazyLoadImageWidget> createState() => _LazyLoadImageWidgetState();
}

class _LazyLoadImageWidgetState extends State<LazyLoadImageWidget> {
  bool _isVisible = false;
  bool _hasLoaded = false;

  @override
  Widget build(BuildContext context) {
    return VisibilityDetector(
      key: Key('visibility-detector-${widget.imageUrl}'),
      onVisibilityChanged: (visibilityInfo) {
        // 当图片至少50%可见时开始加载
        if (!_hasLoaded && visibilityInfo.visibleFraction > 0.5) {
          setState(() {
            _isVisible = true;
            _hasLoaded = true;
          });
        }
      },
      child: _buildImage(),
    );
  }

  Widget _buildImage() {
    if (!_isVisible) {
      // 占位符
      return Container(
        width: widget.width,
        height: widget.height ?? 200,
        color: Colors.grey[200],
        child: Center(
          child: SizedBox(
            width: 30,
            height: 30,
            child: CircularProgressIndicator(
              strokeWidth: 2,
              valueColor: AlwaysStoppedAnimation<Color>(Colors.grey[400]!),
            ),
          ),
        ),
      );
    }

    return CachedNetworkImage(
      imageUrl: widget.imageUrl,
      width: widget.width,
      height: widget.height,
      fit: widget.fit,
      placeholder: (context, url) => Container(
        width: widget.width,
        height: widget.height ?? 200,
        color: Colors.grey[200],
        child: Center(
          child: SizedBox(
            width: 30,
            height: 30,
            child: CircularProgressIndicator(strokeWidth: 2),
          ),
        ),
      ),
      errorWidget: (context, url, error) => Container(
        width: widget.width,
        height: widget.height ?? 200,
        color: Colors.grey[300],
        child: const Icon(Icons.broken_image, size: 50, color: Colors.grey),
      ),
      memCacheWidth: widget.width?.toInt(),
      memCacheHeight: widget.height?.toInt(),
      maxWidthDiskCache: 1000,
      maxHeightDiskCache: 1000,
    );
  }
}
```

#### 3. 优化HTML内容Widget
**文件**: `flutter_app_new/lib/widgets/optimized_html_content_widget.dart`

```dart
import 'package:flutter/material.dart';
import 'package:flutter_html/flutter_html.dart';
import 'package:visibility_detector/visibility_detector.dart';

class OptimizedHtmlContentWidget extends StatefulWidget {
  final String content;
  final String? title;

  const OptimizedHtmlContentWidget({
    Key? key,
    required this.content,
    this.title,
  }) : super(key: key);

  @override
  State<OptimizedHtmlContentWidget> createState() => _OptimizedHtmlContentWidgetState();
}

class _OptimizedHtmlContentWidgetState extends State<OptimizedHtmlContentWidget> {
  bool _isVisible = false;

  @override
  Widget build(BuildContext context) {
    return VisibilityDetector(
      key: Key('html-content-${widget.title}'),
      onVisibilityChanged: (visibilityInfo) {
        if (!_isVisible && visibilityInfo.visibleFraction > 0.3) {
          setState(() {
            _isVisible = true;
          });
        }
      },
      child: _buildContent(),
    );
  }

  Widget _buildContent() {
    if (!_isVisible) {
      // 占位骨架屏
      return _buildSkeleton();
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        if (widget.title != null && widget.title!.isNotEmpty)
          Padding(
            padding: const EdgeInsets.all(16.0),
            child: Text(
              widget.title!,
              style: Theme.of(context).textTheme.titleLarge,
            ),
          ),
        Html(
          data: widget.content,
          style: {
            'body': Style(
              fontSize: FontSize(16.0),
              lineHeight: const LineHeight(1.5),
              color: Colors.black87,
              padding: HtmlPaddings.all(16),
            ),
            // ... 其他样式配置
          },
          // 优化图片渲染
          customWidgetBuilder: (element) {
            if (element.localName == 'img') {
              final src = element.attributes['src'];
              if (src != null) {
                return LazyLoadImageWidget(
                  imageUrl: src,
                  width: double.infinity,
                );
              }
            }
            return null;
          },
        ),
      ],
    );
  }

  Widget _buildSkeleton() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        if (widget.title != null && widget.title!.isNotEmpty)
          Padding(
            padding: const EdgeInsets.all(16.0),
            child: Container(
              width: 200,
              height: 24,
              color: Colors.grey[200],
            ),
          ),
        Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            children: List.generate(
              5,
              (index) => Padding(
                padding: const EdgeInsets.only(bottom: 12.0),
                child: Container(
                  width: double.infinity,
                  height: 16,
                  color: Colors.grey[200],
                ),
              ),
            ),
          ),
        ),
      ],
    );
  }
}
```

#### 4. 实现智能缓存策略
**文件**: `flutter_app_new/lib/utils/cache_manager.dart`

```dart
import 'package:flutter_cache_manager/flutter_cache_manager.dart';

class CustomCacheManager {
  static const key = 'customCacheKey';

  static CacheManager instance = CacheManager(
    Config(
      key,
      stalePeriod: const Duration(days: 7), // 缓存7天
      maxNrOfCacheObjects: 200, // 最多缓存200个文件
      repo: JsonCacheInfoRepository(databaseName: key),
      fileSystem: IOFileSystem(key),
      fileService: HttpFileService(),
    ),
  );
}

// 针对不同类型图片使用不同策略
class ImageCacheStrategy {
  static const productImageCache = CacheManager(
    Config(
      'productImages',
      stalePeriod: Duration(days: 14), // 商品图片缓存14天
      maxNrOfCacheObjects: 100,
    ),
  );

  static const detailImageCache = CacheManager(
    Config(
      'detailImages',
      stalePeriod: Duration(days: 7), // 详情图片缓存7天
      maxNrOfCacheObjects: 200,
    ),
  );
}
```

#### 5. 优化商品详情页滚动性能
**文件**: `flutter_app_new/lib/presentation/pages/optimized_product_detail_page.dart`

```dart
import 'package:flutter/material.dart';
import 'package:flutter_app_new/data/models/product.dart';
import 'package:flutter_app_new/widgets/lazy_load_image_widget.dart';
import 'package:flutter_app_new/widgets/optimized_html_content_widget.dart';

class OptimizedProductDetailPage extends StatefulWidget {
  final Product product;

  const OptimizedProductDetailPage({
    Key? key,
    required this.product,
  }) : super(key: key);

  @override
  State<OptimizedProductDetailPage> createState() => _OptimizedProductDetailPageState();
}

class _OptimizedProductDetailPageState extends State<OptimizedProductDetailPage>
    with AutomaticKeepAliveClientMixin {
  @override
  bool get wantKeepAlive => true; // 保持页面状态

  @override
  Widget build(BuildContext context) {
    super.build(context); // 必须调用

    return Scaffold(
      appBar: AppBar(title: Text(widget.product.title)),
      body: SingleChildScrollView(
        physics: const BouncingScrollPhysics(), // iOS风格弹性滚动
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // 主图（使用懒加载）
            LazyLoadImageWidget(
              imageUrl: widget.product.imageUrl,
              height: 300,
              fit: BoxFit.contain,
            ),

            // 基本信息卡片
            _buildBasicInfo(),

            // 内容分区列表（使用优化后的HTML Widget）
            if (widget.product.contentSections != null)
              ...widget.product.contentSections!.map((section) {
                return OptimizedHtmlContentWidget(
                  content: section.content,
                  title: section.title ?? _getDefaultTitle(section.sectionType),
                );
              }),

            // 营养成分表
            if (widget.product.nutritionFacts != null)
              _buildNutritionTable(),
          ],
        ),
      ),
    );
  }

  Widget _buildBasicInfo() {
    return Card(
      margin: const EdgeInsets.all(16),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              widget.product.title,
              style: Theme.of(context).textTheme.headlineSmall,
            ),
            const SizedBox(height: 8),
            Text(
              '¥${widget.product.price.toStringAsFixed(2)}',
              style: Theme.of(context).textTheme.titleLarge?.copyWith(
                    color: Colors.red,
                    fontWeight: FontWeight.bold,
                  ),
            ),
            const SizedBox(height: 16),
            Text(widget.product.description ?? ''),
          ],
        ),
      ),
    );
  }

  Widget _buildNutritionTable() {
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
            _buildNutritionTableContent(),
          ],
        ),
      ),
    );
  }

  Widget _buildNutritionTableContent() {
    final nutrition = widget.product.nutritionFacts!;
    final nutrients = [
      {'name': '热量', 'value': nutrition['calories'], 'unit': 'kcal'},
      {'name': '蛋白质', 'value': nutrition['protein'], 'unit': 'g'},
      {'name': '脂肪', 'value': nutrition['fat'], 'unit': 'g'},
      {'name': '碳水化合物', 'value': nutrition['carbohydrates'], 'unit': 'g'},
      {'name': '钠', 'value': nutrition['sodium'], 'unit': 'mg'},
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

  String _getDefaultTitle(String sectionType) {
    switch (sectionType) {
      case 'story':
        return '菜品故事';
      case 'nutrition':
        return '营养价值';
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

#### 6. 实现预加载策略
**文件**: `flutter_app_new/lib/services/preloading_service.dart`

```dart
import 'package:flutter_cache_manager/flutter_cache_manager.dart';
import 'package:cached_network_image/cached_network_image.dart';

class PreloadingService {
  // 预加载商品详情中的所有图片
  static Future<void> preloadProductImages(Product product) async {
    final imageUrls = <String>[];

    // 添加主图
    if (product.imageUrl != null) {
      imageUrls.add(product.imageUrl!);
    }

    // 添加内容分区中的图片
    if (product.contentSections != null) {
      for (final section in product.contentSections!) {
        // 从HTML中提取img标签的src
        final imgRegex = RegExp(r'<img[^>]+src="([^">+]"');
        final matches = imgRegex.allMatches(section.content);
        for (final match in matches) {
          final url = match.group(1);
          if (url != null) {
            imageUrls.add(url);
          }
        }
      }
    }

    // 并行预加载所有图片
    await Future.wait(
      imageUrls.map((url) => precacheImage(CachedNetworkImageProvider(url), navigatorKey)),
    );
  }

  // 预加载相邻商品（在列表页使用）
  static Future<void> preloadAdjacentProducts(List<Product> products, int currentIndex) async {
    final startIndex = currentIndex - 1;
    final endIndex = currentIndex + 1;

    for (var i = startIndex; i <= endIndex; i++) {
      if (i >= 0 && i < products.length && i != currentIndex) {
        final product = products[i];
        if (product.imageUrl != null) {
          try {
            await DefaultCacheManager().getSingleFile(product.imageUrl!);
          } catch (e) {
            print('Failed to preload image: $e');
          }
        }
      }
    }
  }
}
```

## 实施步骤

### 步骤1: 安装依赖
```bash
cd flutter_app_new
flutter pub add visibility_detector flutter_cache_manager
```

### 步骤2: 创建懒加载图片Widget
创建`lib/widgets/lazy_load_image_widget.dart`

### 步骤3: 创建优化后的HTML内容Widget
创建`lib/widgets/optimized_html_content_widget.dart`

### 步骤4: 实现智能缓存策略
- 创建`lib/utils/cache_manager.dart`
- 配置不同的缓存策略
- 设置缓存有效期和大小限制

### 步骤5: 优化商品详情页
- 使用`AutomaticKeepAliveClientMixin`保持页面状态
- 实现弹性滚动
- 使用懒加载Widget
- 优化Widget树结构

### 步骤6: 实现预加载
创建`lib/services/preloading_service.dart`

### 步骤7: 性能测试和优化
- 测试滚动流畅度
- 测试内存使用
- 测试图片加载速度
- 优化关键指标

## 验收标准

| 验收标准 | 测试方法 | 目标值 |
|---------|---------|--------|
| 图片懒加载正常工作 | 快速滚动查看图片 | 可见时才加载 |
| 缓存命中率≥80% | 多次访问同一商品 | ≥80% |
| 滚动FPS≥55 | DevTools性能分析 | ≥55 |
| 内存占用<200MB | DevTools内存分析 | <200MB |
| 首屏加载时间<2秒 | 计时测试 | <2s |
| 缓存清理正常工作 | 测试缓存过期 | 自动清理 |

## 性能优化指标

### 滚动性能
- **目标FPS**: ≥55 (60fps理想)
- **帧构建时间**: <16ms
- **GPU渲染**: 避免overdraw

### 内存优化
- **图片内存**: 使用memCacheWidth/Height限制
- **Widget缓存**: 使用const构造函数
- **状态保持**: AutomaticKeepAliveClientMixin

### 网络优化
- **预加载**: 提前加载相邻商品图片
- **缓存策略**: 7-14天缓存有效期
- **图片优化**: 使用WebP格式（后端支持）

### 用户体验
- **骨架屏**: 加载时显示占位符
- **渐进式加载**: 先显示低分辨率图
- **错误处理**: 优雅的失败提示

## 文件清单

**新建文件**:
- `flutter_app_new/lib/widgets/lazy_load_image_widget.dart`
- `flutter_app_new/lib/widgets/optimized_html_content_widget.dart`
- `flutter_app_new/lib/utils/cache_manager.dart`
- `flutter_app_new/lib/services/preloading_service.dart`
- `flutter_app_new/lib/presentation/pages/optimized_product_detail_page.dart`

**修改文件**:
- `flutter_app_new/pubspec.yaml` - 添加依赖
- `flutter_app_new/lib/data/models/product.dart` - 可能需要添加预加载方法

## 技术要点

### VisibilityDetector使用
- 检测Widget可见性
- 设置合理的可见阈值（0.3-0.5）
- 避免重复加载

### CachedNetworkImage配置
- memCacheWidth/Height: 限制内存缓存大小
- maxWidthDiskCache/maxHeightDiskCache: 限制磁盘缓存
- 自定义CacheManager: 不同类型使用不同策略

### 性能监控
```dart
// 使用Flutter DevTools
// 1. flutter pub global activate devtools
// 2. flutter pub global run devtools
// 3. 在应用中运行: flutter run --profile
```

### 内存优化技巧
1. 使用`const`构造函数
2. 避免在build中创建对象
3. 使用`ListView.builder`而非`ListView`
4. 及时释放不用的资源
5. 合理使用图片缓存

## 注意事项

1. **iOS配置**: 确保Info.plist中有网络权限
2. **Android配置**: 确保AndroidManifest.xml有网络权限
3. **缓存清理**: 提供清除缓存的功能
4. **错误处理**: 网络错误时的降级方案
5. **测试环境**: 在真实设备上测试性能

## 与其他任务的集成

- **依赖APP-001**: 基于已实现的HtmlContentWidget优化
- **依赖API-002**: 使用后端图片处理API
- **为TEST-001准备**: 优化后的代码需要更新测试用例

## 性能测试方法

### 1. 滚动性能测试
```bash
# 在profile模式运行
flutter run --profile

# 使用DevTools连接
flutter attach --profile
```

### 2. 内存测试
```dart
// 打印内存使用
import 'dart:developer';
void printMemoryUsage() {
  final info = VMInfo_getCurrentRSS();
  print('Memory usage: ${info / 1024 / 1024} MB');
}
```

### 3. 缓存命中率测试
```dart
// 统计缓存命中
int cacheHits = 0;
int totalRequests = 0;
// 计算命中率
final hitRate = cacheHits / totalRequests;
print('Cache hit rate: ${hitRate * 100}%');
```

### 4. 加载时间测试
```dart
final stopwatch = Stopwatch()..start();
await loadImage();
stopwatch.stop();
print('Load time: ${stopwatch.elapsedMilliseconds}ms');
```
