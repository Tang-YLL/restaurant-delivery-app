import 'package:flutter/foundation.dart';
import '../../data/models/order.dart';
import '../../data/models/cart_item.dart';
import '../../repositories/order_repository.dart';

/// OrderProvider - 订单状态管理
class OrderProvider with ChangeNotifier {
  List<Order> _orders = [];
  bool _isLoading = false;
  String? _selectedStatus;
  Order? _currentOrder;
  String? _errorMessage;

  final OrderRepository _repository = OrderRepository();

  List<Order> get orders => _orders;
  bool get isLoading => _isLoading;
  String? get selectedStatus => _selectedStatus;
  Order? get currentOrder => _currentOrder;
  String? get errorMessage => _errorMessage;

  /// 获取筛选后的订单列表
  List<Order> get filteredOrders {
    if (_selectedStatus == null || _selectedStatus == 'all') {
      return _orders;
    }
    return _orders
        .where((order) => order.status.value == _selectedStatus)
        .toList();
  }

  /// 加载订单列表
  Future<void> loadOrders({String? status}) async {
    _isLoading = true;
    _selectedStatus = status;
    notifyListeners();

    try {
      final response = await _repository.getOrders(status: status);

      if (response.success && response.data != null) {
        _orders = (response.data! as List)
            .map((item) => Order.fromJson(item as Map<String, dynamic>))
            .toList();
        // 按创建时间倒序排序
        _orders.sort((a, b) => b.createdAt.compareTo(a.createdAt));
      }
    } catch (e) {
      debugPrint('加载订单失败: $e');
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  /// 创建订单
  Future<bool> createOrder({
    required List<CartItem> items,
    required DeliveryType deliveryType,
    String? deliveryAddress,
    String? contactName,
    String? contactPhone,
    String? remark,
  }) async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      final itemsData = items.map((item) {
        return {
          'product_id': item.product.id,
          'quantity': item.quantity,
          'price': item.product.price,
        };
      }).toList();

      final response = await _repository.createOrder(
        items: itemsData,
        deliveryType: deliveryType.value,
        deliveryAddress: deliveryAddress,
        contactName: contactName,
        contactPhone: contactPhone,
        remark: remark,
      );

      if (response.success && response.data != null) {
        debugPrint('✅ 订单创建API响应成功');
        debugPrint('📦 响应数据: ${response.data}');

        try {
          _currentOrder = Order.fromJson(response.data!);
          debugPrint('✅ Order解析成功: orderId=${_currentOrder!.id}, orderNo=${_currentOrder!.orderNo}');
          debugPrint('📦 订单商品数量: ${_currentOrder!.items.length}');

          _orders.insert(0, _currentOrder!);
          debugPrint('✅ 订单已添加到列表，当前订单总数: ${_orders.length}');

          _isLoading = false;
          notifyListeners();
          return true;
        } catch (parseError) {
          debugPrint('❌ Order解析失败: $parseError');
          debugPrint('堆栈: ${StackTrace.current}');
          _errorMessage = '订单数据解析失败: $parseError';
          _isLoading = false;
          notifyListeners();
          return false;
        }
      }

      debugPrint('❌ 订单创建失败: ${response.message}');
      _errorMessage = response.message ?? '创建订单失败';
      _isLoading = false;
      notifyListeners();
      return false;
    } catch (e, stackTrace) {
      debugPrint('❌ 创建订单异常: $e');
      debugPrint('堆栈: $stackTrace');
      _errorMessage = '创建订单失败: $e';
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }

  /// 获取订单详情
  Future<Order?> getOrderDetail(String orderId) async {
    _isLoading = true;
    notifyListeners();

    try {
      final response = await _repository.getOrderDetail(orderId);

      if (response.success && response.data != null) {
        final order = Order.fromJson(response.data!);
        _currentOrder = order;

        // 更新列表中的订单
        final index = _orders.indexWhere((o) => o.id == orderId);
        if (index >= 0) {
          _orders[index] = order;
        }

        _isLoading = false;
        notifyListeners();
        return order;
      }
      _isLoading = false;
      notifyListeners();
      return null;
    } catch (e) {
      debugPrint('获取订单详情失败: $e');
      _isLoading = false;
      notifyListeners();
      return null;
    }
  }

  /// 取消订单
  Future<bool> cancelOrder(String orderId) async {
    _isLoading = true;
    notifyListeners();

    try {
      final response = await _repository.cancelOrder(orderId);

      if (response.success) {
        // 更新订单状态
        final index = _orders.indexWhere((o) => o.id == orderId);
        if (index >= 0) {
          _orders[index] = _orders[index].copyWith(
            status: OrderStatus.cancelled,
            updatedAt: DateTime.now(),
          );
        }
        if (_currentOrder?.id == orderId) {
          _currentOrder = _currentOrder?.copyWith(
            status: OrderStatus.cancelled,
            updatedAt: DateTime.now(),
          );
        }
        _isLoading = false;
        notifyListeners();
        return true;
      }
      _isLoading = false;
      notifyListeners();
      return false;
    } catch (e) {
      debugPrint('取消订单失败: $e');
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }

  /// 支付订单
  Future<bool> payOrder(String orderId) async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      debugPrint('💰 开始支付订单: $orderId');
      final response = await _repository.payOrder(orderId);

      if (response.success && response.data != null) {
        debugPrint('✅ 支付成功，解析订单数据');
        final updatedOrder = Order.fromJson(response.data!);

        // 更新列表中的订单
        final index = _orders.indexWhere((o) => o.id == orderId);
        if (index >= 0) {
          _orders[index] = updatedOrder;
          debugPrint('✅ 订单列表已更新: index=$index, status=${updatedOrder.status.label}');
        }

        // 更新当前订单
        if (_currentOrder?.id == orderId) {
          _currentOrder = updatedOrder;
          debugPrint('✅ 当前订单已更新');
        }

        _isLoading = false;
        notifyListeners();
        debugPrint('✅ 支付订单完成');
        return true;
      }

      debugPrint('❌ 支付失败: ${response.message}');
      _errorMessage = response.message ?? '支付失败';
      _isLoading = false;
      notifyListeners();
      return false;
    } catch (e, stackTrace) {
      debugPrint('❌ 支付订单异常: $e');
      debugPrint('堆栈: $stackTrace');
      _errorMessage = '支付失败: $e';
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }

  /// 确认收货
  Future<bool> confirmOrder(String orderId) async {
    _isLoading = true;
    notifyListeners();

    try {
      final response = await _repository.confirmOrder(orderId);

      if (response.success) {
        // 更新订单状态为"已完成"
        final index = _orders.indexWhere((o) => o.id == orderId);
        if (index >= 0) {
          _orders[index] = _orders[index].copyWith(
            status: OrderStatus.completed,
            completedAt: DateTime.now(),
            updatedAt: DateTime.now(),
          );
        }
        if (_currentOrder?.id == orderId) {
          _currentOrder = _currentOrder?.copyWith(
            status: OrderStatus.completed,
            completedAt: DateTime.now(),
            updatedAt: DateTime.now(),
          );
        }
        _isLoading = false;
        notifyListeners();
        return true;
      }
      _isLoading = false;
      notifyListeners();
      return false;
    } catch (e) {
      debugPrint('确认收货失败: $e');
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }

  /// 按状态筛选订单
  void filterByStatus(String? status) {
    _selectedStatus = status;
    notifyListeners();
  }

  /// 清除当前订单
  void clearCurrentOrder() {
    _currentOrder = null;
    notifyListeners();
  }

  /// 刷新订单列表
  Future<void> refreshOrders() {
    return loadOrders(status: _selectedStatus);
  }
}
