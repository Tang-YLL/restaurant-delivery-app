import 'dart:async';
import '../core/models/api_response.dart';
import '../data/models/user.dart';
import '../data/models/product.dart';
import '../data/models/order.dart';

/// Mock数据服务
class MockService {
  // 模拟延迟
  static Future<T> _delay<T>([T? value]) async {
    await Future.delayed(const Duration(milliseconds: 500));
    return value as T;
  }

  // ============ Mock数据 ============

  /// Mock用户数据
  static const Map<String, dynamic> mockUser = {
    'id': '1',
    'username': 'test_user',
    'email': 'test@example.com',
    'phone': '13800138000',
    'avatar': 'https://via.placeholder.com/150',
    'nickname': '测试用户',
    'createdAt': '2024-01-01T00:00:00.000Z',
  };

  /// Mock商品列表
  static const List<Map<String, dynamic>> mockProducts = [
    {
      'id': '1',
      'name': '经典汉堡',
      'description': '美味多汁的牛肉汉堡,配新鲜蔬菜和特制酱料',
      'price': 28.00,
      'originalPrice': 35.00,
      'imageUrl': 'https://via.placeholder.com/300x200?text=Burger',
      'category': '汉堡',
      'rating': 4.8,
      'sales': 1234,
      'stock': 99,
      'tags': ['热销', '推荐'],
    },
    {
      'id': '2',
      'name': '意大利面',
      'description': '正宗意大利风味,番茄肉酱',
      'price': 32.00,
      'originalPrice': 42.00,
      'imageUrl': 'https://via.placeholder.com/300x200?text=Pasta',
      'category': '意面',
      'rating': 4.6,
      'sales': 856,
      'stock': 50,
      'tags': ['新品'],
    },
    {
      'id': '3',
      'name': '凯撒沙拉',
      'description': '新鲜蔬菜配凯撒酱和烤面包丁',
      'price': 22.00,
      'originalPrice': 28.00,
      'imageUrl': 'https://via.placeholder.com/300x200?text=Salad',
      'category': '沙拉',
      'rating': 4.5,
      'sales': 632,
      'stock': 30,
      'tags': ['健康'],
    },
    {
      'id': '4',
      'name': '炸鸡套餐',
      'description': '酥脆炸鸡配可乐和薯条',
      'price': 38.00,
      'originalPrice': 48.00,
      'imageUrl': 'https://via.placeholder.com/300x200?text=Fried+Chicken',
      'category': '套餐',
      'rating': 4.7,
      'sales': 2341,
      'stock': 100,
      'tags': ['超值', '热门'],
    },
    {
      'id': '5',
      'name': '草莓奶昔',
      'description': '新鲜草莓制作,口感丝滑',
      'price': 18.00,
      'originalPrice': 22.00,
      'imageUrl': 'https://via.placeholder.com/300x200?text=Milkshake',
      'category': '饮品',
      'rating': 4.9,
      'sales': 1876,
      'stock': 60,
      'tags': ['限时优惠'],
    },
  ];

  /// Mock分类列表
  static const List<Map<String, dynamic>> mockCategories = [
    {'id': '1', 'name': '汉堡', 'icon': '🍔', 'count': 25},
    {'id': '2', 'name': '意面', 'icon': '🍝', 'count': 18},
    {'id': '3', 'name': '沙拉', 'icon': '🥗', 'count': 12},
    {'id': '4', 'name': '套餐', 'icon': '🍱', 'count': 30},
    {'id': '5', 'name': '饮品', 'icon': '🥤', 'count': 20},
    {'id': '6', 'name': '甜点', 'icon': '🍰', 'count': 15},
  ];

  // ============ Mock API ============

