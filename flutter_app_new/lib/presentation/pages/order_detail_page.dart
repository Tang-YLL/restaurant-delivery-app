import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/order_provider.dart';
import '../../data/models/order.dart';
import 'package:intl/intl.dart';

/// 订单详情页面
class OrderDetailPage extends StatefulWidget {
  final String orderId;

  const OrderDetailPage({super.key, required this.orderId});

  @override
  State<OrderDetailPage> createState() => _OrderDetailPageState();
}

class _OrderDetailPageState extends State<OrderDetailPage> {
  @override
  void initState() {
    super.initState();
    Future.microtask(() {
      context.read<OrderProvider>().getOrderDetail(widget.orderId);
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('订单详情'),
      ),
      body: Consumer<OrderProvider>(
        builder: (context, provider, _) {
          if (provider.isLoading) {
            return const Center(child: CircularProgressIndicator());
          }

          final order = provider.currentOrder;

          if (order == null) {
            return const Center(
              child: Text('订单不存在'),
            );
          }

          return SingleChildScrollView(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // 订单状态
                _buildStatusCard(order),
                const SizedBox(height: 16),

                // 配送信息
                _buildDeliveryCard(order),
                const SizedBox(height: 16),

                // 商品列表
                _buildProductsCard(order),
                const SizedBox(height: 16),

                // 订单信息
                _buildInfoCard(order),
                const SizedBox(height: 16),

                // 价格明细
                _buildPriceCard(order),

                // 底部按钮
                if (order.status == OrderStatus.pending) ...[
                  const SizedBox(height: 24),
                  _buildActionButtons(order),
                ],
              ],
            ),
          );
        },
      ),
    );
  }

  /// 状态卡片
  Widget _buildStatusCard(Order order) {
    IconData icon;
    Color color;
    String title;
    String? subtitle;

    switch (order.status) {
      case OrderStatus.pending:
        icon = Icons.payment;
        color = Colors.orange;
        title = '待付款';
        subtitle = '请尽快完成支付';
        break;
      case OrderStatus.paid:
        icon = Icons.check_circle;
        color = Colors.teal;
        title = '已付款';
        subtitle = '支付成功，等待处理';
        break;
      case OrderStatus.preparing:
        icon = Icons.restaurant;
        color = Colors.blue;
        title = '制作中';
        subtitle = '商家正在为您准备美食';
        break;
      case OrderStatus.ready:
        icon = Icons.fastfood;
        color = Colors.purple;
        title = '待取餐';
        subtitle = '餐品已准备好，请及时取餐';
        break;
      case OrderStatus.delivering:
        icon = Icons.delivery_dining;
        color = Colors.green;
        title = '配送中';
        subtitle = '骑手正在配送中';
        break;
      case OrderStatus.completed:
        icon = Icons.done_all;
        color = Colors.grey;
        title = '已完成';
        subtitle = '订单已完成，感谢您的订购';
        break;
      case OrderStatus.cancelled:
        icon = Icons.cancel;
        color = Colors.red;
        title = '已取消';
        subtitle = '订单已取消';
        break;
    }

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Row(
        children: [
          Icon(icon, size: 48, color: color),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                    color: color,
                  ),
                ),
                if (subtitle != null) ...[
                  const SizedBox(height: 4),
                  Text(
                    subtitle!,
                    style: TextStyle(color: Colors.grey[700]),
                  ),
                ],
              ],
            ),
          ),
        ],
      ),
    );
  }

  /// 配送信息卡片
  Widget _buildDeliveryCard(Order order) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              '配送信息',
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.bold,
                color: Colors.grey[800],
              ),
            ),
            const Divider(height: 16),
            _buildInfoRow('配送方式', order.deliveryType.label),
            if (order.deliveryType == DeliveryType.delivery &&
                order.deliveryAddress != null)
              _buildInfoRow('配送地址', order.deliveryAddress!),
            if (order.contactName != null)
              _buildInfoRow('联系人', order.contactName!),
            if (order.contactPhone != null)
              _buildInfoRow('联系电话', order.contactPhone!),
            if (order.remark != null && order.remark!.isNotEmpty)
              _buildInfoRow('订单备注', order.remark!),
          ],
        ),
      ),
    );
  }

  /// 商品列表卡片
  Widget _buildProductsCard(Order order) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              '商品信息',
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.bold,
                color: Colors.grey[800],
              ),
            ),
            const Divider(height: 16),
            ...order.items.map((item) => Padding(
                  padding: const EdgeInsets.only(bottom: 12),
                  child: Row(
                    children: [
                      ClipRRect(
                        borderRadius: BorderRadius.circular(8),
                        child: item.productImage != null && item.productImage!.isNotEmpty
                            ? Image.network(
                                item.productImage!,
                                width: 60,
                                height: 60,
                                fit: BoxFit.cover,
                                errorBuilder: (context, error, stackTrace) {
                                  return Container(
                                    width: 60,
                                    height: 60,
                                    decoration: BoxDecoration(
                                      color: Colors.grey[200],
                                      borderRadius: BorderRadius.circular(8),
                                    ),
                                    child: Icon(
                                      Icons.restaurant_menu,
                                      color: Colors.grey[400],
                                      size: 30,
                                    ),
                                  );
                                },
                                loadingBuilder: (context, child, loadingProgress) {
                                  if (loadingProgress == null) return child;
                                  return Container(
                                    width: 60,
                                    height: 60,
                                    decoration: BoxDecoration(
                                      color: Colors.grey[100],
                                      borderRadius: BorderRadius.circular(8),
                                    ),
                                    child: Center(
                                      child: CircularProgressIndicator(
                                        value: loadingProgress.expectedTotalBytes != null
                                            ? loadingProgress.cumulativeBytesLoaded /
                                                loadingProgress.expectedTotalBytes!
                                            : null,
                                        strokeWidth: 2,
                                      ),
                                    ),
                                  );
                                },
                              )
                            : Container(
                                width: 60,
                                height: 60,
                                decoration: BoxDecoration(
                                  color: Colors.grey[200],
                                  borderRadius: BorderRadius.circular(8),
                                ),
                                child: Icon(
                                  Icons.restaurant_menu,
                                  color: Colors.grey[400],
                                  size: 30,
                                ),
                              ),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              item.productName,
                              style: const TextStyle(
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                            const SizedBox(height: 4),
                            Text(
                              '¥${item.price.toStringAsFixed(2)} x${item.quantity}',
                              style: TextStyle(
                                color: Colors.grey[600],
                                fontSize: 12,
                              ),
                            ),
                          ],
                        ),
                      ),
                      Text(
                        '¥${item.subtotal.toStringAsFixed(2)}',
                        style: const TextStyle(
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ],
                  ),
                )),
          ],
        ),
      ),
    );
  }

  /// 订单信息卡片
  Widget _buildInfoCard(Order order) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              '订单信息',
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.bold,
                color: Colors.grey[800],
              ),
            ),
            const Divider(height: 16),
            _buildInfoRow('订单号', order.orderNo),
            _buildInfoRow(
              '下单时间',
              DateFormat('yyyy-MM-dd HH:mm:ss').format(order.createdAt),
            ),
            if (order.paidAt != null)
              _buildInfoRow(
                '支付时间',
                DateFormat('yyyy-MM-dd HH:mm:ss').format(order.paidAt!),
              ),
            if (order.completedAt != null)
              _buildInfoRow(
                '完成时间',
                DateFormat('yyyy-MM-dd HH:mm:ss').format(order.completedAt!),
              ),
          ],
        ),
      ),
    );
  }

  /// 价格明细卡片
  Widget _buildPriceCard(Order order) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              '价格明细',
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.bold,
                color: Colors.grey[800],
              ),
            ),
            const Divider(height: 16),
            _buildPriceRow('商品总价', '¥${order.totalAmount.toStringAsFixed(2)}'),
            _buildPriceRow('配送费', '¥${order.deliveryFee.toStringAsFixed(2)}'),
            const Divider(height: 8),
            _buildPriceRow(
              '实付金额',
              '¥${order.finalAmount.toStringAsFixed(2)}',
              isTotal: true,
            ),
          ],
        ),
      ),
    );
  }

  /// 信息行
  Widget _buildInfoRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 80,
            child: Text(
              label,
              style: TextStyle(color: Colors.grey[600]),
            ),
          ),
          Expanded(
            child: Text(value),
          ),
        ],
      ),
    );
  }

  /// 价格行
  Widget _buildPriceRow(String label, String value, {bool isTotal = false}) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(
            label,
            style: TextStyle(
              fontSize: isTotal ? 16 : 14,
              fontWeight: isTotal ? FontWeight.bold : FontWeight.normal,
            ),
          ),
          Text(
            value,
            style: TextStyle(
              fontSize: isTotal ? 18 : 14,
              fontWeight: isTotal ? FontWeight.bold : FontWeight.normal,
              color: isTotal ? Colors.orange : null,
            ),
          ),
        ],
      ),
    );
  }

  /// 操作按钮
  Widget _buildActionButtons(Order order) {
    return Row(
      children: [
        Expanded(
          child: OutlinedButton(
            onPressed: () {
              _showCancelDialog(order.id);
            },
            style: OutlinedButton.styleFrom(
              foregroundColor: Colors.grey[700],
              side: BorderSide(color: Colors.grey[300]!),
              minimumSize: const Size(double.infinity, 48),
            ),
            child: const Text('取消订单'),
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: ElevatedButton(
            onPressed: () {
              _payOrder(order.id);
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.orange,
              foregroundColor: Colors.white,
              minimumSize: const Size(double.infinity, 48),
            ),
            child: const Text('去支付'),
          ),
        ),
      ],
    );
  }

  /// 支付订单
  Future<void> _payOrder(String orderId) async {
    final provider = context.read<OrderProvider>();
    final success = await provider.payOrder(orderId);

    if (success && mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('支付成功')),
      );
    } else if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('支付失败')),
      );
    }
  }

  /// 取消订单对话框
  void _showCancelDialog(String orderId) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('取消订单'),
        content: const Text('确定要取消该订单吗?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('取消'),
          ),
          TextButton(
            onPressed: () async {
              Navigator.of(context).pop();
              final provider = context.read<OrderProvider>();
              final success = await provider.cancelOrder(orderId);
              if (success && mounted) {
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('订单已取消')),
                );
                Navigator.of(context).pop();
              }
            },
            child: const Text('确定', style: TextStyle(color: Colors.red)),
          ),
        ],
      ),
    );
  }
}
