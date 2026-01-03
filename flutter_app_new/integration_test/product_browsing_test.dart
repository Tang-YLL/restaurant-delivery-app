import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';
import 'package:flutter_app_new/main.dart' as app;
import 'package:flutter/material.dart';

void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();

  group('商品浏览和搜索测试', () {
    testWidgets('查看商品列表', (WidgetTester tester) async {
      // 启动应用
      app.main();
      await tester.pumpAndSettle();

      // 等待加载完成
      await tester.pump(const Duration(seconds: 3));

      // 验证主页标题
      expect(find.text('美食外卖'), findsOneWidget);

      // 验证搜索框存在
      expect(find.byType(TextField), findsAtLeastNWidgets(1));

      // 验证分类筛选存在
      expect(find.text('全部'), findsOneWidget);

      // 等待商品加载
      await tester.pumpAndSettle();

      // 验证商品列表存在（至少有一个商品）
      expect(find.byType(GridView), findsOneWidget);
    });

    testWidgets('搜索商品', (WidgetTester tester) async {
      // 启动应用
      app.main();
      await tester.pumpAndSettle();

      // 等待加载完成
      await tester.pump(const Duration(seconds: 3));

      // 点击搜索框
      final searchField = find.byType(TextField);
      await tester.tap(searchField);
      await tester.pumpAndSettle();

      // 输入搜索关键词
      await tester.enterText(searchField, '米饭');
      await tester.pumpAndSettle();

      // 等待搜索结果
      await tester.pump(const Duration(seconds: 2));

      // 验证搜索结果
      expect(find.byType(GridView), findsOneWidget);
    });

    testWidgets('分类筛选', (WidgetTester tester) async {
      // 启动应用
      app.main();
      await tester.pumpAndSettle();

      // 等待加载完成
      await tester.pump(const Duration(seconds: 3));

      // 点击第一个分类（非"全部"）
      final categoryChips = find.byType(Card);
      expect(categoryChips, findsAtLeastNWidgets(1));

      if (categoryChips.evaluate().length > 1) {
        // 点击第二个分类
        await tester.tap(categoryChips.at(1));
        await tester.pumpAndSettle();

        // 等待筛选结果
        await tester.pump(const Duration(seconds: 2));

        // 验证商品列表更新
        expect(find.byType(GridView), findsOneWidget);
      }

      // 点击"全部"分类
      await tester.tap(find.text('全部'));
      await tester.pumpAndSettle();

      // 验证显示所有商品
      expect(find.byType(GridView), findsOneWidget);
    });

    testWidgets('下拉刷新商品列表', (WidgetTester tester) async {
      // 启动应用
      app.main();
      await tester.pumpAndSettle();

      // 等待加载完成
      await tester.pump(const Duration(seconds: 3));

      // 执行下拉刷新
      await tester.drag(
        find.byType(GridView),
        const Offset(0, 300),
      );
      await tester.pumpAndSettle();

      // 等待刷新完成
      await tester.pump(const Duration(seconds: 2));

      // 验证商品列表仍然存在
      expect(find.byType(GridView), findsOneWidget);
    });

    testWidgets('清除搜索条件', (WidgetTester tester) async {
      // 启动应用
      app.main();
      await tester.pumpAndSettle();

      // 等待加载完成
      await tester.pump(const Duration(seconds: 3));

      // 输入搜索关键词
      final searchField = find.byType(TextField);
      await tester.enterText(searchField, '测试');
      await tester.pumpAndSettle();

      // 点击清除按钮
      final clearButton = find.byIcon(Icons.clear);
      if (clearButton.evaluate().isNotEmpty) {
        await tester.tap(clearButton);
        await tester.pumpAndSettle();

        // 验证搜索框被清空
        final textField = tester.widget<TextField>(searchField);
        expect(textField.controller?.text, '');
      }
    });
  });
}
