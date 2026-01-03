/// 应用路由名称常量
class AppRoutes {
  static const String splash = '/';
  static const String login = '/login';
  static const String register = '/register';
  static const String main = '/main';
  static const String home = '/home';
  static const String category = '/category';
  static const String productDetail = '/product-detail';
  static const String cart = '/cart';
  static const String orderConfirm = '/order-confirm';
  static const String orderList = '/order-list';
  static const String orderDetail = '/order-detail';
  static const String orderReview = '/order-review';
  static const String productReviews = '/product-reviews';
  static const String addressList = '/address-list';
  static const String addressEdit = '/address-edit';
  static const String favorites = '/favorites';
  static const String profile = '/profile';
  static const String settings = '/settings';
}

/// 路由守卫
typedef RouteGuard = Future<bool> Function();

/// 路由守卫管理
class RouteGuards {
  /// 认证守卫 - 需要登录才能访问
  static RouteGuard authGuard = () async {
    // 从AuthProvider检查认证状态
    // 这里简化处理,实际应该从Provider获取
    final token = await Future.delayed(
      const Duration(milliseconds: 100),
      () => 'mock_token', // 实际从Storage读取
    );
    return token != null && token.isNotEmpty;
  };

  /// 游客守卫 - 未登录才能访问
  static RouteGuard guestGuard = () async {
    final token = await Future.delayed(
      const Duration(milliseconds: 100),
      () => '', // 实际从Storage读取
    );
    return token.isEmpty;
  };
}