  /// Mock登录
  static Future<ApiResponse<Map<String, dynamic>>> login(
    String username,
    String password,
  ) async {
    await _delay();

    // 简单验证
    if (username == 'test' && password == '123456') {
      final token = 'mock_jwt_token_${DateTime.now().millisecondsSinceEpoch}';
      final refreshToken = 'mock_refresh_token_${DateTime.now().millisecondsSinceEpoch}';

      return ApiResponse.success({
        'token': token,
        'refreshToken': refreshToken,
        'user': mockUser,
      }, message: '登录成功');
    } else {
      return ApiResponse.error(401, '用户名或密码错误');
    }
  }

  /// Mock注册
  static Future<ApiResponse<Map<String, dynamic>>> register(
    String username,
    String password,
    String email,
  ) async {
    await _delay();

    final token = 'mock_jwt_token_${DateTime.now().millisecondsSinceEpoch}';
    final refreshToken = 'mock_refresh_token_${DateTime.now().millisecondsSinceEpoch}';

    return ApiResponse.success({
      'token': token,
      'refreshToken': refreshToken,
      'user': mockUser,
    }, message: '注册成功');
  }

  /// Mock获取商品列表
  static Future<ApiResponse<List<Map<String, dynamic>>>> getProducts({
    String? category,
    String? search,
  }) async {
    await _delay();

    List<Map<String, dynamic>> products = List.from(mockProducts);

    // 按分类筛选
    if (category != null && category.isNotEmpty) {
      products = products.where((p) => p['category'] == category).toList();
    }

    // 搜索
    if (search != null && search.isNotEmpty) {
      products = products
          .where((p) => p['name'].toString().toLowerCase().contains(search.toLowerCase()))
          .toList();
    }

    return ApiResponse.success(products, message: '获取成功');
  }

  /// Mock获取商品详情
  static Future<ApiResponse<Map<String, dynamic>>> getProductDetail(String id) async {
    await _delay();

    final product = mockProducts.firstWhere(
      (p) => p['id'] == id,
      orElse: () => {},
    );

    if (product.isEmpty) {
      return ApiResponse.error(404, '商品不存在');
    }

    return ApiResponse.success(product, message: '获取成功');
  }

  /// Mock获取分类列表
  static Future<ApiResponse<List<Map<String, dynamic>>>> getCategories() async {
    await _delay();

    return ApiResponse.success(mockCategories, message: '获取成功');
  }

  /// Mock获取用户信息
  static Future<ApiResponse<Map<String, dynamic>>> getUserInfo() async {
    await _delay();

    return ApiResponse.success(mockUser, message: '获取成功');
  }

  /// Mock更新用户信息
  static Future<ApiResponse<Map<String, dynamic>>> updateUserInfo(
    Map<String, dynamic> data,
  ) async {
    await _delay();

    final updatedUser = Map<String, dynamic>.from(mockUser);
    updatedUser.addAll(data);

    return ApiResponse.success(updatedUser, message: '更新成功');
  }

  /// Mock获取购物车
  static Future<ApiResponse<List<Map<String, dynamic>>>> getCart() async {
    await _delay();

    return ApiResponse.success([
      {
        'id': '1',
        'product': mockProducts[0],
        'quantity': 2,
      },
      {
        'id': '2',
        'product': mockProducts[3],
        'quantity': 1,
      },
    ], message: '获取成功');
  }

  /// Mock添加到购物车
  static Future<ApiResponse<Map<String, dynamic>>> addToCart(
    String productId,
    int quantity,
  ) async {
    await _delay();

    return ApiResponse.success({
      'cartItemId': 'cart_${DateTime.now().millisecondsSinceEpoch}',
      'quantity': quantity,
    }, message: '添加成功');
  }

