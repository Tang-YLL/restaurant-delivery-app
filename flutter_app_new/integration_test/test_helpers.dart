import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'test_config.dart';

/// 测试辅助工具类
class TestHelpers {
  /// 等待页面加载完成
  static Future<void> waitForPageLoad(WidgetTester tester) async {
    await tester.pumpAndSettle(TestConfig.pageLoadTimeout);
  }

  /// 等待API响应
  static Future<void> waitForApi(WidgetTester tester) async {
    await tester.pump(TestConfig.apiWaitTimeout);
  }

  /// 等待动画完成
  static Future<void> waitForAnimation(WidgetTester tester) async {
    await tester.pump(TestConfig.animationTimeout);
  }

  /// 等待指定时间
  static Future<void> wait(Duration duration) async {
    await Future.delayed(duration);
  }

  /// 查找包含特定文本的按钮
  static Finder findButtonWithText(String text) {
    return find.widgetWithText(ElevatedButton, text) ||
           find.widgetWithText(TextButton, text) ||
           find.widgetWithText(IconButton, text);
  }

  /// 查找包含特定文本的输入框
  static Finder findTextFieldWithText(String text) {
    return find.byWidgetPredicate(
      (widget) =>
          widget is TextField &&
          widget.decoration?.hintText == text,
    );
  }

  /// 滚动到指定Widget
  static Future<void> scrollToWidget(
    WidgetTester tester,
    Finder scrollable,
    Finder target,
  ) async {
    await tester.scrollUntilVisible(
      target,
      500.0,
      scrollable: scrollable,
    );
    await waitForAnimation(tester);
  }

  /// 验证SnackBar显示
  static bool hasSnackBar(Finder finder) {
    return finder
        .evaluate()
        .any((element) => element.widget is SnackBar);
  }

  /// 验证AlertDialog显示
  static bool hasDialog(WidgetTester tester) {
    return tester
        .widgetList<AlertDialog>(find.byType(AlertDialog))
        .isNotEmpty;
  }

  /// 获取显示的SnackBar消息
  static String? getSnackBarMessage(WidgetTester tester) {
    final snackBar = tester.widget<SnackBar>(find.byType(SnackBar));
    final content = snackBar.content as Text;
    return content.data;
  }

  /// 验证当前路由
  static String? getCurrentRoute(WidgetTester tester) {
    final navigator = tester.widget<Navigator>(find.byType(Navigator));
    // 这里可以根据需要添加路由提取逻辑
    return null;
  }

  /// 打印Widget树（调试用）
  static void printWidgetTree(WidgetTester tester) {
    debugPrint('-- Widget Tree --');
    debugPrint(tester.binding.pipelineOwner.rootElement?.toStringDeep() ?? 'No root element');
    debugPrint('-- End Widget Tree --');
  }

  /// 截图（用于调试）
  static Future<void> takeScreenshot(
    WidgetTester tester,
    String name,
  ) async {
    // integration_test支持截图功能
    // 可以在测试报告中使用
    await binding.takeScreenshot(name);
  }

  static final IntegrationTestWidgetsFlutterBinding binding =
      IntegrationTestWidgetsFlutterBinding.ensureInitialized();
}
