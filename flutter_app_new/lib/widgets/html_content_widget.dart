import 'package:flutter/material.dart';
import 'package:flutter_html/flutter_html.dart';

class HtmlContentWidget extends StatelessWidget {
  final String content;
  final String? title;

  const HtmlContentWidget({
    super.key,
    required this.content,
    this.title,
  });

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
            // 链接点击事件
            debugPrint('Link tapped: $url');
          },
          extensions: [
            TagExtension(
              tagsToExtend: {'img'},
              builder: (element) {
                // 自定义图片渲染
                final src = element.attributes['src'];
                if (src != null) {
                  return Padding(
                    padding: const EdgeInsets.symmetric(vertical: 16),
                    child: Image.network(
                      src,
                      fit: BoxFit.cover,
                      errorBuilder: (context, error, stackTrace) {
                        return Container(
                          height: 200,
                          color: Colors.grey[300],
                          child: const Icon(Icons.broken_image),
                        );
                      },
                      loadingBuilder: (context, child, loadingProgress) {
                        if (loadingProgress == null) return child;
                        return Container(
                          height: 200,
                          color: Colors.grey[200],
                          child: Center(
                            child: CircularProgressIndicator(
                              value: loadingProgress.expectedTotalBytes != null
                                  ? loadingProgress.cumulativeBytesLoaded /
                                      loadingProgress.expectedTotalBytes!
                                  : null,
                            ),
                          ),
                        );
                      },
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
}
