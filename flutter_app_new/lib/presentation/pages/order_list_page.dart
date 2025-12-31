import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/order_provider.dart';
import '../data/models/order.dart';
import 'order_detail_page.dart';
import 'package:intl/intl.dart';

/// 订单列表页面
class OrderListPage extends StatefulWidget {
  final String? initialStatus; // 初始筛选状态

  const OrderListPage({super.key, this.initialStatus});

  @override
  State<OrderListPage> createState() => _OrderListPageState();
}

class _OrderListPageState extends State<OrderListPage> {
  final List<Map<String, String>> _statusFilters = [
    {'value': 'all', 'label': '全部'},
    {'value': 'pending', 'label': '待付款'},
    {'value': 'preparing', 'label': '制作中'},
    {'value': 'delivering', 'label': '配送中'},
    {'value': 'completed', 'label': '已完成'},
  ];

  @override
  void initState() {
    super.initState();
    Future.microtask(() {
      context.read<OrderProvider>().loadOrders(status: widget.initialStatus);
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('我的订单'),
      ),
      body: Column(
        children: [
          // 状态筛选
          _buildStatusFilter(),
          // 订单列表
          Expanded(
            child: Consumer<OrderProvider>(
              builder: (context, provider, _) {
                if (provider.isLoading && provider.orders.isEmpty) {
                  return const Center(child: CircularProgressIndicator());
                }

                final orders = provider.filteredOrders;

                if (orders.isEmpty) {
                  return const Center(
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Icon(Icons.receipt_long, size: 64, color: Colors.grey),
                        SizedBox(height: 16),
                        Text('暂无订单', style: TextStyle(color: Colors.grey)),
                      ],
                    ),
                  );
                }

                return RefreshIndicator(
                  onRefresh: provider.refreshOrders,
                  child: ListView.builder(
                    padding: const EdgeInsets.all(12),
                    itemCount: orders.length,
                    itemBuilder: (context, index) {
                      return _buildOrderCard(orders[index]);
                    },
                  ),
                );
              },
            ),
          ),
        ],
      ),
    );
  }

  /// 状态筛选栏
  Widget _buildStatusFilter() {
    return Consumer<OrderProvider>(
      builder: (context, provider, _) {
        return Container(
          padding: const EdgeInsets.symmetric(vertical: 12),
          decoration: BoxDecoration(
            color: Colors.white,
            border: Border(bottom: BorderSide(color: Colors.grey[200]!)),
          ),
          child: SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            padding: const EdgeInsets.symmetric(horizontal: 12),
            child: Row(
              children: _statusFilters.map((filter) {
                final isSelected = provider.selectedStatus == filter['value'];
                return Padding(
                  padding: const EdgeInsets.only(right: 12),
                  child: FilterChip(
                    label: Text(filter['label']!),
                    selected: isSelected,
                    onSelected: (selected) {
                      provider.filterByStatus(
                        selected ? filter['value']! : null,
                      );
                      provider.loadOrders(status: filter['value']);
                    },
                    selectedColor: Colors.orange.withOpacity(0.2),
                    checkmarkColor: Colors.orange,
                  ),
                );
              }).toList(),
            ),
          ),
        );
      },
    );
  }

  /// 订单卡片
  Widget _buildOrderCard(Order order) {
    return GestureDetector(
      onTap: () {
        Navigator.of(context).push(
          MaterialPageRoute(
            builder: (context) => OrderDetailPage(orderId: order.id),
          ),
        );
      },
      child: Card(
        margin: const EdgeInsets.only(bottom: 12),
        child: Padding(
          padding: const EdgeInsets.all(12),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // 订单头部
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    '订单号: ${order.orderNo}',
                    style: const TextStyle(fontSize: 12, color: Colors.grey),
                  ),
                  _buildStatusChip(order.status),
                ],
              ),
              const Divider(height: 16),
              // 商品列表
              ...order.items.map((item) => Padding(
                    padding: const EdgeInsets.only(bottom: 8),
                    child: Row(
                      children: [
                        ClipRRect(
                          borderRadius: BorderRadius.circular(8),
                          child: Image.network(
                            item.product.imageUrl,
                            width: 60,
                            height: 60,
                            fit: BoxFit.cover,
                            errorBuilder: (context, error, stackTrace) {
                              return Container(
                                width: 60,
                                height: 60,
                                color: Colors.grey[200],
                                child: const Icon(Icons.restaurant),
                              );
                            },
                          ),
                        ),
                        const SizedBox(width: 12),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                item.product.name,
                                style: const TextStyle(
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                              const SizedBox(height: 4),
                              Text(
                                'x${item.quantity}',
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
              const Divider(height: 16),
              // 订单底部
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    '下单时间: ${DateFormat('yyyy-MM-dd HH:mm').format(order.createdAt)}',
                    style: const TextStyle(fontSize: 12, color: Colors.grey),
                  ),
                  Text(
                    '实付: ¥${order.finalAmount.toStringAsFixed(2)}',
                    style: const TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                      color: Colors.orange,
                    ),
                  ),
                ],
              ),
              if (order.status == OrderStatus.pending) ...[
                const SizedBox(height: 12),
                Row(
                  mainAxisAlignment: MainAxisAlignment.end,
                  children: [
                    OutlinedButton(
                      onPressed: () {
                        _showCancelDialog(order.id);
                      },
                      child: const Text('取消订单'),
                    ),
                    const SizedBox(width: 8),
                    ElevatedButton(
                      onPressed: () {
                        _payOrder(order.id);
                      },
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.orange,
                        foregroundColor: Colors.white,
                      ),
                      child: const Text('去支付'),
                    ),
                  ],
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }

  /// 状态标签
  Widget _buildStatusChip(OrderStatus status) {
    Color color;
    String label;

    switch (status) {
      case OrderStatus.pending:
        color = Colors.orange;
        label = '待付款';
        break;
      case OrderStatus.preparing:
        color = Colors.blue;
        label = '制作中';
        break;
      case OrderStatus.delivering:
        color = Colors.green;
        label = '配送中';
        break;
      case OrderStatus.completed:
        color = Colors.grey;
        label = '已完成';
        break;
      case OrderStatus.cancelled:
        color = Colors.red;
        label = '已取消';
        break;
    }

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(4),
      ),
      child: Text(
        label,
        style: TextStyle(
          color: color,
          fontSize: 12,
          fontWeight: FontWeight.bold,
        ),
      ),
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
      provider.loadOrders();
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
              }
            },
            child: const Text('确定', style: TextStyle(color: Colors.red)),
          ),
        ],
      ),
    );
  }
}
