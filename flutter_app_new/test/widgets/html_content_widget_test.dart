import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_app_new/widgets/html_content_widget.dart';

void main() {
  group('HtmlContentWidget Tests', () {
    testWidgets('应该渲染HTML内容', (WidgetTester tester) async {
      // Arrange
      const htmlContent = '<p>这是一段测试内容</p>';

      // Act
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(
            body: HtmlContentWidget(
              content: htmlContent,
            ),
          ),
        ),
      );

      // Assert
      expect(find.text('这是一段测试内容'), findsOneWidget);
    });

    testWidgets('应该渲染带标题的HTML内容', (WidgetTester tester) async {
      // Arrange
      const htmlContent = '<p>内容</p>';
      const title = '品牌故事';

      // Act
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(
            body: HtmlContentWidget(
              content: htmlContent,
              title: title,
            ),
          ),
        ),
      );

      // Assert
      expect(find.text(title), findsOneWidget);
      expect(find.text('内容'), findsOneWidget);
    });

    testWidgets('应该渲染HTML标题标签', (WidgetTester tester) async {
      // Arrange
      const htmlContent = '<h1>主标题</h1><h2>副标题</h2>';

      // Act
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(
            body: HtmlContentWidget(
              content: htmlContent,
            ),
          ),
        ),
      );

      // Assert
      expect(find.text('主标题'), findsOneWidget);
      expect(find.text('副标题'), findsOneWidget);
    });

    testWidgets('应该渲染HTML列表', (WidgetTester tester) async {
      // Arrange
      const htmlContent = '<ul><li>项目1</li><li>项目2</li></ul>';

      // Act
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(
            body: HtmlContentWidget(
              content: htmlContent,
            ),
          ),
        ),
      );

      // Assert
      expect(find.text('项目1'), findsOneWidget);
      expect(find.text('项目2'), findsOneWidget);
    });
  });
}
