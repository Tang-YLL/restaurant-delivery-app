/// API常量
class ApiConstants {
  // 基础URL (可根据环境切换)
  static const String baseUrl = 'http://localhost:8000/api';

  // 图片基础URL (用于拼接相对路径)
  static const String baseImageUrl = 'http://localhost:8000';

  // API版本
  static const String apiVersion = '/v1';

  // 连接超时时间(毫秒)
  static const int connectTimeout = 15000;
  static const int receiveTimeout = 15000;
  static const int sendTimeout = 15000;

  // API端点
  static const String login = '/auth/login';
  static const String register = '/auth/register';
  static const String logout = '/auth/logout';
  static const String refreshToken = '/auth/refresh';

  static const String products = '/products';
  static const String productDetail = '/products/{id}';
  static const String categories = '/categories';

  static const String cart = '/cart';
  static const String addToCart = '/cart/add';
  static const String updateCart = '/cart/update';
  static const String removeFromCart = '/cart/remove';

  static const String orders = '/orders';
  static const String orderDetail = '/orders/{id}';
  static const String createOrder = '/orders/create';

  static const String userProfile = '/user/profile';
  static const String updateProfile = '/user/profile/update';
}
