# Flutter项目启动指南

## 前置要求

1. 安装 Flutter SDK (3.19+)
2. 安装 Android Studio 或 Xcode
3. 配置 Android/iOS 模拟器或连接真实设备

## 快速启动

### 1. 进入项目目录

```bash
cd flutter_app
```

### 2. 安装依赖

```bash
flutter pub get
```

### 3. 检查Flutter环境

```bash
flutter doctor
```

确保所有必需的项目都已安装。

### 4. 运行应用

#### 方法一: 使用VS Code / Android Studio
- 打开项目文件夹
- 选择模拟器或设备
- 点击运行按钮

#### 方法二: 使用命令行

```bash
# 查看可用设备
flutter devices

# 运行应用(会自动选择设备)
flutter run

# 指定设备运行
flutter run -d <device_id>
```

### 5. 测试功能

#### 登录测试
- 用户名: `test`
- 密码: `123456`

#### 主要功能
1. ✅ 用户登录/登出
2. ✅ 商品浏览
3. ✅ 分类筛选
4. ✅ 搜索商品
5. ✅ 商品详情
6. ✅ 购物车管理
7. ✅ 主题切换(浅色/深色模式)

## 项目结构说明

```
flutter_app/
├── lib/
│   ├── core/              # 核心功能
│   ├── data/              # 数据模型
│   ├── presentation/      # UI层
│   ├── services/          # 服务层
│   └── main.dart          # 应用入口
├── pubspec.yaml           # 依赖配置
├── README.md              # 项目文档
└── SETUP.md               # 本文件
```

## 常见问题

### Q: 运行时报错 "Error: Not found: 'package:xxx'"
**A:** 运行 `flutter pub get` 安装依赖

### Q: iOS模拟器无法启动
**A:** 确保已安装 Xcode 和 CocoaPods,运行:
```bash
cd ios
pod install
cd ..
```

### Q: Android构建失败
**A:** 检查 Android SDK 版本,确保 compileSdkVersion 至少为 33

### Q: 网络请求失败
**A:** 本项目使用Mock数据,不需要真实后端,直接使用即可

## 开发说明

### 代码生成
项目包含JSON序列化代码,如需重新生成:

```bash
flutter pub run build_runner build
```

### 清理缓存
```bash
flutter clean
flutter pub get
```

### 调试模式
运行时添加调试标志:
```bash
flutter run --debug
```

## 技术支持

- Flutter文档: https://flutter.dev/docs
- Provider文档: https://pub.dev/packages/provider
- Dio文档: https://pub.dev/packages/dio
- Hive文档: https://pub.dev/packages/hive

## 下一步

1. 完善UI界面设计
2. 添加更多页面(订单、地址等)
3. 集成真实后端API
4. 添加单元测试
5. 优化性能和用户体验
