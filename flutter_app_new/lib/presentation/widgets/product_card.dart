import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../data/models/product.dart';
import '../providers/cart_provider.dart';

/// 商品卡片
class ProductCard extends StatelessWidget {
  final Product product;

  const ProductCard({super.key, required this.product});

  @override
  Widget build(BuildContext context) {
    return Card(
      clipBehavior: Clip.antiAlias,
      child: InkWell(
        onTap: () {
          Navigator.pushNamed(
            context,
            '/product-detail',
            arguments: product.id,
          );
        },
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // 商品图片
            Expanded(
              child: Stack(
                children: [
                  Positioned.fill(
                    child: Image.network(
                      product.imageUrl,
                      fit: BoxFit.cover,
                      errorBuilder: (context, error, stackTrace) {
                        return Container(
                          color: Colors.grey[200],
                          child: const Icon(Icons.restaurant, size: 50),
                        );
                      },
                    ),
                  ),

                  // 折扣标签
                  if (product.discount != null)
                    Positioned(
                      top: 8,
                      left: 8,
                      child: Container(
                        padding: const EdgeInsets.symmetric(
                          horizontal: 8,
                          vertical: 4,
                        ),
                        decoration: BoxDecoration(
                          color: Colors.red,
                          borderRadius: BorderRadius.circular(4),
                        ),
                        child: Text(
                          '${product.discount!.toStringAsFixed(0)}% OFF',
                          style: const TextStyle(
                            color: Colors.white,
                            fontSize: 12,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ),
                    ),
                ],
              ),
            ),

            // 商品信息
            Padding(
              padding: const EdgeInsets.all(8.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // 商品名称
                  Text(
                    product.name,
                    style: const TextStyle(
                      fontWeight: FontWeight.bold,
                      fontSize: 14,
                    ),
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                  ),

                  const SizedBox(height: 4),

                  // 评分
                  Row(
                    children: [
                      const Icon(Icons.star, color: Colors.amber, size: 14),
                      const SizedBox(width: 2),
                      Text(
                        product.rating.toString(),
                        style: const TextStyle(fontSize: 12),
                      ),
                      const SizedBox(width: 8),
                      Text(
                        '月销 ${product.sales}',
                        style: TextStyle(
                          fontSize: 12,
                          color: Colors.grey[600],
                        ),
                      ),
                    ],
                  ),

                  const SizedBox(height: 8),

                  // 价格
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              '¥${product.price.toStringAsFixed(2)}',
                              style: TextStyle(
                                color: Theme.of(context).colorScheme.primary,
                                fontWeight: FontWeight.bold,
                                fontSize: 16,
                              ),
                            ),
                            if (product.originalPrice != null)
                              Text(
                                '¥${product.originalPrice!.toStringAsFixed(2)}',
                                style: TextStyle(
                                  color: Colors.grey[400],
                                  fontSize: 12,
                                  decoration: TextDecoration.lineThrough,
                                ),
                              ),
                          ],
                        ),
                      ),

                      // 添加购物车按钮
                      InkWell(
                        onTap: () {
                          context.read<CartProvider>().addToCart(product);
                          ScaffoldMessenger.of(context).showSnackBar(
                            SnackBar(
                              content: Text('${product.name} 已添加到购物车'),
                              duration: const Duration(seconds: 1),
                            ),
                          );
                        },
                        child: Container(
                          padding: const EdgeInsets.all(8),
                          decoration: BoxDecoration(
                            color: Theme.of(context).colorScheme.primary,
                            shape: BoxShape.circle,
                          ),
                          child: const Icon(
                            Icons.add_shopping_cart,
                            color: Colors.white,
                            size: 18,
                          ),
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
