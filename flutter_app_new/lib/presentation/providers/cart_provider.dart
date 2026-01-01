import 'package:flutter/foundation.dart';
import '../../data/models/product.dart';
import '../../data/models/cart_item.dart';
import '../../repositories/cart_repository.dart';

/// CartProvider - 购物车状态管理
class CartProvider with ChangeNotifier {
  List<CartItem> _items = [];
  bool _isLoading = false;

  final CartRepository _repository = CartRepository();

  List<CartItem> get items => _items;
  bool get isLoading => _isLoading;

  // 购物车商品数量
  int get itemCount => _items.fold(0, (sum, item) => sum + item.quantity);

  // 购物车总价
  double get totalAmount => _items.fold(0.0, (sum, item) => sum + item.subtotal);

  CartProvider() {
    loadCart();
  }

  /// 加载购物车
  Future<void> loadCart() async {
    _isLoading = true;
    notifyListeners();

    try {
      final response = await _repository.getCart();

      if (response.success && response.data != null) {
        _items = (response.data! as List)
            .map((item) => CartItem.fromJson(item as Map<String, dynamic>))
            .toList();
      }
    } catch (e) {
      debugPrint('加载购物车失败: $e');
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  /// 添加商品到购物车
  Future<bool> addToCart(Product product, {int quantity = 1}) async {
    try {
      // 检查商品是否已在购物车中
      final existingIndex = _items.indexWhere((item) => item.product.id == product.id);

      if (existingIndex >= 0) {
        // 已存在,增加数量
        _items[existingIndex].quantity += quantity;
      } else {
        // 不存在,添加新项
        final cartItem = CartItem(
          id: 'cart_${DateTime.now().millisecondsSinceEpoch}',
          product: product,
          quantity: quantity,
        );
        _items.add(cartItem);
      }

      notifyListeners();
      return true;
    } catch (e) {
      debugPrint('添加到购物车失败: $e');
      return false;
    }
  }

  /// 从购物车移除商品
  void removeFromCart(String cartItemId) {
    _items.removeWhere((item) => item.id == cartItemId);
    notifyListeners();
  }

  /// 更新商品数量
  void updateQuantity(String cartItemId, int quantity) {
    final index = _items.indexWhere((item) => item.id == cartItemId);

    if (index >= 0) {
      if (quantity <= 0) {
        _items.removeAt(index);
      } else {
        _items[index].quantity = quantity;
      }
      notifyListeners();
    }
  }

  /// 清空购物车
  void clearCart() {
    _items.clear();
    notifyListeners();
  }

  /// 获取指定商品的数量
  int getProductQuantity(String productId) {
    final item = _items.firstWhere(
      (item) => item.product.id == productId,
      orElse: () => CartItem(
        id: '',
        product: Product(
          id: '',
          name: '',
          description: '',
          price: 0,
          imageUrl: '',
          category: '',
          rating: 0,
          sales: 0,
          stock: 0,
        ),
        quantity: 0,
      ),
    );
    return item.quantity;
  }
}
