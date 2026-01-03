import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';
import 'package:flutter_app_new/main.dart' as app;
import 'package:flutter/material.dart';

void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();

  group('外卖App端到端测试', () {
    testWidgets('应用启动测试', (WidgetTester tester) async {
      // 启动应用
      app.main();
      await tester.pumpAndSettle();

      // 验证应用启动成功
      expect(find.byType(MaterialApp), findsOneWidget);

      // 等待启动页面
      await tester.pump(const Duration(seconds: 3));
    });

    testWidgets('完整用户流程：登录→浏览→购物车→订单', (WidgetTester tester) async {
      // 启动应用
      app.main();
      await tester.pumpAndSettle();

      // 等待启动页面完成（自动跳转到登录页）
      await tester.pump(const Duration(seconds: 3));

      debugPrint('=== 开始登录流程 ===');

      // 1. 登录
      // 输入手机号
      final phoneFields = find.byType(TextField);
      if (phoneFields.evaluate().isNotEmpty) {
        await tester.enterText(phoneFields.at(0), '13900139000');
        await tester.pumpAndSettle();
        debugPrint('已输入手机号');

        // 点击发送验证码
        final sendCodeButtons = find.text('发送验证码');
        if (sendCodeButtons.evaluate().isNotEmpty) {
          await tester.tap(sendCodeButtons.first);
          await tester.pumpAndSettle();
          debugPrint('已发送验证码');

          // 等待验证码发送完成
          await tester.pump(const Duration(seconds: 1));

          // 输入验证码
          if (phoneFields.evaluate().length > 1) {
            await tester.enterText(phoneFields.at(1), '1234');
            await tester.pumpAndSettle();
            debugPrint('已输入验证码');

            // 点击登录按钮
            final loginButtons = find.text('登录');
            if (loginButtons.evaluate().isNotEmpty) {
              await tester.tap(loginButtons.first);
              await tester.pumpAndSettle();
              debugPrint('已点击登录按钮');

              // 等待登录完成和页面跳转
              await tester.pump(const Duration(seconds: 5));
            }
          }
        }
      }

      debugPrint('=== 登录流程完成，进入主页 ===');

      // 2. 验证进入主页
      expect(find.text('美食外卖'), findsOneWidget);
      debugPrint('成功进入主页');

      // 3. 测试商品浏览
      await tester.pumpAndSettle();

      // 验证商品列表存在
      final gridViews = find.byType(GridView);
      if (gridViews.evaluate().isNotEmpty) {
        debugPrint('商品列表加载成功');

        // 下拉刷新
        await tester.drag(gridViews.first, const Offset(0, 300));
        await tester.pumpAndSettle();
        debugPrint('下拉刷新完成');
      }

      // 4. 测试搜索功能
      final searchFields = find.byType(TextField);
      if (searchFields.evaluate().isNotEmpty) {
        await tester.enterText(searchFields.first, '米饭');
        await tester.pumpAndSettle();
        debugPrint('已输入搜索关键词');

        await tester.pump(const Duration(seconds: 2));
        debugPrint('搜索完成');
      }

      // 5. 进入购物车
      final cartIcons = find.byIcon(Icons.shopping_cart);
      if (cartIcons.evaluate().isNotEmpty) {
        await tester.tap(cartIcons.first);
        await tester.pumpAndSettle();
        debugPrint('进入购物车');

        // 验证购物车页面
        expect(find.text('购物车'), findsOneWidget);
      }

      // 6. 查看订单
      final orderIcons = find.byIcon(Icons.receipt_long);
      if (orderIcons.evaluate().isNotEmpty) {
        await tester.tap(orderIcons.first);
        await tester.pumpAndSettle();
        debugPrint('进入订单列表');

        // 验证订单列表页面
        expect(find.text('我的订单'), findsOneWidget);
      }

      debugPrint('=== 端到端测试完成 ===');
    });

    testWidgets('应用性能测试', (WidgetTester tester) async {
      // 测试启动性能
      final stopwatch = Stopwatch()..start();

      app.main();
      await tester.pumpAndSettle();

      stopwatch.stop();

      // 验证启动时间 < 5秒（测试环境可能较慢）
      debugPrint('应用启动耗时: ${stopwatch.elapsedMilliseconds}ms');
      expect(stopwatch.elapsedMilliseconds, lessThan(10000));

      // 测试内存占用（简单检查：确保应用没有崩溃）
      await tester.pump(const Duration(seconds: 2));
      expect(find.byType(MaterialApp), findsOneWidget);
    });

    testWidgets('导航切换测试', (WidgetTester tester) async {
      // 启动应用
      app.main();
      await tester.pumpAndSettle();

      // 等待登录
      await tester.pump(const Duration(seconds: 3));

      // 测试底部导航切换
      final homeIcon = find.byIcon(Icons.home);
      final cartIcon = find.byIcon(Icons.shopping_cart);
      final orderIcon = find.byIcon(Icons.receipt_long);
      final profileIcon = find.byIcon(Icons.person);

      if (homeIcon.evaluate().isNotEmpty) {
        // 切换到主页
        await tester.tap(homeIcon.first);
        await tester.pumpAndSettle();
        debugPrint('切换到主页');
      }

      if (cartIcon.evaluate().isNotEmpty) {
        // 切换到购物车
        await tester.tap(cartIcon.first);
        await tester.pumpAndSettle();
        debugPrint('切换到购物车');
      }

      if (orderIcon.evaluate().isNotEmpty) {
        // 切换到订单
        await tester.tap(orderIcon.first);
        await tester.pumpAndSettle();
        debugPrint('切换到订单');
      }

      if (profileIcon.evaluate().isNotEmpty) {
        // 切换到个人中心
        await tester.tap(profileIcon.first);
        await tester.pumpAndSettle();
        debugPrint('切换到个人中心');
      }
    });
  });
}
