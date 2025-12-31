# iOS快速开始指南

## 快速启动iOS应用

### 1. 启动模拟器

```bash
# 方法1: 启动默认模拟器
open -a Simulator

# 方法2: 启动特定设备
xcrun simctl boot "iPhone 16 Pro"
```

### 2. 运行应用

```bash
cd flutter_app

# 查看可用设备
flutter devices

# 运行应用（会自动选择设备）
flutter run

# 或指定设备运行
flutter run -d <device_id>
```

### 3. 热重载

应用运行后，修改代码可使用热重载:

```bash
# 在终端中按 'r' 热重载
# 按 'R' 热重启
# 按 'q' 退出
```

### 4. 截图

```bash
# 截取模拟器屏幕
xcrun simctl io <device_id> screenshot screenshot.png
```

## 常用命令

```bash
# 清理构建
flutter clean

# 重新安装依赖
flutter pub get
cd ios && pod install && cd ..

# 检查环境
flutter doctor

# 查看日志
flutter logs
```

## 已知问题

### 应用代码编译错误

当前使用的是简化版测试应用。完整功能应用需要修复编译错误:

1. 恢复原有代码: `cp lib/main.dart.backup lib/main.dart`
2. 修复缺失的导入和模型定义
3. 修复StorageUtil和ApiService方法调用

详见: `TASK011_IOS_CONFIG_REPORT.md`

## 配置文件

- **Bundle ID**: `com.restaurant.deliveryapp`
- **应用名称**: `美食外卖`
- **iOS版本**: ≥ 13.0
- **权限配置**: `ios/Runner/Info.plist`

## 测试截图

运行成功截图: `ios_simulator_screenshot.png`

## 下一步

1. ✅ iOS配置完成
2. ⏳ 修复应用代码错误
3. ⏳ 配置自定义图标
4. ⏳ Release构建测试
5. ⏳ 真机测试（需要Apple Developer账号）

详细文档: `TASK011_IOS_CONFIG_REPORT.md`
