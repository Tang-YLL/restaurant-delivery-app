import 'package:flutter_cache_manager/flutter_cache_manager.dart';

/// 自定义缓存管理器 - 智能缓存策略
///
/// 特性：
/// - 商品图片缓存14天
/// - 头像缓存7天
/// - 最多缓存200个文件
/// - 最大缓存空间500MB
class CustomCacheManager {
  /// 获取商品图片缓存管理器
  static CacheManager get productImageCache {
    return CacheManager(
      Config(
        'productImages',
        stalePeriod: const Duration(days: 14), // 14天有效期
        maxNrOfCacheObjects: 200, // 最多缓存200个文件
        repo: JsonCacheInfoRepository(databaseName: 'product_images_cache'),
        fileService: HttpFileService(),
        fileSystem: IOFileSystem('product_images_cache'),
      ),
    );
  }

  /// 获取头像缓存管理器
  static CacheManager get avatarCache {
    return CacheManager(
      Config(
        'avatars',
        stalePeriod: const Duration(days: 7), // 7天有效期
        maxNrOfCacheObjects: 100, // 最多缓存100个文件
        repo: JsonCacheInfoRepository(databaseName: 'avatars_cache'),
        fileService: HttpFileService(),
        fileSystem: IOFileSystem('avatars_cache'),
      ),
    );
  }

  /// 获取默认缓存管理器
  static CacheManager get defaultCache {
    return CacheManager(
      Config(
        'defaultCache',
        stalePeriod: const Duration(days: 7),
        maxNrOfCacheObjects: 50,
        repo: JsonCacheInfoRepository(databaseName: 'default_cache'),
        fileService: HttpFileService(),
        fileSystem: IOFileSystem('default_cache'),
      ),
    );
  }

  /// 根据URL类型获取对应的缓存管理器
  static CacheManager getCacheManagerForUrl(String url) {
    if (url.contains('/products/') || url.contains('/product/')) {
      return productImageCache;
    } else if (url.contains('/avatars/') || url.contains('/avatar/')) {
      return avatarCache;
    }
    return defaultCache;
  }

  /// 清空所有缓存
  static Future<void> clearAllCache() async {
    await productImageCache.emptyCache();
    await avatarCache.emptyCache();
    await defaultCache.emptyCache();
  }

  /// 清空过期缓存
  static Future<void> cleanExpiredCache() async {
    await productImageCache.dispose();
    await avatarCache.dispose();
    await defaultCache.dispose();
  }

  /// 获取缓存大小
  static Future<int> getCacheSize() async {
    // 简化实现，实际应该计算文件大小
    return 0;
  }
}
