import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/auth_provider.dart';
import '../providers/theme_provider.dart';
import '../providers/order_provider.dart';
import '../providers/favorite_provider.dart';
import '../providers/address_provider.dart';
import '../../data/models/order.dart';
import 'order_list_page.dart';
import 'favorites_page.dart';
import 'address_list_page.dart';
import '../routes/app_routes.dart';

/// 个人中心页面
class ProfilePage extends StatefulWidget {
  const ProfilePage({super.key});

  @override
  State<ProfilePage> createState() => _ProfilePageState();
}

class _ProfilePageState extends State<ProfilePage> {
  @override
  void initState() {
    super.initState();
    _loadData();
  }

  Future<void> _loadData() async {
    // 加载订单统计数据
    context.read<OrderProvider>().loadOrders();
    // 加载收藏数量
    context.read<FavoriteProvider>().loadFavorites();
    // 加载地址列表
    context.read<AddressProvider>().loadAddresses();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('个人中心'),
        actions: [
          IconButton(
            icon: const Icon(Icons.settings),
            onPressed: () {
              // TODO: 导航到设置页面
            },
          ),
        ],
      ),
      body: Consumer<AuthProvider>(
        builder: (context, authProvider, _) {
          if (authProvider.user == null) {
            return Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const Icon(Icons.account_circle, size: 80, color: Colors.grey),
                  const SizedBox(height: 16),
                  const Text('未登录', style: TextStyle(fontSize: 18)),
                  const SizedBox(height: 16),
                  ElevatedButton(
                    onPressed: () {
                      Navigator.pushNamed(context, AppRoutes.login);
                    },
                    child: const Text('立即登录'),
                  ),
                ],
              ),
            );
          }

          final user = authProvider.user!;

          return RefreshIndicator(
            onRefresh: _loadData,
            child: ListView(
              children: [
                // 用户信息卡片
                _buildUserInfoCard(context, user, authProvider),

                const SizedBox(height: 16),

                // 订单统计卡片
                _buildOrderStatsCard(context),

                const SizedBox(height: 16),

                // 功能菜单列表
                _buildMenuList(context),

                const SizedBox(height: 24),

                // 登出按钮
                _buildLogoutButton(context, authProvider),
              ],
            ),
          );
        },
      ),
    );
  }

  Widget _buildUserInfoCard(BuildContext context, dynamic user, AuthProvider authProvider) {
    return Container(
      padding: const EdgeInsets.all(20),
      child: Card(
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            children: [
              GestureDetector(
                onTap: () {
                  // TODO: 更换头像
                },
                child: Stack(
                  children: [
                    CircleAvatar(
                      radius: 50,
                      backgroundImage: user.avatar != null
                          ? NetworkImage(user.avatar!)
                          : null,
                      child: user.avatar == null
                          ? Text(
                              user.nickname?.substring(0, 1) ??
                              user.username?.substring(0, 1) ??
                              'U',
                              style: const TextStyle(fontSize: 36),
                            )
                          : null,
                    ),
                    Positioned(
                      bottom: 0,
                      right: 0,
                      child: Container(
                        padding: const EdgeInsets.all(8),
                        decoration: BoxDecoration(
                          color: Theme.of(context).colorScheme.primary,
                          shape: BoxShape.circle,
                        ),
                        child: const Icon(
                          Icons.camera_alt,
                          color: Colors.white,
                          size: 20,
                        ),
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 16),
              Text(
                user.nickname ?? user.username ?? '用户',
                style: Theme.of(context).textTheme.titleLarge?.copyWith(
                      fontWeight: FontWeight.bold,
                    ),
              ),
              const SizedBox(height: 8),
              if (user.email != null)
                Text(
                  user.email!,
                  style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                        color: Colors.grey,
                      ),
                ),
              if (user.phone != null) ...[
                const SizedBox(height: 4),
                Text(
                  user.phone!,
                  style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                        color: Colors.grey,
                      ),
                ),
              ],
              const SizedBox(height: 16),
              OutlinedButton.icon(
                onPressed: () {
                  // TODO: 编辑个人信息
                },
                icon: const Icon(Icons.edit, size: 18),
                label: const Text('编辑资料'),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildOrderStatsCard(BuildContext context) {
    return Consumer<OrderProvider>(
      builder: (context, orderProvider, _) {
        final orders = orderProvider.orders;

        final pendingCount = orders.where((o) => o.status == OrderStatus.pending).length;
        final deliveringCount = orders.where((o) => o.status == OrderStatus.delivering).length;
        final completedCount = orders.where((o) => o.status == OrderStatus.completed).length;

        return Card(
          margin: const EdgeInsets.symmetric(horizontal: 16),
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      '我的订单',
                      style: Theme.of(context).textTheme.titleMedium?.copyWith(
                            fontWeight: FontWeight.bold,
                          ),
                    ),
                    TextButton(
                      onPressed: () {
                        Navigator.push(
                          context,
                          MaterialPageRoute(
                            builder: (context) => const OrderListPage(),
                          ),
                        );
                      },
                      child: const Text('全部订单'),
                    ),
                  ],
                ),
                const SizedBox(height: 16),
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceAround,
                  children: [
                    _buildOrderStatItem(
                      context,
                      Icons.account_balance_wallet_outlined,
                      '待付款',
                      pendingCount,
                      OrderStatus.pending,
                    ),
                    _buildOrderStatItem(
                      context,
                      Icons.delivery_dining_outlined,
                      '待收货',
                      deliveringCount,
                      OrderStatus.delivering,
                    ),
                    _buildOrderStatItem(
                      context,
                      Icons.check_circle_outline,
                      '已完成',
                      completedCount,
                      OrderStatus.completed,
                    ),
                  ],
                ),
              ],
            ),
          ),
        );
      },
    );
  }

  Widget _buildOrderStatItem(
    BuildContext context,
    IconData icon,
    String label,
    int count,
    OrderStatus status,
  ) {
    return InkWell(
      onTap: () {
        Navigator.push(
          context,
          MaterialPageRoute(
            builder: (context) => OrderListPage(initialStatus: status.value),
          ),
        );
      },
      child: Column(
        children: [
          Stack(
            children: [
              Icon(icon, size: 32, color: Theme.of(context).colorScheme.primary),
              if (count > 0)
                Positioned(
                  top: 0,
                  right: 0,
                  child: Container(
                    padding: const EdgeInsets.all(2),
                    decoration: BoxDecoration(
                      color: Colors.red,
                      shape: BoxShape.circle,
                    ),
                    constraints: const BoxConstraints(minWidth: 18, minHeight: 18),
                    child: Center(
                      child: Text(
                        count > 99 ? '99+' : count.toString(),
                        style: const TextStyle(color: Colors.white, fontSize: 10),
                      ),
                    ),
                  ),
                ),
            ],
          ),
          const SizedBox(height: 8),
          Text(label),
        ],
      ),
    );
  }

  Widget _buildMenuList(BuildContext context) {
    return Card(
      margin: const EdgeInsets.symmetric(horizontal: 16),
      child: Column(
        children: [
          _buildMenuItem(
            context,
            Icons.favorite_border,
            '我的收藏',
            trailing: Consumer<FavoriteProvider>(
              builder: (context, provider, _) {
                return provider.favoriteCount > 0
                    ? Text(
                        provider.favoriteCount.toString(),
                        style: TextStyle(color: Colors.grey[600]),
                      )
                    : const SizedBox.shrink();
              },
            ),
            onTap: () {
              Navigator.push(
                context,
                MaterialPageRoute(builder: (context) => const FavoritesPage()),
              );
            },
          ),
          const Divider(height: 1),
          _buildMenuItem(
            context,
            Icons.location_on_outlined,
            '收货地址',
            onTap: () {
              Navigator.push(
                context,
                MaterialPageRoute(builder: (context) => const AddressListPage()),
              );
            },
          ),
          const Divider(height: 1),
          _buildMenuItem(
            context,
            Icons.receipt_long_outlined,
            '历史订单',
            onTap: () {
              Navigator.push(
                context,
                MaterialPageRoute(builder: (context) => const OrderListPage()),
              );
            },
          ),
          const Divider(height: 1),
          Consumer<ThemeProvider>(
            builder: (context, themeProvider, _) {
              return ListTile(
                leading: const Icon(Icons.dark_mode),
                title: const Text('深色模式'),
                trailing: Switch(
                  value: themeProvider.isDarkMode,
                  onChanged: (_) {
                    themeProvider.toggleTheme();
                  },
                ),
              );
            },
          ),
          const Divider(height: 1),
          _buildMenuItem(
            context,
            Icons.help_outline,
            '帮助与反馈',
            onTap: () {
              // TODO: 导航到帮助页面
            },
          ),
          const Divider(height: 1),
          _buildMenuItem(
            context,
            Icons.info_outline,
            '关于我们',
            onTap: () {
              // TODO: 导航到关于页面
            },
          ),
        ],
      ),
    );
  }

  Widget _buildMenuItem(
    BuildContext context,
    IconData icon,
    String title, {
    Widget? trailing,
    VoidCallback? onTap,
  }) {
    return ListTile(
      leading: Icon(icon),
      title: Text(title),
      trailing: trailing ?? const Icon(Icons.chevron_right),
      onTap: onTap,
    );
  }

  Widget _buildLogoutButton(BuildContext context, AuthProvider authProvider) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 20),
      child: SizedBox(
        width: double.infinity,
        child: ElevatedButton(
          onPressed: () => _showLogoutDialog(context, authProvider),
          style: ElevatedButton.styleFrom(
            backgroundColor: Colors.red,
            foregroundColor: Colors.white,
            padding: const EdgeInsets.symmetric(vertical: 16),
          ),
          child: const Text('退出登录'),
        ),
      ),
    );
  }

  void _showLogoutDialog(BuildContext context, AuthProvider authProvider) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('退出登录'),
        content: const Text('确定要退出登录吗?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('取消'),
          ),
          TextButton(
            onPressed: () {
              authProvider.logout();
              Navigator.pop(context);
              // 不需要手动导航,AuthProvider会处理
            },
            child: const Text('确定'),
          ),
        ],
      ),
    );
  }
}
