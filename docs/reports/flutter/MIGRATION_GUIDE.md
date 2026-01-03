# 代码迁移指南

## 概述

本文档说明如何从旧项目 `flutter_app/` 迁移代码到新项目 `flutter_app_new/`。

## 迁移原则

1. **按模块迁移**: 不要一次性迁移所有代码
2. **保持可运行**: 每个阶段完成后都要确保项目可以运行
3. **测试先行**: 迁移后立即测试相关功能
4. **渐进式迁移**: 先迁移基础功能，再迁移高级功能

## 迁移顺序

### 第一阶段: 基础设施 (2-3天)

#### 1. 常量和配置

**源文件**: `flutter_app/lib/utils/constants.dart`

**目标**: `flutter_app_new/lib/core/constants/`

```bash
cp flutter_app/lib/utils/constants.dart flutter_app_new/lib/core/constants/
```

**任务**:
- [ ] 复制常量定义
- [ ] 更新import路径
- [ ] 验证编译通过

#### 2. 工具类

**源文件**: `flutter_app/lib/utils/`

**目标**: `flutter_app_new/lib/core/utils/`

```bash
cp flutter_app/lib/utils/*.dart flutter_app_new/lib/core/utils/
```

**任务**:
- [ ] 复制所有工具类
- [ ] 更新import路径
- [ ] 移除未使用的工具类

#### 3. 配置文件

**源文件**: `flutter_app/lib/config/`

**目标**: `flutter_app_new/lib/core/config/`

**任务**:
- [ ] 复制API配置
- [ ] 复制应用配置
- [ ] 更新环境配置

### 第二阶段: 数据层 (3-4天)

#### 1. 数据模型

**源文件**: `flutter_app/lib/models/`

**目标**: `flutter_app_new/lib/data/models/`

**步骤**:
```bash
# 复制模型文件
cp flutter_app/lib/models/*.dart flutter_app_new/lib/data/models/

# 生成JSON序列化代码
flutter pub run build_runner build --delete-conflicting-outputs
```

**任务**:
- [ ] 复制所有模型类
- [ ] 添加 @JsonSerializable 注解
- [ ] 生成序列化代码
- [ ] 验证模型序列化/反序列化

#### 2. 本地存储

**源文件**: `flutter_app/lib/services/storage_service.dart`

**目标**: `flutter_app_new/lib/services/storage_service.dart`

**任务**:
- [ ] 复制存储服务
- [ ] 配置Hive初始化
- [ ] 创建Hive适配器
- [ ] 测试存储功能

#### 3. API服务

**源文件**: `flutter_app/lib/services/api_service.dart`

**目标**: `flutter_app_new/lib/services/api_service.dart`

**任务**:
- [ ] 复制API服务
- [ ] 配置Dio实例
- [ ] 实现拦截器
- [ ] 测试API调用

#### 4. 仓库实现

**源文件**: `flutter_app/lib/repositories/`

**目标**: `flutter_app_new/lib/data/repositories/`

**任务**:
- [ ] 复制仓库实现
- [ ] 更新依赖注入
- [ ] 测试仓库方法

### 第三阶段: 状态管理 (3-4天)

#### 1. Provider基础

**源文件**: `flutter_app/lib/providers/`

**目标**: `flutter_app_new/lib/presentation/providers/`

**步骤**:
```bash
cp flutter_app/lib/providers/*.dart flutter_app_new/lib/presentation/providers/
```

**迁移顺序**:
1. base_provider.dart - 基础Provider
2. auth_provider.dart - 认证Provider
3. restaurant_provider.dart - 餐厅Provider
4. cart_provider.dart - 购物车Provider
5. order_provider.dart - 订单Provider

**任务**:
- [ ] 复制Provider文件
- [ ] 更新import路径
- [ ] 修复依赖注入
- [ ] 测试状态管理

### 第四阶段: UI层 (5-7天)

#### 1. 通用组件

**源文件**: `flutter_app/lib/widgets/`

**目标**: `flutter_app_new/lib/presentation/widgets/`

```bash
cp flutter_app/lib/widgets/*.dart flutter_app_new/lib/presentation/widgets/
```

**任务**:
- [ ] 复制通用组件
- [ ] 更新import路径
- [ ] 测试组件渲染

#### 2. 页面

**源文件**: `flutter_app/lib/screens/` 或 `flutter_app/lib/pages/`

**目标**: `flutter_app_new/lib/presentation/pages/`

**迁移顺序**:
1. 启动页/登录页
2. 首页
3. 餐厅列表页
4. 菜品详情页
5. 购物车页
6. 订单页
7. 个人中心页

**任务**:
- [ ] 复制页面文件
- [ ] 更新import路径
- [ ] 更新路由配置
- [ ] 测试页面导航

#### 3. 路由配置

**源文件**: `flutter_app/lib/routes.dart`

**目标**: `flutter_app_new/lib/presentation/routes/app_router.dart`

**任务**:
- [ ] 复制路由配置
- [ ] 更新路由路径
- [ ] 测试页面跳转

### 第五阶段: 资源文件 (1-2天)

#### 1. 图片资源

**源目录**: `flutter_app/assets/images/`

**目标**: `flutter_app_new/assets/images/`

```bash
mkdir -p flutter_app_new/assets/images
cp -r flutter_app/assets/images/* flutter_app_new/assets/images/
```

#### 2. 图标资源

