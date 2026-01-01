import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:provider/provider.dart';
import 'package:hive_flutter/hive_flutter.dart';
import 'presentation/providers/theme_provider.dart';
import 'presentation/providers/auth_provider.dart';
import 'presentation/providers/cart_provider.dart';
import 'presentation/providers/product_provider.dart';
import 'presentation/providers/order_provider.dart';
import 'presentation/providers/address_provider.dart';
import 'presentation/providers/favorite_provider.dart';
import 'presentation/providers/review_provider.dart';
import 'presentation/routes/app_routes.dart';
import 'presentation/routes/route_generator.dart';
import 'presentation/services/navigation_service.dart';
import 'core/config/hive_config.dart';

final GlobalKey<NavigatorState> navigatorKey = GlobalKey<NavigatorState>();

void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  // 初始化Hive
  await HiveConfig.init();

  // 初始化导航服务
  NavigationService.initialize(navigatorKey);

  runApp(const FoodDeliveryApp());

  // 设置状态栏样式
  SystemChrome.setSystemUIOverlayStyle(
    const SystemUiOverlayStyle(
      statusBarColor: Colors.transparent,
      statusBarIconBrightness: Brightness.dark,
    ),
  );
}

class FoodDeliveryApp extends StatelessWidget {
  const FoodDeliveryApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        ChangeNotifierProvider.value(value: ThemeProvider()),
        ChangeNotifierProvider.value(value: AuthProvider()),
        ChangeNotifierProvider.value(value: CartProvider()),
        ChangeNotifierProvider.value(value: ProductProvider()),
        ChangeNotifierProvider.value(value: OrderProvider()),
        ChangeNotifierProvider.value(value: AddressProvider()),
        ChangeNotifierProvider.value(value: FavoriteProvider()),
        ChangeNotifierProvider.value(value: ReviewProvider()),
      ],
      child: Consumer<ThemeProvider>(
        builder: (context, themeProvider, _) {
          return MaterialApp(
            title: '美食外卖',
            debugShowCheckedModeBanner: false,
            theme: themeProvider.themeData,
            initialRoute: AppRoutes.splash,
            onGenerateRoute: RouteGenerator.generateRoute,
            navigatorKey: navigatorKey,
          );
        },
      ),
    );
  }
}
