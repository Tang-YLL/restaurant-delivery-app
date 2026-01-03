import '../utils/cache_manager.dart';
import '../data/models/product.dart';

/// 图片预加载服务
///
/// 特性：
/// - 预加载商品详情所有图片
/// - 预加载相邻商品图片
/// - 从HTML中提取图片URL
/// - 使用智能缓存管理器
class PreloadingService {
  static const int maxPreloadImages = 5; // 最多预加载5张图片

  /// 预加载商品详情的所有图片
  ///
  /// [product] 商品对象
  /// [priority] 是否为高优先级（立即加载）
  Future<void> preloadProductImages(Product product,
      {bool priority = false}) async {
    try {
      final imageUrls = <String>[];

      // 1. 添加主图
      if (product.imageUrl.isNotEmpty) {
        imageUrls.add(product.imageUrl);
      }

      // 2. 从HTML内容中提取图片
      if (product.contentSections != null) {
        for (final section in product.contentSections!) {
          final urls = _extractImageUrlsFromHtml(section.content);
          imageUrls.addAll(urls);
        }
      }

      // 3. 限制预加载数量
      final urlsToPreload =
          imageUrls.take(maxPreloadImages).where((url) => url.isNotEmpty).toList();

      if (urlsToPreload.isEmpty) {
        return;
      }

      // 4. 并发预加载（限制并发数）
      final futures = <Future>[];
      for (final url in urlsToPreload) {
        if (priority) {
          // 高优先级：立即加载
          futures.add(_preloadImage(url));
        } else {
          // 低优先级：延迟加载
          futures.add(
              Future.delayed(const Duration(milliseconds: 100), () => _preloadImage(url)));
        }
      }

      await Future.wait(futures);
    } catch (e) {
      // 预加载失败，静默处理
    }
  }

  /// 预加载相邻商品的图片
  ///
  /// [products] 商品列表
  /// [currentIndex] 当前商品索引
  Future<void> preloadAdjacentProducts(
      List<Product> products, int currentIndex) async {
    try {
      final adjacentProducts = <Product>[];

      // 添加前2个商品
      if (currentIndex > 0) {
        adjacentProducts.add(products[currentIndex - 1]);
      }
      if (currentIndex > 1) {
        adjacentProducts.add(products[currentIndex - 2]);
      }

      // 添加后2个商品
      if (currentIndex < products.length - 1) {
        adjacentProducts.add(products[currentIndex + 1]);
      }
      if (currentIndex < products.length - 2) {
        adjacentProducts.add(products[currentIndex + 2]);
      }

      // 预加载相邻商品的主图
      final futures = adjacentProducts.map((product) {
        return _preloadImage(product.imageUrl);
      }).toList();

      await Future.wait(futures);
    } catch (e) {
      // 预加载失败，静默处理
    }
  }

  /// 预加载单个图片
  Future<void> _preloadImage(String imageUrl) async {
    try {
      if (imageUrl.isEmpty) return;

      final cacheManager = CustomCacheManager.getCacheManagerForUrl(imageUrl);

      // 使用CachedNetworkImage预加载
      await cacheManager.getSingleFile(imageUrl);
    } catch (e) {
      // 预加载失败，静默处理
    }
  }

  /// 从HTML中提取图片URL
  List<String> _extractImageUrlsFromHtml(String htmlContent) {
    final imageUrls = <String>[];

    try {
      // 简单的正则表达式提取img标签的src
      final regex = RegExp(r'''<img[^>]+src=["']([^"']+)["']''',
          caseSensitive: false);
      final matches = regex.allMatches(htmlContent);

      for (final match in matches) {
        final url = match.group(1);
        if (url != null && url.isNotEmpty && !url.startsWith('data:')) {
          imageUrls.add(url);
        }
      }
    } catch (e) {
      // 提取失败，返回空列表
    }

    return imageUrls;
  }

  /// 清空预加载缓存
  Future<void> clearPreloadCache() async {
    try {
      await CustomCacheManager.clearAllCache();
    } catch (e) {
      // 清空缓存失败，静默处理
    }
  }

  /// 预加载图片列表
  Future<void> preloadImageUrls(List<String> imageUrls) async {
    try {
      final urlsToPreload =
          imageUrls.take(maxPreloadImages).where((url) => url.isNotEmpty).toList();

      final futures = urlsToPreload.map((url) => _preloadImage(url));

      await Future.wait(futures);
    } catch (e) {
      // 预加载失败，静默处理
    }
  }

  /// 预加载单个图片URL
  Future<void> preloadSingleImage(String imageUrl) async {
    await _preloadImage(imageUrl);
  }
}
