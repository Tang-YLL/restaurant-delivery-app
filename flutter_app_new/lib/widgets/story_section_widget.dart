import 'package:flutter/material.dart';
import 'html_content_widget.dart';

class StorySectionWidget extends StatelessWidget {
  final String content;
  final String? title;

  const StorySectionWidget({
    super.key,
    required this.content,
    this.title,
  });

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