  /// Mock创建订单
  static Future<ApiResponse<Map<String, dynamic>>> createOrder({
    required List<Map<String, dynamic>> items,
    required String deliveryType,
    String? deliveryAddress,
    String? contactName,
    String? contactPhone,
    String? remark,
  }) async {
    await _delay();

    // 计算订单金额
    double totalAmount = items.fold(0, (sum, item) {
      return sum + (item['price'] as double) * (item['quantity'] as int);
    });

    // 配送费
    double deliveryFee = deliveryType == 'delivery' ? 5.0 : 0.0;

    final orderId = 'order_${DateTime.now().millisecondsSinceEpoch}';
    final orderNo = 'ORD${DateTime.now().millisecondsSinceEpoch.toString().substring(8)}';

    return ApiResponse.success({
      'id': orderId,
      'orderNo': orderNo,
      'items': items,
      'totalAmount': totalAmount,
      'deliveryFee': deliveryFee,
      'status': 'pending',
      'deliveryType': deliveryType,
      'deliveryAddress': deliveryAddress,
      'contactName': contactName,
      'contactPhone': contactPhone,
      'remark': remark,
      'createdAt': DateTime.now().toIso8601String(),
      'updatedAt': DateTime.now().toIso8601String(),
    }, message: '订单创建成功');
  }

  /// Mock订单列表
  static final List<Map<String, dynamic>> _mockOrders = [
    {
      'id': 'order_1',
      'orderNo': 'ORD20240101001',
      'items': [
        {
          'id': 'order_item_1',
          'product': {
            'id': '1',
            'name': '经典汉堡',
            'description': '美味多汁的牛肉汉堡',
            'price': 28.00,
            'imageUrl': 'https://via.placeholder.com/300x200?text=Burger',
            'category': '汉堡',
            'rating': 4.8,
            'sales': 1234,
            'stock': 99,
          },
          'quantity': 2,
          'price': 28.00,
        },
      ],
      'totalAmount': 56.00,
      'deliveryFee': 5.00,
      'status': 'completed',
      'deliveryType': 'delivery',
      'deliveryAddress': '北京市朝阳区xxx',
      'contactName': '张三',
      'contactPhone': '13800138000',
      'remark': '少放辣',
      'createdAt': '2024-01-01T10:00:00.000Z',
      'updatedAt': '2024-01-01T11:00:00.000Z',
      'paidAt': '2024-01-01T10:05:00.000Z',
      'completedAt': '2024-01-01T11:00:00.000Z',
    },
    {
      'id': 'order_2',
      'orderNo': 'ORD20240101002',
      'items': [
        {
          'id': 'order_item_2',
          'product': {
            'id': '4',
            'name': '炸鸡套餐',
            'description': '酥脆炸鸡配可乐和薯条',
            'price': 38.00,
            'imageUrl': 'https://via.placeholder.com/300x200?text=Fried+Chicken',
            'category': '套餐',
            'rating': 4.7,
            'sales': 2341,
            'stock': 100,
          },
          'quantity': 1,
          'price': 38.00,
        },
      ],
      'totalAmount': 38.00,
      'deliveryFee': 0.0,
      'status': 'preparing',
      'deliveryType': 'pickup',
      'contactName': '李四',
      'contactPhone': '13900139000',
      'createdAt': '2024-01-01T12:00:00.000Z',
      'updatedAt': '2024-01-01T12:10:00.000Z',
      'paidAt': '2024-01-01T12:10:00.000Z',
    },
    {
      'id': 'order_3',
      'orderNo': 'ORD20240101003',
      'items': [
        {
          'id': 'order_item_3',
          'product': {
            'id': '5',
            'name': '草莓奶昔',
            'description': '新鲜草莓制作,口感丝滑',
            'price': 18.00,
            'imageUrl': 'https://via.placeholder.com/300x200?text=Milkshake',
            'category': '饮品',
            'rating': 4.9,
            'sales': 1876,
            'stock': 60,
          },
          'quantity': 3,
          'price': 18.00,
        },
      ],
      'totalAmount': 54.00,
      'deliveryFee': 5.0,
      'status': 'delivering',
      'deliveryType': 'delivery',
      'deliveryAddress': '北京市海淀区xxx',
      'contactName': '王五',
      'contactPhone': '13700137000',
      'createdAt': '2024-01-01T13:00:00.000Z',
      'updatedAt': '2024-01-01T13:30:00.000Z',
      'paidAt': '2024-01-01T13:05:00.000Z',
    },
  ];

