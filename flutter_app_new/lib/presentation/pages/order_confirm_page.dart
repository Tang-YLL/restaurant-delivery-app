import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/cart_provider.dart';
import '../providers/order_provider.dart';
import '../../data/models/order.dart';
import 'package:intl/intl.dart';

/// 确认订单页面
class OrderConfirmPage extends StatefulWidget {
  const OrderConfirmPage({super.key});

  @override
  State<OrderConfirmPage> createState() => _OrderConfirmPageState();
}

class _OrderConfirmPageState extends State<OrderConfirmPage> {
  DeliveryType _deliveryType = DeliveryType.delivery;
  final TextEditingController _addressController = TextEditingController();
  final TextEditingController _nameController = TextEditingController();
  final TextEditingController _phoneController = TextEditingController();
  final TextEditingController _remarkController = TextEditingController();
  final _formKey = GlobalKey<FormState>();

  @override
  void dispose() {
    _addressController.dispose();
    _nameController.dispose();
    _phoneController.dispose();
    _remarkController.dispose();
    super.dispose();
  }

  /// 创建订单
  Future<void> _createOrder() async {
    if (!_formKey.currentState!.validate()) {
      return;
    }

    final cartProvider = context.read<CartProvider>();
    final orderProvider = context.read<OrderProvider>();

    if (cartProvider.items.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('购物车为空')),
      );
      return;
    }

    final success = await orderProvider.createOrder(
      items: cartProvider.items,
      deliveryType: _deliveryType,
      deliveryAddress: _deliveryType == DeliveryType.delivery
          ? _addressController.text
          : null,
      contactName: _nameController.text,
      contactPhone: _phoneController.text,
      remark: _remarkController.text.isEmpty ? null : _remarkController.text,
    );

    if (success && mounted) {
      // 清空购物车
      cartProvider.clearCart();
      // 跳转到订单详情
      if (orderProvider.currentOrder != null) {
        Navigator.of(context).pushReplacementNamed(
          '/order-detail',
          arguments: orderProvider.currentOrder!.id,
        );
      }
    } else if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('创建订单失败')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('确认订单'),
      ),
      body: Form(
        key: _formKey,
        child: Column(
          children: [
            Expanded(
              child: SingleChildScrollView(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // 配送方式选择
                    _buildDeliveryTypeSection(),
                    const SizedBox(height: 16),

                    // 配送信息表单
                    _buildDeliveryForm(),
                    const SizedBox(height: 16),

                    // 商品列表
                    _buildProductsSection(),
                    const SizedBox(height: 16),

                    // 订单备注
                    _buildRemarkSection(),
                  ],
                ),
              ),
            ),

            // 底部结算栏
            _buildBottomBar(),
          ],
        ),
      ),
    );
  }

  /// 配送方式选择
  Widget _buildDeliveryTypeSection() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              '配送方式',
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                Expanded(
                  child: RadioListTile<DeliveryType>(
                    title: const Text('外卖配送'),
                    subtitle: const Text('预计30-45分钟送达'),
                    value: DeliveryType.delivery,
                    groupValue: _deliveryType,
                    onChanged: (value) {
                      setState(() {
                        _deliveryType = value!;
                      });
                    },
                  ),
                ),
                Expanded(
                  child: RadioListTile<DeliveryType>(
                    title: const Text('到店自取'),
                    subtitle: const Text('到店即可取餐'),
                    value: DeliveryType.pickup,
                    groupValue: _deliveryType,
                    onChanged: (value) {
                      setState(() {
                        _deliveryType = value!;
                      });
                    },
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  /// 配送信息表单
  Widget _buildDeliveryForm() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              _deliveryType == DeliveryType.delivery ? '配送信息' : '取餐信息',
              style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 12),
            if (_deliveryType == DeliveryType.delivery) ...[
              TextFormField(
                controller: _addressController,
                maxLines: 2,
                decoration: const InputDecoration(
                  labelText: '配送地址',
                  hintText: '请输入详细地址',
                  prefixIcon: Icon(Icons.location_on),
                  border: OutlineInputBorder(),
                ),
                validator: (value) {
                  if (value == null || value.isEmpty) {
                    return '请输入配送地址';
                  }
                  return null;
                },
              ),
              const SizedBox(height: 12),
            ],
            TextFormField(
              controller: _nameController,
              decoration: InputDecoration(
                labelText: _deliveryType == DeliveryType.delivery
                    ? '联系人'
                    : '取餐人姓名',
                hintText: '请输入姓名',
                prefixIcon: const Icon(Icons.person),
                border: const OutlineInputBorder(),
              ),
              validator: (value) {
                if (value == null || value.isEmpty) {
                  return '请输入姓名';
                }
                return null;
              },
            ),
            const SizedBox(height: 12),
            TextFormField(
              controller: _phoneController,
              keyboardType: TextInputType.phone,
              maxLength: 11,
              decoration: const InputDecoration(
                labelText: '联系电话',
                hintText: '请输入手机号',
                prefixIcon: Icon(Icons.phone),
                border: OutlineInputBorder(),
              ),
              validator: (value) {
                if (value == null || value.isEmpty) {
                  return '请输入手机号';
                }
                if (value.length != 11) {
                  return '请输入正确的手机号';
                }
                return null;
              },
            ),
          ],
        ),
      ),
    );
  }

  /// 商品列表
  Widget _buildProductsSection() {
    return Consumer<CartProvider>(
      builder: (context, cartProvider, _) {
        if (cartProvider.items.isEmpty) {
          return const SizedBox.shrink();
        }

        return Card(
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  '商品清单',
                  style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                ),
                const Divider(height: 16),
                ...cartProvider.items.map((item) {
                  return Padding(
                    padding: const EdgeInsets.only(bottom: 12),
                    child: Row(
                      children: [
                        ClipRRect(
                          borderRadius: BorderRadius.circular(8),
                          child: Image.network(
                            item.product.imageUrl,
                            width: 50,
                            height: 50,
                            fit: BoxFit.cover,
                            errorBuilder: (context, error, stackTrace) {
                              return Container(
                                width: 50,
                                height: 50,
                                color: Colors.grey[200],
                                child: const Icon(Icons.restaurant),
                              );
                            },
                          ),
                        ),
                        const SizedBox(width: 12),
                        Expanded(
                          child: Text(
                            item.product.name,
                            style: const TextStyle(
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ),
                        Text('x${item.quantity}'),
                        const SizedBox(width: 8),
                        Text(
                          '¥${item.subtotal.toStringAsFixed(2)}',
                          style: const TextStyle(
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ],
                    ),
                  );
                }),
              ],
            ),
          ),
        );
      },
    );
  }

  /// 订单备注
  Widget _buildRemarkSection() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              '订单备注',
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 12),
            TextFormField(
              controller: _remarkController,
              maxLines: 3,
              decoration: const InputDecoration(
                hintText: '请输入备注信息(选填)',
                border: OutlineInputBorder(),
              ),
            ),
          ],
        ),
      ),
    );
  }

  /// 底部结算栏
  Widget _buildBottomBar() {
    return Consumer<CartProvider>(
      builder: (context, cartProvider, _) {
        final deliveryFee = _deliveryType == DeliveryType.delivery ? 5.0 : 0.0;
        final totalAmount = cartProvider.totalAmount + deliveryFee;

        return Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: Colors.white,
            boxShadow: [
              BoxShadow(
                color: Colors.grey.withOpacity(0.2),
                blurRadius: 10,
                offset: const Offset(0, -2),
              ),
            ],
          ),
          child: SafeArea(
            child: Row(
              children: [
                Expanded(
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        '合计: ¥${totalAmount.toStringAsFixed(2)}',
                        style: const TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.bold,
                          color: Colors.orange,
                        ),
                      ),
                      Text(
                        '已优惠¥0.00',
                        style: TextStyle(
                          fontSize: 12,
                          color: Colors.grey[600],
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(width: 16),
                ElevatedButton(
                  onPressed: cartProvider.items.isEmpty ? null : _createOrder,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.orange,
                    foregroundColor: Colors.white,
                    padding: const EdgeInsets.symmetric(
                      horizontal: 32,
                      vertical: 12,
                    ),
                  ),
                  child: const Text(
                    '提交订单',
                    style: TextStyle(fontSize: 16),
                  ),
                ),
              ],
            ),
          ),
        );
      },
    );
  }
}
