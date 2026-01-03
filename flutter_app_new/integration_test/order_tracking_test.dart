import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';
import 'package:flutter_app_new/main.dart' as app;
import 'package:flutter/material.dart';

void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();

  group('订单支付和状态跟踪测试', () {
    testWidgets('查看订单列表', (WidgetTester tester) async {
      // 启动应用
      app.main();
      await tester.pumpAndSettle();

      // 等待加载完成
      await tester.pump(const Duration(seconds: 3));

      // 进入订单列表（通过底部导航）
      final orderIcon = find.byIcon(Icons.receipt_long);
      if (orderIcon.evaluate().isNotEmpty) {
        await tester.tap(orderIcon);
        await tester.pumpAndSettle();

        // 验证进入订单列表页面
        expect(find.text('我的订单'), findsOneWidget);

        // 验证状态筛选存在
        expect(find.text('全部'), findsOneWidget);
        expect(find.text('待付款'), findsOneWidget);
        expect(find.text('制作中'), findsOneWidget);
        expect(find.text('配送中'), findsOneWidget);
        expect(find.text('已完成'), findsOneWidget);
      }
    });

    testWidgets('按状态筛选订单', (WidgetTester tester) async {
      // 启动应用
      app.main();
      await tester.pumpAndSettle();

      // 等待加载完成
      await tester.pump(const Duration(seconds: 3));

      // 进入订单列表
      final orderIcon = find.byIcon(Icons.receipt_long);
      if (orderIcon.evaluate().isNotEmpty) {
        await tester.tap(orderIcon);
        await tester.pumpAndSettle();

        // 点击"待付款"筛选
        await tester.tap(find.text('待付款'));
        await tester.pumpAndSettle();

        // 等待筛选结果
        await tester.pump(const Duration(seconds: 1));

        // 点击"已完成"筛选
        await tester.tap(find.text('已完成'));
        await tester.pumpAndSettle();

        // 等待筛选结果
        await tester.pump(const Duration(seconds: 1));
      }
    });

    testWidgets('查看订单详情', (WidgetTester tester) async {
      // 启动应用
      app.main();
      await tester.pumpAndSettle();

      // 等待加载完成
      await tester.pump(const Duration(seconds: 3));

      // 进入订单列表
      final orderIcon = find.byIcon(Icons.receipt_long);
      if (orderIcon.evaluate().isNotEmpty) {
        await tester.tap(orderIcon);
        await tester.pumpAndSettle();

        // 如果有订单，点击第一个订单
        final orderCards = find.byType(Card);
        if (orderCards.evaluate().isNotEmpty) {
          await tester.tap(orderCards.first);
          await tester.pumpAndSettle();

          // 验证进入订单详情页
          expect(find.text('订单详情'), findsOneWidget);
        }
      }
    });

    testWidgets('下拉刷新订单列表', (WidgetTester tester) async {
      // 启动应用
      app.main();
      await tester.pumpAndSettle();

      // 等待加载完成
      await tester.pump(const Duration(seconds: 3));

      // 进入订单列表
      final orderIcon = find.byIcon(Icons.receipt_long);
      if (orderIcon.evaluate().isNotEmpty) {
        await tester.tap(orderIcon);
        await tester.pumpAndSettle();

        // 执行下拉刷新
        await tester.drag(
          find.byType(RefreshIndicator),
          const Offset(0, 300),
        );
        await tester.pumpAndSettle();

        // 等待刷新完成
        await tester.pump(const Duration(seconds: 2));

        // 验证订单列表仍然存在
        expect(find.text('我的订单'), findsOneWidget);
      }
    });

    testWidgets('订单状态变化流程', (WidgetTester tester) async {
      // 启动应用
      app.main();
      await tester.pumpAndSettle();

      // 等待加载完成
      await tester.pump(const Duration(seconds: 3));

      // 进入订单列表
      final orderIcon = find.byIcon(Icons.receipt_long);
      if (orderIcon.evaluate().isNotEmpty) {
        await tester.tap(orderIcon);
        await tester.pumpAndSettle();

        // 查看所有订单
        expect(find.text('全部'), findsOneWidget);

        // 筛选待付款订单
        await tester.tap(find.text('待付款'));
        await tester.pumpAndSettle();

        // 如果有待付款订单，可以模拟支付流程
        final orderCards = find.byType(Card);
        if (orderCards.evaluate().isNotEmpty) {
          await tester.tap(orderCards.first);
          await tester.pumpAndSettle();

          // 在订单详情页查找支付按钮
          final payButton = find.text('立即支付');
          if (payButton.evaluate().isNotEmpty) {
            await tester.tap(payButton);
            await tester.pumpAndSettle();

            // 验证支付对话框或页面
            expect(find.byType(AlertDialog), findsOneWidget);
          }
        }
      }
    });

    testWidgets('取消订单', (WidgetTester tester) async {
      // 启动应用
      app.main();
      await tester.pumpAndSettle();

      // 等待加载完成
      await tester.pump(const Duration(seconds: 3));

      // 进入订单列表
      final orderIcon = find.byIcon(Icons.receipt_long);
      if (orderIcon.evaluate().isNotEmpty) {
        await tester.tap(orderIcon);
        await tester.pumpAndSettle();

        // 查看待付款订单
        await tester.tap(find.text('待付款'));
        await tester.pumpAndSettle();

        // 如果有待付款订单，尝试取消
        final orderCards = find.byType(Card);
        if (orderCards.evaluate().isNotEmpty) {
          await tester.tap(orderCards.first);
          await tester.pumpAndSettle();

          // 查找取消按钮
          final cancelButton = find.text('取消订单');
          if (cancelButton.evaluate().isNotEmpty) {
            await tester.tap(cancelButton);
            await tester.pumpAndSettle();

            // 确认取消
            expect(find.byType(AlertDialog), findsOneWidget);

            final confirmButton = find.text('确认');
            if (confirmButton.evaluate().isNotEmpty) {
              await tester.tap(confirmButton);
              await tester.pumpAndSettle();

              // 验证成功提示
              expect(find.byType(SnackBar), findsOneWidget);
            }
          }
        }
      }
    });
  });
}
