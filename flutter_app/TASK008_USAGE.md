# 任务008功能使用指南

## 新增功能概览

### 1. 评价功能

#### 订单评价
在订单详情页面，当订单状态为"已完成"时，可以进入评价页面：

```dart
Navigator.pushNamed(
  context,
  AppRoutes.orderReview,
  arguments: order, // 传入Order对象
);
```

功能：
- 为每个商品单独评分（1-5星）
- 输入文字评价
- 上传评价图片（最多3张）
- 提交后保存到服务器和本地

#### 查看商品评价
```dart
Navigator.pushNamed(
  context,
  AppRoutes.productReviews,
  arguments: {
    'productId': product.id,
    'productName': product.name,
  },
);
```

展示：
- 评价统计（平均分、总评价数）
- 评分分布（5星到1星的百分比）
- 评价列表（用户信息、评分、内容、图片）

### 2. 地址管理

#### 地址列表
```dart
// 查看地址列表
Navigator.pushNamed(context, AppRoutes.addressList);

// 选择地址（下单时）
Navigator.pushNamed(
  context,
  AppRoutes.addressList,
  arguments: true, // isSelectMode = true
);
```

功能：
- 查看所有地址
- 设置默认地址
- 编辑/删除地址
- 选择地址用于下单

#### 添加/编辑地址
```dart
// 添加新地址
Navigator.pushNamed(context, AppRoutes.addressEdit);

// 编辑地址
Navigator.pushNamed(
  context,
  AppRoutes.addressEdit,
  arguments: address, // 传入Address对象
);
```

表单字段：
- 联系人姓名（必填）
- 联系电话（必填，手机号格式验证）
- 省市区（必填）
- 详细地址（必填）
- 地址类型（家/公司/其他）
- 是否默认地址

### 3. 收藏功能

#### 收藏列表
```dart
Navigator.pushNamed(context, AppRoutes.favorites);
```

功能：
- 网格布局展示收藏商品
- 取消收藏
- 清空所有收藏
- 快速添加到购物车
- Hero动画查看商品详情

#### 添加/取消收藏
```dart
final favoriteProvider = context.read<FavoriteProvider>();

// 添加收藏
await favoriteProvider.addFavorite(product);

// 取消收藏
await favoriteProvider.removeFavorite(productId);

// 切换收藏状态
await favoriteProvider.toggleFavorite(product);

// 检查是否已收藏
if (favoriteProvider.isFavorite(productId)) {
  // 已收藏
}
```

### 4. 个人中心增强

#### 订单统计
个人中心页面显示：
- 待付款订单数量
- 待收货订单数量
- 已完成订单数量
- 点击数字快速跳转到对应订单列表

#### 功能菜单
- 我的收藏（带数量徽章）
- 收货地址管理
- 历史订单
- 深色模式切换
- 帮助与反馈
- 关于我们

### 5. UI组件使用

#### 骨架屏加载
在数据加载时使用骨架屏：

```dart
import '../widgets/loading_widgets.dart';

// 商品骨架屏
const ProductSkeleton()

// 订单骨架屏
const OrderSkeleton()

// 评价骨架屏
const ReviewSkeleton()
```

#### 空状态组件
```dart
import '../widgets/empty_state_widget.dart';

// 使用预定义空状态
EmptyStates.cart()
EmptyStates.orders()
EmptyStates.favorites()
EmptyStates.addresses()
EmptyStates.reviews()
EmptyStates.error()
EmptyStates.noSearchResults()

// 自定义空状态
EmptyStateWidget(
  message: '暂无数据',
  subMessage: '点击按钮添加数据',
  icon: Icons.inbox,
  action: ElevatedButton(
    onPressed: () {},
    child: Text('添加'),
  ),
)
```

### 6. 通知功能

#### 初始化通知服务
已在`main.dart`中自动初始化：

```dart
await NotificationService().initialize();
```

#### 发送通知
```dart
final notificationService = NotificationService();

// 订单状态变更通知
await notificationService.showOrderNotification(
  orderId: order.id,
  status: order.status.value,
  statusText: order.status.label,
);

// 促销活动通知
await notificationService.showPromotionNotification(
  title: '限时优惠',
  content: '全场满100减20',
);

// 定时通知
await notificationService.scheduleNotification(
  id: 1,
  title: '订单提醒',
  body: '您的订单即将送达',
  scheduledTime: DateTime.now().add(Duration(minutes: 30)),
);
```

## Provider使用示例

### ReviewProvider
```dart
final reviewProvider = context.read<ReviewProvider>();

// 加载商品评价
await reviewProvider.loadReviews(productId);

// 提交评价
await reviewProvider.submitReview(review);

// 获取评价列表
List<Review> reviews = reviewProvider.reviews;

// 获取评价统计
ReviewStatistics? stats = reviewProvider.statistics;
```

