# Food Delivery App

一个使用Flutter开发的美食外卖应用,包含完整的基础架构。

## 技术栈

- **Flutter**: 3.19+
- **状态管理**: Provider ^6.1.0
- **网络请求**: Dio ^5.4.0
- **本地存储**: Hive ^2.2.3
- **UI**: Material Design 3

## 项目结构

```
lib/
├── core/                   # 核心功能
│   ├── config/            # 配置文件
│   │   ├── dio_config.dart      # Dio网络配置
│   │   └── hive_config.dart     # Hive本地存储配置
│   ├── constants/         # 常量定义
│   │   ├── api_constants.dart   # API常量
│   │   └── storage_constants.dart  # 存储常量
│   ├── models/            # 数据模型
│   │   └── api_response.dart     # API响应模型
│   └── utils/             # 工具类
│       └── storage_util.dart     # 存储工具类
├── data/                  # 数据层
│   ├── models/            # 数据模型
│   │   ├── user.dart
│   │   ├── product.dart
│   │   ├── category.dart
│   │   └── cart_item.dart
│   ├── repositories/      # 仓库层(待实现)
│   └── datasources/       # 数据源(待实现)
├── domain/                # 领域层(待实现)
│   ├── entities/
│   ├── repositories/
│   └── usecases/
├── presentation/          # 展示层
│   ├── providers/         # Provider状态管理
│   │   ├── auth_provider.dart
│   │   ├── cart_provider.dart
│   │   ├── theme_provider.dart
│   │   └── product_provider.dart
│   ├── routes/            # 路由配置
│   │   ├── app_routes.dart
│   │   └── route_generator.dart
│   ├── pages/             # 页面
│   │   ├── splash_page.dart
│   │   ├── login_page.dart
│   │   ├── home_page.dart
│   │   ├── product_detail_page.dart
│   │   ├── cart_page.dart
│   │   └── profile_page.dart
│   └── widgets/           # 通用组件
│       ├── product_card.dart
│       └── category_chip.dart
├── services/              # 服务层
│   ├── api_service.dart   # API服务
│   └── mock_service.dart  # Mock数据服务
└── main.dart              # 应用入口
```

## 主要功能

### 1. 认证系统
- 用户登录/注册
- JWT Token管理
- 自动Token注入
- 登录状态持久化

### 2. 商品管理
- 商品列表展示
- 分类筛选
- 搜索功能
- 商品详情

### 3. 购物车
- 添加商品
- 修改数量
- 删除商品
- 价格计算

### 4. 主题系统
- 浅色/深色模式
- 主题持久化
- Material Design 3

### 5. 本地存储
- Hive集成
- Token持久化
- 用户信息缓存

## 快速开始

### 1. 安装依赖

```bash
flutter pub get
```

### 2. 运行代码生成

```bash
# 生成JSON序列化代码
flutter pub run build_runner build

# 生成Hive适配器代码(如需要)
flutter pub run build_runner build --delete-conflicting-outputs
```

### 3. 运行应用

```bash
# iOS
flutter run

# Android
flutter run

# 指定设备
flutter devices
flutter run -d <device_id>
```

## 测试账号

```
用户名: test
密码: 123456
```

## Mock数据

项目内置了Mock服务,可以独立运行测试:

- Mock登录: `MockService.login()`
- Mock商品列表: `MockService.getProducts()`
- Mock商品详情: `MockService.getProductDetail()`
- Mock分类: `MockService.getCategories()`
- Mock购物车: `MockService.getCart()`

## 网络层配置

Dio配置在 `lib/core/config/dio_config.dart`:

- 统一的错误处理
- 自动JWT Token注入
- 请求/响应日志
- 超时配置
- 拦截器系统

## 状态管理

使用Provider进行状态管理:

- **AuthProvider**: 用户认证状态
- **CartProvider**: 购物车状态
- **ThemeProvider**: 主题状态
- **ProductProvider**: 商品状态

## 路由系统

- 命名路由支持
- 路由守卫(待完善)
- 传递参数支持

## 待完成功能

- [ ] 完善路由守卫
- [ ] 实现订单系统
- [ ] 实现支付功能
- [ ] 实现地址管理
- [ ] 添加更多页面
- [ ] 完善单元测试
- [ ] 集成真实后端API

## 注意事项

1. 运行前需要先执行 `flutter pub run build_runner build` 生成模型代码
2. Mock服务用于开发测试,生产环境请替换为真实API
3. Token存储在本地Hive中,登出时会清除

## 许可证

MIT License
