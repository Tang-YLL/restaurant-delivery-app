import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/product_provider.dart';
import '../providers/cart_provider.dart';
import '../../data/models/product.dart';

/// 商品详情页
class ProductDetailPage extends StatefulWidget {
  final String productId;

  const ProductDetailPage({super.key, required this.productId});

  @override
  State<ProductDetailPage> createState() => _ProductDetailPageState();
}

class _ProductDetailPageState extends State<ProductDetailPage> {
  Product? _product;
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadProduct();
  }

  Future<void> _loadProduct() async {
    final provider = context.read<ProductProvider>();
    final product = await provider.getProductDetail(widget.productId);

    if (mounted) {
      setState(() {
        _product = product;
        _isLoading = false;
      });
    }
  }

  void _addToCart() {
    if (_product == null) return;

    context.read<CartProvider>().addToCart(_product!);

    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('已添加到购物车')),
    );
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return Scaffold(
        appBar: AppBar(title: const Text('商品详情')),
        body: const Center(child: CircularProgressIndicator()),
      );
    }

    if (_product == null) {
      return Scaffold(
        appBar: AppBar(title: const Text('商品详情')),
        body: const Center(child: Text('商品不存在')),
      );
    }

    return Scaffold(
      appBar: AppBar(
        title: Text(_product!.name),
        actions: [
          IconButton(
            icon: const Icon(Icons.shopping_cart),
            onPressed: () {
              Navigator.pushNamed(context, '/cart');
            },
          ),
        ],
      ),
      body: SingleChildScrollView(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // 商品图片
            Container(
              width: double.infinity,
              height: 300,
              decoration: BoxDecoration(
                image: DecorationImage(
                  image: NetworkImage(_product!.imageUrl),
                  fit: BoxFit.cover,
                ),
              ),
            ),

            // 商品信息
            Padding(
              padding: const EdgeInsets.all(16.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // 商品名称
                  Text(
                    _product!.name,
                    style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                          fontWeight: FontWeight.bold,
                        ),
                  ),

                  const SizedBox(height: 8),

                  // 商品描述
                  Text(
                    _product!.description,
                    style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                          color: Colors.grey,
                        ),
                  ),

                  const SizedBox(height: 16),

                  // 价格
                  Row(
                    children: [
                      Text(
                        '¥${_product!.price.toStringAsFixed(2)}',
                        style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                              color: Theme.of(context).colorScheme.primary,
                              fontWeight: FontWeight.bold,
                            ),
                      ),
                      if (_product!.originalPrice != null) ...[
                        const SizedBox(width: 8),
                        Text(
                          '¥${_product!.originalPrice!.toStringAsFixed(2)}',
                          style: Theme.of(context).textTheme.titleMedium?.copyWith(
                                color: Colors.grey,
                                decoration: TextDecoration.lineThrough,
                              ),
                        ),
                      ],
                    ],
                  ),

                  const SizedBox(height: 16),

                  // 评分和销量
                  Row(
                    children: [
                      const Icon(Icons.star, color: Colors.amber, size: 20),
                      const SizedBox(width: 4),
                      Text(_product!.rating.toString()),
                      const SizedBox(width: 16),
                      Text('销量 ${_product!.sales}'),
                    ],
                  ),

                  const SizedBox(height: 24),

                  // 标签
                  if (_product!.tags != null && _product!.tags!.isNotEmpty)
                    Wrap(
                      spacing: 8,
                      children: _product!.tags!
                          .map((tag) => Chip(
                                label: Text(tag),
                                backgroundColor: Theme.of(context)
                                    .colorScheme
                                    .primaryContainer,
                              ))
                          .toList(),
                    ),
                ],
              ),
            ),
          ],
        ),
      ),

      // 底部添加购物车按钮
      bottomNavigationBar: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: SizedBox(
            width: double.infinity,
            child: ElevatedButton(
              onPressed: _addToCart,
              child: const Text('加入购物车'),
            ),
          ),
        ),
      ),
    );
  }
}
