import 'package:flutter/material.dart';

/// 空状态组件
class EmptyStateWidget extends StatelessWidget {
  final String message;
  final String? subMessage;
  final IconData? icon;
  final Widget? action;

  const EmptyStateWidget({
    super.key,
    required this.message,
    this.subMessage,
    this.icon,
    this.action,
  });

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            // 图标或插画
            Container(
              width: 120,
              height: 120,
              decoration: BoxDecoration(
                color: Theme.of(context).colorScheme.primaryContainer,
                shape: BoxShape.circle,
              ),
              child: Icon(
                icon ?? Icons.inbox_outlined,
                size: 60,
                color: Theme.of(context).colorScheme.primary,
              ),
            ),
            const SizedBox(height: 24),

            // 主要提示
            Text(
              message,
              style: Theme.of(context).textTheme.titleLarge?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
              textAlign: TextAlign.center,
            ),

            // 次要提示
            if (subMessage != null) ...[
              const SizedBox(height: 8),
              Text(
                subMessage!,
                style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                      color: Colors.grey,
                    ),
                textAlign: TextAlign.center,
              ),
            ],

            // 操作按钮
            if (action != null) ...[
              const SizedBox(height: 24),
              action!,
            ],
          ],
        ),
      ),
    );
  }
}

/// 预定义的空状态组件
class EmptyStates {
  /// 空购物车
  static Widget cart({VoidCallback? onShop}) {
    return EmptyStateWidget(
      icon: Icons.shopping_cart_outlined,
      message: '购物车是空的',
      subMessage: '快去选购喜欢的美食吧',
      action: onShop != null
          ? ElevatedButton(
              onPressed: onShop,
              child: const Text('去购物'),
            )
          : null,
    );
  }

  /// 空订单
  static Widget orders() {
    return const EmptyStateWidget(
      icon: Icons.receipt_long_outlined,
      message: '暂无订单',
      subMessage: '您还没有任何订单记录',
    );
  }

  /// 空收藏
  static Widget favorites() {
    return const EmptyStateWidget(
      icon: Icons.favorite_border,
      message: '暂无收藏',
      subMessage: '收藏喜欢的商品,方便下次购买',
    );
  }

  /// 空地址
  static Widget addresses({VoidCallback? onAdd}) {
    return EmptyStateWidget(
      icon: Icons.location_on_outlined,
      message: '暂无收货地址',
      subMessage: '请添加收货地址以便配送',
      action: onAdd != null
          ? ElevatedButton(
              onPressed: onAdd,
              child: const Text('添加地址'),
            )
          : null,
    );
  }

  /// 空评价
  static Widget reviews() {
    return const EmptyStateWidget(
      icon: Icons.rate_review_outlined,
      message: '暂无评价',
      subMessage: '成为第一个评价的人吧',
    );
  }

  /// 网络错误
  static Widget error({String? message, VoidCallback? onRetry}) {
    return EmptyStateWidget(
      icon: Icons.error_outline,
      message: message ?? '加载失败',
      subMessage: '请检查网络连接后重试',
      action: onRetry != null
          ? ElevatedButton(
              onPressed: onRetry,
              child: const Text('重试'),
            )
          : null,
    );
  }

  /// 无搜索结果
  static Widget noSearchResults() {
    return const EmptyStateWidget(
      icon: Icons.search_off,
      message: '未找到相关结果',
      subMessage: '试试其他搜索词吧',
    );
  }
}
