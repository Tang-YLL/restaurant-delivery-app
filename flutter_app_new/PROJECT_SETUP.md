# Flutter外卖App项目配置文档

## 项目信息

- **项目名称**: flutter_app_new
- **应用名称**: 美食外卖
- **组织**: com.restaurant
- **Bundle ID / Package**: com.restaurant.deliveryapp
- **版本**: 1.0.0 (versionCode: 1)

## 环境要求

- Flutter: 3.38.4+
- Dart: >=3.0.0 <4.0.0
- iOS: 13.0+
- Android: API 21+ (Android 5.0+)
- Android SDK: 36 (compileSdk & targetSdk)

## 项目创建步骤

### 1. 创建Flutter项目

```bash
cd "/Volumes/545S/general final"
flutter create --platforms=ios,android --org com.restaurant flutter_app_new
```

### 2. 安装依赖

```bash
cd flutter_app_new
flutter pub get
```

### 3. 安装iOS依赖

```bash
cd ios
pod install
cd ..
```

## 依赖包说明

### 核心依赖

- **provider**: ^6.1.0 - 状态管理
- **dio**: ^5.4.0 - 网络请求
- **hive**: ^2.2.3 & **hive_flutter**: ^1.1.0 - 本地存储

### UI组件

- **cached_network_image**: ^3.3.0 - 图片缓存
- **shimmer**: ^3.0.0 - 加载动画
- **image_picker**: ^1.0.4 - 图片选择

### 工具库

- **logger**: ^2.0.2 - 日志记录
- **intl**: ^0.19.0 - 国际化

### 通知与权限

- **flutter_local_notifications**: ^19.5.0 - 本地通知
- **permission_handler**: ^11.0.1 - 权限处理

### 开发依赖

- **build_runner**: ^2.4.6 - 代码生成
- **json_serializable**: ^6.7.1 - JSON序列化
- **hive_generator**: ^2.0.1 - Hive代码生成
- **flutter_launcher_icons**: ^0.13.1 - 应用图标
- **flutter_native_splash**: ^2.3.9 - 启动屏

## iOS配置说明

### Info.plist配置

文件位置: `ios/Runner/Info.plist`

**应用配置**:
- CFBundleDisplayName: 美食外卖
- Bundle Identifier: com.restaurant.deliveryapp

**权限描述**:
- NSCameraUsageDescription: 需要使用相机拍摄美食照片
- NSPhotoLibraryUsageDescription: 需要访问相册选择美食图片
- NSLocationWhenInUseUsageDescription: 需要获取您的位置信息以提供配送服务
- NSPhotoLibraryAddUsageDescription: 需要保存美食图片到相册

### Podfile配置

文件位置: `ios/Podfile`

- platform :ios, '13.0'

### iOS依赖安装

```bash
cd ios
pod install
```

## Android配置说明

### build.gradle.kts配置

文件位置: `android/app/build.gradle.kts`

**应用配置**:
```kotlin
namespace = "com.restaurant.deliveryapp"
applicationId = "com.restaurant.deliveryapp"
compileSdk = 36
minSdk = 21
targetSdk = 36
versionCode = 1
versionName = "1.0.0"

// Core library desugaring for compatibility
isCoreLibraryDesugaringEnabled = true
```

**依赖**:
```kotlin
dependencies {
    coreLibraryDesugaring("com.android.tools:desugar_jdk_libs:2.1.4")
}
```

### AndroidManifest.xml配置

文件位置: `android/app/src/main/AndroidManifest.xml`

**应用名称**: 美食外卖

**权限**:
- INTERNET - 网络访问
- CAMERA - 相机
- READ_EXTERNAL_STORAGE - 读取外部存储
- WRITE_EXTERNAL_STORAGE - 写入外部存储
- POST_NOTIFICATIONS - 通知权限

## Clean Architecture目录结构

```
lib/
├── core/
│   ├── config/         # 配置文件
│   ├── constants/      # 常量定义
│   └── utils/          # 工具类
├── data/
│   ├── models/         # 数据模型
│   └── repositories/   # 仓库实现
├── presentation/
│   ├── providers/      # 状态管理Provider
│   ├── pages/          # 页面
│   ├── routes/         # 路由配置
│   └── widgets/        # 通用组件
└── services/           # 服务层
```

## 开发环境配置

### VSCode配置

文件位置: `.vscode/settings.json`

```json
{
  "dart.lineLength": 120
}
```

### Lint规则

文件位置: `analysis_options.yaml`

启用规则:
- prefer_const_constructors
- prefer_const_declarations
- avoid_print

## 运行项目

### iOS模拟器

```bash
flutter run -d ios
```

### Android模拟器

```bash
flutter run -d android
```

### 热重载

在运行时:
- 按 `r` 热重载
- 按 `R` 热重启
- 按 `q` 退出

## 代码生成

### JSON序列化代码生成

```bash
flutter pub run build_runner build
```

### Hive适配器生成

```bash
flutter pub run build_runner build
```

### 清理生成的代码

```bash
flutter pub run build_runner clean
```

## 常见问题

### CocoaPods问题

如果遇到CocoaPods问题:

```bash
cd ios
pod deintegrate
pod install
```

### Android构建问题

如果遇到Android构建问题:

```bash
cd android
./gradlew clean
cd ..
flutter clean
flutter pub get
```

### 依赖冲突

```bash
flutter pub upgrade
flutter pub outdated
```

## 项目验证

### 验证Flutter环境

```bash
flutter doctor
```

### 验证依赖安装

```bash
flutter pub get
flutter analyze
```

### 验证双平台构建

```bash
# iOS
flutter build ios --debug

# Android
flutter build apk --debug
```

## 后续步骤

1. 从 `flutter_app/` 迁移业务代码
2. 实现数据模型
3. 实现API服务
4. 实现状态管理
5. 实现UI页面
6. 配置应用图标和启动屏

## 参考资源

- [Flutter文档](https://flutter.dev/docs)
- [Dart语言指南](https://dart.dev/guides)
- [Provider状态管理](https://pub.dev/packages/provider)
- [Dio网络请求](https://pub.dev/packages/dio)
- [Hive本地存储](https://pub.dev/packages/hive)
