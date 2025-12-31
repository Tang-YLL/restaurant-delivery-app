import 'package:flutter/material.dart';
import 'app_routes.dart';
import '../pages/splash_page.dart';
import '../pages/login_page.dart';
import '../pages/main_page.dart';
import '../pages/home_page.dart';
import '../pages/product_detail_page.dart';
import '../pages/cart_page.dart';
import '../pages/category_page.dart';
import '../pages/order_list_page.dart';
import '../pages/order_detail_page.dart';
import '../pages/order_confirm_page.dart';
import '../pages/profile_page.dart';
import '../pages/review_page.dart';
import '../pages/review_list_page.dart';
import '../pages/address_list_page.dart';
import '../pages/address_edit_page.dart';
import '../pages/favorites_page.dart';
import 'package:provider/provider.dart';
import '../providers/auth_provider.dart';
import '../../data/models/order.dart';

/// 路由生成器
class RouteGenerator {
  static Route<dynamic> generateRoute(RouteSettings settings) {
    final args = settings.arguments;

    switch (settings.name) {
      case AppRoutes.splash:
        return MaterialPageRoute(
          builder: (_) => const SplashPage(),
        );

      case AppRoutes.login:
        return MaterialPageRoute(
          builder: (_) => const LoginPage(),
        );

      case AppRoutes.main:
        return MaterialPageRoute(
          builder: (_) => const MainPage(),
        );

      case AppRoutes.home:
        return MaterialPageRoute(
          builder: (_) => const MainPage(initialIndex: 0),
        );

      case AppRoutes.category:
        return MaterialPageRoute(
          builder: (_) => const MainPage(initialIndex: 1),
        );

      case AppRoutes.productDetail:
        if (args is String) {
          return MaterialPageRoute(
            builder: (_) => ProductDetailPage(productId: args),
          );
        }
        return _errorRoute();

      case AppRoutes.cart:
        return MaterialPageRoute(
          builder: (_) => const MainPage(initialIndex: 2),
        );

      case AppRoutes.orderConfirm:
        return MaterialPageRoute(
          builder: (_) => const OrderConfirmPage(),
        );

      case AppRoutes.orderList:
        return MaterialPageRoute(
          builder: (_) => const MainPage(initialIndex: 3),
        );

      case AppRoutes.orderDetail:
        if (args is String) {
          return MaterialPageRoute(
            builder: (_) => OrderDetailPage(orderId: args),
          );
        }
        return _errorRoute();

      case AppRoutes.orderReview:
        if (args is Order) {
          return MaterialPageRoute(
            builder: (_) => OrderReviewPage(order: args),
          );
        }
        return _errorRoute();

      case AppRoutes.productReviews:
        if (args is Map<String, String>) {
          return MaterialPageRoute(
            builder: (_) => ProductReviewsPage(
              productId: args['productId']!,
              productName: args['productName'] ?? '',
            ),
          );
        }
        return _errorRoute();

      case AppRoutes.addressList:
        final isSelectMode = args is bool ? args : false;
        return MaterialPageRoute(
          builder: (_) => AddressListPage(isSelectMode: isSelectMode),
        );

      case AppRoutes.addressEdit:
        if (args == null) {
          return MaterialPageRoute(
            builder: (_) => const AddressEditPage(),
          );
        } else if (args is Address) {
          return MaterialPageRoute(
            builder: (_) => AddressEditPage(address: args),
          );
        }
        return _errorRoute();

      case AppRoutes.favorites:
        return MaterialPageRoute(
          builder: (_) => const FavoritesPage(),
        );

      case AppRoutes.profile:
        return MaterialPageRoute(
          builder: (_) => const MainPage(initialIndex: 4),
        );

      default:
        return _errorRoute();
    }
  }

  static Route<dynamic> _errorRoute() {
    return MaterialPageRoute(
      builder: (_) => Scaffold(
        appBar: AppBar(title: const Text('错误')),
        body: const Center(
          child: Text('页面未找到'),
        ),
      ),
    );
  }
}