### AddressProvider
```dart
final addressProvider = context.read<AddressProvider>();

// 加载地址列表
await addressProvider.loadAddresses();

// 添加地址
await addressProvider.addAddress(address);

// 更新地址
await addressProvider.updateAddress(address);

// 删除地址
await addressProvider.deleteAddress(addressId);

// 设置默认地址
await addressProvider.setDefaultAddress(addressId);

// 选择地址（下单时）
addressProvider.selectAddress(address);
Address? selected = addressProvider.selectedAddress;

// 获取默认地址
Address? defaultAddress = addressProvider.defaultAddress;
```

### FavoriteProvider
```dart
final favoriteProvider = context.read<FavoriteProvider>();

// 加载收藏列表
await favoriteProvider.loadFavorites();

// 添加收藏
await favoriteProvider.addFavorite(product);

// 取消收藏
await favoriteProvider.removeFavorite(productId);

// 切换收藏状态
await favoriteProvider.toggleFavorite(product);

// 清空所有收藏
await favoriteProvider.clearAll();

// 检查是否已收藏
bool isFav = favoriteProvider.isFavorite(productId);

// 获取收藏数量
int count = favoriteProvider.favoriteCount;
```

## 页面导航示例

### 从订单详情跳转评价
```dart
// 在OrderDetailPage中
ElevatedButton(
  onPressed: () {
    Navigator.pushNamed(
      context,
      AppRoutes.orderReview,
      arguments: widget.order,
    );
  },
  child: Text('评价订单'),
)
```

### 从商品详情查看评价
```dart
// 在ProductDetailPage中
TextButton(
  onPressed: () {
    Navigator.pushNamed(
      context,
      AppRoutes.productReviews,
      arguments: {
        'productId': widget.product.id,
        'productName': widget.product.name,
      },
    );
  },
  child: Text('查看全部评价'),
)
```

### 下单时选择地址
```dart
// 在OrderConfirmPage中
GestureDetector(
  onTap: () async {
    final selectedAddress = await Navigator.pushNamed(
      context,
      AppRoutes.addressList,
      arguments: true, // 选择模式
    );
    if (selectedAddress != null) {
      // 使用选择的地址
      setState(() {
        _selectedAddress = selectedAddress as Address;
      });
    }
  },
  child: Text('选择收货地址'),
)
```

### 在商品卡片添加收藏按钮
```dart
Consumer<FavoriteProvider>(
  builder: (context, favoriteProvider, _) {
    final isFav = favoriteProvider.isFavorite(product.id);
    return IconButton(
      icon: Icon(
        isFav ? Icons.favorite : Icons.favorite_border,
        color: isFav ? Colors.red : null,
      ),
      onPressed: () async {
        await favoriteProvider.toggleFavorite(product);
      },
    );
  },
)
```

## 权限配置

### Android权限
在`android/app/src/main/AndroidManifest.xml`中添加：

```xml
<!-- 相机权限 -->
<uses-permission android:name="android.permission.CAMERA" />

<!-- 存储权限 -->
<uses-permission android:name="android.permission.READ_EXTERNAL_STORAGE" />
<uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE" />

<!-- 通知权限 -->
<uses-permission android:name="android.permission.POST_NOTIFICATIONS" />
```

### iOS权限
在`ios/Runner/Info.plist`中添加：

```xml
<!-- 相册权限 -->
<key>NSPhotoLibraryUsageDescription</key>
<string>需要访问相册选择评价图片</string>
<key>NSPhotoLibraryAddUsageDescription</key>
<string>需要保存图片到相册</string>

<!-- 相机权限 -->
<key>NSCameraUsageDescription</key>
<string>需要使用相机拍摄评价图片</string>

<!-- 通知权限 -->
<key>UIBackgroundModes</key>
<array>
  <string>remote-notification</string>
</array>
```

## 常见问题

### Q: 如何批量评价订单中的所有商品？
A: 在OrderReviewPage中，系统会为每个商品创建独立的评价卡片，用户需要为每个商品单独评分和填写评价内容。

### Q: 地址可以保存多少个？
A: 目前没有限制数量，用户可以根据需要添加任意数量的地址。

### Q: 收藏的商品会被删除吗？
A: 不会。收藏列表持久化存储在本地，除非用户主动删除或清空。

### Q: 通知需要联网吗？
A: 本地通知不需要联网，但如果要实现远程推送通知（FCM），则需要联网连接到推送服务器。

### Q: 如何测试通知功能？
A:
1. 确保设备/模拟器支持通知
2. 确保应用有通知权限
3. 调用NotificationService的相关方法发送通知
4. 检查通知栏是否收到通知

## 下一步优化建议

1. **评价功能**
   - 添加评价点赞功能
   - 商家回复评价
   - 评价图片放大查看

2. **地址管理**
   - 地图定位选择地址
   - 智能地址识别
   - 地址搜索

3. **收藏功能**
   - 收藏分组管理
   - 收藏降价提醒
   - 收藏分享

4. **通知功能**
   - 集成FCM推送
   - 通知分类管理
   - 通知设置页面