  /// Mock获取订单列表
  static Future<ApiResponse<List<Map<String, dynamic>>>> getOrders({
    String? status,
  }) async {
    await _delay();

    List<Map<String, dynamic>> orders = List.from(_mockOrders);

    // 按状态筛选
    if (status != null && status.isNotEmpty && status != 'all') {
      orders = orders.where((o) => o['status'] == status).toList();
    }

    return ApiResponse.success(orders, message: '获取成功');
  }

  /// Mock获取订单详情
  static Future<ApiResponse<Map<String, dynamic>>> getOrderDetail(String orderId) async {
    await _delay();

    final order = _mockOrders.firstWhere(
      (o) => o['id'] == orderId,
      orElse: () => {},
    );

    if (order.isEmpty) {
      return ApiResponse.error(404, '订单不存在');
    }

    return ApiResponse.success(order, message: '获取成功');
  }

  /// Mock取消订单
  static Future<ApiResponse<String>> cancelOrder(String orderId) async {
    await _delay();

    final index = _mockOrders.indexWhere((o) => o['id'] == orderId);
    if (index >= 0) {
      _mockOrders[index]['status'] = 'cancelled';
      _mockOrders[index]['updatedAt'] = DateTime.now().toIso8601String();
      return ApiResponse.success('', message: '订单已取消');
    }

    return ApiResponse.error(404, '订单不存在');
  }

  /// Mock确认收货
  static Future<ApiResponse<String>> confirmOrder(String orderId) async {
    await _delay();

    final index = _mockOrders.indexWhere((o) => o['id'] == orderId);
    if (index >= 0) {
      _mockOrders[index]['status'] = 'completed';
      _mockOrders[index]['completedAt'] = DateTime.now().toIso8601String();
      _mockOrders[index]['updatedAt'] = DateTime.now().toIso8601String();
      return ApiResponse.success('', message: '订单已完成');
    }

    return ApiResponse.error(404, '订单不存在');
  }

  /// Mock发送验证码
  static Future<ApiResponse<String>> sendVerificationCode(String phone) async {
    await _delay();

    // 简单验证手机号格式
    if (phone.length != 11 || !phone.startsWith('1')) {
      return ApiResponse.error(400, '手机号格式不正确');
    }

    return ApiResponse.success('', message: '验证码已发送');
  }

  /// Mock验证验证码
  static Future<ApiResponse<Map<String, dynamic>>> verifyCode(
    String phone,
    String code,
  ) async {
    await _delay();

    // 固定验证码: 1234
    if (code != '1234') {
      return ApiResponse.error(400, '验证码错误');
    }

    final token = 'mock_jwt_token_${DateTime.now().millisecondsSinceEpoch}';
    final refreshToken = 'mock_refresh_token_${DateTime.now().millisecondsSinceEpoch}';

    return ApiResponse.success({
      'token': token,
      'refreshToken': refreshToken,
      'user': mockUser,
    }, message: '登录成功');
  }

  /// Mock商品收藏列表
  static final List<String> _favoriteProducts = [];

  /// Mock获取收藏列表
  static Future<ApiResponse<List<Map<String, dynamic>>>> getFavorites() async {
    await _delay();

    final favoriteProducts = mockProducts.where((p) => _favoriteProducts.contains(p['id'])).toList();

    return ApiResponse.success(favoriteProducts, message: '获取成功');
  }

  /// Mock添加收藏
  static Future<ApiResponse<String>> addFavorite(String productId) async {
    await _delay();

    if (!_favoriteProducts.contains(productId)) {
      _favoriteProducts.add(productId);
    }

    return ApiResponse.success('', message: '收藏成功');
  }

  /// Mock取消收藏
  static Future<ApiResponse<String>> removeFavorite(String productId) async {
    await _delay();

    _favoriteProducts.remove(productId);

    return ApiResponse.success('', message: '已取消收藏');
  }

  /// Mock检查是否已收藏
  bool isFavorite(String productId) {
    return _favoriteProducts.contains(productId);
  }
}
