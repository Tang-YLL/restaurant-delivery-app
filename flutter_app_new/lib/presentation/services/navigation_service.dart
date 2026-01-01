import 'package:flutter/material.dart';
import '../routes/app_routes.dart';

/// 导航服务 - 用于在应用任何地方进行路由跳转
class NavigationService {
  static GlobalKey<NavigatorState>? _navigatorKey;

  /// 初始化导航服务
  static void initialize(GlobalKey<NavigatorState> navigatorKey) {
    _navigatorKey = navigatorKey;
  }

  /// 获取当前导航上下文
  static BuildContext? get context {
    return _navigatorKey?.currentContext;
  }

  /// 跳转到指定路由
  static Future<void> navigateTo(String routeName) async {
    final navigator = _navigatorKey;
    if (navigator?.currentState == null) return;

    await navigator!.currentState!.pushNamed(routeName);
  }

  /// 替换当前路由
  static Future<void> replaceWith(String routeName) async {
    final navigator = _navigatorKey;
    if (navigator?.currentState == null) return;

    await navigator!.currentState!.pushReplacementNamed(routeName);
  }

  /// 跳转到新路由并清除所有之前的路由
  static Future<void> navigateAndClearAll(String routeName) async {
    final navigator = _navigatorKey;
    if (navigator?.currentState == null) return;

    await navigator!.currentState!.pushNamedAndRemoveUntil(
      routeName,
      (route) => false,
    );
  }

  /// 返回上一页
  static void goBack() {
    final navigator = _navigatorKey;
    if (navigator?.currentState == null) return;

    navigator!.currentState!.pop();
  }

  /// 显示SnackBar
  static void showSnackBar(String message) {
    final context = _navigatorKey?.currentContext;
    if (context == null) return;

    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(message)),
    );
  }

  /// 退出登录并跳转到登录页
  static Future<void> logoutAndNavigateToLogin() async {
    final navigator = _navigatorKey;
    if (navigator?.currentState == null) return;

    // 清除所有路由栈，跳转到登录页
    await navigator!.currentState!.pushNamedAndRemoveUntil(
      AppRoutes.login,
      (route) => false,
    );

    // 显示提示
    showSnackBar('登录已过期，请重新登录');
  }
}
