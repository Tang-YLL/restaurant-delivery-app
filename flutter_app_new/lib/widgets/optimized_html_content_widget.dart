import 'package:flutter/material.dart';
import 'package:flutter_html/flutter_html.dart';
import 'package:visibility_detector/visibility_detector.dart';
import 'lazy_load_image_widget.dart';

/// 优化的HTML内容Widget
///
/// 特性：
/// - 基于HtmlContentWidget优化
/// - 可见性检测（30%可见阈值）
/// - 骨架屏占位符
/// - 使用懒加载图片
/// - 优化渲染性能
class OptimizedHtmlContentWidget extends StatefulWidget {
  final String content;
  final String? title;
  final double visibilityThreshold;

  const OptimizedHtmlContentWidget({
    super.key,
    required this.content,
    this.title,
    this.visibilityThreshold = 0.3,
  });

  @override
  State<OptimizedHtmlContentWidget> createState() =>
      _OptimizedHtmlContentWidgetState();
}

class _OptimizedHtmlContentWidgetState
    extends State<OptimizedHtmlContentWidget> {
  bool _isVisible = false;

  @override
  Widget build(BuildContext context) {
    return VisibilityDetector(
      key: Key('html_visibility_${widget.title}'),
      onVisibilityChanged: (VisibilityInfo info) {
        if (info.visibleFraction >= widget.visibilityThreshold && !_isVisible) {
          if (mounted) {
            setState(() {
              _isVisible = true;
            });
          }
        }
      },
      child: _isVisible
          ? _buildContent()
          : _buildSkeletonPlaceholder(),
    );
  }

  /// 构建内容
  Widget _buildContent() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        if (widget.title != null && widget.title!.isNotEmpty)
          Padding(
            padding: const EdgeInsets.all(16.0),
            child: Text(
              widget.title!,
              style: Theme.of(context).textTheme.titleLarge?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
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
              padding: HtmlPaddings.only(left: 24),
            ),
            'ol': Style(
              padding: HtmlPaddings.only(left: 24),
            ),
            'li': Style(
              margin: Margins.only(bottom: 8),
            ),
            'img': Style(
              width: Width(100, Unit.percent),
              margin: Margins.symmetric(vertical: 16),
            ),
          },
          onLinkTap: (url, _, __) {
            debugPrint('Link tapped: $url');
          },
          extensions: [
            TagExtension(
              tagsToExtend: {'img'},
              builder: (element) {
                final src = element.attributes['src'];
                if (src != null && src.isNotEmpty) {
                  return Padding(
                    padding: const EdgeInsets.symmetric(vertical: 16.0),
                    child: LazyLoadImageWidget(
                      imageUrl: src,
                      width: double.infinity,
                      fit: BoxFit.cover,
                      visibilityThreshold: 0.3,
                    ),
                  );
                }
                return const SizedBox.shrink();
              },
            ),
          ],
        ),
      ],
    );
  }

  /// 骨架屏占位符
  Widget _buildSkeletonPlaceholder() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        if (widget.title != null && widget.title!.isNotEmpty)
          Padding(
            padding: const EdgeInsets.all(16.0),
            child: Container(
              width: 200,
              height: 28,
              decoration: BoxDecoration(
                color: Colors.grey[300],
                borderRadius: BorderRadius.circular(4),
              ),
            ),
          ),
        Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: List.generate(
              5,
              (index) => Padding(
                padding: const EdgeInsets.only(bottom: 12.0),
                child: Container(
                  width: double.infinity,
                  height: 16,
                  decoration: BoxDecoration(
                    color: Colors.grey[200],
                    borderRadius: BorderRadius.circular(4),
                  ),
                ),
              ),
            ),
          ),
        ),
      ],
    );
  }
}
