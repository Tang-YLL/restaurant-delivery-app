import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';
import 'package:flutter_app_new/main.dart' as app;
import 'package:flutter/material.dart';

void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();

  group('用户注册登录流程测试', () {
    testWidgets('完整登录流程', (WidgetTester tester) async {
      // 启动应用
      app.main();
      await tester.pumpAndSettle();

      // 等待启动页面完成
      await tester.pump(const Duration(seconds: 2));

      // 验证进入登录页面
      expect(find.text('登录'), findsOneWidget);

      // 输入手机号
      final phoneField = find.byType(TextField).first;
      await tester.enterText(phoneField, '13900139000');
      await tester.pumpAndSettle();

      // 点击发送验证码按钮
      final sendCodeButton = find.text('发送验证码');
      await tester.tap(sendCodeButton);
      await tester.pumpAndSettle();

      // 等待验证码发送
      await tester.pump(const Duration(seconds: 1));

      // 输入验证码（测试环境固定验证码：1234）
      final codeField = find.byType(TextField).last;
      await tester.enterText(codeField, '1234');
      await tester.pumpAndSettle();

      // 点击登录按钮
      final loginButton = find.text('登录');
      await tester.tap(loginButton);
      await tester.pumpAndSettle();

      // 等待登录完成和页面跳转
      await tester.pump(const Duration(seconds: 3));

      // 验证跳转到主页
      expect(find.text('美食外卖'), findsOneWidget);
    });

    testWidgets('验证码错误提示', (WidgetTester tester) async {
      // 启动应用
      app.main();
      await tester.pumpAndSettle();

      // 输入手机号
      final phoneField = find.byType(TextField).first;
      await tester.enterText(phoneField, '13900139001');
      await tester.pumpAndSettle();

      // 点击发送验证码
      final sendCodeButton = find.text('发送验证码');
      await tester.tap(sendCodeButton);
      await tester.pumpAndSettle();

      // 输入错误验证码
      final codeField = find.byType(TextField).last;
      await tester.enterText(codeField, '0000');
      await tester.pumpAndSettle();

      // 点击登录
      final loginButton = find.text('登录');
      await tester.tap(loginButton);
      await tester.pumpAndSettle();

      // 验证错误提示
      expect(find.text('验证码错误'), findsOneWidget);
    });

    testWidgets('手机号格式验证', (WidgetTester tester) async {
      // 启动应用
      app.main();
      await tester.pumpAndSettle();

      // 输入无效手机号
      final phoneField = find.byType(TextField).first;
      await tester.enterText(phoneField, '123');
      await tester.pumpAndSettle();

      // 尝试发送验证码
      final sendCodeButton = find.text('发送验证码');
      await tester.tap(sendCodeButton);
      await tester.pumpAndSettle();

      // 验证提示信息
      expect(find.text('请输入正确的手机号'), findsOneWidget);
    });
  });
}
