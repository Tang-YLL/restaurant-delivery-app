import 'package:hive/hive.dart';
import 'product.dart';

part 'order.g.dart';

/// 订单状态枚举
enum OrderStatus {
  pending,    // 待付款
  preparing,  // 制作中
  delivering, // 配送中
  completed,  // 已完成
  cancelled,  // 已取消
}

/// 订单状态扩展
extension OrderStatusExtension on OrderStatus {
  String get label {
    switch (this) {
      case OrderStatus.pending:
        return '待付款';
      case OrderStatus.preparing:
        return '制作中';
      case OrderStatus.delivering:
        return '配送中';
      case OrderStatus.completed:
        return '已完成';
      case OrderStatus.cancelled:
        return '已取消';
    }
  }

  String get value {
    switch (this) {
      case OrderStatus.pending:
        return 'pending';
      case OrderStatus.preparing:
        return 'preparing';
      case OrderStatus.delivering:
        return 'delivering';
      case OrderStatus.completed:
        return 'completed';
      case OrderStatus.cancelled:
        return 'cancelled';
    }
  }

  static OrderStatus fromString(String value) {
    switch (value) {
      case 'pending':
        return OrderStatus.pending;
      case 'preparing':
        return OrderStatus.preparing;
      case 'delivering':
        return OrderStatus.delivering;
      case 'completed':
        return OrderStatus.completed;
      case 'cancelled':
        return OrderStatus.cancelled;
      default:
        return OrderStatus.pending;
    }
  }
}

/// 配送方式枚举
enum DeliveryType {
  delivery,  // 外卖配送
  pickup,    // 到店自取
}

/// 配送方式扩展
extension DeliveryTypeExtension on DeliveryType {
  String get label {
    switch (this) {
      case DeliveryType.delivery:
        return '外卖配送';
      case DeliveryType.pickup:
        return '到店自取';
    }
  }

  String get value {
    switch (this) {
      case DeliveryType.delivery:
        return 'delivery';
      case DeliveryType.pickup:
        return 'pickup';
    }
  }

  static DeliveryType fromString(String value) {
    switch (value) {
      case 'delivery':
        return DeliveryType.delivery;
      case 'pickup':
        return DeliveryType.pickup;
      default:
        return DeliveryType.delivery;
    }
  }
}

/// 订单项模型
@HiveType(typeId: 6)
class OrderItem {
  @HiveField(0)
  final String id;

  @HiveField(1)
  final Product product;

  @HiveField(2)
  final int quantity;

  @HiveField(3)
  final double price;

  OrderItem({
    required this.id,
    required this.product,
    required this.quantity,
    required this.price,
  });

  /// 小计
  double get subtotal => price * quantity;

  factory OrderItem.fromJson(Map<String, dynamic> json) {
    return OrderItem(
      id: json['id'] as String,
      product: Product.fromJson(json['product'] as Map<String, dynamic>),
      quantity: json['quantity'] as int,
      price: (json['price'] as num).toDouble(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'product': product.toJson(),
      'quantity': quantity,
      'price': price,
    };
  }

  OrderItem copyWith({
    String? id,
    Product? product,
    int? quantity,
    double? price,
  }) {
    return OrderItem(
      id: id ?? this.id,
      product: product ?? this.product,
      quantity: quantity ?? this.quantity,
      price: price ?? this.price,
    );
  }
}

/// 订单模型
@HiveType(typeId: 5)
class Order {
  @HiveField(0)
  final String id;

  @HiveField(1)
  final String orderNo;

  @HiveField(2)
  final List<OrderItem> items;

  @HiveField(3)
  final double totalAmount;

  @HiveField(4)
  final double deliveryFee;

  @HiveField(5)
  final OrderStatus status;

  @HiveField(6)
  final DeliveryType deliveryType;

  @HiveField(7)
  final String? deliveryAddress;

  @HiveField(8)
  final String? contactName;

  @HiveField(9)
  final String? contactPhone;

  @HiveField(10)
  final String? remark;

  @HiveField(11)
  final DateTime createdAt;

  @HiveField(12)
  final DateTime? updatedAt;

  @HiveField(13)
  final DateTime? paidAt;

  @HiveField(14)
  final DateTime? completedAt;

  Order({
    required this.id,
    required this.orderNo,
    required this.items,
    required this.totalAmount,
    required this.deliveryFee,
    required this.status,
    required this.deliveryType,
    this.deliveryAddress,
    this.contactName,
    this.contactPhone,
    this.remark,
    required this.createdAt,
    this.updatedAt,
    this.paidAt,
    this.completedAt,
  });

  /// 商品总数
  int get itemCount => items.fold(0, (sum, item) => sum + item.quantity);

  /// 实付金额
  double get finalAmount => totalAmount + deliveryFee;

  factory Order.fromJson(Map<String, dynamic> json) {
    return Order(
      id: json['id'] as String,
      orderNo: json['orderNo'] as String,
      items: (json['items'] as List)
          .map((item) => OrderItem.fromJson(item as Map<String, dynamic>))
          .toList(),
      totalAmount: (json['totalAmount'] as num).toDouble(),
      deliveryFee: (json['deliveryFee'] as num?)?.toDouble() ?? 0.0,
      status: OrderStatusExtension.fromString(json['status'] as String),
      deliveryType: DeliveryTypeExtension.fromString(json['deliveryType'] as String),
      deliveryAddress: json['deliveryAddress'] as String?,
      contactName: json['contactName'] as String?,
      contactPhone: json['contactPhone'] as String?,
      remark: json['remark'] as String?,
      createdAt: DateTime.parse(json['createdAt'] as String),
      updatedAt: json['updatedAt'] != null
          ? DateTime.parse(json['updatedAt'] as String)
          : null,
      paidAt: json['paidAt'] != null
          ? DateTime.parse(json['paidAt'] as String)
          : null,
      completedAt: json['completedAt'] != null
          ? DateTime.parse(json['completedAt'] as String)
          : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'orderNo': orderNo,
      'items': items.map((item) => item.toJson()).toList(),
      'totalAmount': totalAmount,
      'deliveryFee': deliveryFee,
      'status': status.value,
      'deliveryType': deliveryType.value,
      'deliveryAddress': deliveryAddress,
      'contactName': contactName,
      'contactPhone': contactPhone,
      'remark': remark,
      'createdAt': createdAt.toIso8601String(),
      'updatedAt': updatedAt?.toIso8601String(),
      'paidAt': paidAt?.toIso8601String(),
      'completedAt': completedAt?.toIso8601String(),
    };
  }

  Order copyWith({
    String? id,
    String? orderNo,
    List<OrderItem>? items,
    double? totalAmount,
    double? deliveryFee,
    OrderStatus? status,
    DeliveryType? deliveryType,
    String? deliveryAddress,
    String? contactName,
    String? contactPhone,
    String? remark,
    DateTime? createdAt,
    DateTime? updatedAt,
    DateTime? paidAt,
    DateTime? completedAt,
  }) {
    return Order(
      id: id ?? this.id,
      orderNo: orderNo ?? this.orderNo,
      items: items ?? this.items,
      totalAmount: totalAmount ?? this.totalAmount,
      deliveryFee: deliveryFee ?? this.deliveryFee,
      status: status ?? this.status,
      deliveryType: deliveryType ?? this.deliveryType,
      deliveryAddress: deliveryAddress ?? this.deliveryAddress,
      contactName: contactName ?? this.contactName,
      contactPhone: contactPhone ?? this.contactPhone,
      remark: remark ?? this.remark,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
      paidAt: paidAt ?? this.paidAt,
      completedAt: completedAt ?? this.completedAt,
    );
  }
}
