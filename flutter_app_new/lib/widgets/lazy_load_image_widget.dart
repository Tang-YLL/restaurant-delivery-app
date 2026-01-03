import 'package:flutter/material.dart';
import 'package:visibility_detector/visibility_detector.dart';
import 'package:cached_network_image/cached_network_image.dart';
import '../utils/cache_manager.dart';

/// 懒加载图片Widget
///
/// 特性：
/// - 使用VisibilityDetector检测可见性
/// - 可见度>50%时才开始加载
/// - 显示骨架屏占位符
/// - 使用CachedNetworkImage进行智能缓存
/// - 限制内存占用（memCacheWidth/Height）
class LazyLoadImageWidget extends StatefulWidget {
  final String imageUrl;
  final double? width;
  final double? height;
  final BoxFit fit;
  final double visibilityThreshold; // 可见度阈值，默认0.5（50%）
  final Widget? placeholder;
  final Widget? errorWidget;
  final bool useCache; // 是否使用缓存

  const LazyLoadImageWidget({
    super.key,
    required this.imageUrl,
    this.width,
    this.height,
    this.fit = BoxFit.cover,
    this.visibilityThreshold = 0.5,
    this.placeholder,
    this.errorWidget,
    this.useCache = true,
  });

  @override
  State<LazyLoadImageWidget> createState() => _LazyLoadImageWidgetState();
}

class _LazyLoadImageWidgetState extends State<LazyLoadImageWidget> {
  bool _isVisible = false;

  @override
  Widget build(BuildContext context) {
    return VisibilityDetector(
      key: Key('visibility_detector_${widget.imageUrl}'),
      onVisibilityChanged: (VisibilityInfo info) {
        // 当可见度超过阈值时才开始加载
        if (info.visibleFraction >= widget.visibilityThreshold && !_isVisible) {
          if (mounted) {
            setState(() {
              _isVisible = true;
            });
          }
        }
      },
      child: SizedBox(
        width: widget.width,
        height: widget.height,
        child: _isVisible
            ? _buildImage()
            : (widget.placeholder ?? _buildDefaultPlaceholder()),
      ),
    );
  }

  /// 构建图片
  Widget _buildImage() {
    if (widget.useCache) {
      // 使用缓存管理器
      // 检查是否为 infinity 或 NaN，避免 toInt() 错误
      final width = widget.width;
      final height = widget.height;
      final isValidWidth = width != null && width.isFinite && width > 0;
      final isValidHeight = height != null && height.isFinite && height > 0;

      return CachedNetworkImage(
        imageUrl: widget.imageUrl,
        width: width,
        height: height,
        fit: widget.fit,
        cacheManager: CustomCacheManager.getCacheManagerForUrl(widget.imageUrl),
        memCacheWidth: isValidWidth ? width.toInt() : null,
        memCacheHeight: isValidHeight ? height.toInt() : null,
        placeholder: (context, url) =>
            widget.placeholder ?? _buildShimmerPlaceholder(),
        errorWidget: (context, url, error) =>
            widget.errorWidget ?? _buildErrorWidget(error),
        imageBuilder: (context, imageProvider) {
          return Image(
            image: imageProvider,
            width: width,
            height: height,
            fit: widget.fit,
          );
        },
      );
    } else {
      // 不使用缓存
      return Image.network(
        widget.imageUrl,
        width: widget.width,
        height: widget.height,
        fit: widget.fit,
        loadingBuilder: (context, child, loadingProgress) {
          if (loadingProgress == null) {
            return child;
          }
          return widget.placeholder ?? _buildShimmerPlaceholder();
        },
        errorBuilder: (context, error, stackTrace) {
          return widget.errorWidget ?? _buildErrorWidget(error);
        },
      );
    }
  }

  /// 默认占位符
  Widget _buildDefaultPlaceholder() {
    return Container(
      width: widget.width,
      height: widget.height,
      color: Colors.grey[200],
      child: const Center(
        child: Icon(
          Icons.image,
          color: Colors.grey,
          size: 48,
        ),
      ),
    );
  }

  /// 骨架屏占位符
  Widget _buildShimmerPlaceholder() {
    return Container(
      width: widget.width,
      height: widget.height,
      decoration: BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [
            Colors.grey[300]!,
            Colors.grey[200]!,
            Colors.grey[300]!,
          ],
          stops: const [0.0, 0.5, 1.0],
        ),
      ),
      child: const Center(
        child: SizedBox(
          width: 24,
          height: 24,
          child: CircularProgressIndicator(
            strokeWidth: 2,
            valueColor: AlwaysStoppedAnimation<Color>(Colors.grey),
          ),
        ),
      ),
    );
  }

  /// 错误Widget
  Widget _buildErrorWidget(dynamic error) {
    return Container(
      width: widget.width,
      height: widget.height,
      color: Colors.grey[200],
      child: const Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            Icons.broken_image,
            color: Colors.grey,
            size: 48,
          ),
          SizedBox(height: 8),
          Text(
            '图片加载失败',
            style: TextStyle(
              color: Colors.grey,
              fontSize: 12,
            ),
          ),
        ],
      ),
    );
  }
}

/// 简化版懒加载图片 - 用于列表项
class LazyLoadImageSimple extends StatelessWidget {
  final String imageUrl;
  final double? width;
  final double? height;
  final BoxFit fit;

  const LazyLoadImageSimple({
    super.key,
    required this.imageUrl,
    this.width,
    this.height,
    this.fit = BoxFit.cover,
  });

  @override
  Widget build(BuildContext context) {
    return LazyLoadImageWidget(
      imageUrl: imageUrl,
      width: width,
      height: height,
      fit: fit,
      visibilityThreshold: 0.3, // 列表项使用更低的阈值（30%）
    );
  }
}
