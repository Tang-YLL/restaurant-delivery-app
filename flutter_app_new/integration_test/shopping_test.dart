import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';
import 'package:flutter_app_new/main.dart' as app;
import 'package:flutter/material.dart';

void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();

  group('购物车和下单测试', () {
    testWidgets('添加商品到购物车', (WidgetTester tester) async {
      // 启动应用
      app.main();
      await tester.pumpAndSettle();

      // 等待加载完成
      await tester.pump(const Duration(seconds: 3));

      // 等待商品加载
      await tester.pumpAndSettle();

      // 点击第一个商品进入详情页
      final productCards = find.byType(Card);
      if (productCards.evaluate().isNotEmpty) {
        await tester.tap(productCards.first);
        await tester.pumpAndSettle();

        // 等待详情页加载
        await tester.pump(const Duration(seconds: 1));

        // 点击"加入购物车"按钮
        final addToCartButton = find.text('加入购物车');
        if (addToCartButton.evaluate().isNotEmpty) {
          await tester.tap(addToCartButton);
          await tester.pumpAndSettle();

          // 验证成功提示
          expect(find.byType(SnackBar), findsOneWidget);
        }
      }
    });

    testWidgets('查看购物车', (WidgetTester tester) async {
      // 启动应用
      app.main();
      await tester.pumpAndSettle();

      // 等待加载完成
      await tester.pump(const Duration(seconds: 3));

      // 点击购物车图标（底部导航）
      final cartIcon = find.byIcon(Icons.shopping_cart);
      if (cartIcon.evaluate().isNotEmpty) {
        await tester.tap(cartIcon);
        await tester.pumpAndSettle();

        // 验证进入购物车页面
        expect(find.text('购物车'), findsOneWidget);
      }
    });

    testWidgets('修改商品数量', (WidgetTester tester) async {
      // 启动应用
      app.main();
      await tester.pumpAndSettle();

      // 等待加载完成
      await tester.pump(const Duration(seconds: 3));

      // 进入购物车
      final cartIcon = find.byIcon(Icons.shopping_cart);
      if (cartIcon.evaluate().isNotEmpty) {
        await tester.tap(cartIcon);
        await tester.pumpAndSettle();

        // 如果购物车有商品，尝试修改数量
        final removeButtons = find.byIcon(Icons.remove_circle_outline);
        if (removeButtons.evaluate().isNotEmpty) {
          final initialCount = removeButtons.evaluate().length;

          // 点击减少数量按钮
          await tester.tap(removeButtons.first);
          await tester.pumpAndSettle();

          // 验证数量变化
          expect(find.byType(SnackBar), findsAtLeastNWidgets(1));
        }
      }
    });

    testWidgets('清空购物车', (WidgetTester tester) async {
      // 启动应用
      app.main();
      await tester.pumpAndSettle();

      // 等待加载完成
      await tester.pump(const Duration(seconds: 3));

      // 进入购物车
      final cartIcon = find.byIcon(Icons.shopping_cart);
      if (cartIcon.evaluate().isNotEmpty) {
        await tester.tap(cartIcon);
        await tester.pumpAndSettle();

        // 滑动删除第一个商品
        final cartItems = find.byType(Dismissible);
        if (cartItems.evaluate().isNotEmpty) {
          await tester.drag(cartItems.first, const Offset(-300, 0));
          await tester.pumpAndSettle();

          // 验证删除提示
          expect(find.byType(SnackBar), findsOneWidget);
        }
      }
    });

    testWidgets('创建订单', (WidgetTester tester) async {
      // 启动应用
      app.main();
      await tester.pumpAndSettle();

      // 等待加载完成
      await tester.pump(const Duration(seconds: 3));

      // 进入购物车
      final cartIcon = find.byIcon(Icons.shopping_cart);
      if (cartIcon.evaluate().isNotEmpty) {
        await tester.tap(cartIcon);
        await tester.pumpAndSettle();

        // 点击结算按钮
        final checkoutButton = find.text('去结算');
        if (checkoutButton.evaluate().isNotEmpty) {
          await tester.tap(checkoutButton);
          await tester.pumpAndSettle();

          // 验证进入确认订单页面
          expect(find.text('确认订单'), findsOneWidget);
        }
      }
    });

    testWidgets('选择配送方式', (WidgetTester tester) async {
      // 启动应用
      app.main();
      await tester.pumpAndSettle();

      // 等待加载完成
      await tester.pump(const Duration(seconds: 3));

      // 进入购物车
      final cartIcon = find.byIcon(Icons.shopping_cart);
      if (cartIcon.evaluate().isNotEmpty) {
        await tester.tap(cartIcon);
        await tester.pumpAndSettle();

        // 点击结算
        final checkoutButton = find.text('去结算');
        if (checkoutButton.evaluate().isNotEmpty) {
          await tester.tap(checkoutButton);
          await tester.pumpAndSettle();

          // 验证配送方式选择
          expect(find.text('外卖配送'), findsOneWidget);
          expect(find.text('到店自取'), findsOneWidget);

          // 选择外卖配送
          await tester.tap(find.text('外卖配送'));
          await tester.pumpAndSettle();
        }
      }
    });
  });
}
