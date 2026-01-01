import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';
import 'package:flutter_app_new/main.dart' as app;
import 'package:flutter/material.dart';

void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();

  group('API联调测试', () {
    testWidgets('应用启动并验证API连接', (WidgetTester tester) async {
      // 启动应用
      app.main();
      await tester.pumpAndSettle();

      // 等待启动页面
      await Future.delayed(const Duration(seconds: 3));

      // 验证应用启动
      expect(find.byType(MaterialApp), findsOneWidget);
    });

    testWidgets('登录并加载商品数据', (WidgetTester tester) async {
      // 启动应用
      app.main();
      await tester.pumpAndSettle();

      // 等待启动页面完成
      await Future.delayed(const Duration(seconds: 3));

      // 尝试登录
      final textFields = find.byType(TextField);
      if (textFields.evaluate().isNotEmpty) {
        await tester.enterText(textFields.at(0), '13900139000');
        await tester.pump();

        final sendCodeButton = find.text('发送验证码');
        if (sendCodeButton.evaluate().isNotEmpty) {
          await tester.tap(sendCodeButton.first);
          await tester.pump();
          await Future.delayed(const Duration(seconds: 1));

          if (textFields.evaluate().length > 1) {
            await tester.enterText(textFields.at(1), '1234');
            await tester.pump();

            final loginButton = find.text('登录');
            if (loginButton.evaluate().isNotEmpty) {
              await tester.tap(loginButton.first);
              await tester.pumpAndSettle();
              await Future.delayed(const Duration(seconds: 5));
            }
          }
        }
      }

      // 验证登录成功并进入主页
      expect(find.text('美食外卖'), findsOneWidget);

      // 等待商品数据加载
      await Future.delayed(const Duration(seconds: 2));

      // 验证商品列表已加载
      expect(find.byType(GridView), findsOneWidget);
    });

    testWidgets('商品搜索API测试', (WidgetTester tester) async {
      // 启动应用并登录
      app.main();
      await tester.pumpAndSettle();
      await Future.delayed(const Duration(seconds: 3));

      // 快速登录流程
      final textFields = find.byType(TextField);
      if (textFields.evaluate().length >= 2) {
        await tester.enterText(textFields.at(0), '13900139001');
        await tester.pump();

        final sendCodeButton = find.text('发送验证码');
        if (sendCodeButton.evaluate().isNotEmpty) {
          await tester.tap(sendCodeButton.first);
          await tester.pump();
          await Future.delayed(const Duration(seconds: 1));

          await tester.enterText(textFields.at(1), '1234');
          await tester.pump();

          final loginButton = find.text('登录');
          if (loginButton.evaluate().isNotEmpty) {
            await tester.tap(loginButton.first);
            await tester.pumpAndSettle();
            await Future.delayed(const Duration(seconds: 5));
          }
        }
      }

      // 测试搜索功能
      final searchField = find.byType(TextField);
      if (searchField.evaluate().isNotEmpty) {
        await tester.enterText(searchField.first, '米饭');
        await tester.pump();
        await Future.delayed(const Duration(seconds: 2));

        // 验证搜索结果
        expect(find.byType(GridView), findsOneWidget);
      }
    });
  });
}