**源目录**: `flutter_app/assets/icons/`

**目标**: `flutter_app_new/assets/icons/`

```bash
mkdir -p flutter_app_new/assets/icons
cp -r flutter_app/assets/icons/* flutter_app_new/assets/icons/
```

#### 3. 更新pubspec.yaml

```yaml
flutter:
  uses-material-design: true

  assets:
    - assets/images/
    - assets/icons/
```

```bash
flutter pub get
```

### 第六阶段: 应用配置 (1天)

#### 1. 应用图标

使用 `flutter_launcher_icons` 生成:

```bash
# 将图标放到 assets/icon/app_icon.png
flutter pub run flutter_launcher_icons
```

#### 2. 启动屏

使用 `flutter_native_splash` 生成:

```bash
# 将启动屏图片放到 assets/icon/splash_logo.png
flutter pub run flutter_native_splash:create
```

### 第七阶段: 测试与优化 (2-3天)

#### 1. 功能测试

**测试清单**:
- [ ] 用户登录/登出
- [ ] 餐厅列表浏览
- [ ] 菜品搜索
- [ ] 购物车操作
- [ ] 订单提交
- [ ] 订单查询
- [ ] 图片上传
- [ ] 推送通知

#### 2. 性能优化

- [ ] 优化图片加载
- [ ] 优化列表滚动
- [ ] 减少不必要的重建
- [ ] 优化网络请求

#### 3. 错误处理

- [ ] 添加全局错误处理
- [ ] 优化错误提示
- [ ] 添加日志记录

## 迁移注意事项

### 1. 路径变更

**旧路径** → **新路径**:
- `lib/utils/` → `lib/core/utils/`
- `lib/models/` → `lib/data/models/`
- `lib/repositories/` → `lib/data/repositories/`
- `lib/providers/` → `lib/presentation/providers/`
- `lib/screens/` → `lib/presentation/pages/`
- `lib/widgets/` → `lib/presentation/widgets/`
- `lib/routes.dart` → `lib/presentation/routes/`

### 2. Import更新

迁移后需要更新所有import语句:

```dart
// 旧
import 'package:food_delivery_app/models/restaurant.dart';
import 'package:food_delivery_app/providers/auth_provider.dart';

// 新
import 'package:flutter_app_new/data/models/restaurant.dart';
import 'package:flutter_app_new/presentation/providers/auth_provider.dart';
```

### 3. 依赖注入

使用Provider的依赖注入时注意:

```dart
MultiProvider(
  providers: [
    ChangeNotifierProvider(create: (_) => AuthProvider()),
    ChangeNotifierProvider(create: (_) => RestaurantProvider()),
    // ... 其他providers
  ],
  child: MyApp(),
)
```

### 4. 资源引用

确保所有资源文件路径正确:

```dart
// 图片
Image.asset('assets/images/logo.png')

// 图标
Image.asset('assets/icons/home.png')
```

### 5. 环境配置

根据环境切换API地址:

```dart
// lib/core/config/api_config.dart
class ApiConfig {
  static const String baseUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: 'https://api.example.com',
  );
}
```

## 验证清单

### 每个阶段完成后

- [ ] 代码无编译错误
- [ ] 无明显警告
- [ ] 相关功能可以正常使用
- [ ] 提交代码到Git

### 最终验证

- [ ] iOS应用可以运行
- [ ] Android应用可以运行
- [ ] 所有核心功能正常
- [ ] 无明显性能问题
- [ ] 代码符合规范

## 常见问题

### Q1: 找不到类或方法

**解决**: 检查import路径是否更新

```bash
# 搜索旧包名
grep -r "food_delivery_app" lib/

# 批量替换
find lib -name "*.dart" -exec sed -i '' 's/food_delivery_app/flutter_app_new/g' {} +
```

### Q2: JSON序列化错误

**解决**: 重新生成代码

```bash
flutter pub run build_runner build --delete-conflicting-outputs
```

### Q3: Provider状态不更新

**解决**: 检查Consumer/Selector使用是否正确

### Q4: 资源文件找不到

**解决**: 检查pubspec.yaml中assets配置

```bash
flutter pub get
flutter clean
flutter run
```

## Git提交策略

每个阶段完成后提交:

```bash
git add .
git commit -m "Issue 011: 迁移第一阶段 - 基础设施"
```

使用详细的commit message:

```
Issue 011: 迁移数据层

- 迁移所有数据模型
- 实现API服务
- 实现本地存储
- 完成仓库层

测试:
- 模型序列化正常
- API调用正常
- 本地存储正常
```

## 回滚计划

如果迁移遇到问题，可以:

1. **回滚到上一个稳定版本**:
   ```bash
   git log --oneline
   git reset --hard <commit-hash>
   ```

2. **保留旧项目**: 旧项目 `flutter_app/` 保持不动，作为参考

3. **分支管理**: 在功能分支上迁移，完成后合并到主分支

## 后续优化

迁移完成后的优化方向:

1. **代码规范**: 统一代码风格
2. **性能优化**: 优化渲染性能
3. **错误处理**: 完善错误处理机制
4. **测试覆盖**: 添加单元测试和集成测试
5. **文档完善**: 补充代码文档和API文档

## 参考资源

- [Flutter文档](https://flutter.dev/docs)
- [Dart语言指南](https://dart.dev/guides)
- [Provider最佳实践](https://pub.dev/packages/provider/example)
- [Clean Architecture](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
